
import tkinter as tk,logging
from .paths import get_data_dir
from .app_service import AppService
from .ui import MainWindow
def main():
 logging.basicConfig(filename=get_data_dir()/"app.log",level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s")
 root=tk.Tk(); MainWindow(root,AppService()); root.mainloop()
if __name__=="__main__": main()
