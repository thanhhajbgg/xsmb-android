"""Exploratory next-draw pair ranking. No calibrated winning probabilities."""
from datetime import date,timedelta
import numpy as np
from .pro_analytics import matrix,normalized
from .pro_backtest import summarize

A,B=np.triu_indices(100,1)
VERSION='cau-1.0'


def wilson(hits,total):
    hits=np.asarray(hits,dtype=float);total=np.asarray(total,dtype=float)
    safe=np.maximum(total,1);p=hits/safe;z=1.96
    lower=(p+z*z/(2*safe)-z*np.sqrt(p*(1-p)/safe+z*z/(4*safe*safe)))/(1+z*z/safe)
    return np.where(total>0,np.maximum(0,lower),0)


def analyze(draws,window=180,min_support=20,limit=20,detail=True):
    window=int(window);min_support=int(min_support)
    if not 60<=window<=730 or not 5<=min_support<=100:raise ValueError('Cửa sổ 60–730 kỳ; số mẫu tối thiểu 5–100.')
    hist=draws[-window:];n=len(hist)
    target=(date.fromisoformat(hist[-1].day)+timedelta(days=1)).isoformat() if hist else None
    config=dict(window=window,min_support=min_support,version=VERSION)
    base=dict(target=target,last_day=hist[-1].day if hist else None,sample_days=n,config=config,
        selected=None,pairs=[],rules=[],transitions=0,number_scores=[],
        method='Song thủ: hai số đánh riêng. Score tương đối, không phải xác suất. Tỷ lệ bảng xếp hạng là mô tả trong mẫu; xem walk-forward để kiểm tra cách tuyển chọn.')
    if not hist:return dict(**base,warning='Chưa có dữ liệu.')
    m=matrix(hist);p=(m>0).astype(int);dates=[date.fromisoformat(d.day) for d in hist]
    valid=np.array([(dates[i]-dates[i-1]).days==1 for i in range(1,n)],dtype=bool)
    prev=p[:-1][valid];nxt=p[1:][valid];transitions=len(prev);base['transitions']=transitions
    if n<60 or transitions<40:
        return dict(**base,warning='Chưa tuyển chọn: cần ít nhất 60 kỳ dữ liệu và 40 cặp ngày liên tiếp. Hãy bổ sung lịch sử.')
    count=prev.sum(axis=0);success=prev.T@nxt;active=np.flatnonzero(p[-1])
    lower=wilson(success,count[:,None]);baseline=nxt.mean(axis=0)
    eligible_sources=[int(s) for s in active if count[s]>=min_support]
    transition=lower[eligible_sources].mean(axis=0) if eligible_sources else np.zeros(100)
    rules=[];support=[[] for _ in range(100)];strength=np.zeros(100)
    def add(kind,source,dest,hits,total,baseline_rate):
        total=int(total);hits=int(hits);eligible=total>=min_support
        row=dict(kind=kind,source=source,number=f'{dest:02}',hits=hits,samples=total,
            rate=round(100*hits/total,2) if total else None,
            lower=round(100*float(wilson(hits,total)),2),baseline=round(100*float(baseline_rate),2),
            lift=round(100*(hits/total-baseline_rate),2) if total else None,eligible=eligible)
        if detail:rules.append(row)
        if eligible:support[dest].append(row)
    target_weekday=date.fromisoformat(target).weekday()
    weekday_mask=np.array([d.weekday()==target_weekday for d in dates])
    heads=prev.reshape(transitions,10,10).any(axis=2)
    tails=prev.reshape(transitions,10,10).any(axis=1)
    for dest in range(100):
        rev=(dest%10)*10+dest//10
        if p[-1,dest]:add('Kép rơi' if dest//10==dest%10 else 'Lô rơi',f'{dest:02}',dest,success[dest,dest],count[dest],baseline[dest])
        if rev!=dest and p[-1,rev]:add('Đảo',f'{rev:02}',dest,success[rev,dest],count[rev],baseline[dest])
        for label,mask,is_active,digit in [('Theo đầu',heads[:,dest//10],p[-1].reshape(10,10)[dest//10].any(),dest//10),('Theo đuôi',tails[:,dest%10],p[-1].reshape(10,10)[:,dest%10].any(),dest%10)]:
            if is_active:add(label,str(digit),dest,nxt[mask,dest].sum(),mask.sum(),baseline[dest])
        add('Theo thứ',str(target_weekday+2 if target_weekday<6 else 'CN'),dest,p[weekday_mask,dest].sum(),weekday_mask.sum(),p[:,dest].mean())
        if detail:
            for source in active:
                if source not in (dest,rev):add('Chuyển tiếp',f'{source:02}',dest,success[source,dest],count[source],baseline[dest])
        else:
            # Keep exactly the same scoring support in the fast backtest path.
            for source in eligible_sources:
                if source not in (dest,rev):add('Chuyển tiếp',f'{source:02}',dest,success[source,dest],count[source],baseline[dest])
        non_transition=[r['lower']/100 for r in support[dest] if r['kind']!='Chuyển tiếp']
        strength[dest]=np.mean(non_transition) if non_transition else 0
    freq30=m[-30:].sum(axis=0);freq7=m[-7:].sum(axis=0)
    momentum=freq7/7-freq30/30
    number_score=.35*normalized(freq30)+.15*normalized(freq7)+.2*normalized(strength)+.2*normalized(transition)+.1*normalized(momentum)
    both=(p.T@p)[A,B];presence=p.sum(axis=0);either=presence[A]+presence[B]-both
    pair_raw=.65*(number_score[A]+number_score[B])/2+.25*normalized(wilson(either,n))+.10*normalized(wilson(both,n))
    scores=normalized(pair_raw)*100
    order=np.argsort(-scores,kind='stable')[:max(1,min(int(limit),100))]
    pairs=[]
    for idx in order:
        a=int(A[idx]);b=int(B[idx]);tags=[]
        if a//10==b//10:tags.append('Cùng đầu')
        if a%10==b%10:tags.append('Cùng đuôi')
        if (a%10)*10+a//10==b:tags.append('Cặp đảo')
        reasons=[]
        for value in (a,b):
            rr=sorted(support[value],key=lambda r:(-(r['lift'] or 0),-r['samples'],r['kind'],r['source']))[:3]
            reasons.extend(f"{r['kind']} {r['source']}→{r['number']}: {r['hits']}/{r['samples']}" for r in rr)
        pairs.append(dict(a=f'{a:02}',b=f'{b:02}',score=round(float(scores[idx]),2),
            either_days=int(either[idx]),both_days=int(both[idx]),sample_days=n,
            either_rate=round(100*float(either[idx])/n,2),both_rate=round(100*float(both[idx])/n,2),
            either_lower=round(100*float(wilson(either[idx],n)),2),both_lower=round(100*float(wilson(both[idx],n)),2),
            tags=tags,reasons=reasons))
    if detail:rules.sort(key=lambda r:(not r['eligible'],-r['lower'],-r['samples'],r['number'],r['kind'],r['source']))
    return dict(**{**base,'pairs':pairs,'selected':pairs[0],'rules':rules,
        'number_scores':[dict(number=f'{i:02}',score=round(float(number_score[i]*100),2),qualified_rules=len(support[i])) for i in range(100)]},
        warning='Tuyển chọn thăm dò trên lịch sử; chưa chứng minh lợi thế ngoài mẫu. Tỷ lệ của cặp đứng đầu có thể bị thiên lệch do chọn từ 4.950 cặp.')


def walk_forward(draws,window=180,min_support=20,points=100,cost_rate=23000,payout_rate=80000,progress=None,cancel=None):
    if min(int(points),int(cost_rate),int(payout_rate))<=0:raise ValueError('Điểm và đơn giá phải dương.')
    # Validate configuration even if history is empty.
    analyze([],window,min_support,detail=False)
    daily=[];skipped=0;insufficient=0
    for i in range(60,len(draws)):
        if cancel and cancel():raise ValueError('Đã hủy tác vụ.')
        if (date.fromisoformat(draws[i].day)-date.fromisoformat(draws[i-1].day)).days!=1:skipped+=1;continue
        result=analyze(draws[:i],window,min_support,limit=1,detail=False);pair=result['selected']
        if pair is None:insufficient+=1;continue
        a,b=pair['a'],pair['b'];hits=draws[i].numbers.count(a)+draws[i].numbers.count(b)
        cost=2*int(points)*int(cost_rate);received=hits*int(points)*int(payout_rate)
        daily.append(dict(day=draws[i].day,picks=[a,b],hits=hits,both=a in draws[i].numbers and b in draws[i].numbers,
            cost=cost,received=received,profit=received-cost))
        if progress and i%5==0:progress(int(100*(i-59)/max(1,len(draws)-60)),f'Kiểm tra cầu {i-59}/{len(draws)-60}')
    result=summarize(daily)
    result.update(both_days=sum(r['both'] for r in daily),both_rate=round(100*sum(r['both'] for r in daily)/len(daily),2) if daily else None,
        skipped_gaps=skipped,skipped_insufficient=insufficient,window=int(window),min_support=int(min_support),
        points=int(points),cost_rate=int(cost_rate),payout_rate=int(payout_rate),version=VERSION,
        methodology='Mỗi kỳ chọn lại cặp từ dữ liệu trước kỳ đó; song thủ hai số, điểm cố định mỗi số. Đây là kiểm tra lịch sử, không phải đảm bảo cho ngày tiếp theo.')
    return result
