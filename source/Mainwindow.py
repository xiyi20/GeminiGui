import time
import threading
import threading
import threading
from functools import partial
from PyQt6.QtGui import QFont,QIcon,QTextCursor
from PyQt6.QtGui import QFont,QIcon,QTextCursor
from PyQt6.QtCore import pyqtSignal,Qt
from PyQt6.QtWidgets import QLabel,QFrame,QMainWindow,\
    QVBoxLayout,QHBoxLayout,QPushButton,QTextEdit
from PyQt6.QtWidgets import QLabel,QFrame,QMainWindow,\
    QVBoxLayout,QHBoxLayout,QPushButton,QTextEdit
from Rwconfig import RwConfig
from Gemini import Gemini
from Settingwindow import SettingWindow
from Blurlabel import BlurredLabel
from Historywindow import HistoryWindow
from CustomFrame import CustomBanner,CustomMenu

from CustomFrame import CustomBanner,CustomMenu


class MainWindow(QMainWindow):
    link=None
    img_a=None
    img_t=None
    image=None
    imgsignal=pyqtSignal(str)
    answersignal=pyqtSignal(str)
    clearsignal=pyqtSignal(str)
    def __init__(self,Main_ins):
        super().__init__()
        self.code=None
        self.state=None
        self.question=None
        self.settingw=None
        self.historyw=None
        self.answer_thread=None
        self.img_thread=None
        self.gemini=Gemini()
        self.gemini_visual=Gemini('gemini-pro-vision')
        self.initUI(Main_ins)
    @staticmethod
    def checkimg(link):
        if MainWindow.img_a is not None:link.setIcon(QIcon('images/elink.png'))
        else:link.setIcon(QIcon('images/link.png'))
    @staticmethod
    def imagethread(self):
        if MainWindow.img_a is not None:
            MainWindow.img_a=None
            MainWindow.checkimg(MainWindow.link)
            return
        self.img_thread=threading.Thread(target=MainWindow.getimage)
        self.img_thread.start()
    @staticmethod
    def getimage():
        from Msgbox import messagebox
        messagebox.connectshow(partial(messagebox.showdialog,'file'))
        messagebox.messageSignal.emit('signal')
    @staticmethod
    def checkapi(self):
        if RwConfig.apikey=='':
            self.t1.setText('当前未配置api,无法使用')
            self.t1.setEnabled(False)
            MainWindow.setenable(self,False)
    @staticmethod
    def setenable(self,bool):
        MainWindow.link.setEnabled(bool)
        self.b2.setEnabled(bool)
        self.b3.setEnabled(bool)
    def closeEvent(self,event):
        windows=[self.settingw,self.historyw]
        for i in windows:
            if i is not None:
                i.close()
        threads=[self.answer_thread,self.img_thread]
        for i in threads:
            if i is not None and i.is_alive():
                i.join()
        event.accept()
    def initUI(self,Main_ins):
        from Main import getcolor
        m_width,m_height=Main_ins.m_width,Main_ins.m_height
        self.setWindowTitle('Gemini AI')
        self.setWindowTitle('Gemini AI')
        self.move(450,20)
        self.setFixedSize(m_width,m_height+30)
        self.setFixedSize(m_width,m_height+30)
        self.setWindowIcon(QIcon('images/Gemini.ico'))
        self.setStyleSheet('border-radius:15px')
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        center=QFrame(self)
        center.resize(self.width(),self.height())
        layout_center=QVBoxLayout(center)
        layout_center.setSpacing(0)
        layout_center.setContentsMargins(0,0,0,0)
        self.setStyleSheet('border-radius:15px')
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        center=QFrame(self)
        center.resize(self.width(),self.height())
        layout_center=QVBoxLayout(center)
        layout_center.setSpacing(0)
        layout_center.setContentsMargins(0,0,0,0)
        shapes=[
            {'type':21,'shape':1,'color':getcolor(),'last_time':6},
            {'type':22,'shape':2,'color':getcolor(),'last_time':5},
            {'type':31,'shape':3,'color':getcolor(),'last_time':7},
            {'type':22,'shape':2,'color':getcolor(),'last_time':5},
            {'type':31,'shape':3,'color':getcolor(),'last_time':7},
            {'type':41,'shape':3,'color':getcolor(),'last_time':8},
            {'type':12,'shape':1,'color':getcolor(),'last_time':9},
            {'type':12,'shape':1,'color':getcolor(),'last_time':9},
        ]
        label=BlurredLabel(center,shapes)
        banner=CustomBanner(self,'images/Gemini.ico','',[1,2,3],True)
        layout_center.addWidget(banner)
        label=BlurredLabel(center,shapes)
        banner=CustomBanner(self,'images/Gemini.ico','',[1,2,3],True)
        layout_center.addWidget(banner)
        self.setCentralWidget(center)

        f1=QFrame()
        f1.setStyleSheet('background:rgba(0,0,0,0)')
        f1=QFrame()
        f1.setStyleSheet('background:rgba(0,0,0,0)')
        layout_f1=QVBoxLayout(f1)

        def showwindow(window):
            window.show()
            if window.isMinimized():
                window.showNormal()
            else:
                flags=window.windowFlags()
                handel=window.windowHandle()#通过句柄添加flags避免窗口闪烁
                handel.setFlags(flags| Qt.WindowType.WindowStaysOnTopHint)
                handel.setFlag(Qt.WindowType.WindowStaysOnTopHint,False)


        def showwindow(window):
            window.show()
            if window.isMinimized():
                window.showNormal()
            else:
                flags=window.windowFlags()
                handel=window.windowHandle()#通过句柄添加flags避免窗口闪烁
                handel.setFlags(flags| Qt.WindowType.WindowStaysOnTopHint)
                handel.setFlag(Qt.WindowType.WindowStaysOnTopHint,False)

        layout_top=QHBoxLayout()
        layout_f1.addLayout(layout_top)
        b1=QPushButton()
        b1.clicked.connect(lambda:showwindow(self.settingw))
        b1.clicked.connect(lambda:showwindow(self.settingw))
        b1.setIcon(QIcon('images/setting.png'))
        b0=QPushButton()
        b0.clicked.connect(lambda:showwindow(self.historyw))
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
        CustomMenu(self.t1,[1,2,3,4,5]).setmenu()
        layout_f1.addWidget(self.t1)
        layout_f1.addStretch(2)

        keywords=['网页','博客','文章','帖子','Wiki','文档','教程','手册','报告','百科','简历',
                      '电子书','演讲稿','课件','规范','合同','论文','文章','新闻','计划','指南','说明',
                      '分析','笔记','词典','诗歌','小说','剧本','攻略','日志','论文','新闻','公告']
        def answer(img):
            if img is None:
                self.code=1
                for i in keywords:
                    if i in self.question:
                        self.code=0
                        break
                answer=self.gemini.get_content(self.code,self.question)
                answer_text='Gemini:\n'+answer+'\n'
                if self.code==0:self.answersignal.emit('<br>'+answer_text)
                else:t2.append(answer_text)
            else:
                answer=self.gemini_visual.get_content(None,self.question,MainWindow.img_a)
                answer_text='Gemini:\n'+answer+'\n'
                t2.append(answer_text)
                MainWindow.img_a=None
            self.historyw.ta.append(answer_text)
            self.clearsignal.emit('signal')
            time.sleep(0.1)
            MainWindow.checkimg(MainWindow.link)
            MainWindow.setenable(self,True)
        def sethtml(html):
            t2.insertHtml(html)
            clearcontent(self.t1)
            MainWindow.setenable(self,True)
        def answerthread():
            self.question=self.t1.toPlainText()
            if MainWindow.img_a is not None:
                self.question+=',语言请用简体中文'
                question_text=self.question
                t2.append('我:\n')
                self.historyw.ta.append('我:\n')
                cursor=t2.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                t2.setTextCursor(cursor)
                cursor.insertImage(MainWindow.img_t)
                cursor=self.historyw.ta.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.historyw.ta.setTextCursor(cursor)
                cursor.insertImage(MainWindow.img_t)
                t2.append(question_text)
                self.historyw.ta.append(question_text)       
            else:
                if self.state==None:
                    self.question+=',语言请用简体中文'
                    self.state=1
                question_text='我:\n'+self.question
                self.historyw.ta.append(question_text)
                t2.append(question_text)
            self.answer_thread=threading.Thread(target=answer,args=(MainWindow.img_a,))
            self.answer_thread.start()
            self.t1.setText('请等待回答...')
            MainWindow.setenable(self,False)
        self.answersignal.connect(sethtml)
        self.clearsignal.connect(lambda:clearcontent(self.t1))
        layout_button=QHBoxLayout()
        self.b2=QPushButton('发送')
        self.b2.setFont(QFont('新宋体',12,500))
        self.b2.setStyleSheet('border-radius:15px')
        self.b2.setMinimumSize(int(m_width*0.5)-26,int(m_height*0.05))
        self.b2.clicked.connect(answerthread)
        def clearcontent(qt):
            qt.clear()
        MainWindow.link=QPushButton()
        MainWindow.link.setMaximumSize(24,25)
        MainWindow.link.clicked.connect(lambda:MainWindow.imagethread(self))
        MainWindow.link.setIcon(QIcon('images/link.png'))
        MainWindow.link.enterEvent=lambda event:SettingWindow.showtext('选择图片以使用visual模型')
        MainWindow.link.setStyleSheet('background:rgba(0,0,0,0)')
        self.b3=QPushButton('清空')
        self.b3.setFont(QFont('新宋体',12,500))
        self.b3.clicked.connect(lambda:clearcontent(t2))
        self.b3.setStyleSheet('border-radius:15px')
        self.b3.setMinimumSize(int(m_width*0.5)-26,int(m_height*0.05))
        for i in self.b2,MainWindow.link,self.b3:
            layout_button.addWidget(i)
        layout_f1.addLayout(layout_button)

        t2=QTextEdit()
        CustomMenu(t2,[1,3]).setmenu()
        t2.setReadOnly(True)
        t2.setMinimumSize(int(m_width*0.9),int(m_height*0.5))
    
        for i in self.t1,t2:
            i.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            i.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout_f1.addWidget(t2)
        layout_center.addWidget(f1)
        MainWindow.checkapi(self)
        self.historyw=HistoryWindow()
        self.settingw=SettingWindow(self,self.historyw,center,label,l1,self.t1,t2,self.b2,self.b3,self.historyw.center,self.historyw.label,Main_ins)  