
from dataclasses import dataclass,asdict
from collections import Counter
@dataclass(frozen=True)
class NumberScore:
 number:str; score:float; f7:int; f14:int; f30:int; f60:int; f90:int; gap:int; reverse14:int
 def to_dict(self): return asdict(self)
def rank_numbers(draws):
 nums=[f"{i:02d}" for i in range(100)]
 wins=[7,14,30,60,90]; weights=[.30,.24,.20,.14,.12]
 raw={n:0.0 for n in nums}; det={n:{} for n in nums}
 for w,wt in zip(wins,weights):
  cnt=Counter(x for d in draws[-w:] for x in d.numbers); mx=max(cnt.values(),default=1)
  for n in nums: det[n][f"f{w}"]=cnt[n]; raw[n]+=wt*(cnt[n]/mx)
 for n in nums:
  gap=0
  for d in reversed(draws):
   if n in d.numbers: break
   gap+=1
  det[n]["gap"]=gap; raw[n]+=.10*min(gap,20)/20
  rev=n[::-1]; rc=sum(rev in d.numbers for d in draws[-14:]) if rev!=n else 0
  det[n]["reverse14"]=rc; raw[n]+=.05*min(rc/5,1)
 lo=min(raw.values()); hi=max(raw.values()); den=hi-lo or 1
 out=[NumberScore(n,round(100*(raw[n]-lo)/den,1),det[n]["f7"],det[n]["f14"],det[n]["f30"],det[n]["f60"],det[n]["f90"],det[n]["gap"],det[n]["reverse14"]) for n in nums]
 return sorted(out,key=lambda x:(-x.score,x.number))
