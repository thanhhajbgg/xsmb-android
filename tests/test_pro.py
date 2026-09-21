from datetime import date,timedelta
import numpy as np
import pytest
from src.models import Draw
from src.storage import Repository
from src.ledger import Ledger
from src import pro_analytics as pa
from src.pro_backtest import evaluate
from src.pro_service import ProService
from src.optimizer import optimize

def history(n=90):
 rng=np.random.default_rng(22)
 return [Draw((date(2025,1,1)+timedelta(days=i)).isoformat(),tuple(f'{v:02}' for v in rng.integers(0,100,27)),'12345','test') for i in range(n)]

def test_features_and_rank():
 d=history(); f=pa.features(d)
 assert f.shape==(100,30) and np.isfinite(f).all()
 r=pa.rank(d)
 assert len(r)==100 and len({x['number'] for x in r})==100
 assert r==pa.rank(d)
 assert all(0<=x['score']<=100 for x in r)

def test_cash_and_no_lookahead():
 d=history(64)
 a=evaluate(d,top_n=5,points=100)
 first=a['daily'][0]
 hits=sum(d[60].numbers.count(n) for n in first['picks'])
 assert first['cost']==11500000 and first['received']==hits*8000000
 assert first['profit']==first['received']-first['cost']
 modified=d[:61]+[Draw(x.day,('99',)*27,'99999') for x in d[61:]]
 assert evaluate(modified,top_n=5,points=100)['daily'][0]==first
 assert a['profit']==sum(x['profit'] for x in a['daily'])
 assert a['wins']+a['losses']+a['breakeven']==a['days']

def test_gap_skipped():
 d=history(64); del d[60]
 assert evaluate(d)['skipped_gaps']==1

def test_finance_and_snapshot(tmp_path):
 repo=Repository(tmp_path/'db'); s=ProService(repo)
 b=Ledger(repo); b.save('15/09/2026','88',100,23000,80000,0)
 b.save('16/09/2026','88',100,23000,80000,1)
 b.save('17/09/2026','88',100,23000,80000,'')
 f=s.finance('month',10000000)
 assert f['profit']==3400000 and f['pending_cost']==2300000
 assert f['cash']==11100000 and f['equity']==13400000
 for d in history():repo.save_draw(d)
 a=s.dashboard(); first=s.journal()['rows'][0]
 s.dashboard(); assert len(s.journal()['rows'])==1
 assert first['picks']==s.journal()['rows'][0]['picks']
 assert a['target']=='2025-04-01'

def test_optimizer_split_and_reproducibility():
 d=history(190)
 a=optimize(d,trials=10); b=optimize(d,trials=10)
 assert a['weights']==b['weights']
 assert a['train']['end']<a['validation']['start']<a['test']['start']
 assert sum(a['weights'].values())==pytest.approx(1)
 assert a['test']['days']>0
 # Unseen test results cannot affect selected training weights.
 cut=next(i for i,x in enumerate(d) if x.day==a['test']['start'])
 changed=d[:cut]+[Draw(x.day,('99',)*27,'99999') for x in d[cut:]]
 assert optimize(changed,trials=10)['weights']==a['weights']

def test_snapshot_stays_unchanged_after_model_change(tmp_path):
 repo=Repository(tmp_path/'db');s=ProService(repo)
 for d in history(90):repo.save_draw(d)
 s.dashboard();before=s.journal()['rows']
 s.set('weights',{'momentum':1.0});s.dashboard()
 assert s.journal()['rows']==before

def test_finance_periods_reconcile(tmp_path):
 s=ProService(Repository(tmp_path/'db'))
 for day_,hits in [('31/12/2025',0),('01/01/2026',1),('05/01/2026',2)]:s.ledger.save(day_,'08',100,23000,80000,hits)
 for period in ('day','week','month','year'):
  f=s.finance(period,10000000)
  assert sum(g['profit'] for g in f['groups'])==f['profit']
  assert f['groups'][-1]['cash']==f['cash']
 f=s.finance('month',10000000,'2026-01-01','2026-01-31')
 assert f['opening']==7700000
 assert f['profit']==19400000

def test_dashboard_forecast_matches_journal_after_model_change(tmp_path):
 repo=Repository(tmp_path/'db');s=ProService(repo)
 for d in history(90):repo.save_draw(d)
 before=s.dashboard()
 s.set('weights',{'momentum':1.0})
 after=s.dashboard();j=s.journal(top_n=10)['rows'][0]
 assert [r['number'] for r in after['forecast_picks']]==j['picks']
 assert after['forecast_picks']==before['forecast_picks']
