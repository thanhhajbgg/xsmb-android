"""Fail closed on incomplete or misdated lottery pages."""
import csv,io,re,json
from datetime import date,datetime,timedelta
from collections import Counter
from bs4 import BeautifulSoup
from .models import Draw
from .data_source import fetch_html

PROVIDERS=[
 {'id':'daiphat','name':'Đại Phát','template':'https://xosodaiphat.com/xsmb-{d:%d-%m-%Y}.html'},
 {'id':'minhngoc','name':'Minh Ngọc','template':'https://www.minhngoc.net.vn/ket-qua-xo-so/mien-bac/{d:%d-%m-%Y}.html'},
 {'id':'xskt','name':'Xổ số KT','template':'https://xskt.com.vn/xsmb/ngay-{day}-{month}-{year}'},
 {'id':'kqxs','name':'KQXS (Ketqua.net)','template':'https://ketqua.net/xo-so-mien-bac.php?ngay={d:%d-%m-%Y}'}]
ALIASES=[['g.đb','đb','g.db','đặc biệt','giải đb','giải đặc biệt'],['g.1','1','giải nhất','giải 1'],['g.2','2','giải nhì','giải 2'],
 ['g.3','3','giải ba','giải 3'],['g.4','4','giải tư','giải 4'],['g.5','5','giải năm','giải 5'],['g.6','6','giải sáu','giải 6'],['g.7','7','giải bảy','giải 7']]
COUNTS=[1,1,2,6,4,6,3,4]; WIDTHS=[5,5,5,5,4,4,3,2]
DATE_RE=r'(?<!\d)(\d{1,2})[/-](\d{1,2})[/-](\d{4})(?!\d)'


def parse_provider(html,expected,source):
    soup=BeautifulSoup(html,'html.parser')
    for junk in soup(['script','style']):junk.decompose()
    errors=[]
    for table in reversed(soup.find_all('table')):
        found={}; first=None; duplicate=False
        for tr in table.find_all('tr'):
            cells=tr.find_all(['td','th'],recursive=False)
            if len(cells)<2:continue
            label=' '.join(cells[0].stripped_strings).strip().rstrip(':').lower()
            idx=next((i for i,aliases in enumerate(ALIASES) if label in aliases),None)
            if idx is None:continue
            if idx in found:duplicate=True; break
            if first is None:first=tr
            text=' '.join(c.get_text(' ',strip=True) for c in cells[1:])
            numbers=re.findall(r'(?<!\d)\d{2,5}(?!\d)',text)
            if len(numbers)!=COUNTS[idx] or any(len(n)!=WIDTHS[idx] for n in numbers):
                found[idx]=None
            else:found[idx]=numbers
        if duplicate or len(found)!=8 or any(v is None for v in found.values()):continue
        # Date must precede this exact prize table; never trust the requested URL.
        prefix=[]
        for node in first.previous_elements:
            # Never borrow a heading from an earlier completed prize table.
            if getattr(node,'name',None)=='tr':
                previous_cells=node.find_all(['td','th'],recursive=False)
                previous_label=' '.join(previous_cells[0].stripped_strings).strip().rstrip(':').lower() if previous_cells else ''
                if any(previous_label in aliases for aliases in ALIASES):break
            if getattr(node,'name',None)=='table' and node is not table:break
            if getattr(node,'name',None) in ('h1','h2','h3','h4','caption'):
                prefix.append(node.get_text(' ',strip=True))
            elif isinstance(node,str):prefix.append(str(node))
            if sum(len(x) for x in prefix)>1200:break
        context=' '.join(reversed(prefix))
        matches=list(re.finditer(DATE_RE,context))
        if not matches:errors.append('Không xác định được ngày của bảng kết quả');continue
        dd,mm,yy=map(int,matches[-1].groups())
        try:actual=date(yy,mm,dd)
        except ValueError:continue
        if actual!=expected:errors.append(f'Ngày nguồn {actual} khác ngày yêu cầu {expected}');continue
        nums=sum((found[i] for i in range(8)),[])
        return Draw(actual.isoformat(),tuple(n[-2:] for n in nums),nums[0],source)
    raise ValueError('; '.join(errors[-2:]) or 'Không đọc được đủ 27 giải đúng định dạng. Không lưu trang này.')


