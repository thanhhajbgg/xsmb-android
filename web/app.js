'use strict';
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const token=$('meta[name="app-token"]').content;
const money=v=>v===null||v===undefined?'—':new Intl.NumberFormat('vi-VN',{maximumFractionDigits:0}).format(v)+' đ';
const num=v=>v===null||v===undefined?'—':new Intl.NumberFormat('vi-VN',{maximumFractionDigits:2}).format(v);
const pct=v=>v===null||v===undefined?'—':num(v)+'%';
const day=v=>v&&/^\d{4}-\d{2}-\d{2}$/.test(v)?v.split('-').reverse().join('/'):v||'—';
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const profit=v=>`<span class="${v>0?'positive':v<0?'negative':'muted'}">${money(v)}</span>`;
const balls=values=>`<div class="pick-set">${values.map(v=>`<span class="pick-ball">${esc(v)}</span>`).join('')}</div>`;
const formData=form=>Object.fromEntries(new FormData(form));
const familyNames={frequency:'Tần suất',recency:'Gần đây',cycle:'Chu kỳ',transition:'Chuyển trạng thái',calendar:'Lịch',structure:'Đầu/đuôi/ĐB',reverse:'Đảo',momentum:'Xu hướng'};
let state=null,finance=null,optimizer=null,currentPage='dashboard',pollTimer=null,toastTimer=null,historyRows=[];
const charts=new Map();
async function api(path,data){
 const res=await fetch('/api/'+path,{method:data===undefined?'GET':'POST',headers:{'X-App-Token':token,'Content-Type':'application/json'},body:data===undefined?undefined:JSON.stringify(data)});
 const body=await res.json();if(!res.ok)throw Error(body.error||'Không thực hiện được');return body;
}
function toast(message,error=false){const el=$('#toast');el.textContent=message;el.style.borderColor=error?'var(--negative)':'var(--accent)';el.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.hidden=true,error?12000:4500)}
async function attempt(fn){try{return await fn()}catch(e){toast(e.message,true)}}
function table(id,columns,rows){
 const el=$(id);if(!rows.length){el.innerHTML='<div class="empty">Chưa có dữ liệu cho mục này.</div>';return}
 el.innerHTML='<div class="table-wrap"><table><thead><tr>'+columns.map(c=>`<th>${esc(c[0])}</th>`).join('')+'</tr></thead><tbody>'+rows.map(r=>'<tr>'+columns.map(c=>`<td${c[2]?' class="wrap"':''}>${c[1](r)}</td>`).join('')+'</tr>').join('')+'</tbody></table></div>';
}
function card(label,value,sub='',extra=''){return `<div class="card ${extra}"><div class="card-label">${esc(label)}</div><div class="card-value">${value}</div><div class="card-sub">${esc(sub)}</div></div>`}
function weightsHTML(weights){return Object.entries(weights).map(([key,val])=>`<div class="weight"><span>${esc(familyNames[key]||key)}</span><div class="weight-bar"><i style="width:${Math.max(0,Math.min(100,val*100))}%"></i></div><b>${num(val*100)}%</b></div>`).join('')}
function showPage(name){
 currentPage=name;$$('.page').forEach(p=>p.classList.toggle('active',p.id===name));$$('.nav').forEach(n=>n.classList.toggle('active',n.dataset.page===name));
 $('#page-title').textContent=$(`.nav[data-page="${name}"]`).textContent.trim().slice(1).trim();
 if(name==='prediction')attempt(loadPrediction);if(name==='cau')attempt(loadCau);if(name==='finance')attempt(loadFinance);if(name==='journal')attempt(loadJournal);if(name==='charts')attempt(loadHistory);
 requestAnimationFrame(()=>charts.forEach(c=>c.draw()));window.scrollTo({top:0,behavior:'smooth'});
}
function renderDashboard(){
 const d=state.dashboard,forecast=d.forecast_picks||[];$('#target-date').textContent=day(d.target);$('#model-badge').textContent=d.model;
 $('#data-caption').textContent=d.count?`${num(d.count)} kỳ • Dữ liệu đến ${day(d.last_day)} • ${d.gaps} ngày thiếu trong lịch sử`:'Chưa có dữ liệu. Mở Dữ liệu để tải kết quả hoặc nhập CSV.';
 const warning=d.warning||(!d.count?'Chưa có dữ liệu để xếp hạng. Sổ thắng/thua vẫn có thể nhập bằng tay.':'');$('#data-warning').textContent=warning;$('#data-warning').hidden=!warning;
 const fp=state.prediction?.snapshot||state.prediction;
 $('#pick-cards').innerHTML=card('Bạch thủ · từ cầu',fp?.bach_thu?balls([fp.bach_thu]):'Chưa đủ mẫu',forecastStatus(fp),'accent')+card('Song thủ · từ cầu',fp?.song_thu?.length?balls(fp.song_thu):'Chưa đủ mẫu','Hai số đánh riêng')+[3,5,10].map(n=>card(`Top ${n} thống kê`,balls(forecast.slice(0,n).map(x=>x.number)),'Tham khảo xếp hạng thống kê')).join('');
 $('#forecast-caption').textContent='Bạch thủ / song thủ lấy từ mô-đun Dự đoán & soi cầu. '+forecastStatus(fp)+' · Kỳ '+day(fp?.target)+'. Top 3/5/10 vẫn là xếp hạng thống kê.';
 const by=Object.fromEntries(d.ranking.map(x=>[x.number,x]));$('#heatmap').innerHTML=Array.from({length:100},(_,i)=>{const n=String(i).padStart(2,'0'),x=by[n],score=x?.score||0;return `<button class="heat-cell" data-number="${n}" style="background:color-mix(in srgb, var(--accent) ${Math.round(score*.7)}%,var(--panel))" title="Số ${n} • Score ${num(x?.score)}"><strong>${n}</strong><span>${num(x?.score)}</span></button>`}).join('');
 const conf=d.confidence;$('#confidence-value').textContent=d.count?conf.value:'—';$('#confidence-gauge').style.setProperty('--value',conf.value);
 $('#confidence-detail').innerHTML=[['Số kỳ dữ liệu',num(conf.sample)],['Độ đầy đủ lịch sử',pct(conf.coverage)],['Đồng thuận các nhóm',pct(conf.agreement)]].map(([a,b])=>`<div><span class="muted">${a}</span><b>${b}</b></div>`).join('');$('#weights-mini').innerHTML=weightsHTML(d.weights);
 table('#top-table',[['Hạng',r=>r.index],['Số',r=>balls([r.number])],['AI Score',r=>`<b>${num(r.score)}</b>`],['7 kỳ',r=>num(r.features.f7)],['30 kỳ',r=>num(r.features.f30)],['Gan (kỳ)',r=>num(r.features.gap)],['Cụm',r=>r.cluster]],d.ranking.slice(0,10).map((r,i)=>({...r,index:i+1})));
 const select=$('#feature-select'),previous=select.value;select.innerHTML=d.features.map(([key,label])=>`<option value="${key}">${esc(label)}</option>`).join('');if(previous)select.value=previous;
 $('#feature-dictionary').innerHTML=d.features.map(([key,label],i)=>`<div><code>${String(i+1).padStart(2,'0')} ${esc(key)}</code>${esc(label)}</div>`).join('');
 table('#pair-table',[['Cặp số',r=>balls([r.a,r.b])],['Ngày cùng xuất hiện',r=>r.days],['Số kỳ mẫu',r=>r.sample]],d.pairs);
 renderAnalysis();$('#initial-capital').value=d.initial_capital;
 $('#provider-list').innerHTML=state.providers.map(p=>`<label><input type="checkbox" name="providers" value="${esc(p.id)}" checked>${esc(p.name)}</label>`).join('');
 if(state.last_update)$('#source-log').textContent=`${state.last_update.success} ngày thành công • ${state.last_update.failed} ngày lỗi • ${state.last_update.skipped} ngày đã có\n`+state.last_update.logs.join('\n');
 renderBacktest(state.last_backtest);if(state.optimizer){optimizer={...state.optimizer.result,model_id:state.optimizer.id};renderOptimizer(optimizer)}
}
function renderAnalysis(){if(!state)return;const key=$('#feature-select').value||'f7',sort=$('#analysis-sort').value,filter=$('#analysis-number').value.trim();let rows=state.dashboard.ranking.filter(r=>!filter||r.number.includes(filter));rows=[...rows].sort((a,b)=>sort==='feature'?b.features[key]-a.features[key]:sort==='number'?a.number.localeCompare(b.number):b.score-a.score);
 const name=state.dashboard.features.find(x=>x[0]===key)?.[1]||key;
 table('#analysis-table',[['Số lô',r=>balls([r.number])],['AI Score',r=>num(r.score)],[name,r=>num(r.features[key])],['Tần suất 7 kỳ',r=>num(r.features.f7)],['Tần suất 30 kỳ',r=>num(r.features.f30)],['Gan',r=>num(r.features.gap)],['Cụm',r=>r.cluster]],rows)
}
class LineChart{
 constructor(canvas,rows,key,formatter=num){this.canvas=canvas;this.rows=rows;this.key=key;this.formatter=formatter;this.start=0;this.end=rows.length;this.hover=null;this.drag=null;
  canvas.onwheel=e=>{e.preventDefault();this.zoom(e.deltaY<0?.8:1.25)};
  canvas.onpointerdown=e=>{this.drag={x:e.clientX,start:this.start};canvas.setPointerCapture(e.pointerId)};
  canvas.onpointermove=e=>{const rect=canvas.getBoundingClientRect();if(this.drag){const count=this.end-this.start;this.start=Math.max(0,Math.min(this.rows.length-count,this.drag.start-(e.clientX-this.drag.x)*count/Math.max(1,rect.width-90)));this.end=this.start+count}else this.hover=e.clientX-rect.left;this.draw()};
  canvas.onpointerup=()=>this.drag=null;canvas.onpointercancel=()=>this.drag=null;canvas.onpointerleave=()=>{this.hover=null;this.draw()};canvas.ondblclick=()=>this.reset();this.observer=new ResizeObserver(()=>this.draw());this.observer.observe(canvas);this.draw();
 }
 destroy(){this.observer.disconnect()}
 reset(){this.start=0;this.end=this.rows.length;this.draw()}
 zoom(factor){if(!this.rows.length)return;const count=Math.max(Math.min(7,this.rows.length),Math.min(this.rows.length,(this.end-this.start)*factor)),mid=(this.start+this.end)/2;this.start=Math.max(0,Math.min(this.rows.length-count,mid-count/2));this.end=this.start+count;this.draw()}
 pan(direction){const count=this.end-this.start;this.start=Math.max(0,Math.min(this.rows.length-count,this.start+direction*count*.3));this.end=this.start+count;this.draw()}
 draw(){const rect=this.canvas.getBoundingClientRect();if(rect.width<10||rect.height<10)return;const dpr=window.devicePixelRatio||1;this.canvas.width=rect.width*dpr;this.canvas.height=rect.height*dpr;const c=this.canvas.getContext('2d');c.scale(dpr,dpr);const w=rect.width,h=rect.height,css=getComputedStyle(document.documentElement),muted=css.getPropertyValue('--muted'),accent=css.getPropertyValue('--accent');c.font='11px Segoe UI, sans-serif';c.fillStyle=muted;
  const rows=this.rows.slice(Math.floor(this.start),Math.ceil(this.end));if(!rows.length){c.textAlign='center';c.fillText('Chưa có dữ liệu để vẽ biểu đồ',w/2,h/2);return}
  const vals=rows.map(r=>Number(r[this.key])||0),lo=Math.min(...vals),hi=Math.max(...vals),span=(hi-lo)||1,min=lo-span*.08,max=hi+span*.08,left=75,right=w-15,top=18,bottom=h-35;
  const x=i=>left+(right-left)*i/Math.max(1,rows.length-1),y=v=>bottom-(v-min)/(max-min)*(bottom-top);
  c.strokeStyle=css.getPropertyValue('--line');c.lineWidth=1;c.textAlign='right';for(let i=0;i<5;i++){const v=min+(max-min)*i/4,yy=y(v);c.beginPath();c.moveTo(left,yy);c.lineTo(right,yy);c.stroke();c.fillStyle=muted;c.fillText(Math.abs(v)>=1e6?num(v/1e6)+' tr':num(v),left-8,yy+4)}
  c.textAlign='left';c.fillText(day(rows[0].day||String(rows[0].trial)),left,h-10);c.textAlign='right';c.fillText(day(rows.at(-1).day||String(rows.at(-1).trial)),right,h-10);
  c.beginPath();vals.forEach((v,i)=>i?c.lineTo(x(i),y(v)):c.moveTo(x(i),y(v)));c.strokeStyle=accent;c.lineWidth=2;c.stroke();
  if(rows.length===1){c.beginPath();c.arc(x(0),y(vals[0]),4,0,Math.PI*2);c.fillStyle=accent;c.fill()}
  c.lineTo(x(vals.length-1),bottom);c.lineTo(left,bottom);c.closePath();const grad=c.createLinearGradient(0,top,0,bottom);grad.addColorStop(0,'rgba(59,130,246,.20)');grad.addColorStop(1,'rgba(59,130,246,0)');c.fillStyle=grad;c.fill();
  if(this.hover!==null){const index=Math.max(0,Math.min(rows.length-1,Math.round((this.hover-left)/(right-left)*(rows.length-1)))),xx=x(index),yy=y(vals[index]);c.strokeStyle=muted;c.setLineDash([3,4]);c.beginPath();c.moveTo(xx,top);c.lineTo(xx,bottom);c.stroke();c.setLineDash([]);const text=`${day(rows[index].day||String(rows[index].trial))} • ${this.formatter(vals[index])}`,tw=c.measureText(text).width+18,tx=Math.min(Math.max(left,xx-tw/2),w-tw-5);c.fillStyle=css.getPropertyValue('--panel2');c.fillRect(tx,top,tw,27);c.fillStyle=css.getPropertyValue('--text');c.textAlign='left';c.fillText(text,tx+9,top+18);c.beginPath();c.arc(xx,yy,4,0,Math.PI*2);c.fillStyle=accent;c.fill()}
 }
}
function chart(id,rows,key,formatter=num){const canvas=$(id);if(!canvas)return;charts.get(id)?.destroy();const c=new LineChart(canvas,rows,key,formatter);charts.set(id,c);return c}
function renderBacktest(b){const el=$('#backtest-results');if(!b){el.innerHTML='<div class="empty">Chạy backtest để xem kết quả thực từ lịch sử đã tải.</div>';return}
 el.innerHTML=`<div class="notice">Top ${b.top_n} • ${num(b.points)} điểm/số • ${b.days} kỳ đánh giá • Bỏ qua ${b.skipped_gaps} kỳ sau ngày bị thiếu. Thắng/thua dưới đây tính theo lãi/lỗ ròng.</div><div class="cards">${card('Hit · ngày có ít nhất một nháy',pct(b.hit_rate))}${card('ROI',pct(b.roi),'Lãi / tổng tiền mua')}${card('Lãi / lỗ',profit(b.profit))}${card('Thắng / Thua',`${b.wins} / ${b.losses}`,`${b.breakeven} ngày hòa vốn`)}${card('Sụt giảm lớn nhất',money(b.max_drawdown),'Từ đỉnh lãi lũy kế')}</div><article class="panel"><div class="panel-title"><h3>Đường lãi/lỗ lũy kế</h3><span class="small muted">Cuộn để zoom • kéo để pan</span></div><canvas id="backtest-chart" class="chart"></canvas></article><article class="panel"><h3>Chi tiết từng kỳ</h3><div id="backtest-table"></div></article>`;
 chart('#backtest-chart',b.daily,'cumulative',money);table('#backtest-table',[['Ngày',r=>day(r.day)],['Số chọn',r=>esc(r.picks.join(' · '))],['Nháy',r=>r.hits],['Tiền mua',r=>money(r.cost)],['Tiền nhận',r=>money(r.received)],['Lãi/lỗ',r=>profit(r.profit)],['Lũy kế',r=>profit(r.cumulative)]],b.daily)
}
async function loadFinance(){const query=new URLSearchParams({period:$('#finance-period').value,start:$('#finance-start').value,end:$('#finance-end').value});finance=await api('finance?'+query);const f=finance;
 $('#finance-cards').innerHTML=card('Vốn khả dụng',money(f.cash),'Đã trừ tiền khoản đang chờ')+card('Doanh thu · tiền nhận',money(f.received))+card('Lãi/lỗ đã chốt',profit(f.profit))+card('ROI đã chốt',pct(f.roi),'Trên tiền mua đã có kết quả')+card('Khoản đang chờ',money(f.pending_cost),`${f.pending} khoản`);
 $('#finance-note').textContent=f.explanation;chart('#finance-chart',f.groups,'cash',money);
 table('#ledger-table',[['Ngày',r=>day(r.day)],['Số',r=>balls([r.number])],['Điểm',r=>num(r.points)],['Nháy',r=>r.hits===null?'Chờ':r.hits],['Tiền mua',r=>money(r.cost)],['Tiền nhận',r=>money(r.received)],['Lãi/lỗ',r=>profit(r.profit)],['Nguồn',r=>esc(r.source)],['Ghi chú',r=>esc(r.note),true],['Thao tác',r=>`<button class="action-small" data-edit="${r.id}">Sửa</button><button class="action-small negative" data-delete="${r.id}">Xóa</button>`]],f.rows);
 table('#finance-table',[['Kỳ',r=>day(r.day)],['Vốn đầu kỳ',r=>money(r.opening)],['Tiền mua',r=>money(r.cost)],['Tiền nhận',r=>money(r.received)],['Lãi/lỗ',r=>profit(r.profit)],['Tiền chờ',r=>money(r.pending_cost)],['Vốn khả dụng',r=>money(r.cash)],['ROI',r=>pct(r.roi)]],f.groups)
}
function clearLedger(){const form=$('#ledger-form');form.elements.id.value='';form.elements.hits.value='';form.elements.note.value='';$('#ledger-heading').textContent='Thêm khoản đánh'}
async function loadJournal(){const values=formData($('#journal-form')),j=await api('journal?'+new URLSearchParams(values));$('#journal-note').textContent=j.notice;
 table('#journal-table',[['Kỳ',r=>day(r.day)],['AI đã chọn',r=>balls(r.picks)],['Số đã trúng',r=>r.matched.length?esc(r.matched.map(m=>`${m.number} × ${m.hits}`).join(' · ')):'—'],['Tổng nháy',r=>r.hits===null?'Chờ':r.hits],['Tiền nhận mô phỏng',r=>money(r.received)],['Lãi/lỗ mô phỏng',r=>profit(r.profit)],['Loại bản ghi',r=>r.kind==='live'?'Lưu trước giờ quay':'Hồi cứu · không tính dự báo thật']],j.rows)
}
async function loadHistory(){const result=await api('history?number='+encodeURIComponent($('#chart-number').value));historyRows=result.rows;chart('#history-chart',historyRows,$('#chart-metric').value,num);table('#history-table',[['Ngày',r=>day(r.day)],['Số',()=>balls([result.number])],['Số nháy',r=>r.hits],['Tổng lũy kế',r=>num(r.cumulative)]],historyRows.slice().reverse())}
function renderOptimizer(o){optimizer=o;$('#optimizer-results').innerHTML=`<div class="cards opt-cards">${[['train','Chọn trọng số'],['validation','Xác nhận'],['test','Kiểm tra cuối']].map(([k,label])=>card(label,pct(o[k].roi),`${day(o[k].start)} – ${day(o[k].end)} · Gốc: ${pct(o[k].baseline_roi)}`)).join('')}</div><div class="two-col"><article class="panel"><h3>Trọng số tìm được · ${num(o.trials)} cấu hình</h3>${weightsHTML(o.weights)}<div class="toolbar"><button id="apply-model" class="primary">Áp dụng cho kỳ tiếp theo</button><button id="reset-model" class="secondary">Dùng trọng số gốc</button></div><p class="small muted">Áp dụng không thay đổi các lựa chọn đã lưu trong nhật ký. Không tự tăng điểm hay tạo khoản đánh.</p></article><article class="panel"><h3>ROI tốt nhất trên tập chọn trọng số</h3><canvas id="optimizer-chart" class="chart"></canvas></article></div><article class="panel"><h3>Đánh giá đầy đủ theo giai đoạn</h3><div id="optimizer-table"></div><p class="small muted">${esc(o.explanation)}</p></article>`;
 chart('#optimizer-chart',o.curve,'train_roi',pct);table('#optimizer-table',[['Giai đoạn',r=>r.label],['Số kỳ',r=>r.days],['Hit',r=>pct(r.hit_rate)],['ROI tìm được',r=>pct(r.roi)],['ROI gốc',r=>pct(r.baseline_roi)],['Lãi/lỗ',r=>profit(r.profit)],['Thắng/Thua',r=>`${r.wins}/${r.losses}`],['Sụt giảm lớn nhất',r=>money(r.max_drawdown)]],[{...o.train,label:'Chọn trọng số'},{...o.validation,label:'Xác nhận'},{...o.test,label:'Kiểm tra'}]);
 $('#apply-model').onclick=()=>attempt(async()=>{const r=await api('model/apply',{id:o.model_id});toast(r.message);await refresh()});$('#reset-model').onclick=()=>attempt(async()=>{toast((await api('model/reset',{})).message);await refresh()})
}
async function refresh(){state=await api('state');renderDashboard();if(currentPage==='prediction')await loadPrediction();if(currentPage==='cau')await loadCau();if(currentPage==='finance')await loadFinance();if(currentPage==='journal')await loadJournal();if(currentPage==='charts')await loadHistory()}
async function startJob(kind,values){await api('job',{kind,...values});$('#job-panel').hidden=false;pollJob()}
async function pollJob(){clearTimeout(pollTimer);try{const j=await api('status');$('#job-panel').hidden=!j.running;$('#job-message').textContent=j.message;$('#job-progress').value=j.progress;$$('#prediction-test,#backtest-form button[type=submit],#optimizer-form button[type=submit],#update-form button[type=submit],#cau-backtest-form button[type=submit]').forEach(b=>b.disabled=j.running);if(j.running){pollTimer=setTimeout(pollJob,900);return}if(j.error)toast(j.error,true);else if(j.result){toast('Đã hoàn tất '+({backtest:'backtest',optimizer:'tối ưu',update:'cập nhật',prediction:'dự đoán từ cầu',cau:'kiểm tra song thủ'}[j.kind]||''));await refresh()}}catch(e){toast(e.message,true)}}
function download(raw,name,mime){const url=URL.createObjectURL(new Blob([raw],{type:mime}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),2000)}
$$('.nav').forEach(b=>b.onclick=()=>showPage(b.dataset.page));$('#go-data').onclick=()=>showPage('data');$('#refresh').onclick=()=>attempt(refresh);
$('#theme').onclick=()=>{const theme=document.documentElement.dataset.theme==='dark'?'light':'dark';document.documentElement.dataset.theme=theme;localStorage.setItem('xsmb_theme',theme);charts.forEach(c=>c.draw())};document.documentElement.dataset.theme=localStorage.getItem('xsmb_theme')||'dark';$('#theme-header').onclick=$('#theme').onclick;
$('#heatmap').onclick=e=>{const cell=e.target.closest('[data-number]');if(cell){$('#chart-number').value=Number(cell.dataset.number);showPage('charts')}};
for(const id of ['#feature-select','#analysis-sort'])$(id).onchange=renderAnalysis;$('#analysis-number').oninput=renderAnalysis;
for(const kind of ['backtest','optimizer'])$('#'+kind+'-form').onsubmit=e=>{e.preventDefault();attempt(()=>startJob(kind,formData(e.target)))};
$('#update-form').onsubmit=e=>{e.preventDefault();const values=formData(e.target);values.providers=$$('#provider-list input:checked').map(x=>x.value);attempt(()=>startJob('update',values))};
$('#cancel').onclick=()=>attempt(async()=>toast((await api('cancel',{})).message));
$('#filter-finance').onclick=()=>attempt(loadFinance);$('#finance-period').onchange=()=>attempt(loadFinance);
$('#save-capital').onclick=()=>attempt(async()=>{toast((await api('settings',{initial_capital:$('#initial-capital').value})).message);await loadFinance()});
$('#ledger-form').onsubmit=e=>{e.preventDefault();const values=formData(e.target);values.day=day(values.day);attempt(async()=>{toast((await api('ledger/save',values)).message);clearLedger();await loadFinance()})};$('#ledger-clear').onclick=clearLedger;
$('#ledger-table').onclick=e=>{const edit=e.target.closest('[data-edit]'),del=e.target.closest('[data-delete]');if(edit){const row=finance.rows.find(r=>r.id===Number(edit.dataset.edit)),form=$('#ledger-form');for(const k of ['id','day','number','points','cost_rate','payout_rate','note'])form.elements[k].value=row[k];form.elements.hits.value=row.manual_hits??'';$('#ledger-heading').textContent=`Sửa khoản #${row.id}`;form.scrollIntoView({behavior:'smooth',block:'center'})}if(del&&confirm('Xóa khoản này khỏi sổ thực tế?'))attempt(async()=>{await api('ledger/delete',{id:del.dataset.delete});clearLedger();await loadFinance()})};
$('#journal-form').onsubmit=e=>{e.preventDefault();attempt(loadJournal)};
$('#load-chart').onclick=()=>attempt(loadHistory);$('#chart-metric').onchange=()=>chart('#history-chart',historyRows,$('#chart-metric').value,num);$('#reset-chart').onclick=()=>charts.get('#history-chart')?.reset();$('#zoom-in').onclick=()=>charts.get('#history-chart')?.zoom(.7);$('#zoom-out').onclick=()=>charts.get('#history-chart')?.zoom(1.4);$('#pan-left').onclick=()=>charts.get('#history-chart')?.pan(-1);$('#pan-right').onclick=()=>charts.get('#history-chart')?.pan(1);
$('#import-csv').onclick=()=>attempt(async()=>{const file=$('#csv-file').files[0];if(!file)throw Error('Chọn file CSV trước.');if(file.size>4000000)throw Error('CSV phải nhỏ hơn 4 MB.');toast((await api('import',{text:await file.text()})).message);await refresh()});$('#csv-template').onclick=()=>download('\ufeffday,numbers,special_prize\r\n','XSMB_mau_cot.csv','text/csv');
$('#show-data').onclick=()=>attempt(async()=>{const d=await api('data');table('#data-table',[['Ngày',r=>day(r.day)],['27 kết quả (hai số cuối)',r=>esc(r.numbers.join(' · ')),true],['Giải ĐB',r=>esc(r.special_prize||'Không có')],['Nguồn',r=>esc(r.source),true]],d.rows.slice().reverse())});
$('#report-form').onsubmit=e=>{e.preventDefault();attempt(async()=>{const values={...formData($('#cau-form')),...formData($('#journal-form')),...formData(e.target),period:$('#finance-period').value,start:$('#finance-start').value,end:$('#finance-end').value};const res=await fetch('/api/export',{method:'POST',headers:{'Content-Type':'application/json','X-App-Token':token},body:JSON.stringify(values)});if(!res.ok)throw Error((await res.json()).error);download(await res.arrayBuffer(),`XSMB_${values.kind}.${values.format}`,res.headers.get('Content-Type'));toast('Đã xuất báo cáo.')})};
$('#shutdown').onclick=()=>{if(confirm('Đóng ứng dụng XSMB trên máy?'))attempt(async()=>{await api('shutdown',{});clearTimeout(pollTimer);document.body.innerHTML='<main style="margin:60px"><h1>Đã đóng XSMB V2 PRO</h1><p>Bạn có thể đóng tab này. Dữ liệu đã lưu vẫn được giữ.</p></main>'})};
(async()=>{try{await refresh();const d=state.dashboard.today;$('#ledger-form').elements.day.value=d;const yesterday=new Date(d+'T12:00:00Z');yesterday.setUTCDate(yesterday.getUTCDate()-1);$('#update-form').elements.end.value=yesterday.toISOString().slice(0,10);const j=await api('status');if(j.running)pollJob()}catch(e){toast(e.message,true)}})();

