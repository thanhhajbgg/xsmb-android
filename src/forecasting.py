"""Chronological rule forecasts. Descriptive evidence, not winning probabilities."""
from datetime import date,timedelta
from collections import defaultdict
import numpy as np
from .pro_analytics import matrix
from .cau import wilson
from .pro_backtest import summarize

def special_candidates(v):
    if len(v)!=5 or not v.isdigit():return {}
    out={f'pos_{i}_{j}':v[i]+v[j] for i in range(5) for j in range(5) if i!=j}
    a=list(map(int,v))
    while len(a)>2:a=[(x+y)%10 for x,y in zip(a,a[1:])]
    out.update(pascal=''.join(map(str,a)),pascal_reverse=''.join(map(str,a[::-1])),sum_double=str(sum(map(int,v))%10)*2)
    return out

def prepare(draws):
    m=matrix(draws);em=[{} for _ in range(len(draws)+1)];base=[None]*len(em)
    for t in range(1,len(em)):
        if t<len(draws) and (date.fromisoformat(draws[t].day)-date.fromisoformat(draws[t-1].day)).days!=1:continue
        em[t]=special_candidates(draws[t-1].special_prize)
        base[t]=f'{int(np.argmax(m[max(0,t-30):t].sum(axis=0))):02}'
        idx=[j for j in range(max(1,t-180),t) if (date.fromisoformat(draws[j].day)-date.fromisoformat(draws[j-1].day)).days==1]
        if idx:
            prev=(m[np.array(idx)-1]>0).astype(float);nxt=(m[idx]>0).astype(float);exposure=prev.sum(axis=0);counts=prev.T@nxt
            sources=np.flatnonzero((m[t-1]>0)&(exposure>=10))
            if len(sources):
                em[t]['transition']=f'{int(np.argmax(((counts[sources]+1)/(exposure[sources,None]+2)).mean(axis=0))):02}'
                em[t]['repeat']=f'{int(sources[np.argmax((counts[sources,sources]+1)/(exposure[sources]+2))]):02}'
    return dict(draws=draws,matrix=m,emissions=em,baseline=base)

def select(p,at):
    rules=[];votes=defaultdict(list)
    for key,candidate in p['emissions'][at].items():
        cohort=[j for j in range(max(1,at-60),at) if key in p['emissions'][j]];n=len(cohort)
        hits=sum(bool(p['matrix'][j,int(p['emissions'][j][key])]) for j in cohort)
        base=sum(bool(p['matrix'][j,int(p['baseline'][j])]) for j in cohort)/n if n else 0
        lower=float(wilson(hits,n))
        if key.startswith('pos_'):
            _,a,b=key.split('_');name=f'ĐB vị trí {int(a)+1} → {int(b)+1}';family='Vị trí ĐB'
        else:name,family={'pascal':('Pascal ĐB','Pascal'),'pascal_reverse':('Pascal đảo','Pascal'),'sum_double':('Kép tổng ĐB','Tổng ĐB'),'repeat':('Lô rơi','Lô rơi'),'transition':('Chuyển tiếp','Chuyển tiếp')}[key]
        r=dict(id=key,name=name,family=family,candidate=candidate,trials=n,hits=hits,rate=hits/n if n else 0,lower=lower,baseline_rate=base,eligible=n>=30 and lower>base);rules.append(r)
        if n>=30:votes[candidate].append(r)
    ranking=[]
    for number,reasons in votes.items():
        families={}
        for r in reasons:families[r['family']]=max(families.get(r['family'],0),int(r['eligible'])+r['lower'])
        ranking.append(dict(number=number,score=round(sum(families.values()),6),reasons=reasons,eligible=any(r['eligible'] for r in reasons)))
    ranking.sort(key=lambda r:(-r['eligible'],-r['score'],r['number']))
    return dict(target=(date.fromisoformat(p['draws'][at-1].day)+timedelta(days=1)).isoformat() if at else None,bach_thu=ranking[0]['number'] if ranking else None,song_thu=[r['number'] for r in ranking[:2]] if len(ranking)>1 else [],ranking=ranking,rules=rules,status='qualified' if any(r['eligible'] for r in rules) else 'exploratory' if ranking else 'insufficient',notice='Kiểm tra từng cầu trên tối đa 60 kỳ đã kết thúc, tối thiểu 30 mẫu. Tín hiệu: cận dưới Wilson vượt tỷ lệ trúng đối chứng tần suất cùng kỳ. Chọn nhiều cầu có thể gây quá khớp; không bảo đảm ngày tới. Song thủ là hai số riêng, không phải xiên.')

def predict(draws):return select(prepare(draws),len(draws))

def backtest(draws,points=100,cost_rate=23000,payout_rate=80000,progress=None,cancel=None):
    p=prepare(draws);rows={'bach_thu':[],'song_thu':[]}
    for at in range(31,len(draws)):
        if cancel and cancel():raise ValueError('Đã dừng kiểm tra.')
        r=select(p,at)
        for key in rows:
            picks=([r[key]] if r[key] else []) if key=='bach_thu' else r[key]
            if not picks:continue
            hits=sum(int(p['matrix'][at,int(n)]) for n in picks);cost=len(picks)*int(points)*int(cost_rate);received=hits*int(points)*int(payout_rate)
            rows[key].append(dict(day=draws[at].day,picks=picks,hits=hits,cost=cost,received=received,profit=received-cost,status=r['status']))
        if progress:progress((at+1)/len(draws)*100,f'Kiểm tra {at+1}/{len(draws)} kỳ')
    return {key:summarize(value) for key,value in rows.items()}
