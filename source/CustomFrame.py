import os
import sys
import subprocess
from PyQt6.QtGui import QIcon,QAction
from PyQt6.QtCore import QSize,Qt,QTimer,QPropertyAnimation,QObject,QEasingCurve
from PyQt6.QtWidgets import QLabel,QFrame,QHBoxLayout,QPushButton,QMenu

class CustomMenu(QMenu):
    def __init__(self,parent,mode):
        super().__init__()
        self.parent=parent
        self.a1=QAction(QIcon('images/selectall.png'),'全选(Ctrl+A)',parent)
        self.a1.triggered.connect(parent.selectAll)
        self.a2=QAction(QIcon('images/cut.png'),'剪切(Ctrl+X)',parent)
        self.a2.triggered.connect(parent.cut)
        self.a3=QAction(QIcon('images/copy.png'),'复制(Ctrl+C)',parent)
        self.a3.triggered.connect(parent.copy)
        self.a4=QAction(QIcon('images/paste.png'),'粘贴(Ctrl+V)',parent)
        self.a4.triggered.connect(parent.paste)
        self.a5=QAction(QIcon('images/undo.png'),'撤销(Ctrl+Z)',parent)
        self.a5.triggered.connect(parent.undo)
        modelist={1:self.a1,2:self.a2,3:self.a3,4:self.a4,5:self.a5}
        for i in mode:
            self.addAction(modelist[i])
        self.setFixedWidth(105)
        self.setWindowOpacity(0.5)
        self.setStyleSheet("Qmenu {background-color:rgba(255,255,255,0.5);border:1px solid white}\
                           QMenu::item:selected {background-color:grey;}")
    def setmenu(self):
        self.parent.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.parent.customContextMenuRequested.connect(lambda pos:self.exec(self.parent.mapToGlobal(pos)))

class CustomBanner(QFrame):
    def __init__(self,parent,icon,name,mode,enlarge=False):
        super().__init__(parent)
        self.parent=parent
        self.icon=icon
        self.name=name
        self.mode=mode
        self.enlarge=enlarge
        self.mouse_pos=None
        self.max=None
        self.setMinimumSize(parent.width(),30)
        self.setStyleSheet('background:rgba(255,255,255,0.01);border-radius:15px')
        self.initUI()
    def initUI(self):
        layout_banner=QHBoxLayout(self)
        layout_banner.setContentsMargins(0,0,0,0)
        icon=QPushButton()
        icon.setIcon(QIcon(self.icon))
        if self.enlarge:icon.setIconSize(QSize(20,20))
        name=QLabel(self.name)

        def modifyicon(qt,icon,text,event):
            qt.setIcon(QIcon(icon))
            if text is not None:
                self.timer=QTimer()
                self.timer.setSingleShot(True)
                from Settingwindow import SettingWindow
                self.timer.timeout.connect(lambda:SettingWindow.showtext(text))
                self.timer.start(1000)
            else:
                if hasattr(self,'timer'):
                    self.timer.stop()
            event.accept()

        mini=QPushButton()
        mini.setIcon(QIcon('images/mini1.png'))
        mini.clicked.connect(self.parent.showMinimized)
        mini.leaveEvent=lambda event:modifyicon(mini,'images/mini1.png',None,event)
        mini.enterEvent=lambda event:modifyicon(mini,'images/mini.png','最小化',event)
        maxi=QPushButton()
        maxi.setIcon(QIcon('images/maxi1.png'))
        maxi.clicked.connect(lambda event:self.mouseDoubleClickEvent(event))
        maxi.leaveEvent=lambda event:modifyicon(maxi,'images/maxi1.png',None,event)
        maxi.enterEvent=lambda event:modifyicon(maxi,'images/maxi.png','最大化',event)
        reboot=QPushButton()
        reboot.setIcon(QIcon('images/reboot1.png'))
        reboot.clicked.connect(self.reboot)
        reboot.leaveEvent=lambda event:modifyicon(reboot,'images/reboot1.png',None,event)
        reboot.enterEvent=lambda event:modifyicon(reboot,'images/reboot.png','重启程序',event)
        close=QPushButton()
        close.setIcon(QIcon('images/close1.png'))
        close.clicked.connect(self.parent.closewindow)
        close.leaveEvent=lambda event:modifyicon(close,'images/close1.png',None,event)
        close.enterEvent=lambda event:modifyicon(close,'images/close.png','关闭',event)

        mode_list={1:mini,2:maxi,3:reboot,4:close}
        layout_banner.addSpacing(5)
        layout_banner.addWidget(icon)
        layout_banner.addWidget(name)
        layout_banner.addStretch()
        for i in self.mode:
            mode_list[i].setStyleSheet('background:rgba(0,0,0,0)')
            mode_list[i].setIconSize(QSize(16,16))
            layout_banner.addWidget(mode_list[i])
        layout_banner.addSpacing(10)

    def reboot(self):
        try:
            python=sys.executable
            os.execl(python,'Main.py',*sys.argv)
        except Exception:
            os.system("taskkill /f /im Gemini.exe")
            subprocess.call('Gemini.exe')

    def mouseDoubleClickEvent(self,event):
        if self.enlarge:
            if self.max is None:
                self.parent.showMaximized()
                self.max=True
            else:
                # self.parent.start_geometry=self.parent.geometry()
                self.parent.showNormal()
                # self.parent.end_geometry=self.parent.geometry()
                self.max=None
            self.resize(self.parent.width(),30)

    def mousePressEvent(self,event):
        self.mouse_pos=event.globalPosition()
        event.accept()

    def mouseMoveEvent(self,event):
        if self.mouse_pos:
            self.parent.move(self.parent.pos()+(event.globalPosition()-self.mouse_pos).toPoint())
            self.mouse_pos=event.globalPosition()
            event.accept()
    
    def mouseReleaseEvent(self,event):
        self.mouse_pos=None
        event.accept()

class CustomAnimation(QObject):
    def __init__(self,parent) -> None:
        super().__init__()
        self.parent=parent
    def setanimation(self,start,end,time,type=b'windowOpacity',curve=QEasingCurve.Type.Linear,slot=None):
        self.animation=QPropertyAnimation(self.parent,type)
        self.animation.setStartValue(start)
        self.animation.setEndValue(end)
        self.animation.setDuration(time)
        self.animation.setEasingCurve(curve)
        if slot is not None:self.animation.finished.connect(slot)
        self.animation.start()