let cauState=null;
async function loadCau(){
 cauState=await api('cau?'+new URLSearchParams(formData($('#cau-form'))));const r=cauState,snap=r.snapshot;
 $('#cau-warning').textContent=(r.stale?'Dữ liệu cũ: hãy cập nhật trước khi xem lựa chọn cho kỳ tới. ':'')+r.warning;
 $('#cau-cards').innerHTML=card('Kỳ mục tiêu',esc(day(r.target)))+card('Cặp đã lưu',snap?balls([snap.pair.a,snap.pair.b]):'Chưa đủ mẫu','Song thủ hai số đánh riêng','accent')+card('Điểm cặp khi lưu',snap?num(snap.pair.score):'—','Điểm tương đối / 100')+card('Số kỳ trong cửa sổ',num(r.sample_days))+card('Cặp ngày liên tiếp',num(r.transitions));
 $('#cau-snapshot-note').textContent=snap?`Lưu ${new Date(snap.created_at).toLocaleString('vi-VN',{timeZone:'Asia/Ho_Chi_Minh'})} • ${snap.kind==='live'?'Trước giờ quay':'Hồi cứu'} • cấu hình đã lưu ${snap.config.window} kỳ / tối thiểu ${snap.config.min_support} mẫu. Không đổi khi chỉnh bảng xem trước.`:'Chưa lưu cặp khi thiếu dữ liệu.';
 table('#cau-pairs-table',[['Hạng',x=>x.index],['Cặp số',x=>balls([x.a,x.b])],['Score',x=>num(x.score)],['Ít nhất 1 số',x=>`${x.either_days}/${x.sample_days} (${pct(x.either_rate)})`],['Cả hai số',x=>`${x.both_days}/${x.sample_days} (${pct(x.both_rate)})`],['Đặc điểm',x=>esc(x.tags.join(' · ')||'Khác đầu/đuôi')],['Cầu đủ mẫu',x=>esc(x.reasons.join('; ')||'Chưa có cầu đủ mẫu; xếp hạng dùng thống kê còn lại.'),true]],r.pairs.map((x,i)=>({...x,index:i+1})));
 renderCauRules();renderCauBacktest(r.backtest);
 table('#cau-journal-table',[['Ngày',x=>day(x.day)],['Cặp đã chọn',x=>balls([x.a,x.b])],['Nháy',x=>x.hits===null?'Chờ':x.hits],['Cả hai xuất hiện',x=>x.both===null?'Chờ':x.both?'Có':'Không'],['Cấu hình khi lưu',x=>`${x.config.window} kỳ / ${x.config.min_support} mẫu`],['Loại bản ghi',x=>x.kind==='live'?'Trước giờ quay':'Hồi cứu']],r.journal);
}
function renderCauRules(){if(!cauState)return;const n=$('#cau-number').value.trim(),kind=$('#cau-rule-type').value,limit=Number($('#cau-row-limit').value);const rows=cauState.rules.filter(r=>(!n||r.number.includes(n))&&(!kind||r.kind===kind)).slice(0,limit);
 table('#cau-rules-table',[['Cầu',r=>esc(r.kind)],['Nguồn → đích',r=>`${esc(r.source)} → <b>${r.number}</b>`],['Số lần đúng / mẫu',r=>`${r.hits}/${r.samples}`],['Tỷ lệ lịch sử',r=>pct(r.rate)],['Cận dưới lịch sử',r=>pct(r.lower)],['Nền',r=>pct(r.baseline)],['Chênh so với nền',r=>r.lift===null?'—':`${num(r.lift)} điểm %`],['Mẫu',r=>r.eligible?'Đủ ngưỡng':'Ít mẫu · không dùng điểm']],rows)
}
function renderCauBacktest(b){const el=$('#cau-backtest-results');if(!b){el.innerHTML='<div class="empty">Chưa có kiểm tra song thủ. Tỷ lệ trong bảng cặp phía trên chưa phải kết quả ngoài mẫu.</div>';return}
 el.innerHTML=`<div class="notice">Kết quả lần chạy: ${b.window} kỳ / tối thiểu ${b.min_support} mẫu • ${num(b.points)} điểm mỗi số • ${b.days} kỳ đánh giá • ${b.skipped_gaps} kỳ thiếu ngày, ${b.skipped_insufficient} kỳ thiếu mẫu bị bỏ qua.</div><div class="cards">${card('Có ít nhất một số',pct(b.hit_rate))}${card('Có cả hai số',pct(b.both_rate))}${card('ROI song thủ',pct(b.roi))}${card('Lãi/lỗ mô phỏng',profit(b.profit))}${card('Ngày thắng / thua',`${b.wins} / ${b.losses}`,`Sụt giảm lớn nhất: ${money(b.max_drawdown)}`)}</div><article class="panel"><h3>Lãi/lỗ lũy kế của cách tuyển chọn</h3><canvas id="cau-chart" class="chart"></canvas><div id="cau-daily-table"></div></article>`;
 chart('#cau-chart',b.daily,'cumulative',money);table('#cau-daily-table',[['Ngày',r=>day(r.day)],['Cặp đã chọn',r=>balls(r.picks)],['Nháy',r=>r.hits],['Cả hai số',r=>r.both?'Có':'Không'],['Tiền mua',r=>money(r.cost)],['Tiền nhận',r=>money(r.received)],['Lãi/lỗ',r=>profit(r.profit)],['Lũy kế',r=>profit(r.cumulative)]],b.daily)
}
$('#cau-form').onsubmit=e=>{e.preventDefault();attempt(loadCau)};
$('#cau-number').oninput=renderCauRules;$('#cau-rule-type').onchange=renderCauRules;$('#cau-row-limit').onchange=renderCauRules;
$('#cau-backtest-form').onsubmit=e=>{e.preventDefault();attempt(()=>startJob('cau',{...formData($('#cau-form')),...formData(e.target)}))};

