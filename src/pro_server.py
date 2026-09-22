import argparse,json,logging,mimetypes,secrets,sqlite3,sys,threading,webbrowser
from datetime import date,datetime,timedelta
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
from .pro_service import ProService,today
from .pro_analytics import DEFAULT_WEIGHTS
from .pro_backtest import evaluate
from .optimizer import optimize
from .cau import walk_forward as cau_backtest
from .pro_data import update,import_csv,PROVIDERS
from .reports import export_bytes
from .paths import get_data_dir


def integer(v,low=1,high=1000000000):
    if isinstance(v,bool) or not str(v).isdigit() or not low<=int(v)<=high:raise ValueError(f'Cần số nguyên từ {low} đến {high}.')
    return int(v)


def cash_options(data):
    return dict(top_n=integer(data.get('top_n',1),1,10),points=integer(data.get('points',100)),
        cost_rate=integer(data.get('cost_rate',23000)),payout_rate=integer(data.get('payout_rate',80000)))


def iso_day(value):
    return date.fromisoformat(value).isoformat() if value else None

class App:
    def __init__(self,service):
        self.service=service;self.lock=threading.Lock();self.cancel_event=threading.Event()
        self.job=dict(running=False,progress=0,message='Sẵn sàng',result=None,error=None,kind=None)
    def status(self):
        with self.lock:return self.job.copy()
    def progress(self,p,msg):
        with self.lock:self.job.update(progress=p,message=msg)
    def start(self,data):
        kind=data.get('kind')
        if kind not in ('backtest','optimizer','update','cau','prediction'):raise ValueError('Tác vụ không hợp lệ.')
        opts=cash_options(data)
        with self.lock:
            if self.job['running']:raise ValueError('Một tác vụ đang chạy. Chờ hoàn tất hoặc hủy trước.')
            self.cancel_event.clear();self.job=dict(running=True,kind=kind,progress=0,message='Đang khởi động…',error=None,result=None)
        def run():
            try:
                if kind=='update':
                    end=date.fromisoformat(data.get('end') or (today()-timedelta(days=1)).isoformat())
                    if end>today():raise ValueError('Không tải kết quả ngày tương lai.')
                    result=update(self.service.repo,end,integer(data.get('days',180),1,1095),data.get('providers'),progress=self.progress,cancel=self.cancel_event.is_set)
                    self.service.set('last_update',result)
                else:
                    draws=self.service.repo.list_draws()
                    if kind=='prediction':
                        from .forecasting import backtest as forecast_backtest
                        result=forecast_backtest(draws,**{k:v for k,v in opts.items() if k!='top_n'},progress=self.progress,cancel=self.cancel_event.is_set)
                        self.service.set('last_prediction_backtest',result)
                    elif kind=='cau':
                        pair_opts={k:v for k,v in opts.items() if k!='top_n'}
                        result=cau_backtest(draws,window=integer(data.get('window',180),60,730),min_support=integer(data.get('min_support',20),5,100),**pair_opts,progress=self.progress,cancel=self.cancel_event.is_set)
                        self.service.set('last_cau_backtest',result)
                    elif kind=='backtest':
                        # Historical comparison always uses original weights; avoid post-selection optimism.
                        result=evaluate(draws,**opts,progress=self.progress,cancel=self.cancel_event.is_set)
                        self.service.set('last_backtest',result)
                    else:
                        result=optimize(draws,trials=integer(data.get('trials',2000),10,10000),**opts,progress=self.progress,cancel=self.cancel_event.is_set)
                        result['model_id']=self.service.save_model(result)
                with self.lock:self.job.update(running=False,progress=100,message='Hoàn tất',result=result)
            except Exception as e:
                logging.exception('Job failed')
                with self.lock:self.job.update(running=False,error=str(e),message=str(e))
        threading.Thread(target=run,daemon=True).start()
        return {'message':'Đã bắt đầu'}


