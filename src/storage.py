
import sqlite3,json
from datetime import datetime,timezone
from .models import Draw
class Repository:
 def __init__(self,path):
  self.path=str(path); self._init()
 def con(self): return sqlite3.connect(self.path)
 def _init(self):
  with self.con() as c:
   c.execute("CREATE TABLE IF NOT EXISTS draws(day TEXT PRIMARY KEY,numbers TEXT NOT NULL,special_prize TEXT,source_url TEXT,fetched_at TEXT)")
   c.execute("CREATE TABLE IF NOT EXISTS predictions(target_day TEXT PRIMARY KEY,ranking TEXT NOT NULL,created_at TEXT)")
   c.execute("CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT)")
 def save_draw(self,d):
  with self.con() as c:c.execute("INSERT OR REPLACE INTO draws VALUES(?,?,?,?,?)",(d.day,json.dumps(d.numbers),d.special_prize,d.source_url,datetime.now(timezone.utc).isoformat()))
 def list_draws(self):
  with self.con() as c:r=c.execute("SELECT day,numbers,special_prize,source_url FROM draws ORDER BY day").fetchall()
  return [Draw(d,tuple(json.loads(n)),sp,u or "") for d,n,sp,u in r]
 def save_prediction(self,target_day,ranking):
  with self.con() as c:c.execute("INSERT OR REPLACE INTO predictions VALUES(?,?,?)",(target_day,json.dumps(ranking,ensure_ascii=False),datetime.now(timezone.utc).isoformat()))
 def list_predictions(self):
  with self.con() as c:r=c.execute("SELECT target_day,ranking,created_at FROM predictions ORDER BY target_day").fetchall()
  return [(d,json.loads(x),t) for d,x,t in r]
