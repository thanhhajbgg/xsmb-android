
from dataclasses import dataclass
from datetime import date,timedelta
from .paths import get_data_dir
from .storage import Repository
from .update_service import update_history
from .analytics import rank_numbers
from .backtest import walk_forward

@dataclass(frozen=True)
class AnalysisResult:
    last_day: str|None
    target_day: str|None
    draws: tuple
    ranking: tuple

class AppService:
 def __init__(self,repo=None): self.repo=repo or Repository(get_data_dir()/"xsmb.db")
 def update(self,days=120): return update_history(self.repo,date.today(),days)
 def analyze(self):
  draws=self.repo.list_draws(); ranking=rank_numbers(draws)
  last_day=draws[-1].day if draws else None
  target=(date.fromisoformat(last_day)+timedelta(days=1)).isoformat() if last_day else None
  if target:
   self.repo.save_prediction(target,[x.to_dict() for x in ranking])
  return AnalysisResult(last_day,target,tuple(draws),tuple(ranking))
 def backtests(self):
  d=self.repo.list_draws(); return [walk_forward(d,n,60) for n in (1,5,10)]
