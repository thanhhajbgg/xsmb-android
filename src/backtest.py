
from dataclasses import dataclass
from .analytics import rank_numbers
@dataclass(frozen=True)
class BacktestResult:
 top_n:int; days:int; hit_days:int; hit_rate:float|None
def walk_forward(draws,top_n,warmup=60):
 hits=0; total=0
 for i in range(warmup,len(draws)):
  picks={x.number for x in rank_numbers(draws[:i])[:top_n]}
  hits+=bool(picks & set(draws[i].numbers)); total+=1
 return BacktestResult(top_n,total,hits,round(100*hits/total,1) if total else None)