def read_csv(text):
    reader=csv.DictReader(io.StringIO(text.lstrip('\ufeff')))
    if not reader.fieldnames or not {'day','numbers'}.issubset(reader.fieldnames):raise ValueError('CSV cần cột day,numbers,special_prize (special_prize có thể để trống).')
    draws=[]; seen=set()
    for line,row in enumerate(reader,2):
        raw=(row.get('day') or '').strip()
        try:day=date.fromisoformat(raw) if '-' in raw else datetime.strptime(raw,'%d/%m/%Y').date()
        except ValueError:raise ValueError(f'Dòng {line}: ngày không hợp lệ.') from None
        if day.isoformat() in seen:raise ValueError(f'Dòng {line}: trùng ngày {day}.')
        numbers=re.split(r'[\s,;|]+',(row.get('numbers') or '').strip())
        if len(numbers)!=27 or any(not re.fullmatch(r'\d{2}',n,flags=re.ASCII) for n in numbers):raise ValueError(f'Dòng {line}: numbers cần đúng 27 số 00–99; giữ số trùng để tính nháy.')
        sp=(row.get('special_prize') or '').strip()
        if sp and (not re.fullmatch(r'[0-9]{5}',sp) or sp[-2:] not in numbers):raise ValueError(f'Dòng {line}: giải đặc biệt phải có 5 chữ số và đuôi nằm trong 27 số.')
        seen.add(day.isoformat());draws.append(Draw(day.isoformat(),tuple(numbers),sp,'CSV'))
    if not draws:raise ValueError('CSV không có dòng dữ liệu.')
    if len(draws)>10000:raise ValueError('Mỗi lần nhập tối đa 10.000 ngày.')
    return sorted(draws,key=lambda x:x.day)


def import_csv(repo,text):
    draws=read_csv(text) # Validate all rows before opening write transaction.
    existing={d.day:d for d in repo.list_draws()}; new=[]; skipped=0
    for d in draws:
        if d.day in existing:
            old=existing[d.day]
            if Counter(old.numbers)!=Counter(d.numbers) or (old.special_prize and d.special_prize and old.special_prize!=d.special_prize):
                raise ValueError(f'Ngày {d.day} khác dữ liệu đã lưu. Không ghi đè lịch sử; hãy kiểm tra nguồn.')
            skipped+=1
        else:new.append(d)
    with repo.con() as c:
        for d in new:c.execute('INSERT INTO draws VALUES(?,?,?,?,?)',(d.day,json.dumps(d.numbers),d.special_prize,d.source_url,datetime.now().isoformat()))
    return dict(success=len(new),skipped=skipped,message=f'Đã nhập {len(new)} ngày; bỏ qua {skipped} ngày trùng khớp.')


def update(repo,start,days,providers=None,fetcher=None,progress=None,cancel=None):
    days=int(days)
    if not 1<=days<=1095:raise ValueError('Số ngày từ 1 đến 1.095.')
    selected=PROVIDERS if providers is None else [p for p in PROVIDERS if p['id'] in providers]
    if not selected:raise ValueError('Chọn ít nhất một nguồn.')
    fetcher=fetcher or (lambda url:fetch_html(url,timeout=8))
    existing={d.day for d in repo.list_draws()}; result=dict(success=0,skipped=0,failed=0,logs=[])
    for i in range(days):
        if cancel and cancel():raise ValueError('Đã hủy cập nhật; các ngày tải xong đã được lưu.')
        d=start-timedelta(days=i)
        if d.isoformat() in existing:result['skipped']+=1;continue
        ok=False
        for p in selected:
            if cancel and cancel():raise ValueError('Đã hủy cập nhật.')
            url=p['template'].format(d=d,day=d.day,month=d.month,year=d.year)
            if progress:progress(int(100*i/days),f'{d:%d/%m/%Y} • {p["name"]}')
            try:
                draw=parse_provider(fetcher(url),d,url);repo.save_draw(draw);result['success']+=1;ok=True
                result['logs'].append(f'{d}: OK • {p["name"]}');break
            except Exception as e:result['logs'].append(f'{d}: {p["name"]} • {e}')
        if not ok:result['failed']+=1
    result['logs']=result['logs'][-200:]
    return result
