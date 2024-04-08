from PyQt6.QtGui import QFont,QIcon,QTextCursor
from PyQt6.QtCore import pyqtSignal,Qt
from PyQt6.QtWidgets import QLabel,QFrame,QMainWindow,\
    QVBoxLayout,QHBoxLayout,QPushButton,QTextEdit

class MainWindow(QMainWindow):
    link=None
    img_a=None
    img_t=None
    image=None
    imgsignal=pyqtSignal(str)
    answersignal=pyqtSignal(int,str)
    clearsignal=pyqtSignal(str)
    def __init__(self,Main_ins):
        super().__init__()
        self.code=None
        self.state=None
        self.question=None
        self.settingw=None
        self.historyw=None
        from Threads import ImgThread,AnswerThread
        self.img_thread=ImgThread()
        self.answer_thread=AnswerThread(self)
        from Gemini import Gemini
        self.gemini=Gemini()
        self.gemini_visual=Gemini('gemini-pro-vision')
        # self.start_geometry=self.end_geometry=None
        from CustomFrame import CustomAnimation
        self.animation=CustomAnimation(self)
        self.initUI(Main_ins)
        from Rwconfig import rwconfig
        self.animation.setanimation(0,rwconfig.opacity,1000)
    @staticmethod
    def checkimg(link):
        if MainWindow.img_a is not None:link.setIcon(QIcon('images/elink.png'))
        else:link.setIcon(QIcon('images/link.png'))
    @staticmethod
    def checkapi(self):
        from Rwconfig import rwconfig
        if rwconfig.apikey=='':
            self.t1.setText('当前未配置api,无法使用')
            self.t1.setEnabled(False)
            MainWindow.setenable(self,False)
    @staticmethod
    def setenable(self,bool):
        MainWindow.link.setEnabled(bool)
        self.b2.setEnabled(bool)
        self.b3.setEnabled(bool)
    def closewindow(self):
        from Rwconfig import rwconfig
        windows=[self.settingw,self.historyw]
        for i in windows:
            if i is not None:
                i.close()
        threads=[self.answer_thread,self.img_thread]
        for i in threads:
            if i is not None and i.isRunning():
                i.quit()
        self.animation.setanimation(rwconfig.opacity,0,500,slot=self.close)
    def resizeEvent(self,event):
        self.label.setGeometry(0,0,self.width(),self.height())
        import Main
        for i in Main.ml[0]:
            i.initUI(self)
        event.accept()
    # def resizeAnimation(self):
    #     print(self.start_geometry,self.end_geometry)
    #     self.animation.setanimation(self.start_geometry,self.end_geometry,1000,b'geometry')
    def initUI(self,Main_ins):
        m_width,m_height=Main_ins.m_width,Main_ins.m_height
        self.setWindowTitle('Gemini AI')
        self.move(450,20)
        self.resize(m_width,m_height+30)
        self.setWindowIcon(QIcon('images/Gemini.ico'))
        self.setStyleSheet('border-radius:15px')
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.center=QFrame(self)
        self.center.resize(self.width(),self.height())
        layout_center=QVBoxLayout(self.center)
        layout_center.setSpacing(0)
        layout_center.setContentsMargins(0,0,0,0)
        from Main import getcolor
        shapes=[
            {'type':21,'shape':1,'color':getcolor(),'last_time':6},
            {'type':22,'shape':2,'color':getcolor(),'last_time':5},
            {'type':31,'shape':3,'color':getcolor(),'last_time':7},
            {'type':41,'shape':3,'color':getcolor(),'last_time':8},
            {'type':12,'shape':1,'color':getcolor(),'last_time':9},
        ]
        from Blurlabel import BlurredLabel
        self.label=BlurredLabel(self.center,shapes)
        from CustomFrame import CustomBanner
        banner=CustomBanner(self,'images/Gemini.ico','',[1,2,3,4],True)
        layout_center.addWidget(banner)
        self.setCentralWidget(self.center)

        f1=QFrame()
        f1.setStyleSheet('background:rgba(0,0,0,0)')
        layout_f1=QVBoxLayout(f1)

        def showwindow(window):
            window.show()
            if window.isMinimized():
                window.showNormal()
            else:
                from Rwconfig import rwconfig
                flags=window.windowFlags()
                handel=window.windowHandle()#通过句柄添加flags避免窗口闪烁
                handel.setFlags(flags| Qt.WindowType.WindowStaysOnTopHint)
                handel.setFlag(Qt.WindowType.WindowStaysOnTopHint,False)
                window.animation.setanimation(0,rwconfig.opacity,1000)

        layout_top=QHBoxLayout()
        layout_f1.addLayout(layout_top)
        b1=QPushButton()
        b1.clicked.connect(lambda:showwindow(self.settingw))
        b1.setIcon(QIcon('images/setting.png'))
        b0=QPushButton()
        b0.clicked.connect(lambda:showwindow(self.historyw))
        for i in b0,b1:
            i.setStyleSheet('background:rgba(255,255,255,0)')
        b0.setIcon(QIcon('images/history.png'))
        layout_top.addWidget(b0)
        layout_top.addStretch(1)
        layout_top.addWidget(b1)

        l1=QLabel('Geimini AI')
        l1.setFont(QFont('微软雅黑',30))
        l1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_f1.addWidget(l1)
        layout_f1.addStretch()

        self.t1=QTextEdit()
        self.t1.setMinimumSize(int(m_width*0.9),int(m_height*0.3))
        from CustomFrame import CustomMenu
        CustomMenu(self.t1,[1,2,3,4,5]).setmenu()
        layout_f1.addWidget(self.t1)
        layout_f1.addStretch(2)
        
        def appendcontent(mode,content):
            if mode==0:
                self.t2.insertHtml(content)
                clearcontent(self.t1)
                MainWindow.setenable(self,True)
            elif mode==1:
                self.t2.append(content)
                self.historyw.ta.append(content)
            elif mode==2:self.t1.setText(content)
            else:
                cursor=self.t2.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.t2.setTextCursor(cursor)
                cursor.insertImage(MainWindow.img_t)
                cursor=self.historyw.ta.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.historyw.ta.setTextCursor(cursor)
                cursor.insertImage(MainWindow.img_t)
        self.answersignal.connect(appendcontent)
        self.clearsignal.connect(lambda:clearcontent(self.t1))

        layout_button=QHBoxLayout()
        self.b2=QPushButton('发送')
        self.b2.setFont(QFont('新宋体',12,500))
        self.b2.setStyleSheet('border-radius:15px')
        self.b2.setMinimumSize(int(m_width*0.5)-26,int(m_height*0.05))
        self.b2.clicked.connect(lambda:self.answer_thread.start())
        def clearcontent(qt):
            qt.clear()
        MainWindow.link=QPushButton()
        MainWindow.link.setMaximumSize(24,25)
        MainWindow.link.clicked.connect(lambda:self.img_thread.start())
        MainWindow.link.setIcon(QIcon('images/link.png'))
        from Settingwindow import SettingWindow
        MainWindow.link.enterEvent=lambda event:SettingWindow.showtext('选择图片以使用visual模型')
        MainWindow.link.setStyleSheet('background:rgba(0,0,0,0)')
        self.b3=QPushButton('清空')
        self.b3.setFont(QFont('新宋体',12,500))
        self.b3.clicked.connect(lambda:clearcontent(self.t2))
        self.b3.setStyleSheet('border-radius:15px')
        self.b3.setMinimumSize(int(m_width*0.5)-26,int(m_height*0.05))
        for i in self.b2,MainWindow.link,self.b3:
            layout_button.addWidget(i)
        layout_f1.addLayout(layout_button)

        self.t2=QTextEdit()
        CustomMenu(self.t2,[1,3]).setmenu()
        self.t2.setReadOnly(True)
        self.t2.setMinimumSize(int(m_width*0.9),int(m_height*0.5))
    
        for i in self.t1,self.t2:
            i.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            i.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout_f1.addWidget(self.t2)
        layout_center.addWidget(f1)
        MainWindow.checkapi(self)
        from Historywindow import HistoryWindow
        self.historyw=HistoryWindow()
        self.settingw=SettingWindow(self,self.historyw,self.center,self.label,l1,self.t1,self.t2,self.b2,self.b3,self.historyw.center,self.historyw.label,Main_ins)  