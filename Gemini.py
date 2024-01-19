import google.generativeai as genai
import sys
import re
import json
import threading
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

find_radius=re.compile(r'border-radius:(.*?)px')
ml=[]
config=None

class RwConfig:
    def __init__(self):
        with open('git/GeminiGui/config.json') as f:
            global config
            config=json.load(f)
    def wconfig(self,zone,name,value):
        with open('git/GeminiGui/config.json','w') as f:
            config[zone][name]=value
            json.dump(config,f,indent=4)
    
rwconfig=RwConfig()

class Gemini:
    genai.configure(api_key="AIzaSyCYbTJdgdMy5ETlRFPAcpQozMrnYLp5g0w",transport='rest')
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
    model=genai.GenerativeModel(model_name="gemini-pro",
                                generation_config=generation_config,
                                safety_settings=safety_settings)
    chat=model.start_chat(history=[])
    def get_content(self,question):
        response=self.chat.send_message(question+'请用简体中文回答')
        return response.text

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
        self.blur(config['blur']['open'],config['blur']['blur_radius'])
    def blur(self,state,num):
        if state==0:
            blur_effect=QGraphicsBlurEffect()
            blur_effect.setBlurRadius(num)
            self.setGraphicsEffect(blur_effect)
        else:
            self.setGraphicsEffect(None)

class MoveLabel(QLabel):
    def __init__(self,parent=None,type=11,shape=0,color='blue',last_time=5):
        super().__init__(parent)
        self.side_width=min(parent.width(),parent.height()) // 2  # 设置半径为父类宽高最小值的一半
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
        self.animationSpeed(config['dynamic']['speed'])
        self.startAnimation(config['dynamic']['open'],eval(config['dynamic']['curve']))
    def paintEvent(self,event):
        super().paintEvent(event)
        painter=QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.shape==1:
            # 计算圆的位置
            rect=self.rect().adjusted(1,1,-1,-1)
            # 设置刷子
            brush=QBrush(QColor(self.color))  # 刷子颜色为半透明红色
            painter.setBrush(brush)
            # 绘制圆
            painter.drawEllipse(rect)
        elif self.shape==2:
            painter.fillRect(0,0,self.side_width,self.side_width,QColor(self.color))  # 使用红色填充正方形
        elif self.shape==3:
            # 计算三角形的顶点坐标
            p1=QPointF(self.width()/2,(self.height()-self.side_width*0.866)/2)  # 0.866 为 sqrt(3)/2,即等边三角形的高度
            p2=QPointF((self.width()-self.side_width)/2,(self.height()+self.side_width*0.866)/2)
            p3=QPointF((self.width()+self.side_width)/2,(self.height()+self.side_width*0.866)/2)
            triangle=QPolygonF([p1,p2,p3])
            painter.setBrush(QBrush(QColor(0,0,255)))  # 使用蓝色填充三角形
            painter.drawPolygon(triangle)
    def toggleAnimation(self):
        # 切换动画的起始值和结束值
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
            self.animation.setEasingCurve(dynamic) # 设置缓动曲线
            self.animation.start()
        else:
            self.animation.stop()

class MessageBox(QMessageBox):
    def __init__(self,msg):
        super().__init__()
        self.setWindowIcon(QIcon('git/GeminiGui/images/warm.png'))
        self.setIcon(QMessageBox.Icon.Warning)
        self.setWindowTitle('警告')
        self.setText(msg)
        self.exec()

