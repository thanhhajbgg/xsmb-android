"""Descriptive statistics. Scores are relative rankings, not probabilities."""
from datetime import date, timedelta
import numpy as np

FEATURES = [
 ('f7','Tần suất 7 kỳ'),('f14','Tần suất 14 kỳ'),('f30','Tần suất 30 kỳ'),
 ('f60','Tần suất 60 kỳ'),('f90','Tần suất 90 kỳ'),('f180','Tần suất 180 kỳ'),
 ('presence7','Ngày xuất hiện / 7 kỳ'),('presence30','Ngày xuất hiện / 30 kỳ'),
 ('gap','Gan hiện tại (kỳ)'),('max_gap','Khoảng cách lớn nhất giữa hai lần xuất hiện'),
 ('mean_cycle','Chu kỳ trung bình'),('std_cycle','Độ lệch chu kỳ'),
 ('last_count','Số nháy kỳ cuối'),('streak','Chuỗi kỳ xuất hiện liên tiếp'),
 ('head30','Tần suất đầu / 30 kỳ'),('tail30','Tần suất đuôi / 30 kỳ'),
 ('double30','Tần suất kép / 30 kỳ'),('reverse14','Tần suất số đảo / 14 kỳ'),
 ('cooccurrence','Đồng xuất hiện với bộ số kỳ cuối'),('markov','Markov có/lặp lại, làm trơn Laplace'),
 ('weekday','Tần suất theo thứ dự báo'),('month','Tần suất cùng tháng dự báo'),
 ('year','Tần suất năm dữ liệu gần nhất'),('special30','Đuôi ĐB / 30 kỳ'),
 ('special_gap','Gan đuôi ĐB'),('momentum','Tần suất 7 kỳ/ngày − 30 kỳ/ngày'),
 ('ema','Tần suất EMA, alpha 0,1'),('repeat30','Ngày nhiều nháy / 30 kỳ'),
 ('cycle_fit','Độ gần chu kỳ lịch sử'),('entropy','Entropy có/không xuất hiện')]
FAMILY_NAMES=['frequency','recency','cycle','transition','calendar','structure','reverse','momentum']
DEFAULT_WEIGHTS=dict(zip(FAMILY_NAMES,[.30,.15,.10,.15,.10,.08,.05,.07]))


def matrix(draws):
    out=np.zeros((len(draws),100),dtype=float)
    for i,d in enumerate(draws):
        for n in d.numbers: out[i,int(n)]+=1
    return out


def normalized(x):
    x=np.asarray(x,dtype=float)
    lo=x.min(axis=0); span=np.ptp(x,axis=0)
    return np.divide(x-lo,span,out=np.zeros_like(x),where=span>1e-12)


