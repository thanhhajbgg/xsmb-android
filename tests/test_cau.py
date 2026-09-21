import unittest
from datetime import date,timedelta
import tempfile
from pathlib import Path
import numpy as np
from src.models import Draw
from src.storage import Repository
from src.pro_service import ProService
from src.cau import analyze,walk_forward,wilson

def history(n=90):
 rng=np.random.default_rng(81)
 return [Draw((date(2025,1,1)+timedelta(days=i)).isoformat(),tuple(f'{x:02}' for x in rng.integers(0,100,27)),'12345') for i in range(n)]

class CauTests(unittest.TestCase):
 def test_insufficient_does_not_select(self):
  self.assertIsNone(analyze(history(20))['selected'])
 def test_unique_pairs_and_counts(self):
  draws=history();r=analyze(draws)
  self.assertEqual(len(r['pairs']),20)
  seen=set()
  for pair in r['pairs']:
   a,b=pair['a'],pair['b'];self.assertLess(a,b);self.assertNotIn((a,b),seen);seen.add((a,b))
   either=sum(a in d.numbers or b in d.numbers for d in draws)
   both=sum(a in d.numbers and b in d.numbers for d in draws)
   self.assertEqual(pair['either_days'],either);self.assertEqual(pair['both_days'],both)
   self.assertLessEqual(pair['both_rate'],pair['either_rate'])
   self.assertTrue(0<=pair['score']<=100)
 def test_wilson_penalizes_small_sample(self):
  self.assertLess(float(wilson(2,2)),float(wilson(40,40)))
  self.assertEqual(float(wilson(0,0)),0)
 def test_gap_not_treated_as_next_day(self):
  d=history(90);del d[40]
  self.assertEqual(analyze(d)['transitions'],87)
 def test_walk_forward_money_and_future(self):
  d=history(66);r=walk_forward(d,points=100)
  self.assertEqual(r['days'],6)
  first=r['daily'][0];a,b=first['picks']
  self.assertEqual(first['cost'],4600000)
  self.assertEqual(first['received'],8000000*(d[60].numbers.count(a)+d[60].numbers.count(b)))
  changed=d[:61]+[Draw(x.day,('99',)*27,'99999') for x in d[61:]]
  self.assertEqual(walk_forward(changed)['daily'][0],first)
 def test_frozen_pair_and_settlement(self):
  with tempfile.TemporaryDirectory() as folder:
   s=ProService(Repository(Path(folder)/'db'))
   for d in history():s.repo.save_draw(d)
   first=s.cau_view();selected=first['snapshot']['pair']
   second=s.cau_view(window=60,min_support=10)
   self.assertEqual(second['snapshot']['pair'],selected)
   self.assertNotEqual(second['snapshot']['config'],second['config'])
   s.repo.save_draw(Draw(first['target'],tuple([selected['a']]*2+[selected['b']]*25),'12345'))
   journal=s.cau_journal()
   self.assertEqual(journal[0]['hits'],27)
   self.assertEqual(journal[0]['both'],True)
if __name__=='__main__':unittest.main()

class CauRegressionTests(unittest.TestCase):
 def test_fast_path_matches_displayed_selection(self):
  d=history(130)
  full=analyze(d,window=90,min_support=20)
  fast=analyze(d,window=90,min_support=20,detail=False)
  self.assertEqual(full['selected'],fast['selected'])
 def test_low_support_rules_not_qualified(self):
  r=analyze(history(90),min_support=100)
  self.assertTrue(all(not rule['eligible'] for rule in r['rules']))
  self.assertTrue(all(row['qualified_rules']==0 for row in r['number_scores']))
 def test_count_pairs_no_self_or_reverse_duplicate(self):
  from src.cau import A,B
  self.assertEqual(len(A),4950)
  self.assertTrue(np.all(A<B))

class SnapshotEligibilityTests(unittest.TestCase):
 def test_saved_pair_remains_visible_if_preview_has_too_many_gaps(self):
  with tempfile.TemporaryDirectory() as folder:
   s=ProService(Repository(Path(folder)/'db'));d=history(90)
   for i,draw in enumerate(d):
    day=draw.day if i<60 else (date(2025,1,1)+timedelta(days=59+2*(i-59))).isoformat()
    s.repo.save_draw(Draw(day,draw.numbers,draw.special_prize))
   saved=s.cau_view(window=180)['snapshot']
   self.assertIsNotNone(saved)
   short=s.cau_view(window=60)
   self.assertIsNone(short['selected'])
   self.assertEqual(short['snapshot'],saved)
