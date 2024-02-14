from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget,QFrame,\
    QMainWindow,QVBoxLayout,QTextEdit
from Blurlabel import BlurredLabel

class HistoryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ta=None
        self.center=None
        self.label=None
        self.initUI()
    def initUI(self):
        from Main import getcolor
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