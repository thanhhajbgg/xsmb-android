import unittest,tempfile
from pathlib import Path
from datetime import date,timedelta
import numpy as np
from src.models import Draw
from src.storage import Repository
from src.pro_service import ProService
from src import forecasting as f

def pattern(n=100):
 # Yesterday's special-prize tail is tomorrow's outcome; generated QA only.
 return [Draw((date(2025,1,1)+timedelta(days=i)).isoformat(),(f'{(i-1)%50:02}',)*27,f'{i%1000:03}{i%50:02}') for i in range(n)]

class ForecastTests(unittest.TestCase):
 def test_explicit_rule_candidates(self):
  c=f.special_candidates('12345')
  self.assertEqual(c['pos_3_4'],'45');self.assertEqual(c['pos_4_3'],'54')
  self.assertEqual(c['pascal'],'08');self.assertEqual(c['pascal_reverse'],'80')
  self.assertEqual(c['sum_double'],'55')
 def test_missing_special_is_not_invented(self):
  self.assertEqual(f.special_candidates(''),{})
 def test_prediction_comes_from_rules_and_has_evidence(self):
  r=f.predict(pattern())
  self.assertEqual(r['bach_thu'],'49')
  self.assertTrue(any(x['id']=='pos_3_4' and x['eligible'] for x in r['rules']))
  self.assertEqual(len(set(r['song_thu'])),2)
  self.assertIn(r['bach_thu'],r['song_thu'])
  for x in r['ranking']:
   self.assertTrue(x['reasons'])
   self.assertTrue(all(reason['candidate']==x['number'] for reason in x['reasons']))
 def test_selector_never_reads_future_outcome(self):
  d=pattern(100);before=f.select(f.prepare(d),80)
  changed=d[:80]+[Draw(x.day,('99',)*27,'99999') for x in d[80:]]
  self.assertEqual(f.select(f.prepare(changed),80),before)
 def test_not_enough_samples_has_no_forecast(self):
  r=f.predict(pattern(20));self.assertIsNone(r['bach_thu']);self.assertEqual(r['status'],'insufficient')
 def test_no_contiguous_date_no_rule_evaluation(self):
  d=pattern(80);del d[40]
  p=f.prepare(d)
  self.assertEqual(p['emissions'][40],{})
 def test_walk_forward_cash(self):
  r=f.backtest(pattern(80),points=100)
  self.assertGreater(r['bach_thu']['days'],0)
  for key,count in [('bach_thu',1),('song_thu',2)]:
   for row in r[key]['daily']:
    self.assertEqual(row['cost'],count*2300000)
    self.assertEqual(row['received'],row['hits']*8000000)
    self.assertEqual(row['profit'],row['received']-row['cost'])
 def test_snapshot_preserves_predictions_and_no_bets(self):
  with tempfile.TemporaryDirectory() as folder:
   s=ProService(Repository(Path(folder)/'db'))
   for d in pattern(80):s.repo.save_draw(d)
   r=s.prediction_view();s.prediction_view()
   self.assertEqual(len(s.prediction_journal()),1)
   self.assertEqual(s.prediction_journal()[0]['bach_thu'],r['snapshot']['bach_thu'])
   self.assertEqual(s.ledger.rows(),[])
if __name__=='__main__':unittest.main()
