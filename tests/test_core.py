
from datetime import date
from src.models import Draw
from src.analytics import rank_numbers
from src.backtest import walk_forward
from src.storage import Repository
def draw(day, offset=0):
 return Draw(day,tuple(f"{(i+offset)%100:02d}" for i in range(27)),"12345","test")
def test_ranking_complete_deterministic():
 d=[draw(f"2026-01-{i:02d}",i) for i in range(1,20)]
 a=rank_numbers(d); b=rank_numbers(d)
 assert len(a)==100 and len({x.number for x in a})==100 and a==b
 assert all(0<=x.score<=100 for x in a)
def test_storage_roundtrip(tmp_path):
 r=Repository(tmp_path/"x.db"); d=draw("2026-01-01"); r.save_draw(d)
 assert r.list_draws()[0].numbers==d.numbers
 r.save_prediction("2026-01-02",[{"number":"01"}])
 assert r.list_predictions()[0][1][0]["number"]=="01"
def test_backtest_no_crash():
 d=[draw(f"2026-{1+(i//28):02d}-{1+(i%28):02d}",i) for i in range(70)]
 b=walk_forward(d,5,60); assert b.days==10
