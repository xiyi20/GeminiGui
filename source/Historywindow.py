from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame,QMainWindow,QVBoxLayout,QTextEdit
from Blurlabel import BlurredLabel
from CustomFrame import CustomBanner

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
        self.setFixedSize(400,430)
        self.setWindowIcon(QIcon('images/history.png'))
        self.setStyleSheet('border-radius:15px')
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.center=QFrame(self)
        self.center.resize(self.width(),self.height())
        layout_center=QVBoxLayout(self.center)
        layout_center.setSpacing(0)
        layout_center.setContentsMargins(0,0,0,0)
        shapes=[
            {'type':11,'shape':1,'color':getcolor(),'last_time':6},
            {'type':21,'shape':3,'color':getcolor(),'last_time':5},
            {'type':31,'shape':1,'color':getcolor(),'last_time':7},
            {'type':41,'shape':2,'color':getcolor(),'last_time':8},
            {'type':12,'shape':1,'color':getcolor(),'last_time':9},
        ]
        self.label=BlurredLabel(self.center,shapes)
        banner=CustomBanner(self,'images/history.png','记录',[1,3])
        layout_center.addWidget(banner)
        self.setCentralWidget(self.center)

        f1=QFrame()
        f1.setStyleSheet('background:rgba(0,0,0,0)')
        layout_f1=QVBoxLayout(f1)
        self.ta=QTextEdit()
        self.ta.setMinimumSize(380,380)
        self.ta.setStyleSheet('background:rgba(255,255,255,0.5);border-radius:15px')
        self.ta.setReadOnly(True)
        layout_f1.addWidget(self.ta)
        layout_center.addWidget(f1)