def make_server(service=None,port=0):
    app=App(service or ProService());token=secrets.token_urlsafe(32)
    web=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent.parent))/'web'
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,fmt,*args):logging.info(fmt,*args)
        def send(self,value,status=200,mime='application/json; charset=utf-8',filename=None):
            raw=value if isinstance(value,bytes) else json.dumps(value,ensure_ascii=False,allow_nan=False).encode()
            self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(len(raw)))
            self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")
            if filename:self.send_header('Content-Disposition',f'attachment; filename="{filename}"')
            self.end_headers();self.wfile.write(raw)
        def allowed(self,api=False):
            host=f'127.0.0.1:{self.server.server_port}'
            if self.headers.get('Host')!=host:self.send({'error':'Host không hợp lệ'},403);return False
            origin=self.headers.get('Origin')
            if origin and origin!=f'http://{host}':self.send({'error':'Origin không hợp lệ'},403);return False
            if api and not secrets.compare_digest(self.headers.get('X-App-Token',''),token):self.send({'error':'Phiên không hợp lệ. Mở lại ứng dụng.'},403);return False
            return True
        def do_GET(self):
            url=urlparse(self.path);path=url.path
            if not self.allowed(path.startswith('/api/')):return
            try:
                args={k:v[0] for k,v in parse_qs(url.query).items()}
                s=app.service
                if path=='/api/health':return self.send({'status':'ok'})
                if path=='/api/state':
                    return self.send(dict(prediction=s.prediction_view(),dashboard=s.dashboard(),last_backtest=s.get('last_backtest'),optimizer=s.get('latest_optimizer'),providers=PROVIDERS,last_update=s.get('last_update')))
                if path=='/api/status':return self.send(app.status())
                if path=='/api/finance':
                    start=iso_day(args.get('start'));end=iso_day(args.get('end'))
                    if start and end and start>end:raise ValueError('Ngày bắt đầu phải trước ngày kết thúc.')
                    return self.send(s.finance(args.get('period','day'),s.get('initial_capital',0),start,end))
                if path=='/api/prediction':return self.send(s.prediction_view())
                if path=='/api/cau':return self.send(s.cau_view(integer(args.get('window',180),60,730),integer(args.get('min_support',20),5,100)))
                if path=='/api/journal':return self.send(s.journal(**cash_options(args)))
                if path=='/api/history':
                    n=f"{integer(args.get('number','0'),0,99):02}";draws=s.repo.list_draws();running=0;rows=[]
                    for d in draws:
                        hits=d.numbers.count(n);running+=hits;rows.append(dict(day=d.day,hits=hits,cumulative=running))
                    return self.send(dict(number=n,rows=rows))
                if path=='/api/data':
                    return self.send({'rows':[dict(day=d.day,numbers=list(d.numbers),special_prize=d.special_prize,source=d.source_url) for d in s.repo.list_draws()]})
                static={'/':'index.html','/app.css':'app.css','/app.js':'app.js'}
                if path not in static:return self.send({'error':'Không tìm thấy'},404)
                file=web/static[path];raw=file.read_bytes()
                if path=='/':raw=raw.replace(b'__APP_TOKEN__',token.encode())
                return self.send(raw,mime=mimetypes.guess_type(str(file))[0] or 'application/octet-stream')
            except Exception as e:
                logging.exception('GET failed');self.send({'error':str(e)},400)
        def do_POST(self):
            if not self.allowed(True):return
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=5_000_000:raise ValueError('Nội dung phải dưới 5 MB.')
                data=json.loads(self.rfile.read(length));s=app.service;path=urlparse(self.path).path
                if not isinstance(data,dict):raise ValueError('Yêu cầu không hợp lệ.')
                if path=='/api/job':return self.send(app.start(data))
                if path=='/api/cancel':app.cancel_event.set();return self.send({'message':'Đã yêu cầu hủy.'})
                if path=='/api/ledger/save':
                    row=s.ledger.save(*(str(data.get(k,'')) for k in ('day','number','points','cost_rate','payout_rate','hits','note')),row_id=integer(data['id']) if data.get('id') else None)
                    return self.send({'id':row,'message':'Đã lưu khoản.'})
                if path=='/api/ledger/delete':s.ledger.delete(integer(data.get('id')));return self.send({'message':'Đã xóa khoản.'})
                if path=='/api/settings':
                    s.set('initial_capital',integer(data.get('initial_capital',0),0,1000000000000));return self.send({'message':'Đã lưu vốn ban đầu.'})
                if path=='/api/model/apply':return self.send(s.activate_model(integer(data.get('id'))))
                if path=='/api/model/reset':s.set('weights',DEFAULT_WEIGHTS);s.set('active_model','Trọng số gốc V2');return self.send({'message':'Đã dùng trọng số gốc.'})
                if path=='/api/import':
                    if app.status()['running']:raise ValueError('Chờ tác vụ đang chạy xong trước khi nhập CSV.')
                    return self.send(import_csv(s.repo,str(data.get('text',''))))
                if path=='/api/export':
                    kind=data.get('kind','ledger');fmt=data.get('format','xlsx');opts=cash_options(data)
                    if kind=='ledger':
                        rows=s.finance('day',s.get('initial_capital',0),iso_day(data.get('start')),iso_day(data.get('end')))['rows'];keys=['day','number','points','cost_rate','payout_rate','hits','cost','received','profit','source','note'];title='Sổ thắng/thua thực tế';note='Đơn vị tiền: đồng. Ô trống = chờ kết quả. ROI chỉ tính khoản đã chốt.'
                    elif kind=='finance':
                        f=s.finance(data.get('period','month'),s.get('initial_capital',0),iso_day(data.get('start')),iso_day(data.get('end')));rows=f['groups'];keys=['day','opening','cost','received','profit','pending_cost','cash','roi'];title='Quản lý vốn thực tế';note=f['explanation']
                    elif kind=='backtest':
                        b=s.get('last_backtest')
                        if not b:raise ValueError('Chạy backtest trước khi xuất.')
                        rows=b['daily'];keys=['day','picks','hits','cost','received','profit','cumulative'];title='Backtest PRO • mô phỏng';note=b['methodology']+f" Top {b['top_n']}, {b['points']} điểm/số, giá mua {b['cost_rate']}, trả {b['payout_rate']} đồng/điểm/nháy. ROI {b['roi']}%."
                    elif kind=='journal':
                        j=s.journal(**opts);rows=j['rows'];keys=['day','created_at','picks','hits','cost','received','profit','kind'];title='Nhật ký dự báo • tiền mô phỏng';note=j['notice']+f" Top {opts['top_n']}, {opts['points']} điểm/số; mua {opts['cost_rate']}, trả {opts['payout_rate']} đồng/điểm/nháy."
                    elif kind=='cau':
                        result=s.cau_view(integer(data.get('window',180),60,730),integer(data.get('min_support',20),5,100));rows=result['pairs'];keys=['a','b','score','either_days','both_days','sample_days','either_rate','both_rate','reasons'];title=f"Cầu lô tô • Xem trước xếp hạng kỳ {result['target']}";note=result['method']+f" Cửa sổ {result['config']['window']} kỳ, tối thiểu {result['config']['min_support']} mẫu mỗi cầu."
                    elif kind=='cau_backtest':
                        b=s.get('last_cau_backtest')
                        if not b:raise ValueError('Chạy kiểm tra cầu trước khi xuất.')
                        rows=b['daily'];keys=['day','picks','hits','both','cost','received','profit','cumulative'];title='Kiểm tra tuyển chọn song thủ';note=b['methodology']+f" {b['points']} điểm/số; mua {b['cost_rate']}, trả {b['payout_rate']} đồng/điểm/nháy."
                    elif kind=='prediction':
                        rows=s.prediction_journal();keys=['day','created_at','bach_thu','song_thu','bach_hits','song_hits','status','kind'];title='Nhật ký dự đoán từ cầu';note='Lựa chọn lần đầu được giữ nguyên. Bản ghi hồi cứu không phải dự báo trực tiếp.'
                    elif kind=='ranking':
                        d=s.dashboard();rows=d['ranking'];keys=['number','score','cluster'];title=f"Xếp hạng kỳ {d['target']}";note='AI Score là xếp hạng tương đối, không phải xác suất trúng.'
                    else:raise ValueError('Loại báo cáo không hợp lệ.')
                    raw,mime=export_bytes(fmt,title,rows,keys,note);return self.send(raw,mime=mime,filename=f'XSMB_{kind}.{fmt}')
                if path=='/api/shutdown':
                    app.cancel_event.set();self.send({'message':'Đã đóng ứng dụng.'});threading.Thread(target=self.server.shutdown,daemon=True).start();return
                self.send({'error':'Không tìm thấy'},404)
            except Exception as e:
                logging.exception('POST failed');self.send({'error':str(e)},400)
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler);server.app=app;server.token=token
    return server


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--no-browser',action='store_true');parser.add_argument('--port',type=int,default=0);args=parser.parse_args()
    directory=get_data_dir();logging.basicConfig(filename=directory/'app_v2.log',level=logging.INFO)
    db=directory/'xsmb.db';backup=directory/'xsmb_before_v2.db'
    if db.exists() and not backup.exists():
        with sqlite3.connect(db) as source,sqlite3.connect(backup) as target:source.backup(target)
    server=make_server(port=args.port);url=f'http://127.0.0.1:{server.server_port}'
    print('XSMB V2.1 PRO:',url,flush=True)
    if not args.no_browser:webbrowser.open(url)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()
