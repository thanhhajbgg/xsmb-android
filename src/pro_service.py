import json
from datetime import date,datetime,timedelta,timezone
from collections import defaultdict
from .storage import Repository
from .paths import get_data_dir
from .ledger import Ledger
from .pro_analytics import rank,confidence,FEATURES,DEFAULT_WEIGHTS,pair_stats

VN=timezone(timedelta(hours=7))

def today():return datetime.now(VN).date()

class ProService:
    def __init__(self,repo=None):
        self.repo=repo or Repository(get_data_dir()/'xsmb.db'); self.ledger=Ledger(self.repo)
        with self.repo.con() as c:
            c.execute('''CREATE TABLE IF NOT EXISTS pro_forecasts(
                target TEXT PRIMARY KEY, created_at TEXT NOT NULL, last_day TEXT NOT NULL,
                picks TEXT NOT NULL, weights TEXT NOT NULL, kind TEXT NOT NULL)''')
            c.execute('CREATE TABLE IF NOT EXISTS pro_pair_forecasts(target TEXT PRIMARY KEY,created_at TEXT NOT NULL,pair TEXT NOT NULL,config TEXT NOT NULL,kind TEXT NOT NULL)')
            c.execute('CREATE TABLE IF NOT EXISTS pro_models(id INTEGER PRIMARY KEY,created_at TEXT NOT NULL,result TEXT NOT NULL)')

    def get(self,key,default=None):
        with self.repo.con() as c:row=c.execute('SELECT value FROM settings WHERE key=?',('pro_'+key,)).fetchone()
        return json.loads(row[0]) if row else default

    def set(self,key,value):
        with self.repo.con() as c:c.execute('INSERT OR REPLACE INTO settings VALUES(?,?)',('pro_'+key,json.dumps(value,ensure_ascii=False)))

    def dashboard(self):
        draws=self.repo.list_draws(); weights=self.get('weights',DEFAULT_WEIGHTS)
        ranked=rank(draws,weights); target=None; warning=''; recorded=[]; recorded_at=None; recorded_kind=None
        if draws:
            target=(date.fromisoformat(draws[-1].day)+timedelta(days=1)).isoformat()
            now=datetime.now(VN)
            kind='live' if target>now.date().isoformat() or (target==now.date().isoformat() and now.hour<18) else 'retrospective'
            if date.fromisoformat(target)<today():warning='Dữ liệu cũ: kỳ phân tích không phải ngày mai. Hãy cập nhật lịch sử.'
            with self.repo.con() as c:
                c.execute('INSERT OR IGNORE INTO pro_forecasts VALUES(?,?,?,?,?,?)',
                    (target,now.isoformat(),draws[-1].day,json.dumps(ranked[:10]),json.dumps(weights),kind))
                snapshot=c.execute('SELECT picks,created_at,kind FROM pro_forecasts WHERE target=?',(target,)).fetchone()
                recorded=json.loads(snapshot[0]);recorded_at=snapshot[1];recorded_kind=snapshot[2]
        gaps=0
        if len(draws)>1:gaps=(date.fromisoformat(draws[-1].day)-date.fromisoformat(draws[0].day)).days+1-len(draws)
        return dict(ranking=ranked,forecast_picks=recorded,forecast_created_at=recorded_at,forecast_kind=recorded_kind,confidence=confidence(draws,weights),last_day=draws[-1].day if draws else None,target=target,
            count=len(draws),gaps=gaps,warning=warning,weights=weights,features=FEATURES,pairs=pair_stats(draws),
            model=self.get('active_model','Trọng số gốc V2'),today=today().isoformat(),initial_capital=self.get('initial_capital',0))

    def journal(self,top_n=5,points=100,cost_rate=23000,payout_rate=80000):
        draws={d.day:d for d in self.repo.list_draws()}; rows=[]
        with self.repo.con() as c:records=c.execute('SELECT * FROM pro_forecasts ORDER BY target DESC').fetchall()
        for target,created,last,picks,weights,kind in records:
            picks=json.loads(picks)[:int(top_n)]; chosen=[x['number'] for x in picks]; draw=draws.get(target)
            matched=[dict(number=n,hits=draw.numbers.count(n)) for n in chosen if draw and n in draw.numbers]
            hits=sum(x['hits'] for x in matched) if draw else None
            cost=len(chosen)*int(points)*int(cost_rate); received=hits*int(points)*int(payout_rate) if hits is not None else None
            rows.append(dict(day=target,created_at=created,last_day=last,picks=chosen,matched=matched,hits=hits,
                cost=cost,received=received,profit=received-cost if received is not None else None,kind=kind,
                result=list(draw.numbers) if draw else None))
        return dict(rows=rows,notice='Nhật ký lưu lựa chọn lần đầu cho từng kỳ; không sửa khi thay mô hình. Tiền ở đây là mô phỏng theo cấu hình hiện tại, không cộng vào vốn thật.')

    def finance(self,period='day',initial=0,start=None,end=None):
        if period not in ('day','week','month','year'):raise ValueError('Kỳ tổng hợp không hợp lệ.')
        all_rows=self.ledger.rows()
        rows=[r for r in all_rows if (not start or r['day']>=start) and (not end or r['day']<=end)]
        opening=float(initial)+sum((r['profit'] if r['profit'] is not None else -r['cost']) for r in all_rows if start and r['day']<start)
        grouped=defaultdict(list)
        for r in rows:
            d=date.fromisoformat(r['day'])
            key=r['day'] if period=='day' else f'{d.isocalendar().year}-W{d.isocalendar().week:02}' if period=='week' else r['day'][:7] if period=='month' else r['day'][:4]
            grouped[key].append(r)
        aggregates=[]; cash=opening
        for key,items in sorted(grouped.items()):
            settled=[r for r in items if r['profit'] is not None]; pending=[r for r in items if r['profit'] is None]
            cost=sum(r['cost'] for r in items); settled_cost=sum(r['cost'] for r in settled)
            received=sum(r['received'] for r in settled); profit=received-settled_cost; pending_cost=sum(r['cost'] for r in pending)
            before=cash; cash+=received-cost
            aggregates.append(dict(day=key,opening=before,cost=cost,received=received,profit=profit,pending_cost=pending_cost,cash=cash,
                roi=round(100*profit/settled_cost,2) if settled_cost else None))
        settled=[r for r in rows if r['profit'] is not None]; pending=[r for r in rows if r['profit'] is None]
        profit=sum(r['profit'] for r in settled); settled_cost=sum(r['cost'] for r in settled)
        return dict(rows=rows,groups=aggregates,initial=float(initial),opening=opening,profit=profit,cost=sum(r['cost'] for r in rows),
            received=sum(r['received'] for r in settled),pending_cost=sum(r['cost'] for r in pending),pending=len(pending),
            cash=cash,equity=opening+profit,roi=round(100*profit/settled_cost,2) if settled_cost else None,
            explanation='Vốn khả dụng = vốn đầu kỳ + tiền nhận − toàn bộ tiền mua. ROI = lãi đã chốt / tiền mua đã chốt. Không tính khoản chờ là thua. Vốn đầu kỳ gồm dòng tiền trước khoảng lọc.')

    def save_model(self,result):
        with self.repo.con() as c:
            model_id=c.execute('INSERT INTO pro_models(created_at,result) VALUES(?,?)',(datetime.now(VN).isoformat(),json.dumps(result))).lastrowid
        self.set('latest_optimizer',dict(id=model_id,result=result))
        return model_id

    def activate_model(self,model_id):
        with self.repo.con() as c:row=c.execute('SELECT result FROM pro_models WHERE id=?',(int(model_id),)).fetchone()
        if not row:raise ValueError('Không tìm thấy mô hình.')
        result=json.loads(row[0]); self.set('weights',result['weights']); self.set('active_model',f'Optimizer #{model_id}')
        return dict(message='Đã áp dụng trọng số. Nhật ký đã lưu không thay đổi.')

    def cau_view(self,window=180,min_support=20):
        from .cau import analyze
        result=analyze(self.repo.list_draws(),window,min_support)
        result['snapshot']=None
        if result['selected']:
            now=datetime.now(VN);target=result['target']
            kind='live' if target>now.date().isoformat() or (target==now.date().isoformat() and now.hour<18) else 'retrospective'
            with self.repo.con() as c:
                c.execute('INSERT OR IGNORE INTO pro_pair_forecasts VALUES(?,?,?,?,?)',(target,now.isoformat(),json.dumps(result['selected']),json.dumps(result['config']),kind))
        if result['target']:
            with self.repo.con() as c:
                row=c.execute('SELECT created_at,pair,config,kind FROM pro_pair_forecasts WHERE target=?',(result['target'],)).fetchone()
            if row:result['snapshot']=dict(created_at=row[0],pair=json.loads(row[1]),config=json.loads(row[2]),kind=row[3])
        result['stale']=bool(result['target'] and result['target']<today().isoformat())
        result['journal']=self.cau_journal()
        result['backtest']=self.get('last_cau_backtest')
        return result

    def cau_journal(self):
        draws={d.day:d for d in self.repo.list_draws()};rows=[]
        with self.repo.con() as c:records=c.execute('SELECT * FROM pro_pair_forecasts ORDER BY target DESC').fetchall()
        for target,created,pair,config,kind in records:
            pair=json.loads(pair);draw=draws.get(target);a,b=pair['a'],pair['b']
            rows.append(dict(day=target,a=a,b=b,created_at=created,config=json.loads(config),kind=kind,
                hits=draw.numbers.count(a)+draw.numbers.count(b) if draw else None,
                both=(a in draw.numbers and b in draw.numbers) if draw else None))
        return rows

    def prediction_view(self):
        from .forecasting import predict
        result=predict(self.repo.list_draws());result['snapshot']=None
        with self.repo.con() as c:
            c.execute('CREATE TABLE IF NOT EXISTS pro_rule_forecasts(target TEXT PRIMARY KEY,created_at TEXT NOT NULL,payload TEXT NOT NULL,kind TEXT NOT NULL)')
            if result['bach_thu']:
                now=datetime.now(VN);target=result['target'];kind='live' if target>now.date().isoformat() or (target==now.date().isoformat() and now.hour<18) else 'retrospective'
                c.execute('INSERT OR IGNORE INTO pro_rule_forecasts VALUES(?,?,?,?)',(target,now.isoformat(),json.dumps(result,ensure_ascii=False),kind))
            row=c.execute('SELECT created_at,payload,kind FROM pro_rule_forecasts WHERE target=?',(result['target'],)).fetchone()
        if row:result['snapshot']={**json.loads(row[1]),'created_at':row[0],'kind':row[2]}
        result['journal']=self.prediction_journal();result['backtest']=self.get('last_prediction_backtest');return result

    def prediction_journal(self):
        draws={d.day:d for d in self.repo.list_draws()};rows=[]
        with self.repo.con() as c:
            c.execute('CREATE TABLE IF NOT EXISTS pro_rule_forecasts(target TEXT PRIMARY KEY,created_at TEXT NOT NULL,payload TEXT NOT NULL,kind TEXT NOT NULL)')
            records=c.execute('SELECT * FROM pro_rule_forecasts ORDER BY target DESC').fetchall()
        for target,created,payload,kind in records:
            p=json.loads(payload);d=draws.get(target)
            rows.append(dict(day=target,created_at=created,kind=kind,bach_thu=p['bach_thu'],song_thu=p['song_thu'],status=p['status'],bach_hits=d.numbers.count(p['bach_thu']) if d else None,song_hits=sum(d.numbers.count(n) for n in p['song_thu']) if d else None))
        return rows
