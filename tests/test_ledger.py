import unittest
import tempfile
from pathlib import Path
from src import ledger
from src.storage import Repository
from src.models import Draw

class LedgerTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
  self.repo=Repository(Path(self.tmp.name)/'db'); self.book=ledger.Ledger(self.repo)
 def test_loss_win_repeat_pending(self):
  for hits,expected in [(0,(2300000,0,-2300000)),(1,(2300000,8000000,5700000)),(2,(2300000,16000000,13700000)),(None,(2300000,None,None))]:
   self.assertEqual(ledger.calculate(100,23000,80000,hits),expected)
 def test_persistence_auto_manual_edit_delete(self):
  a=self.book.save('15/09/2026','88','100','23000','80000','0','Ví dụ')
  b=self.book.save('16/09/2026','08','10','23000','80000','','')
  self.assertIsNone(self.book.rows()[1]['profit'])
  self.repo.save_draw(Draw('2026-09-16',('08','88','08'),'00008'))
  rows=ledger.Ledger(Repository(self.repo.path)).rows()
  self.assertEqual(rows[0]['profit'],-2300000)
  self.assertEqual(rows[1]['hits'],2)
  self.assertEqual(rows[1]['profit'],1370000)
  self.book.save('15/09/2026','88','100','23000','80000','1','',a)
  self.assertEqual(self.book.rows()[0]['profit'],5700000)
  self.book.delete(b); self.assertEqual(len(self.book.rows()),1)
  self.assertEqual(self.repo.list_draws()[0].day,'2026-09-16')
 def test_invalid_input(self):
  for index,value in [(0,'31/02/2026'),(1,'888'),(2,'0'),(2,'nan'),(2,'1.5'),(3,'-1'),(4,'0'),(5,'-1'),(5,'1.5')]:
   with self.subTest(index=index,value=value):
    args=['15/09/2026','88','100','23000','80000','0','']; args[index]=value
    with self.assertRaises(ValueError): self.book.save(*args)
if __name__=='__main__': unittest.main()
