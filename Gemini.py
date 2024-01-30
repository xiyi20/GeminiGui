import re
import sys
import time
import json
import random
import markdown
import datetime
import requests
import threading
import webbrowser
import PIL.Image
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from functools import partial
import google.generativeai as genai

ml=[]
link=None
img_a=None
img_t=None
image=None
config=None
VERSION=1.80
qt_newversion=None
qt_lasttime=None
m_width=None
m_height=None
find_radius=re.compile(r'border-radius:(.*?)px')
find_text=re.compile(r'text: "(.*?)"')
find_color=re.compile(r'background:(.*?);')

def getcolor():
    rgb=(random.randint(0,255),random.randint(0,255),random.randint(0,255))
    color="#"+"".join(["{:02x}".format(value) for value in rgb])
    return color

class RwConfig:
    def __init__(self):
        try:
            with open('config.json') as f:
                global config
                config=json.load(f)
        except FileNotFoundError:
            MessageBox('配置文件不存在或路径错误!')
        except json.decoder.JSONDecodeError:
            MessageBox('配置文件不是有效的JSON格式!')
        except PermissionError:
            MessageBox('没有足够权限读取或写入配置文件!')
    def wconfig(self,zone,name,value):
        try:
            with open('config.json','w') as f:
                config[zone][name]=value
                json.dump(config,f,indent=4)
        except PermissionError:
            MessageBox('没有足够权限读取或写入配置文件!')

rwconfig=RwConfig()
apikey=config['gemini']['apikey']

blopen=config['blur']['open']
blradius=config['blur']['blur_radius']

bgcolor=config['window']['bg_color']
bgtheme=config['window']['theme']
qradius=config['window']['q_radius']
aradius=config['window']['a_radius']
opacity=config['window']['opacity']

dnopen=config['dynamic']['open']
dnspeed=config['dynamic']['speed']
dncurve=config['dynamic']['curve']

interval=config['update']['interval']
lasttime=datetime.datetime.strptime(config['update']['lasttime'],'%Y-%m-%d %H:%M:%S')

