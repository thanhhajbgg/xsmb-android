from datetime import date
import numpy as np
from .pro_analytics import features,families,weight_vector,matrix


def prepare(draws,warmup=60,progress=None,cancel=None):
    frames=[]; actual=[]; days=[]; skipped=0
    for i in range(warmup,len(draws)):
        if cancel and cancel():raise ValueError('Đã hủy tác vụ.')
        if (date.fromisoformat(draws[i].day)-date.fromisoformat(draws[i-1].day)).days!=1:
            skipped+=1; continue
        frames.append(families(features(draws[:i]))); actual.append(matrix([draws[i]])[0]); days.append(draws[i].day)
        if progress and i%10==0:progress(int(100*(i-warmup+1)/max(1,len(draws)-warmup)),f'Tạo đặc trưng {i-warmup+1}/{len(draws)-warmup}')
    return np.array(frames),np.array(actual),days,skipped


def summarize(daily):
    cost=sum(r['cost'] for r in daily); received=sum(r['received'] for r in daily); profit=received-cost
    running=0; peak=0; drawdown=0
    for r in daily:
        running+=r['profit']; r['cumulative']=running; peak=max(peak,running); drawdown=max(drawdown,peak-running)
    return dict(days=len(daily),hit_days=sum(r['hits']>0 for r in daily),
        hit_rate=round(100*sum(r['hits']>0 for r in daily)/len(daily),2) if daily else None,
        wins=sum(r['profit']>0 for r in daily),losses=sum(r['profit']<0 for r in daily),breakeven=sum(r['profit']==0 for r in daily),
        cost=cost,received=received,profit=profit,roi=round(100*profit/cost,2) if cost else None,max_drawdown=drawdown,daily=daily)


def from_prepared(prepared,top_n=1,points=100,cost_rate=23000,payout_rate=80000,weights=None):
    f,actual,days,skipped=prepared
    if not 1<=int(top_n)<=10 or int(points)<=0 or int(cost_rate)<=0 or int(payout_rate)<=0:raise ValueError('Thông số tính tiền không hợp lệ.')
    daily=[]
    if len(days):
        scores=f@weight_vector(weights); picks=np.argsort(-scores,axis=1,kind='stable')[:,:int(top_n)]
        for i,day in enumerate(days):
            chosen=picks[i]; hits=int(actual[i,chosen].sum()); cost=int(top_n)*int(points)*int(cost_rate); received=hits*int(points)*int(payout_rate)
            daily.append(dict(day=day,picks=[f'{n:02}' for n in chosen],hits=hits,cost=cost,received=received,profit=received-cost))
    return dict(**summarize(daily),top_n=int(top_n),points=int(points),cost_rate=int(cost_rate),payout_rate=int(payout_rate),skipped_gaps=skipped,
                methodology='Walk-forward: chỉ dùng kỳ trước; điểm cố định mỗi số; nhiều nháy trả nhiều lần. Không mô phỏng thiếu vốn hay giới hạn cược.')


def evaluate(draws,top_n=1,points=100,cost_rate=23000,payout_rate=80000,weights=None,warmup=60,progress=None,cancel=None):
    return from_prepared(prepare(draws,warmup,progress,cancel),top_n,points,cost_rate,payout_rate,weights)