class GetColor(QColorDialog):
    def __init__(self):
        super().__init__()  
    def getcolor(self):
        self.color=self.getColor()
        if self.color.isValid():
            return self.color.name()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300,50,800,800)
        self.settingw=None
        self.thread=None
        self.initUI()
    def closeEvent(self,event):
        if self.settingw is not None:
            self.settingw.close()
        if self.thread is not None:
            if self.thread.is_alive():
                self.thread.join()
        event.accept()
    def initUI(self):
        self.setWindowIcon(QIcon('git/GeminiGui/images/Gemini.png'))
        center=QWidget(self)
        shapes=[
            {'type':11,'shape':1,'color':'red','last_time':6},
            {'type':21,'shape':3,'color':'blue','last_time':5},
            {'type':31,'shape':1,'color':'orange','last_time':7},
            {'type':41,'shape':2,'color':'purple','last_time':8},
            {'type':12,'shape':1,'color':'pink','last_time':9},
        ]
        label=BlurredLabel(self,shapes)
        self.setCentralWidget(center)
        self.setWindowTitle('Gemini AI')
        center.setStyleSheet('background:'+config['window']['bg_color'])

        f1=QFrame(self)
        f1.resize(800,800)
        layout_f1=QVBoxLayout(f1)
        
        def settingwindow():
            self.settingw.show()

        layout_top=QHBoxLayout()
        layout_f1.addLayout(layout_top)
        b1=QPushButton()
        b1.clicked.connect(settingwindow)
        b1.setStyleSheet('background:rgba(255,255,255,0)')
        b1.setIcon(QIcon('git/GeminiGui/images/setting.png'))
        layout_top.addStretch(1)
        layout_top.addWidget(b1)

        l1=QLabel('Geimini Ai')
        l1.setFont(QFont('微软雅黑',30))
        l1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_f1.addWidget(l1)
        layout_f1.addStretch()

        t1=QTextEdit()
        t1.setMinimumSize(750,230)
        t1.setStyleSheet('background:rgba(255,255,255,0.5);border-radius:15px')
        layout_f1.addWidget(t1)
        layout_f1.addStretch(2)

        def answer():
            question=t1.toPlainText()
            answer=Gemini().get_content(question)
            t2.append('Gemini:\n'+answer+'\n')
        def answerthread():
            t2.append('我:'+t1.toPlainText())
            self.thread=threading.Thread(target=answer)
            self.thread.start()
        layout_content=QHBoxLayout()
        b2=QPushButton('确定')
        b2.setStyleSheet('background:rgba(0,0,0,0.5);border-radius:15px')
        b2.setMinimumSize(380,30)
        b2.clicked.connect(answerthread)
        def clearcontent():
            t2.clear()
        b3=QPushButton('清空')
        b3.clicked.connect(clearcontent)
        b3.setStyleSheet('background:rgba(0,0,0,0.5);border-radius:15px')
        b3.setMinimumSize(380,30)
        layout_content.addWidget(b2)
        layout_content.addWidget(b3)
        layout_f1.addLayout(layout_content)
        layout_f1.addStretch(1)

        t2=QTextEdit()
        t2.setReadOnly(True)
        t2.setMinimumSize(750,400)
        t2.setStyleSheet('background:rgba(255,255,255,0.5);border-radius:15px')
        layout_f1.addWidget(t2)
        self.settingw=SettingWindow(center,label,t1,t2,b2,b3)
        
