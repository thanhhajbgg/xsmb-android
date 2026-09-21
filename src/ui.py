import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from queue import Queue, Empty
from .ledger_ui import LedgerTab, display_day

class MainWindow:
    def __init__(self,root,service):
        self.root=root; self.service=service; self.events=Queue()
        root.title('XSMB AI Indicator • V1.3'); root.geometry('1250x820'); root.minsize(1080,700)
        root.configure(background='#f1f5f9')
        style=ttk.Style(root); style.theme_use('clam')
        style.configure('.',font=('Segoe UI',10))
        style.configure('TFrame',background='#f1f5f9'); style.configure('TLabel',background='#f1f5f9',foreground='#0f172a')
        style.configure('Title.TLabel',font=('Segoe UI',19,'bold'))
        style.configure('Summary.TLabel',font=('Segoe UI',11,'bold'),padding=10,background='#dbeafe',foreground='#1e3a8a')
        style.configure('Treeview',rowheight=32,font=('Segoe UI',11),background='white',fieldbackground='white')
        style.configure('Treeview.Heading',font=('Segoe UI',10,'bold'),padding=8)
        style.configure('TNotebook.Tab',padding=(16,10)); style.configure('TButton',padding=(9,6))
        top=ttk.Frame(root,padding=16); top.pack(fill='x')
        ttk.Label(top,text='XSMB AI INDICATOR',style='Title.TLabel').pack(side='left')
        self.status=tk.StringVar(value='Sẵn sàng'); ttk.Label(top,textvariable=self.status).pack(side='right')
        actions=ttk.Frame(root,padding=(16,0)); actions.pack(fill='x')
        self.update_btn=ttk.Button(actions,text='Cập nhật dữ liệu',command=self.update); self.update_btn.pack(side='left',padx=(0,8))
        self.analyze_btn=ttk.Button(actions,text='Phân tích kỳ tiếp theo',command=self.analyze); self.analyze_btn.pack(side='left')
        ttk.Label(actions,text='AI Score là điểm xếp hạng thống kê, không phải xác suất trúng.').pack(side='left',padx=16)
        self.nb=ttk.Notebook(root); self.nb.pack(fill='both',expand=True,padx=16,pady=14)
        self.over=ttk.Frame(self.nb,padding=14); self.radar=ttk.Frame(self.nb,padding=12); self.detail=ttk.Frame(self.nb,padding=12); self.bt=ttk.Frame(self.nb,padding=12)
        for frame,label in [(self.over,'Tổng quan'),(self.radar,'Radar 00–99'),(self.detail,'Chi tiết thống kê'),(self.bt,'Backtest')]:self.nb.add(frame,text=label)
        self.ledger=LedgerTab(self.nb,service.repo); self.nb.add(self.ledger,text='Sổ thắng / thua')
        self.info=tk.StringVar(value='Chưa có dữ liệu. Bấm Cập nhật dữ liệu để bắt đầu.')
        ttk.Label(self.over,textvariable=self.info,style='Summary.TLabel').pack(fill='x',pady=(0,12))
        ttk.Label(self.over,text='TOP 10 • XẾP HẠNG THỐNG KÊ',font=('Segoe UI',14,'bold')).pack(anchor='w',pady=(0,10))
        self.top_tree=self.table(self.over,('rank','number','score','f7','f30','gap'),('Hạng','Số lô','AI Score / 100','Số lần • 7 kỳ','Số lần • 30 kỳ','Kỳ chưa xuất hiện'))
        ttk.Label(self.over,text='Kỳ phân tích = ngày tiếp theo của dữ liệu mới nhất. Nếu dữ liệu cũ, hãy cập nhật trước khi xem.').pack(anchor='w',pady=10)
        self.cells=[]
        for i in range(100):
            label=tk.Label(self.radar,text=f'{i:02d}\n—',font=('Segoe UI',13,'bold'),bg='#e2e8f0',fg='#334155',padx=4,pady=4)
            label.grid(row=i//10,column=i%10,sticky='nsew',padx=3,pady=3); self.cells.append(label)
        for i in range(10):self.radar.columnconfigure(i,weight=1); self.radar.rowconfigure(i,weight=1)
        self.tree=self.table(self.detail,('number','score','f7','f14','f30','f60','f90','gap','reverse'),('Số','Score','7 kỳ','14 kỳ','30 kỳ','60 kỳ','90 kỳ','Gan (kỳ)','Đảo 14'))
        ttk.Label(self.bt,text='Kiểm tra trên lịch sử • tỷ lệ ngày có ít nhất một số xuất hiện, không phải tỷ suất lợi nhuận.',wraplength=1000).pack(anchor='w',pady=10)
        self.bt_tree=self.table(self.bt,('top','rate','hits','days'),('Nhóm số','Tỷ lệ có số xuất hiện','Số ngày trúng','Số ngày kiểm tra'))
        root.after(100,self.poll)
        self.analyze(show_notice=False)

    def table(self,parent,cols,heads):
        frame=ttk.Frame(parent); frame.pack(fill='both',expand=True)
        tree=ttk.Treeview(frame,columns=cols,show='headings')
        for c,h in zip(cols,heads):tree.heading(c,text=h); tree.column(c,width=105,anchor='center')
        bar=ttk.Scrollbar(frame,command=tree.yview); bar.pack(side='right',fill='y')
        tree.configure(yscrollcommand=bar.set); tree.pack(side='left',fill='both',expand=True)
        tree.tag_configure('odd',background='#eff6ff')
        return tree

    def busy(self,on,msg=''):
        state='disabled' if on else 'normal'; self.update_btn.configure(state=state); self.analyze_btn.configure(state=state)
        if msg:self.status.set(msg)

    def background(self,fn,done):
        self.busy(True,'Đang xử lý…')
        def work():
            try:self.events.put((done,fn()))
            except Exception as e:self.events.put((self.fail,str(e)))
        Thread(target=work,daemon=True).start()

    def poll(self):
        try:
            while True:
                fn,value=self.events.get_nowait()
                try:fn(value)
                except Exception as e:self.fail(str(e))
        except Empty:pass
        self.root.after(100,self.poll)

    def fail(self,msg):
        self.busy(False,'Có lỗi'); messagebox.showerror('XSMB AI Indicator',msg)

    def update(self):
        def done(rep):
            self.busy(False,f'Cập nhật: {rep.success} thành công, {rep.failed} lỗi')
            if rep.failed:messagebox.showwarning('Cập nhật dữ liệu',f'{rep.success} kỳ thành công, {rep.failed} kỳ lỗi.\n'+'\n'.join(rep.errors[:4]))
            self.ledger.refresh(); self.analyze(show_notice=False)
        self.background(lambda:self.service.update(120),done)

    def analyze(self,show_notice=True):
        self.background(lambda:(self.service.analyze(),self.service.backtests()),self.render)

    def render(self,payload):
        result,backtests=payload
        self.busy(False,'Sẵn sàng')
        for tree in (self.top_tree,self.tree,self.bt_tree):tree.delete(*tree.get_children())
        if not result.draws:
            self.info.set('Chưa có dữ liệu. Bấm Cập nhật dữ liệu. Sổ thắng/thua vẫn dùng được với kết quả nhập tay.'); return
        self.info.set(f'Dữ liệu đến: {display_day(result.last_day)}  |  {len(result.draws)} kỳ\nKỳ phân tích: {display_day(result.target_day)}')
        for i,x in enumerate(result.ranking):
            tags=('odd',) if i%2==0 else ()
            if i<10:self.top_tree.insert('','end',values=(i+1,x.number,f'{x.score:.1f}',x.f7,x.f30,x.gap),tags=tags)
            self.tree.insert('','end',values=(x.number,x.score,x.f7,x.f14,x.f30,x.f60,x.f90,x.gap,x.reverse14),tags=tags)
            self.cells[int(x.number)].configure(text=f'{x.number}\n{x.score:.1f}',bg='#bfdbfe' if i<10 else '#e2e8f0',fg='#1e40af' if i<10 else '#334155')
        for b in backtests:self.bt_tree.insert('','end',values=(f'Top {b.top_n}','Chưa đủ dữ liệu' if b.hit_rate is None else f'{b.hit_rate:.1f}%',b.hit_days,b.days))
        self.status.set(f'Đã phân tích kỳ {display_day(result.target_day)}')
