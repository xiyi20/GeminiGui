import re
import sys
import random
from PyQt6.QtWidgets import QApplication
from Rwconfig import RwConfig
from Decrypt import Decrypt
from Mainwindow import MainWindow
from Settingwindow import SettingWindow

ml=[]
config=None

class Main:
    VERSION=2.00
    find_radius=re.compile(r'border-radius:(.*?)px')
    find_text=re.compile(r'text: "(.*?)"')
    find_color=re.compile(r'background:(.*?);')
    def __init__(self) -> None:
        self.m_width=None
        self.m_height=None
        self.VERSION=2.00
        self.l14=None
        self.l15=None

Main_ins=Main()

def getcolor():
    rgb=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
    color="#"+"".join(["{:02x}".format(value) for value in rgb])
    return color

def main():
    app=QApplication(sys.argv)
    try:
        RwConfig.apikey=Decrypt().decrypt('mh04qE4YbgNW0b/fUWnlFD6kJh09aBEfE9n0IinC/rfBr8IidY41iuPY4jiRMbKj',RwConfig.adminkey)
    except Exception:
        pass
    if RwConfig.apikey=='':
        from Msgbox import messagebox
        messagebox.showdialog()
    Main_ins.m_width=int(app.primaryScreen().size().width()*0.4)
    Main_ins.m_height=int(app.primaryScreen().size().height()*0.88)
    mainWindow=MainWindow(Main_ins)
    mainWindow.show()
    SettingWindow.updatethread(self=SettingWindow,Main_ins=Main_ins)
    sys.exit(app.exec())

if __name__=='__main__':
    main()