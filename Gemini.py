import google.generativeai as genai
import sys
import re
import threading
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

find_radius=re.compile(r'border-radius:(.*?)px')
ml=[]

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
        self.blur(0,100)
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
        self.animationSpeed(500)
        self.startAnimation()
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
    def startAnimation(self):
        self.animation.setStartValue(self.start_rect)
        self.animation.setEndValue(self.end_rect)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuart)  # 设置缓动曲线
        self.animation.start()

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
        layout_center=QVBoxLayout(center)
        shapes=[
            {'type':11,'shape':1,'color':'red','last_time':6},
            {'type':21,'shape':3,'color':'blue','last_time':5},
            {'type':31,'shape':1,'color':'orange','last_time':7},
            {'type':41,'shape':2,'color':'purple','last_time':8},
            {'type':12,'shape':1,'color':'pink','last_time':9},
        ]
        label=BlurredLabel(self,shapes)
        layout_center.addWidget(label)
        self.setCentralWidget(center)
        self.setWindowTitle('Gemini AI')

        f1=QFrame(self)
        f1.resize(800,800)
        layout_f1=QVBoxLayout(f1)
        
        def settingwindow():
            if self.settingw is None:
                self.settingw=SettingWindow(label,center,label,t1,t2,b2,b3)
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
        
class SettingWindow(QMainWindow):
    def __init__(self,bg,mwbg,mwlb,tq,ta,ba,bc):
        super().__init__()
        self.bg=bg
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
        layout_center=QVBoxLayout(center)
        shapes=[
            {'type':11,'shape':1,'color':'green','last_time':6},
            {'type':21,'shape':3,'color':'blue','last_time':5},
            {'type':31,'shape':1,'color':'red','last_time':7},
            {'type':41,'shape':2,'color':'purple','last_time':8},
            {'type':12,'shape':1,'color':'pink','last_time':9},
        ]
        label=BlurredLabel(self,shapes)
        layout_center.addWidget(label)
        self.setCentralWidget(center)

        f1=QFrame(self)
        f1.resize(400,400)
        layout_f1=QVBoxLayout(f1)

        l1=QLabel('模糊设置')
        l1.setFont(QFont('微软雅黑',15))
        l1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        def blur_open(bg,state,num):
            bg.blur(state,num)
            label.blur(state,num)
        cb1=QCheckBox('取消模糊')
        cb1.stateChanged.connect(lambda state: blur_open(self.bg,state,100))

        def blur_radius(num):
            try:
                a=int(num)
                blur_open(self.bg,0,int(a))
                cb1.setChecked(False)
            except ValueError:
                MessageBox('模糊程度应为整型(int)')

        layout_blur=QHBoxLayout()
        l2=QLabel('模糊程度:')
        t1=QLineEdit()
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
            self.mwbg.setStyleSheet('background:'+color)
            center.setStyleSheet('background:'+color)
            b3.setStyleSheet(center.styleSheet())
            self.mwlb.setStyleSheet('background:0,0,0,0')
            label.setStyleSheet('background:0,0,0,0')
        b3=QPushButton()
        b3.clicked.connect(setwindowcolor)
        b3.setMaximumSize(40,40)
        layout_window1.addWidget(l4)
        layout_window1.addWidget(b3)

        layout_window2=QHBoxLayout()
        l5=QLabel('主题模式:')
        btg=QButtonGroup()
        def settheme(color):
            code_dict={'white':'0','default':'255'}
            code=code_dict.get(color, '255')
            self.mwbg.setStyleSheet('background:'+color)
            center.setStyleSheet('background:'+color)
            tq_style=f'background:rgba({code},{code},{code},0.5);border-radius:15px'
            self.tq.setStyleSheet(tq_style)
            self.ta.setStyleSheet(tq_style)
            self.ba.setStyleSheet(tq_style)
            self.bc.setStyleSheet(tq_style)
            if color=='default':
                self.mwbg.setStyleSheet('background:white')
                center.setStyleSheet('background:white')
                self.tq.setStyleSheet(tq_style)
                self.ta.setStyleSheet(tq_style)
                self.ba.setStyleSheet('background:rgba(0,0,0,0.5);border-radius:15px')
                self.bc.setStyleSheet(self.ba.styleSheet())
            b3.setStyleSheet(center.styleSheet())
            self.mwlb.setStyleSheet('background:0,0,0,0')
            label.setStyleSheet('background:0,0,0,0')
        b4=QRadioButton('明亮')
        b4.clicked.connect(lambda:settheme('white'))
        b5=QRadioButton('暗黑')
        b5.clicked.connect(lambda:settheme('black'))
        b6=QRadioButton('默认')
        b6.clicked.connect(lambda:settheme('default'))
        btg.addButton(b4)
        btg.addButton(b5)
        btg.addButton(b6)
        layout_window2.addWidget(l5)
        layout_window2.addWidget(b6)
        layout_window2.addWidget(b4)
        layout_window2.addWidget(b5)
        def setradius(te,num):
            try:
                a=int(num)
                style=te.styleSheet()
                patten=re.findall(find_radius,style)[0]
                style=str(style).replace(patten,a)
                te.setStyleSheet(style)
            except ValueError:
                MessageBox('圆角应为整形(int)')
        layout_window3=QHBoxLayout()
        l6=QLabel('输入框圆角:')
        t2=QLineEdit()
        t2.setMaximumWidth(50)
        t2.setStyleSheet('background:rgba(255,255,255,0.5)')
        b7=QPushButton()
        b7.setIcon(QIcon('git/GeminiGui/images/save.png'))
        b7.setStyleSheet('background:rgba(0,0,0,0)')
        b7.clicked.connect(lambda:setradius(self.tq,t2.text()))
        layout_window3.addWidget(l6)
        layout_window3.addWidget(t2)
        layout_window3.addStretch(1)
        layout_window3.addWidget(b7)
        layout_window4=QHBoxLayout()
        l7=QLabel('回答框圆角:')
        t3=QLineEdit()
        t3.setMaximumWidth(50)
        t3.setStyleSheet('background:rgba(255,255,255,0.5)')
        b8=QPushButton()
        b8.setIcon(QIcon('git/GeminiGui/images/save.png'))
        b8.setStyleSheet('background:rgba(0,0,0,0)')
        b8.clicked.connect(lambda:setradius(self.ta,t3.text()))
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
        l9=QLabel('运动速度:')
        t4=QLineEdit()
        t4.setMaximumWidth(50)
        t4.setStyleSheet('background:rgba(255,255,255,0.5)')
        def setspeed(num):
            try:
                a=int(num)
                for i in ml:
                    i.animationSpeed(a)
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


        layout_f1.addWidget(l1)
        layout_f1.addWidget(cb1)
        layout_f1.addLayout(layout_blur)
        layout_f1.addWidget(l3)
        layout_f1.addLayout(layout_window)
        layout_f1.addWidget(l8)
        layout_f1.addLayout(layout_dynamic)
        layout_f1.addStretch(1)


           
def main():
    app=QApplication(sys.argv)
    mainWindow=MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
if __name__=='__main__':
    main()