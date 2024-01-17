import google.generativeai as genai
import sys
import threading
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

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
        self.setGeometry(0,0,parent.width(),parent.height())
        for item in items:
            type=item.get('type',11)
            color=item.get('color','red')
            last_time=item.get('last_time',3)
            shape=item.get('shape',1)
            MoveLabel(self,type=type,color=color,last_time=last_time,shape=shape)
        blur_effect=QGraphicsBlurEffect()
        blur_effect.setBlurRadius(300)
        # self.setGraphicsEffect(blur_effect)

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
    def startAnimation(self):
        self.animation.setStartValue(self.start_rect)
        self.animation.setEndValue(self.end_rect)
        self.animation.setDuration(self.last_time*1000)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)  # 设置缓动曲线
        self.animation.start()

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
            {'type':11,'shape':1,'color':'#FF416C','last_time':6},
            {'type':21,'shape':3,'color':'#12c2e9','last_time':5},
            {'type':31,'shape':1,'color':'#c471ed','last_time':7},
            {'type':41,'shape':2,'color':'#f64f59','last_time':8},
            {'type':12,'shape':1,'color':'#7303c0','last_time':9},
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
                self.settingw=SettingWindow()
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
        b2=QPushButton('确定')
        b2.setStyleSheet('background:rgba(0,0,0,0.5);border-radius:15px')
        b2.setMinimumSize(400,30)
        b2.clicked.connect(answerthread)
        layout_f1.addWidget(b2)
        layout_f1.addStretch(1)

        t2=QTextEdit()
        t2.setReadOnly(True)
        t2.setMinimumSize(750,400)
        t2.setStyleSheet('background:rgba(255,255,255,0.5);border-radius:15px')
        layout_f1.addWidget(t2)
        
class SettingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        self.setWindowTitle('设置')   
        self.setGeometry(1100,100,400,400)
        self.setWindowIcon(QIcon('git/GeminiGui/images/setting.png'))
        center=QWidget(self)
        layout_center=QVBoxLayout(center)
        shapes=[
            {'type':11,'shape':1,'color':'#FF416C','last_time':6},
            {'type':21,'shape':3,'color':'#12c2e9','last_time':5},
            {'type':31,'shape':1,'color':'#c471ed','last_time':7},
            {'type':41,'shape':2,'color':'#f64f59','last_time':8},
            {'type':12,'shape':1,'color':'#7303c0','last_time':9},
        ]
        label=BlurredLabel(self,shapes)
        layout_center.addWidget(label)
        self.setCentralWidget(center)

           
def main():
    app=QApplication(sys.argv)
    mainWindow=MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
if __name__ == '__main__':
    main()