class MessageBox(QObject):
    messageSignal=pyqtSignal(str)
    connection=None
    def __init__(self):
        super().__init__()
    def connectshow(self,slot):
        if self.connection is not None:self.messageSignal.disconnect(self.connection)
        self.connection=self.messageSignal.connect(slot)
    @pyqtSlot(str)
    def showmsg(self,msg='测试',tittle='警告',level='QMessageBox.Icon.Warning',url=None,open=False,qt=None):
        messagebox=QMessageBox()
        messagebox.setWindowIcon(QIcon('images/warm.png'))
        messagebox.setIcon(eval(level))
        messagebox.setWindowTitle(tittle)
        messagebox.setText(msg)
        messagebox.accepted.connect(lambda:self.onAccepted(url,open))
        messagebox.exec()
        if qt is not None:
            qt.setEnabled(True)
            qt.setText('检查更新')
    def showdialog(self,mode='input'):
        if mode=='input':
            api,ok=QInputDialog.getText(None,'提示','输入你的apikey:')  
            if ok:
                rwconfig.wconfig('gemini','apikey',api)
                global apikey
                apikey=api
                self.showmsg('设置成功','提示','QMessageBox.Icon.Information')
            else:sys.exit()
        if mode=='file':
            global image,img_a,img_t,link
            image,_=QFileDialog.getOpenFileName(None, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
            if image:
                img_a=PIL.Image.open(image)
                img_t=QImage(image)
                img_t=img_t.scaled(int(img_t.width()/10),int(img_t.height()/10), 
                                                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio
                                                ,transformMode=Qt.TransformationMode.SmoothTransformation) 
                checkimg(link)
    def onAccepted(self,url,open):
        if open:webbrowser.open(url)

messagebox=MessageBox()

class CheckUpdate:
    def __init__(self):
        super().__init__()
    def check(self,skip=False,qt=None):
        if skip:
            self.checkUpdate(qt)
            return
        a=datetime.datetime.now()
        b=lasttime+datetime.timedelta(days=int(interval))
        if a<b:return
        self.checkUpdate(qt)
    def checkUpdate(self,qt=None):
        global lasttime
        try:
            data=self.get_data()
            if data is None:return
            new_version=data["version"]
            if VERSION<new_version:
                    messagebox.connectshow(partial(messagebox.showmsg,'当前版本:'+str(VERSION)
                                                    +'\n云端版本:'+str(new_version)+'\n更新说明:'+data["desc"]
                                                    +'\n更新地址:'+data["url"]+'\n点击OK将跳转下载','检测到更新'
                                                    ,'QMessageBox.Icon.Information',data["url"],True,qt))
            else:
                messagebox.connectshow(partial(messagebox.showmsg,'当前已是最新版本!\n'+str(new_version)
                                                +'更新日志:\n'+data["desc"],'通知','QMessageBox.Icon.Information',qt=qt))
            rwconfig.wconfig('update','lasttime',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            lasttime=config['update']['lasttime']
            qt_newversion.setText('云端版本:'+str(new_version))
            qt_lasttime.setText('检查时间:'+lasttime)
        except Exception as e:
            messagebox.connectshow(partial(messagebox.showmsg,f'原因:\n{type(e).__name__}:{e}','检查更新失败','QMessageBox.Icon.Warning',qt=qt))
        messagebox.messageSignal.emit('signal')
    def get_data(self):
        try:
            url="https://raw.githubusercontent.com/xiyi20/GeminiGui/main/update.json"
            response=requests.get(url)
            data=response.json()
            return data
        except Exception as e:
            messagebox.connectshow(partial(messagebox.showmsg,f'原因:\n{type(e).__name__}:{e}','检查更新失败','QMessageBox.Icon.Warning'))
            messagebox.messageSignal.emit('signal')
            return None

checkupdate=CheckUpdate()

class Gemini:
    def __init__(self,model="gemini-pro"):
        genai.configure(api_key=apikey,transport='rest')
        # Set up the model
        generation_config={
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        }
        safety_settings=[
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]
        self.model=genai.GenerativeModel(model_name=model,
                                           generation_config=generation_config,
                                           safety_settings=safety_settings)
        self.chat=self.model.start_chat(history=[])

    def get_content(self,code,question,img=None):
        try:
            if img is None:
                response=self.chat.send_message(question).text
                if code==0:
                    response=markdown.markdown(response)
            else:
                response=self.model.generate_content([question,img]).text
            return response
        except Exception as e:
            return f'{type(e).__name__}:{e}'
            # messagebox.messageSignal.connect(messagebox.showmsg)
            # messagebox.messageSignal.emit(f'{type(e).__name__}:{e}')

class BlurredLabel(QLabel):
    def __init__(self,parent=None,items=[]):
        super().__init__(parent)
        global ml
        self.setGeometry(0,0,parent.width(),parent.height())
        for item in items:
            type=item.get('type',11)
            color=item.get('color','red')
            last_time=item.get('last_time',3)
            shape=item.get('shape',1)
            ml.append(MoveLabel(self,type=type,color=color,last_time=last_time,shape=shape))
        self.blur(blopen,blradius)
    def blur(self,state,num):
        if state==0:
            blur_effect=QGraphicsBlurEffect()
            blur_effect.setBlurRadius(num)
            self.setGraphicsEffect(blur_effect)
        else:
            self.setGraphicsEffect(None)

class MoveLabel(QLabel):
    def __init__(self,parent,type,shape,color,last_time):
        super().__init__(parent)
        self.side_width=min(parent.width(),parent.height()) // 2  #设置半径为父类宽高最小值的一半
        self.setGeometry(0,0,self.side_width,self.side_width)
        self.shape=shape
        self.last_time=last_time
        self.color=color
        if type==11:
            self.start_rect=QRectF(0,0,self.width(),self.height())
            self.end_rect=QRectF(self.parent().width()-self.side_width,self.parent().height()-self.side_width,self.side_width,self.side_width)
        elif type==12:
            self.start_rect=QRectF(parent.width()-self.side_width,parent.height()-self.side_width,self.side_width,self.side_width)
            self.end_rect=QRectF(0,0,self.width(),self.height())
        elif type==21:
            self.start_rect=QRectF((parent.width()-self.side_width)//2,0,self.side_width,self.side_width)
            self.end_rect=QRectF((parent.width()-self.side_width)//2,parent.height()-self.side_width,self.side_width,self.side_width)
        elif type==22:
            self.start_rect=QRectF((parent.width()-self.side_width)//2,parent.height()-self.side_width,self.side_width,self.side_width)
            self.end_rect=QRectF((parent.width()-self.side_width)//2,0,self.side_width,self.side_width)
        elif type==31:
            self.start_rect=QRectF(parent.width()-self.side_width,0,self.side_width,self.side_width)
            self.end_rect= QRectF(0,parent.height()-self.side_width,self.side_width,self.side_width)
        elif type==32:
            self.start_rect=QRectF(0,parent.height()-self.side_width,self.side_width,self.side_width)
            self.end_rect=QRectF(parent.width()-self.side_width,0,self.side_width,self.side_width)
        elif type==41:
            self.start_rect=QRectF(parent.width()-self.side_width,(parent.height()-self.side_width)//2,self.side_width,self.side_width)
            self.end_rect=QRectF(0,(parent.height()-self.side_width)//2,self.side_width,self.side_width)
        elif type==42:
            self.start_rect=QRectF(0,(parent.height()-self.side_width)//2,self.side_width,self.side_width)
            self.end_rect=QRectF(parent.width()-self.side_width,(parent.height()-self.side_width)//2,self.side_width,self.side_width)
        self.animation=QPropertyAnimation(self,b'geometry')
        self.animation.finished.connect(self.toggleAnimation)
        self.animationSpeed(dnspeed)
        self.startAnimation(dnopen,eval(dncurve))
    def paintEvent(self,event):
        super().paintEvent(event)
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.shape==1:
            #计算圆的位置
            rect=self.rect().adjusted(1,1,-1,-1)
            #设置刷子
            brush=QBrush(QColor(self.color))  #设置刷子颜色
            painter.setBrush(brush)
            #绘制圆
            painter.drawEllipse(rect)
        elif self.shape==2:
            painter.fillRect(0,0,self.side_width,self.side_width,QColor(self.color))  #设置刷子颜色
        elif self.shape==3:
            #计算三角形的顶点坐标
            p1=QPointF(self.width()/2,(self.height()-self.side_width*0.866)/2)  #设置刷子颜色
            p2=QPointF((self.width()-self.side_width)/2,(self.height()+self.side_width*0.866)/2)
            p3=QPointF((self.width()+self.side_width)/2,(self.height()+self.side_width*0.866)/2)
            triangle=QPolygonF([p1,p2,p3])
            painter.setBrush(QBrush(QColor(self.color)))  #设置刷子颜色
            painter.drawPolygon(triangle)
    def toggleAnimation(self):
        #切换动画的起始值和结束值
        a,b=self.animation.startValue(),self.animation.endValue()
        a,b=b,a
        self.animation.setStartValue(a)
        self.animation.setEndValue(b)
        self.animation.start()
    def animationSpeed(self,speed):
        self.animation.setDuration(self.last_time*speed)
    def startAnimation(self,open,dynamic):
        self.animation.setStartValue(self.start_rect)
        self.animation.setEndValue(self.end_rect)
        if open==0:
            self.animation.setEasingCurve(dynamic) #设置缓动曲线
            self.animation.start()
        else:
            self.animation.stop()

class GetColor(QColorDialog):
    def __init__(self):
        super().__init__()  
    def getcolor(self):
        self.color=self.getColor()
        if self.color.isValid():
            return self.color.name()

class MainWindow(QMainWindow):
    imgsignal=pyqtSignal(str)
    answersignal=pyqtSignal(str)
    clearsignal=pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.code=None
        self.state=None
        self.thread=None
        self.question=None
        self.settingw=None
        self.historyw=None
        self.gemini=Gemini()
        self.gemini_visual=Gemini('gemini-pro-vision')
        self.initUI()
    def closeEvent(self,event):
        window=[self.settingw,self.historyw]
        for i in window:
            if i is not None:
                i.close()
        if self.thread is not None:
            if self.thread.is_alive():
                self.thread.join()
        event.accept()
    @staticmethod
    def getimage():
        messagebox.connectshow(partial(messagebox.showdialog,'file'))
        messagebox.messageSignal.emit('signal')
    def initUI(self):
        self.move(450,20)
        self.setFixedSize(m_width,m_height)
        self.setWindowIcon(QIcon('images/Gemini.ico'))
        center=QWidget(self)
        shapes=[
            {'type':21,'shape':1,'color':getcolor(),'last_time':6},
            {'type':22,'shape':1,'color':getcolor(),'last_time':5},
            {'type':31,'shape':2,'color':getcolor(),'last_time':7},
            {'type':41,'shape':3,'color':getcolor(),'last_time':8},
            {'type':12,'shape':3,'color':getcolor(),'last_time':9},
        ]
        label=BlurredLabel(self,shapes)
        self.setCentralWidget(center)
        self.setWindowTitle('Gemini AI')

        f1=QFrame(self)
        f1.resize(m_width,m_height)
        layout_f1=QVBoxLayout(f1)
        
        def settingwindow():
            self.settingw.show()
        def showhistory():
            self.historyw.show()
        layout_top=QHBoxLayout()
        layout_f1.addLayout(layout_top)
        b1=QPushButton()
        b1.clicked.connect(settingwindow)
        b1.setIcon(QIcon('images/setting.png'))
        b0=QPushButton()
        b0.clicked.connect(showhistory)
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

        t1=QTextEdit()
        t1.setMinimumSize(int(m_width*0.9),int(m_height*0.3))
        layout_f1.addWidget(t1)
        layout_f1.addStretch(2)

        keywords=['网页','博客','文章','帖子','Wiki','文档','教程','手册','报告','百科','简历',
                      '电子书','演讲稿','课件','规范','合同','论文','文章','新闻','计划','指南','说明',
                      '分析','笔记','词典','诗歌','小说','剧本','攻略','日志','论文','新闻','公告']
        def answer(img):
            global img_a
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
                answer=self.gemini_visual.get_content(None,self.question,img_a)
                answer_text='Gemini:\n'+answer+'\n'
                t2.append(answer_text)
                img_a=None
            self.historyw.ta.append(answer_text)
            self.clearsignal.emit('signal')
            time.sleep(0.1)
            checkimg(link)
            setenable(True)
        def sethtml(html):
            t2.insertHtml(html)
            clearcontent(t1)
            setenable(True)
        def answerthread():
            self.question=t1.toPlainText()
            global img_a,img_t
            if img_a is not None:
                self.question+=',语言请用简体中文'
                question_text=self.question
                t2.append('我:\n')
                self.historyw.ta.append('我:\n')
                cursor=t2.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                t2.setTextCursor(cursor)
                cursor.insertImage(img_t)
                cursor=self.historyw.ta.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.historyw.ta.setTextCursor(cursor)
                cursor.insertImage(img_t)
                t2.append(question_text)
                self.historyw.ta.append(question_text)       
            else:
                if self.state==None:
                    self.question+=',语言请用简体中文'
                    self.state=1
                question_text='我:\n'+self.question
                self.historyw.ta.append(question_text)
                t2.append(question_text)
            self.thread=threading.Thread(target=answer,args=(img_a,))
            self.thread.start()
            t1.setText('请等待回答...')
            setenable(False)
        self.answersignal.connect(sethtml)
        self.clearsignal.connect(lambda:clearcontent(t1))
        layout_content=QHBoxLayout()
        b2=QPushButton('发送')
        b2.setStyleSheet('border-radius:15px')
        b2.setMinimumSize(int(m_width*0.5)-26,int(m_height*0.05))
        b2.clicked.connect(answerthread)
        def setenable(bool):
            link.setEnabled(bool)
            b2.setEnabled(bool)
            b3.setEnabled(bool)
        def clearcontent(qt):
            qt.clear()
        global link
        link=QPushButton()
        link.setMaximumSize(24,25)
        link.clicked.connect(imagethread)
        link.setIcon(QIcon('images/link.png'))
        link.setStyleSheet('background:rgba(0,0,0,0)')
        b3=QPushButton('清空')
        b3.clicked.connect(lambda:clearcontent(t2))
        b3.setStyleSheet('border-radius:15px')
        b3.setMinimumSize(int(m_width*0.5)-26,int(m_height*0.05))
        for i in b2,link,b3:
            layout_content.addWidget(i)
        layout_f1.addLayout(layout_content)

        t2=QTextEdit()
        t2.setReadOnly(True)
        t2.setMinimumSize(int(m_width*0.9),int(m_height*0.5))
    
        for i in t1,t2:
            i.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            i.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout_f1.addWidget(t2)
        self.historyw=HistoryWindow()
        self.settingw=SettingWindow(self,self.historyw,center,label,l1,t1,t2,b2,b3,self.historyw.center,self.historyw.label)  
    
class HistoryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ta=None
        self.center=None
        self.label=None
        self.initUI()
    def initUI(self):
        self.setWindowTitle('对话历史')
        self.move(50,80)
        self.setFixedSize(400,400) 
        self.setWindowIcon(QIcon('images/history.png'))
        self.center=QWidget(self)
        shapes=[
            {'type':11,'shape':1,'color':getcolor(),'last_time':6},
            {'type':21,'shape':3,'color':getcolor(),'last_time':5},
            {'type':31,'shape':1,'color':getcolor(),'last_time':7},
            {'type':41,'shape':2,'color':getcolor(),'last_time':8},
            {'type':12,'shape':1,'color':getcolor(),'last_time':9},
        ]
        self.label=BlurredLabel(self,shapes)
        self.setCentralWidget(self.center)

        f1=QFrame(self)
        layout_f1=QVBoxLayout(f1)
        f1.resize(400,400)
        self.ta=QTextEdit()
        self.ta.setMinimumSize(380,380)
        self.ta.setStyleSheet('background:rgba(255,255,255,0.5);border-radius:15px')
        self.ta.setReadOnly(True)
        layout_f1.addWidget(self.ta)

class SettingWindow(QMainWindow):
    def __init__(self,mwsf,htsf,mwbg,mwlb,mwl1,tq,ta,ba,bc,htbg,htlb):
        super().__init__()
        self.mwsf=mwsf
        self.htsf=htsf
        self.mwbg=mwbg
        self.mwlb=mwlb
        self.mwl1=mwl1
        self.htbg=htbg
        self.htlb=htlb
        self.tq=tq
        self.ta=ta
        self.ba=ba
        self.bc=bc
        self.initUI()
    def initUI(self):
        self.setWindowTitle('设置') 
        self.move(m_width+450,80)  
        self.setFixedSize(400,550)
        self.setWindowIcon(QIcon('images/setting.png'))
        center=QWidget(self)
        shapes=[
            {'type':11,'shape':1,'color':getcolor(),'last_time':6},
            {'type':21,'shape':3,'color':getcolor(),'last_time':5},
            {'type':31,'shape':1,'color':getcolor(),'last_time':7},
            {'type':41,'shape':2,'color':getcolor(),'last_time':8},
            {'type':12,'shape':1,'color':getcolor(),'last_time':9},
        ]
        label=BlurredLabel(self,shapes)
        self.setCentralWidget(center)

        f1=QFrame(self)
        f1.resize(400,550)
        layout_f1=QVBoxLayout(f1)

        def blur_open(state,num):
            self.mwlb.blur(state,num)
            self.htlb.blur(state,num)
            label.blur(state,num)
            rwconfig.wconfig('blur','open',state)
        
        def blur_radius(num):
            try:
                a=int(num)
                blur_open(0,a)
                cb1.setChecked(False)
                rwconfig.wconfig('blur','blur_radius',a)
            except ValueError:
                messagebox.showmsg('模糊程度应为整型(int)')
        def showtext(text):
            QToolTip.showText(QCursor.pos(),text)

        layout_blur=QVBoxLayout()
        l1=QLabel('模糊设置')
        cb1=QCheckBox('取消模糊')
        if blopen==2:
            cb1.setChecked(True)
        else:cb1.setChecked(False)
        cb1.stateChanged.connect(lambda state: blur_open(state,blradius))
        layout_blur1=QHBoxLayout()
        l2=QLabel('模糊程度:')
        t1=QLineEdit()
        t1.setText(str(blradius))
        t1.setFixedWidth(40)
        b1=QPushButton()
        b1.setIcon(QIcon('images/warm.png'))
        b1.clicked.connect(lambda:showtext('数字越大性能开销越大!'))
        b2=QPushButton()
        b2.setIcon(QIcon('images/save.png'))
        b2.clicked.connect(lambda: blur_radius(t1.text()))
        for i in l2,t1,b1,0,b2:
            if i==0:layout_blur1.addStretch(1)
            else:layout_blur1.addWidget(i)
        for i in l1,cb1,layout_blur1:
            if i in [l1,cb1]:layout_blur.addWidget(i)
            else:layout_blur.addLayout(i)
        
        layout_window=QVBoxLayout()
        l3=QLabel('界面设置')
        layout_window1=QHBoxLayout()
        l4=QLabel('窗口背景色:')
        def setwindowcolor(skip=False):
            if not skip:
                color=GetColor().getcolor()
                if color is not None:
                    self.mwbg.setStyleSheet('background:'+color)
                    self.htbg.setStyleSheet('background:'+color)
                    center.setStyleSheet('background:'+color)
                    b3.setStyleSheet(center.styleSheet()+';border-radius:9px')
            else:
                color=re.findall(find_color,b3.styleSheet())[0]
                rwconfig.wconfig('window','bg_color',color)
        b19=QPushButton()
        b19.setIcon(QIcon('images/warm.png'))
        b19.clicked.connect(lambda:showtext('背景色的优先级大于主题样式,更改后注意保存'))
        b3=QPushButton()
        b3.setMaximumSize(40,40)
        b3.clicked.connect(setwindowcolor) 
        b13=QPushButton()
        b13.setIcon(QIcon('images/save.png'))
        b13.clicked.connect(lambda:setwindowcolor(True))
        qt=[l4,b3,b19,0,b13]
        for i in qt:
            if i==0:layout_window1.addStretch(1)
            else:layout_window1.addWidget(i)

        layout_window2=QHBoxLayout()
        l5=QLabel('主题模式:')
        btg1=QButtonGroup()
        def settheme(color):
            if color=='default':
                self.mwl1.setStyleSheet('color:black')
                self.mwbg.setStyleSheet('background:white')
                center.setStyleSheet('background:white')
                self.tq.setStyleSheet(f'background:rgba(255,255,255,0.5);border-radius:{qradius}px')
                self.ba.setStyleSheet('background:rgba(0,0,0,0.5);border-radius:15px')
            else:
                if color=='white':
                    self.mwl1.setStyleSheet('color:black')
                    self.mwbg.setStyleSheet('background:white')
                    center.setStyleSheet('background:white')
                    self.tq.setStyleSheet(f'background:rgba(0,0,0,0.5);border-radius:{qradius}px')
                    self.ba.setStyleSheet('background:rgba(0,0,0,0.5);border-radius:15px')
                else:
                    self.mwl1.setStyleSheet('color:white')
                    self.mwbg.setStyleSheet('background:black')
                    center.setStyleSheet('background:black')
                    self.tq.setStyleSheet(f'background:rgba(255,255,255,0.5);border-radius:{qradius}px')
                    self.ba.setStyleSheet('background:rgba(255,255,255,0.5);border-radius:15px')
            self.ta.setStyleSheet(self.tq.styleSheet())
            self.bc.setStyleSheet(self.ba.styleSheet())
            b3.setStyleSheet(center.styleSheet()+';border-radius:9px')
            rwconfig.wconfig('window','theme',color)
        b4=QRadioButton('明亮')
        b4.clicked.connect(lambda:settheme('white'))
        b5=QRadioButton('暗黑')
        b5.clicked.connect(lambda:settheme('black'))
        b6=QRadioButton('默认')
        b6.clicked.connect(lambda:settheme('default'))
        for i in l5,b6,b4,b5:
            if i!=l5:btg1.addButton(i)
            layout_window2.addWidget(i)
        if bgtheme=='default':b6.click()
        elif bgtheme=='white':b4.click()
        else:b5.click()

        def setradius(code,te,num):
            try:
                a=int(num)
                style=te.styleSheet()
                patten=re.findall(find_radius,style)[0]
                style=str(style).replace(patten,num)
                te.setStyleSheet(style)
                rwconfig.wconfig('window',code,a)
            except ValueError:
                messagebox.showmsg('圆角应为整形(int)')
        layout_window3=QHBoxLayout()
        l6=QLabel('输入框圆角:')
        t2=QLineEdit()
        t2.setFixedWidth(40)
        t2.setText(str(qradius))
        b7=QPushButton()
        b7.setIcon(QIcon('images/save.png'))
        b7.clicked.connect(lambda:setradius('q_radius',self.tq,t2.text()))
        qt=[l6,t2,0,b7]
        for i in qt:
            if i==0:layout_window3.addStretch(1)
            else:layout_window3.addWidget(i)

        layout_window4=QHBoxLayout()
        l7=QLabel('回答框圆角:')
        t3=QLineEdit()
        t3.setFixedWidth(40)
        t3.setText(str(aradius))
        b8=QPushButton()
        b8.setIcon(QIcon('images/save.png'))
        b8.clicked.connect(lambda:setradius('a_radius',self.ta,t3.text()))
        for i in l7,t3,0,b8:
            if i==0:layout_window4.addStretch(1)
            else:layout_window4.addWidget(i)

        def setopacity(num):
            try:
                a=float(num)
                if 0<=a<=1:
                    self.setWindowOpacity(a)
                    self.mwsf.setWindowOpacity(a)
                    self.htsf.setWindowOpacity(a)
                    rwconfig.wconfig('window','opacity',a)
                else:messagebox.showmsg('值范围应为0—1')
            except ValueError:
                messagebox.showmsg('透明度应为浮点型(float)')
        layout_window5=QHBoxLayout()
        l16=QLabel('窗口透明度:')
        t5=QLineEdit()
        t5.setFixedWidth(40)
        t5.setText(str(opacity))
        setopacity(opacity)
        b20=QPushButton()
        b20.setIcon(QIcon('images/tip.png'))
        b20.clicked.connect(lambda:showtext('数字越小越透明,仅支持0-1'))
        b21=QPushButton()
        b21.setIcon(QIcon('images/save.png'))
        b21.clicked.connect(lambda:setopacity(t5.text()))

        for i in l16,t5,b20,0,b21:
            if i==0:layout_window5.addStretch(1)
            else:layout_window5.addWidget(i)

        for i in l3,layout_window1,layout_window2,layout_window3,layout_window4,layout_window5:
            if i==l3:layout_window.addWidget(i)
            else:layout_window.addLayout(i)
  
        layout_dynamic=QVBoxLayout()
        l8=QLabel('动效设置')
        def setdynamic(state,curve):
            if state==2:
                for i in ml:
                    i.startAnimation(state,None)
            else:
                for i in ml:
                    i.startAnimation(state,curve)
                    rwconfig.wconfig('dynamic','curve','QEasingCurve.'+str(curve_dict[combobox1.currentText()]))
            rwconfig.wconfig('dynamic','open',state)
        cb2=QCheckBox('关闭动效')
        if dnopen==2:
            cb2.setChecked(True)
        else:cb2.setChecked(False)
        cb2.stateChanged.connect(lambda state:setdynamic(state,eval(dncurve)))
        layout_dynamic1=QHBoxLayout()
        l9=QLabel('运动速度:')
        t4=QLineEdit()
        t4.setFixedWidth(40)
        t4.setText(str(dnspeed))
        def setspeed(num):
            try:
                a=int(num)
                for i in ml:
                    i.animationSpeed(a)
                rwconfig.wconfig('dynamic','speed',a)
            except ValueError:
                messagebox.showmsg('运动速度应为整形(int)')
        b9=QPushButton()
        b9.setIcon(QIcon('images/warm.png'))
        b9.clicked.connect(lambda:showtext('数字越大运动越慢,建议500-1000'))
        b10=QPushButton()
        b10.setIcon(QIcon('images/save.png'))
        b10.clicked.connect(lambda:setspeed(t4.text()))
        for i in l9,t4,b9,0,b10:
            if i==0:layout_dynamic1.addStretch(1)
            else:layout_dynamic1.addWidget(i)

        layout_dynamic2=QHBoxLayout()
        curve_dict={
            "线性": QEasingCurve.Type.Linear,
            "二次方进入": QEasingCurve.Type.InQuad,
            "二次方退出": QEasingCurve.Type.OutQuad,
            "二次方进入退出": QEasingCurve.Type.InOutQuad,
            "三次方进入": QEasingCurve.Type.InCubic,
            "三次方退出": QEasingCurve.Type.OutCubic,
            "三次方进入退出": QEasingCurve.Type.InOutCubic,
            "四次方进入": QEasingCurve.Type.InQuart,
            "四次方退出": QEasingCurve.Type.OutQuart,
            "四次方进入退出": QEasingCurve.Type.InOutQuart
        }
        curve_des=[
            "线性曲线，即匀速运动",
            "二次方曲线，开始缓慢，后期加速",
            "二次方曲线，开始加速，后期减速",
            "二次方曲线，开始缓慢，后期加速，再后期减速",
            "三次方曲线，开始缓慢，后期加速",
            "三次方曲线，开始加速，后期减速",
            "三次方曲线，开始缓慢，后期加速，再后期减速",
            "四次方曲线，开始缓慢，后期加速",
            "四次方曲线，开始加速，后期减速",
            "四次方曲线，开始缓慢，后期加速，再后期减速"
        ]  
        l10=QLabel('动画曲线:')
        combobox1=QComboBox()
        for key,value in curve_dict.items():
            combobox1.addItem(key)
            if str(value)==dncurve[13:]:
                combobox1.setCurrentText(key)
        b11=QPushButton()
        b11.setIcon(QIcon('images/tip.png'))
        b11.clicked.connect(lambda:showtext(curve_des[combobox1.currentIndex()]))
        b12=QPushButton()
        b12.setIcon(QIcon('images/save.png'))
        b12.clicked.connect(lambda:setdynamic(0,curve_dict[combobox1.currentText()]))
        for i in l10,combobox1,b11,0,b12:
            if i==0:layout_dynamic2.addStretch(1)
            else:layout_dynamic2.addWidget(i)

        for i in l8,cb2,layout_dynamic1,layout_dynamic2:
            if i in [l8,cb2]:layout_dynamic.addWidget(i)
            else:layout_dynamic.addLayout(i)

        layout_update=QVBoxLayout()
        l11=QLabel('更新设置')
        def setinterval(days):
            rwconfig.wconfig('update','interval',days)
        layout_update1=QHBoxLayout()
        interval_dict={'每次':0,'1天':1,'3天':3,'5天':5,'7天':7}
        l12=QLabel('检查间隔:')
        combobox2=QComboBox()
        for key,value in interval_dict.items():
            combobox2.addItem(key)
            if value==interval:combobox2.setCurrentText(key)
        b14=QPushButton()
        b14.setIcon(QIcon('images/save.png'))
        b14.clicked.connect(lambda:setinterval(interval_dict[combobox2.currentText()]))
        for i in l12,combobox2,0,b14:
            if i==0:layout_update1.addStretch()
            else:layout_update1.addWidget(i)

        l13=QLabel('当前版本:'+str(VERSION))
        def setnewversion(qt):
            newversion=checkupdate.get_data()
            if newversion is None:result='检查失败!'
            else:result=str(newversion['version'])
            qt.setText('云端版本:'+result)
        global qt_newversion
        l14=QLabel('云端版本:未知')
        qt_newversion=l14
        global qt_lasttime
        version_thread=threading.Thread(target=setnewversion,args=(l14,))
        version_thread.start()
        l15=QLabel('检查时间:'+str(lasttime))
        qt_lasttime=l15
        layout_update2=QHBoxLayout()
        for i in l13,l14,l15:
            if i==0:layout_update2.addStretch()
            else:layout_update2.addWidget(i)
        b18=QPushButton('检查更新')
        b18.clicked.connect(lambda:updatethread(True,b18))
        layout_update3=QVBoxLayout()
        layout_update3.addWidget(b18)
        for i in l11,layout_update1,layout_update2,layout_update3:
            if i==l11:layout_update.addWidget(i)
            else:layout_update.addLayout(i)
        def setapi(key):
            if key=='':
                messagebox.showmsg('APIKEY不能为空')
                return
            rwconfig.wconfig('gemini','apikey',key)
        layout_gemini=QVBoxLayout()
        l17=QLabel('API设置')
        layout_gemini1=QHBoxLayout()
        l18=QLabel('APIKEY:')
        t6=QLineEdit()
        t6.setFixedWidth(300)
        t6.setText(apikey)
        b22=QPushButton()
        b22.setIcon(QIcon('images/save.png'))
        b22.clicked.connect(lambda:setapi(t6.text()))
        for i in l18,t6,0,b22:
            if i==0:layout_gemini1.addStretch(1)
            else:layout_gemini1.addWidget(i)

        for i in l17,layout_gemini1:
            if i==l17:layout_gemini.addWidget(i)
            else:layout_gemini.addLayout(i)

        for i in l1,l3,l8,l11,l17:
            i.setFont(QFont('微软雅黑',15))
            i.setAlignment(Qt.AlignmentFlag.AlignCenter)

        for i in combobox1,combobox2:
            i.setStyleSheet("QComboBox { background-color: rgba(255,255,255,0.1); }"
                        "QComboBox QAbstractItemView { background-color: rgba(255,255,255,0.1); }")
        
        for i in t1,t2,t3,t4,t5,t6:
            i.setStyleSheet('background:rgba(255,255,255,0.5);border-radius:6px')

        for i in b1,b2,b7,b8,b9,b10,b11,b12,b13,b14,b19,b20,b21,b22:
            i.setStyleSheet('background:rgba(0,0,0,0)')

        for i in layout_gemini,layout_blur,layout_window,layout_dynamic,layout_update:
            layout_f1.addLayout(i)
        layout_f1.addStretch(1)

        self.mwbg.setStyleSheet('background:'+bgcolor)
        center.setStyleSheet('background:'+bgcolor)
        b3.setStyleSheet(center.styleSheet()+';border-radius:9px')

def checkimg(link):
    global img_a
    if img_a is not None:link.setIcon(QIcon('images/elink.png'))
    else:link.setIcon(QIcon('images/link.png'))

def imagethread():
    global img_a,link
    if img_a is not None:
        img_a=None
        checkimg(link)
        return
    img_thread=threading.Thread(target=MainWindow.getimage)
    img_thread.start()

def updatethread(skip=False,qt=None):
    if qt is not None:
        qt.setText('正在检查...')
        qt.setEnabled(False)
    update_thread=threading.Thread(target=checkupdate.check,args=(skip,qt))
    update_thread.start()

def main():
    app=QApplication(sys.argv)
    if apikey=='':messagebox.showdialog()
    global m_width,m_height
    m_width=int(app.primaryScreen().size().width()*0.4)
    m_height=int(app.primaryScreen().size().height()*0.88)
    mainWindow=MainWindow()
    mainWindow.show()
    updatethread()
    sys.exit(app.exec())

if __name__=='__main__':
    main()