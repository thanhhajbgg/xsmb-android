
from dataclasses import dataclass,field
from datetime import timedelta
from .parser import parse_draw
from .data_source import fetch_html
@dataclass
class UpdateReport:
 success:int=0; skipped:int=0; failed:int=0; errors:list[str]=field(default_factory=list)
BASE="https://xosodaiphat.com"
def update_history(repository,start_day,days,fetcher=fetch_html):
 rep=UpdateReport()
 for i in range(days):
  d=start_day-timedelta(days=i); url=f"{BASE}/xsmb-{d:%d-%m-%Y}.html"
  try:
   draw=parse_draw(fetcher(url),url); repository.save_draw(draw); rep.success+=1
  except Exception as e: rep.failed+=1; rep.errors.append(f"{d:%d/%m/%Y}: {e}")
 return rep
