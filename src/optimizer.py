"""Chronological holdout search. More trials do not imply better future returns."""
import numpy as np
from .pro_analytics import DEFAULT_WEIGHTS,FAMILY_NAMES,weight_vector
from .pro_backtest import prepare,from_prepared


def optimize(draws,trials=2000,top_n=1,points=100,cost_rate=23000,payout_rate=80000,progress=None,cancel=None):
    trials=int(trials)
    if not 10<=trials<=10000:raise ValueError('Số thử từ 10 đến 10.000.')
    prepared=prepare(draws,60,progress,cancel); f,actual,days,skipped=prepared
    n=len(days)
    if n<120:raise ValueError('Optimizer cần ít nhất 120 kỳ kiểm tra sau 60 kỳ khởi động, tức khoảng 180 ngày liên tục.')
    ntrain=int(n*.6); nval=int(n*.8)
    rng=np.random.default_rng(20260916)
    candidates=[weight_vector()]
    base=weight_vector()
    for freq in (.15,.20,.25,.30,.35):
        w=base.copy(); w[1:]*=(1-freq)/w[1:].sum(); w[0]=freq; candidates.append(w)
    candidates.extend(rng.dirichlet(np.ones(len(FAMILY_NAMES))*2,size=max(0,trials-len(candidates))))
    candidates=np.array(candidates[:trials]); best=-float('inf'); bestw=base; curve=[]
    for start in range(0,len(candidates),32):
        if cancel and cancel():raise ValueError('Đã hủy tác vụ.')
        batch=candidates[start:start+32]
        scores=np.einsum('dnf,cf->cdn',f[:ntrain],batch,optimize=True)
        picks=np.argsort(-scores,axis=2,kind='stable')[:,:,:int(top_n)]
        hits=np.take_along_axis(np.broadcast_to(actual[:ntrain],(len(batch),ntrain,100)),picks,axis=2).sum(axis=(1,2))
        rois=100*(hits*int(payout_rate)-ntrain*int(top_n)*int(cost_rate))/(ntrain*int(top_n)*int(cost_rate))
        for j,roi in enumerate(rois):
            if roi>best:best=float(roi); bestw=batch[j]
            curve.append(dict(trial=start+j+1,train_roi=round(best,4)))
        if progress:progress(int(100*min(start+32,trials)/trials),f'Thử {min(start+32,trials):,}/{trials:,} bộ trọng số')
    weights=dict(zip(FAMILY_NAMES,map(float,bestw)))
    result=dict(weights=weights,trials=trials,curve=curve,top_n=int(top_n),seed=20260916,
        explanation='Chọn ROI cao nhất trên 60% kỳ đầu; 20% kế tiếp để xác nhận; 20% cuối chỉ báo cáo. Thử lại nhiều lần trên cùng dữ liệu làm suy yếu ý nghĩa tập kiểm tra.')
    for label,a,b in [('train',0,ntrain),('validation',ntrain,nval),('test',nval,n)]:
        part=(f[a:b],actual[a:b],days[a:b],0)
        result[label]=from_prepared(part,top_n,points,cost_rate,payout_rate,weights)
        result[label].update(start=days[a],end=days[b-1])
        result[label]['baseline_roi']=from_prepared(part,top_n,points,cost_rate,payout_rate,DEFAULT_WEIGHTS)['roi']
    return result
