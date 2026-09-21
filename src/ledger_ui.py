import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime
from .ledger import Ledger

def money(value):
    return '—' if value is None else f'{value:,.0f}'.replace(',','.')+' đ'

def display_day(value):
    return date.fromisoformat(value).strftime('%d/%m/%Y')

class LedgerTab(ttk.Frame):
    def __init__(self,parent,repo):
        super().__init__(parent,padding=12)
        self.book=Ledger(repo); self.selected_id=None; self.visible=[]
        ttk.Label(self,text='SỔ THẮNG / THUA',style='Title.TLabel').pack(anchor='w')
        ttk.Label(self,text='Tiền nhận = điểm × tiền trả/điểm × số lần trúng. Lãi/lỗ = tiền nhận − tiền mua.').pack(anchor='w',pady=(4,10))
        form=ttk.LabelFrame(self,text='Nhập khoản đánh • đơn giá bằng đồng, không nhập dấu chấm',padding=10); form.pack(fill='x')
        self.fields={}
        specs=[('day','Ngày (DD/MM/YYYY)',date.today().strftime('%d/%m/%Y')),('number','Số lô','88'),('points','Điểm','100'),('cost_rate','Giá mua / điểm','23000'),('payout_rate','Tiền trả / điểm','80000'),('hits','Số lần trúng','')]
        for i,(key,label,default) in enumerate(specs):
            ttk.Label(form,text=label).grid(row=0,column=i,sticky='w',padx=4)
            var=tk.StringVar(value=default); self.fields[key]=var
            ttk.Entry(form,textvariable=var,width=16).grid(row=1,column=i,sticky='ew',padx=4,pady=4)
            form.columnconfigure(i,weight=1)
        ttk.Label(form,text='Số lần trúng: để trống = tự đối chiếu; 0 = thua; 1, 2… = số lần xuất hiện.').grid(row=2,column=0,columnspan=6,sticky='w',padx=4)
        self.fields['note']=tk.StringVar()
        ttk.Label(form,text='Ghi chú').grid(row=3,column=0,sticky='w',padx=4,pady=8)
        ttk.Entry(form,textvariable=self.fields['note']).grid(row=3,column=1,columnspan=5,sticky='ew',padx=4)
        actions=ttk.Frame(self); actions.pack(fill='x',pady=8)
        for label,cmd in [('Lưu khoản',self.save),('Nhập mới',self.clear),('Xóa dòng chọn',self.delete),('Đối chiếu lại',self.refresh),('Xuất CSV',self.export)]:
            ttk.Button(actions,text=label,command=cmd).pack(side='left',padx=(0,6))
        self.edit_label=tk.StringVar(value='Đang nhập mới'); ttk.Label(actions,textvariable=self.edit_label).pack(side='right')
        filters=ttk.Frame(self); filters.pack(fill='x',pady=(0,8))
        self.start=tk.StringVar(); self.end=tk.StringVar()
        for text,var in [('Từ ngày',self.start),('Đến ngày',self.end)]:
            ttk.Label(filters,text=text).pack(side='left',padx=4); ttk.Entry(filters,textvariable=var,width=14).pack(side='left')
        ttk.Button(filters,text='Lọc',command=self.refresh).pack(side='left',padx=6)
        ttk.Label(filters,text='DD/MM/YYYY • Để trống để xem tất cả').pack(side='left')
        self.summary=tk.StringVar(); ttk.Label(self,textvariable=self.summary,style='Summary.TLabel',wraplength=1060).pack(fill='x',pady=8)
        cols=('day','number','points','cost_rate','payout_rate','hits','cost','received','profit','running','source','note')
        area=ttk.Frame(self); area.pack(fill='both',expand=True); area.rowconfigure(0,weight=1); area.columnconfigure(0,weight=1)
        self.tree=ttk.Treeview(area,columns=cols,show='headings',selectmode='browse')
        for key,label,width in zip(cols,['Ngày','Lô','Điểm','Giá mua/đ','Trả/đ','Lần trúng','Tiền mua','Tiền nhận','Lãi / lỗ','Lũy kế','Kết quả từ','Ghi chú'],[100,50,65,95,95,80,115,115,120,120,110,150]):
            self.tree.heading(key,text=label); self.tree.column(key,width=width,minwidth=45,anchor='center' if key in ('day','number','hits','source') else 'e',stretch=False)
        self.tree.grid(row=0,column=0,sticky='nsew')
        ys=ttk.Scrollbar(area,command=self.tree.yview); ys.grid(row=0,column=1,sticky='ns')
        xs=ttk.Scrollbar(area,orient='horizontal',command=self.tree.xview); xs.grid(row=1,column=0,sticky='ew')
        self.tree.configure(yscrollcommand=ys.set,xscrollcommand=xs.set)
        self.tree.tag_configure('win',foreground='#047857'); self.tree.tag_configure('loss',foreground='#be123c'); self.tree.tag_configure('pending',foreground='#986000')
        self.tree.bind('<<TreeviewSelect>>',self.select)
        ttk.Label(self,text='Chọn một dòng để sửa. Lũy kế tính trong khoảng lọc, chỉ cộng khoản đã có kết quả.').pack(anchor='w',pady=6)
        self.refresh()

    def clear(self):
        self.selected_id=None; self.edit_label.set('Đang nhập mới')
        self.fields['hits'].set(''); self.fields['note'].set('')
        self.tree.selection_remove(*self.tree.selection())

    def select(self,event=None):
        selected=self.tree.selection()
        if not selected:return
        row=next((r for r in self.visible if r['id']==int(selected[0])),None)
        if not row:return
        self.selected_id=row['id']; self.edit_label.set(f"Đang sửa dòng #{row['id']}")
        for k,v in self.fields.items():
            value=display_day(row['day']) if k=='day' else (row['manual_hits'] if k=='hits' else row[k])
            v.set('' if value is None else str(value))

    def save(self):
        try:
            self.book.save(*(self.fields[k].get() for k in ('day','number','points','cost_rate','payout_rate','hits','note')),row_id=self.selected_id)
            self.clear(); self.refresh()
        except Exception as e:messagebox.showerror('Không lưu được',str(e))

    def delete(self):
        if self.selected_id is None:return
        if messagebox.askyesno('Xóa khoản','Xóa khoản đang chọn khỏi sổ?'):
            self.book.delete(self.selected_id); self.clear(); self.refresh()

    def refresh(self):
        try:
            bounds=[datetime.strptime(v.get().strip(),'%d/%m/%Y').date().isoformat() if v.get().strip() else None for v in (self.start,self.end)]
            if all(bounds) and bounds[0]>bounds[1]: raise ValueError('Ngày bắt đầu phải trước hoặc bằng ngày kết thúc.')
            rows=[r for r in self.book.rows() if (not bounds[0] or r['day']>=bounds[0]) and (not bounds[1] or r['day']<=bounds[1])]
        except ValueError as e:
            messagebox.showerror('Khoảng ngày không hợp lệ',str(e)); return
        self.visible=rows; self.tree.delete(*self.tree.get_children())
        running=0
        for r in rows:
            profit=r['profit']; running+=profit or 0
            vals=(display_day(r['day']),r['number'],r['points'],money(r['cost_rate']),money(r['payout_rate']),'Chờ' if r['hits'] is None else r['hits'],money(r['cost']),money(r['received']),money(profit),money(running),r['source'],r['note'])
            self.tree.insert('', 'end',iid=str(r['id']),values=vals,tags=('pending' if profit is None else 'win' if profit>=0 else 'loss',))
        settled=[r for r in rows if r['profit'] is not None]; pending=[r for r in rows if r['profit'] is None]
        self.summary.set(f"{len(rows)} khoản  |  Tổng tiền mua: {money(sum(r['cost'] for r in rows))}  |  Đã nhận: {money(sum(r['received'] for r in settled))}\nLãi/lỗ đã chốt: {money(sum(r['profit'] for r in settled))}  |  Chờ kết quả: {len(pending)} khoản / {money(sum(r['cost'] for r in pending))}")

    def export(self):
        path=filedialog.asksaveasfilename(defaultextension='.csv',filetypes=[('CSV','*.csv')],initialfile='So_thang_thua.csv')
        if not path:return
        try:
            keys=['day','number','points','cost_rate','payout_rate','hits','cost','received','profit','source','note']
            with open(path,'w',encoding='utf-8-sig',newline='') as f:
                writer=csv.writer(f); writer.writerow(['Ngày','Số lô','Điểm','Giá mua/điểm','Trả/điểm','Lần trúng','Tiền mua','Tiền nhận','Lãi/lỗ','Nguồn','Ghi chú'])
                for r in self.visible:
                    values=[r[k] for k in keys]
                    # Prevent text notes from being evaluated as spreadsheet formulas.
                    values[-1]="'"+values[-1] if values[-1].startswith(('=','+','-','@','\t','\r')) else values[-1]
                    writer.writerow(values)
            messagebox.showinfo('Xuất CSV','Đã xuất các khoản trong khoảng lọc.')
        except OSError as e: messagebox.showerror('Không xuất được',str(e))