class SettingWindow(QMainWindow):
    def __init__(self,mwbg,mwlb,tq,ta,ba,bc):
        super().__init__()
        self.mwbg=mwbg
        self.mwlb=mwlb
        self.tq=tq
        self.ta=ta
        self.ba=ba
        self.bc=bc
        self.initUI()
    def initUI(self):
        self.setWindowTitle('设置')   
        self.setGeometry(1100,100,400,400)
        self.setWindowIcon(QIcon('git/GeminiGui/images/setting.png'))
        center=QWidget(self)
        shapes=[
            {'type':11,'shape':1,'color':'green','last_time':6},
            {'type':21,'shape':3,'color':'blue','last_time':5},
            {'type':31,'shape':1,'color':'red','last_time':7},
            {'type':41,'shape':2,'color':'purple','last_time':8},
            {'type':12,'shape':1,'color':'pink','last_time':9},
        ]
        label=BlurredLabel(self,shapes)
        self.setCentralWidget(center)
        center.setStyleSheet('background:'+config['window']['bg_color'])
        center.setStyleSheet('background:'+'blue')

        f1=QFrame(self)
        f1.resize(400,400)
        layout_f1=QVBoxLayout(f1)

        l1=QLabel('模糊设置')
        l1.setFont(QFont('微软雅黑',15))
        l1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def blur_open(bg,state,num):
            bg.blur(state,num)
            label.blur(state,num)
            rwconfig.wconfig('blur','open',state)

        cb1=QCheckBox('取消模糊')
        if config['blur']['open']==2:
            cb1.setChecked(True)
        else:cb1.setChecked(False)
        cb1.stateChanged.connect(lambda state: blur_open(self.mwlb,state,100))

        def blur_radius(num):
            try:
                a=int(num)
                blur_open(self.mwlb,0,a)
                cb1.setChecked(False)
                rwconfig.wconfig('blur','blur_radius',a)
            except ValueError:
                MessageBox('模糊程度应为整型(int)')

        layout_blur=QHBoxLayout()
        l2=QLabel('模糊程度:')
        t1=QLineEdit()
        t1.setText(str(config['blur']['blur_radius']))
        t1.setStyleSheet('background:rgba(255,255,255,0.5)')
        t1.setMaximumWidth(50)
        def showtext(text):
            QToolTip.showText(QCursor.pos(),text)
        b1=QPushButton()
        b1.setIcon(QIcon('git/GeminiGui/images/warm.png'))
        b1.setStyleSheet('background:rgba(0,0,0,0)')
        b1.clicked.connect(lambda:showtext('数字越大性能开销越大!'))
        b2=QPushButton()
        b2.setIcon(QIcon('git/GeminiGui/images/save.png'))
        b2.setStyleSheet('background:rgba(0,0,0,0)')
        b2.clicked.connect(lambda: blur_radius(t1.text()))
        layout_blur.addWidget(l2)
        layout_blur.addWidget(t1)
        layout_blur.addWidget(b1)
        layout_blur.addStretch(1)
        layout_blur.addWidget(b2)

        l3=QLabel('界面设置')
        l3.setFont(QFont('微软雅黑',15))
        l3.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_window=QVBoxLayout()

        layout_window1=QHBoxLayout()
        l4=QLabel('窗口背景色:')
        def setwindowcolor():
            color=GetColor().getcolor()
            if color is not None:
                self.mwbg.setStyleSheet('background:'+color)
                center.setStyleSheet('background:'+color)
                b3.setStyleSheet(center.styleSheet())
                rwconfig.wconfig('window','bg_color',color)

        b3=QPushButton()
        b3.setStyleSheet(center.styleSheet())
        b3.setMaximumSize(40,40)
        b3.clicked.connect(setwindowcolor) 
        b13=QPushButton()
        b13.setIcon(QIcon('git/GeminiGui/images/save.png'))
        b13.setStyleSheet('background:rgba(0,0,0,0)')
        layout_window1.addWidget(l4)
        layout_window1.addWidget(b3)
        layout_window1.addStretch(1)
        layout_window1.addWidget(b13)

        layout_window2=QHBoxLayout()
        l5=QLabel('主题模式:')
        btg=QButtonGroup()
        def settheme(color):
            if color=='default':
                self.mwbg.setStyleSheet('background:white')
                center.setStyleSheet('background:white')
                self.tq.setStyleSheet('background:rgba(255,255,255,0.5);border-radius:15px')
                self.ta.setStyleSheet(self.tq.styleSheet())
                self.ba.setStyleSheet('background:rgba(0,0,0,0.5);border-radius:15px')
                self.bc.setStyleSheet(self.ba.styleSheet())
            elif color=='white':
                self.mwbg.setStyleSheet('background:white')
                center.setStyleSheet('background:white')
                self.tq.setStyleSheet('background:rgba(0,0,0,0.5);border-radius:15px')
                self.ta.setStyleSheet(self.tq.styleSheet())
                self.ba.setStyleSheet(self.tq.styleSheet())
                self.bc.setStyleSheet(self.tq.styleSheet())
            else:
                self.mwbg.setStyleSheet('background:black')
                center.setStyleSheet('background:black')
                self.tq.setStyleSheet('background:rgba(255,255,255,0.5);border-radius:15px')
                self.ta.setStyleSheet(self.tq.styleSheet())
                self.ba.setStyleSheet(self.tq.styleSheet())
                self.bc.setStyleSheet(self.tq.styleSheet())
            b3.setStyleSheet(center.styleSheet())
            rwconfig.wconfig('window','theme',color)
        b4=QRadioButton('明亮')
        b4.clicked.connect(lambda:settheme('white'))
        b5=QRadioButton('暗黑')
        b5.clicked.connect(lambda:settheme('black'))
        b6=QRadioButton('默认')
        b6.clicked.connect(lambda:settheme('default'))
        if config['window']['theme']=='default':b6.click()
        elif config['window']['theme']=='white':b4.click()
        else:b5.click()
        btg.addButton(b4)
        btg.addButton(b5)
        btg.addButton(b6)
        layout_window2.addWidget(l5)
        layout_window2.addWidget(b6)
        layout_window2.addWidget(b4)
        layout_window2.addWidget(b5)
        def setradius(code,te,num):
            try:
                a=int(num)
                style=te.styleSheet()
                patten=re.findall(find_radius,style)[0]
                style=str(style).replace(patten,num)
                te.setStyleSheet(style)
                rwconfig.wconfig('window',code,a)
            except ValueError:
                MessageBox('圆角应为整形(int)')
        layout_window3=QHBoxLayout()
        l6=QLabel('输入框圆角:')
        t2=QLineEdit()
        t2.setMaximumWidth(50)
        t2.setStyleSheet('background:rgba(255,255,255,0.5)')
        t2.setText(str(config['window']['q_radius']))
        b7=QPushButton()
        b7.setIcon(QIcon('git/GeminiGui/images/save.png'))
        b7.setStyleSheet('background:rgba(0,0,0,0)')
        b7.clicked.connect(lambda:setradius('q_radius',self.tq,t2.text()))
        layout_window3.addWidget(l6)
        layout_window3.addWidget(t2)
        layout_window3.addStretch(1)
        layout_window3.addWidget(b7)
        layout_window4=QHBoxLayout()
        l7=QLabel('回答框圆角:')
        t3=QLineEdit()
        t3.setMaximumWidth(50)
        t3.setStyleSheet('background:rgba(255,255,255,0.5)')
        t3.setText(str(config['window']['a_radius']))
        b8=QPushButton()
        b8.setIcon(QIcon('git/GeminiGui/images/save.png'))
        b8.setStyleSheet('background:rgba(0,0,0,0)')
        b8.clicked.connect(lambda:setradius('a_radius',self.ta,t3.text()))
        layout_window4.addWidget(l7)
        layout_window4.addWidget(t3)
        layout_window4.addStretch(1)
        layout_window4.addWidget(b8)
        layout_window.addLayout(layout_window1)
        layout_window.addLayout(layout_window2)
        layout_window.addLayout(layout_window3)
        layout_window.addLayout(layout_window4)

        l8=QLabel('动效设置')
        l8.setFont(QFont('微软雅黑',15))
        l8.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout_dynamic=QHBoxLayout()
        def setdynamic(state,curve):
            if state==2:
                for i in ml:
                    i.startAnimation(state,None)
            else:
                for i in ml:
                    i.startAnimation(state,curve)
                    rwconfig.wconfig('dynamic','curve','QEasingCurve.'+str(curve_dict[combobox.currentText()]))
            rwconfig.wconfig('dynamic','open',state)
        cb2=QCheckBox('关闭动效')
        if config['dynamic']['open']==2:
            cb2.setChecked(True)
        else:cb2.setChecked(False)
        cb2.stateChanged.connect(lambda state:setdynamic(state,eval(config['dynamic']['curve'])))
        l9=QLabel('运动速度:')
        t4=QLineEdit()
        t4.setMaximumWidth(50)
        t4.setStyleSheet('background:rgba(255,255,255,0.5)')
        t4.setText(str(config['dynamic']['speed']))
        def setspeed(num):
            try:
                a=int(num)
                for i in ml:
                    i.animationSpeed(a)
                rwconfig.wconfig('dynamic','speed',a)
            except ValueError:
                MessageBox('运动速度应为整形(int)')
        b9=QPushButton()
        b9.setIcon(QIcon('git/GeminiGui/images/warm.png'))
        b9.setStyleSheet('background:rgba(0,0,0,0)')
        b9.clicked.connect(lambda:showtext('数字越大运动越慢,建议500-1000'))
        b10=QPushButton()
        b10.setIcon(QIcon('git/GeminiGui/images/save.png'))
        b10.setStyleSheet('background:rgba(0,0,0,0)')
        b10.clicked.connect(lambda:setspeed(t4.text()))
        layout_dynamic.addWidget(l9)
        layout_dynamic.addWidget(t4)
        layout_dynamic.addWidget(b9)
        layout_dynamic.addStretch(1)
        layout_dynamic.addWidget(b10)

        layout_dynamic1=QHBoxLayout()
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
        combobox=QComboBox()

        for key,value in curve_dict.items():
            combobox.addItem(key)
            if str(value)==config['dynamic']['curve'][13:]:
                combobox.setCurrentText(key)

        b11=QPushButton()
        b11.setIcon(QIcon('git/GeminiGui/images/tip.png'))
        b11.setStyleSheet('background:rgba(0,0,0,0)')
        b11.clicked.connect(lambda:showtext(curve_des[combobox.currentIndex()]))
        b12=QPushButton()
        b12.setIcon(QIcon('git/GeminiGui/images/save.png'))
        b12.setStyleSheet('background:rgba(0,0,0,0)')
        b12.clicked.connect(lambda:setdynamic(0,curve_dict[combobox.currentText()]))
        layout_dynamic1.addWidget(l10)
        layout_dynamic1.addWidget(combobox)
        layout_dynamic1.addWidget(b11)
        layout_dynamic1.addStretch(1)
        layout_dynamic1.addWidget(b12)

        layout_f1.addWidget(l1)
        layout_f1.addWidget(cb1)
        layout_f1.addLayout(layout_blur)
        layout_f1.addWidget(l3)
        layout_f1.addLayout(layout_window)
        layout_f1.addWidget(l8)
        layout_f1.addWidget(cb2)
        layout_f1.addLayout(layout_dynamic)
        layout_f1.addLayout(layout_dynamic1)
        layout_f1.addStretch(1)
        
     
def main():
    app=QApplication(sys.argv)
    mainWindow=MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
if __name__=='__main__':
    main()