function forecastStatus(r){return !r||r.status==='insufficient'?'Chưa đủ 30 mẫu kiểm tra':r.status==='qualified'?'Có cầu vượt đối chứng lịch sử':'Ứng viên thăm dò · chưa vượt đối chứng'}
async function loadPrediction(){
 const r=await api('prediction'),s=r.snapshot||r;
 $('#prediction-notice').textContent=(r.target&&r.target<state.dashboard.today?'Dữ liệu cũ — cập nhật trước khi xem kỳ tới. ':'')+r.notice;
 $('#prediction-cards').innerHTML=card('Kỳ dự đoán',day(s.target))+card('Bạch thủ',s.bach_thu?balls([s.bach_thu]):'—',forecastStatus(s),'accent')+card('Song thủ',s.song_thu.length?balls(s.song_thu):'—','Hai số riêng; số thứ hai có thể chỉ là thăm dò')+card('Thời điểm ghi',s.created_at?esc(new Date(s.created_at).toLocaleString('vi-VN')):'Chưa ghi',s.kind==='live'?'Trước giờ quay':'Hồi cứu / chưa ghi');
 table('#prediction-reasons',[['Số',x=>balls([x.number])],['Điểm hợp nhất',x=>num(x.score)],['Bằng chứng',x=>x.eligible?'Có cầu vượt đối chứng':'Thăm dò'],['Cầu đề xuất',x=>esc(x.reasons.map(a=>`${a.name}: ${a.hits}/${a.trials} kỳ`).join('; ')),true]],s.ranking.slice(0,10));
 table('#prediction-rules',[['Cầu',x=>esc(x.name)],['Số đề xuất',x=>balls([x.candidate])],['Đúng / mẫu',x=>`${x.hits}/${x.trials}`],['Tỷ lệ lịch sử',x=>pct(x.rate*100)],['Cận dưới',x=>pct(x.lower*100)],['Đối chứng tần suất',x=>pct(x.baseline_rate*100)],['Đánh giá',x=>x.trials<30?'Thiếu mẫu':x.eligible?'Vượt đối chứng':'Chưa vượt']],r.rules);
 table('#prediction-journal',[['Ngày',x=>day(x.day)],['Bạch thủ',x=>balls([x.bach_thu])],['Song thủ',x=>balls(x.song_thu)],['Nháy bạch / song',x=>x.bach_hits===null?'Chờ':`${x.bach_hits} / ${x.song_hits}`],['Loại',x=>x.kind==='live'?'Trước giờ quay':'Hồi cứu']],r.journal);
 $('#prediction-backtest').innerHTML=r.backtest?Object.entries(r.backtest).map(([k,b])=>`<h3>${k==='bach_thu'?'Bạch thủ':'Song thủ'}</h3><div class="cards">${card('Kỳ kiểm tra',b.days)}${card('Có trúng',pct(b.hit_rate))}${card('ROI',pct(b.roi))}${card('Lãi/lỗ',profit(b.profit))}</div><canvas class="chart" id="forecast-${k}"></canvas>`).join(''):'Chưa chạy kiểm tra bộ chọn. Bảng cầu phía trên chưa chứng minh hiệu quả dự đoán.';
 if(r.backtest)Object.entries(r.backtest).forEach(([k,b])=>chart('#forecast-'+k,b.daily,'cumulative',money));
}
$('#prediction-test').onclick=()=>attempt(()=>startJob('prediction',{points:100,cost_rate:23000,payout_rate:80000}));
