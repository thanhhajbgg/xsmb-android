from datetime import date
import pytest
from src.pro_data import read_csv,parse_provider,update,PROVIDERS
from src.storage import Repository

def page(day='15/09/2026'):
 labels=['G.ĐB','G.1','G.2','G.3','G.4','G.5','G.6','G.7']
 counts=[1,1,2,6,4,6,3,4]; widths=[5,5,5,5,4,4,3,2]
 rows=''.join('<tr><td>'+label+'</td><td>'+' '.join(str(8).zfill(w) for _ in range(c))+'</td></tr>' for label,c,w in zip(labels,counts,widths))
 return '<h2>XSMB '+day+'</h2><table>'+rows+'</table>'

def test_parse_strict_date_complete():
 d=parse_provider(page(),date(2026,9,15),'test')
 assert len(d.numbers)==27 and d.numbers.count('08')==27
 with pytest.raises(ValueError):parse_provider(page(),date(2026,9,14),'test')
 with pytest.raises(ValueError):parse_provider(page().replace('00008','...',1),date(2026,9,15),'test')

def test_csv_atomic_validation(tmp_path):
 header='day,numbers,special_prize\n'
 good='2026-09-15,"'+' '.join(['08']*27)+'",00008\n'
 assert len(read_csv(header+good))==1
 with pytest.raises(ValueError):read_csv(header+good+good)
 with pytest.raises(ValueError):read_csv(header+good.replace('08 ','',1))
 with pytest.raises(ValueError):read_csv(header+good.replace('2026-09-15','2026-02-30'))

def test_fallback_rejects_wrong_day(tmp_path):
 calls=[]
 def fetch(url):
  calls.append(url)
  return page('14/09/2026') if len(calls)==1 else page()
 repo=Repository(tmp_path/'db')
 result=update(repo,date(2026,9,15),1,fetcher=fetch)
 assert result['success']==1 and len(calls)==2
 assert repo.list_draws()[0].day=='2026-09-15'

def test_import_conflict_is_atomic(tmp_path):
 from src.pro_data import import_csv
 from src.models import Draw
 repo=Repository(tmp_path/'db');repo.save_draw(Draw('2026-09-15',('08',)*27,'00008'))
 text='day,numbers,special_prize\n2026-09-14,"'+' '.join(['01']*27)+'",00001\n2026-09-15,"'+' '.join(['02']*27)+'",00002\n'
 with pytest.raises(ValueError):import_csv(repo,text)
 assert len(repo.list_draws())==1

def test_multiple_tables_cannot_mix_days():
 html=page('14/09/2026')+page('15/09/2026')
 assert parse_provider(html,date(2026,9,15),'test').day=='2026-09-15'
 assert parse_provider(html,date(2026,9,14),'test').day=='2026-09-14'

def test_undated_table_cannot_borrow_previous_result_date():
 undated=page().replace('<h2>XSMB 15/09/2026</h2>','').replace('08','09')
 draw=parse_provider(page()+undated,date(2026,9,15),'test')
 assert draw.numbers==('08',)*27