def features(draws,target=None):
    out=np.zeros((100,30),dtype=float)
    if not draws:return out
    target=target or date.fromisoformat(draws[-1].day)+timedelta(days=1)
    m=matrix(draws); p=m>0; total=len(draws)
    for j,w in enumerate((7,14,30,60,90,180)):out[:,j]=m[-w:].sum(axis=0)
    out[:,6]=p[-7:].sum(axis=0); out[:,7]=p[-30:].sum(axis=0)
    for n in range(100):
        ix=np.flatnonzero(p[:,n]); cycles=np.diff(ix)
        gap=total-1-ix[-1] if len(ix) else total
        mean=float(cycles.mean()) if len(cycles) else 0
        std=float(cycles.std()) if len(cycles) else 0
        streak=0
        for yes in p[::-1,n]:
            if not yes:break
            streak+=1
        out[n,8:14]=[gap,float(cycles.max()) if len(cycles) else 0,mean,std,m[-1,n],streak]
        if len(cycles)>=2:out[n,28]=np.exp(-abs((gap+1)-mean)/(std+1))
    freq30=out[:,2].reshape(10,10)
    out[:,14]=np.repeat(freq30.sum(axis=1),10)
    out[:,15]=np.tile(freq30.sum(axis=0),10)
    out[:,16]=[out[n,2] if n//10==n%10 else 0 for n in range(100)]
    out[:,17]=out[:,1].reshape(10,10).T.reshape(100)
    last=np.flatnonzero(p[-1]); recent=p[-90:].astype(float)
    co=recent.T@recent
    np.fill_diagonal(co,0)
    out[:,18]=co[:,last].mean(axis=1) if len(last) else 0
    if total>1:
        prev=p[:-1]; nxt=p[1:]; condition=prev==p[-1]
        out[:,19]=((condition & nxt).sum(axis=0)+1)/(condition.sum(axis=0)+2)
    dates=[date.fromisoformat(d.day) for d in draws]
    for col,mask in [(20,[x.weekday()==target.weekday() for x in dates]),(21,[x.month==target.month for x in dates]),(22,[x.year==dates[-1].year for x in dates])]:
        if any(mask):out[:,col]=m[mask].mean(axis=0)
    specials=[int(d.special_prize[-2:]) if d.special_prize.isdigit() and len(d.special_prize)>=2 else -1 for d in draws]
    for n in range(100):
        out[n,23]=specials[-30:].count(n)
        out[n,24]=next((i for i,v in enumerate(reversed(specials)) if v==n),total)
    out[:,25]=out[:,0]/min(7,total)-out[:,2]/min(30,total)
    ema=np.zeros(100)
    for row in m:ema=.1*row+.9*ema
    out[:,26]=ema
    out[:,27]=(m[-30:]>1).sum(axis=0)
    rate=p.mean(axis=0); safe=np.clip(rate,1e-12,1-1e-12)
    out[:,29]=-safe*np.log2(safe)-(1-safe)*np.log2(1-safe)
    return out


def families(f):
    z=normalized(f)
    return np.column_stack((z[:,:6]@np.array([.28,.23,.20,.14,.10,.05]),z[:,26],z[:,28],
        (z[:,19]+z[:,18])/2,(z[:,20]+z[:,21]+z[:,22])/3,
        (z[:,14]+z[:,15]+z[:,23])/3,z[:,17],z[:,25]))


def weight_vector(weights=None):
    weights=DEFAULT_WEIGHTS if weights is None else weights
    v=np.array([float(weights.get(k,0)) for k in FAMILY_NAMES])
    if not np.isfinite(v).all() or (v<0).any() or v.sum()<=0:raise ValueError('Trọng số phải không âm và tổng lớn hơn 0.')
    return v/v.sum()


def rank(draws,weights=None):
    if not draws:return []
    f=features(draws); scores=normalized(families(f)@weight_vector(weights))*100
    # Cluster descriptive feature profiles, never interpreted as predictive class.
    cluster_data=normalized(f[:,[0,2,8,25,26]])
    centers=cluster_data[[0,33,66,99]].copy(); labels=np.zeros(100,dtype=int)
    for _ in range(20):
        labels=((cluster_data[:,None,:]-centers[None,:,:])**2).sum(axis=2).argmin(axis=1)
        new=np.array([cluster_data[labels==k].mean(axis=0) if (labels==k).any() else centers[k] for k in range(4)])
        if np.allclose(new,centers):break
        centers=new
    order=np.lexsort((np.arange(100),-scores))
    return [dict(number=f'{n:02}',score=round(float(scores[n]),2),cluster=int(labels[n])+1,
        features={key:round(float(f[n,j]),4) for j,(key,_) in enumerate(FEATURES)}) for n in order]


def pair_stats(draws,limit=20):
    if not draws:return []
    p=(matrix(draws[-90:])>0).astype(int); co=p.T@p
    pairs=[(int(co[a,b]),a,b) for a in range(100) for b in range(a+1,100)]
    pairs.sort(key=lambda x:(-x[0],x[1],x[2]))
    return [dict(a=f'{a:02}',b=f'{b:02}',days=c,sample=len(p)) for c,a,b in pairs[:limit]]


def confidence(draws,weights=None):
    if not draws:return dict(value=0,label='Chưa có dữ liệu',coverage=0,agreement=0,sample=0)
    fs=families(features(draws)); combined=np.lexsort((np.arange(100),-(fs@weight_vector(weights))))[:10]
    agreement=float(np.mean([len(set(combined)&set(np.lexsort((np.arange(100),-fs[:,j]))[:10]))/10 for j in range(fs.shape[1])]))
    dates=[date.fromisoformat(d.day) for d in draws]
    coverage=len(set(dates))/((dates[-1]-dates[0]).days+1)
    sample=min(len(draws)/365,1)
    value=round(100*(.4*sample+.3*coverage+.3*agreement))
    return dict(value=value,label='Độ đầy đủ & đồng thuận tín hiệu',coverage=round(100*coverage,1),agreement=round(100*agreement,1),sample=len(draws))
