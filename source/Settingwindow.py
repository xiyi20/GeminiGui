import re
import threading
from PyQt6.QtGui import QFont,QIcon,QCursor
from PyQt6.QtCore import Qt,QEasingCurve
from PyQt6.QtWidgets import QLabel,QFrame,\
    QMainWindow,QColorDialog,QToolTip,\
    QVBoxLayout,QHBoxLayout,QPushButton,QCheckBox,\
    QButtonGroup,QRadioButton,QLineEdit,QComboBox
from Checkupdate import checkupdate
from Blurlabel import BlurredLabel
from CustomFrame import CustomBanner

class ColorDialog(QColorDialog):
    def __init__(self):
        super().__init__()
    def opendialog(self):
        self.color=self.getColor()
        if self.color.isValid():
            return self.color.name()

class SettingWindow(QMainWindow):
    def __init__(self,htsf,mwsf,mwbg,mwlb,mwl1,tq,ta,ba,bc,htbg,htlb,Main_ins):
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
        self.update_thread=None
        self.version_thread=None
        self.Main_ins=Main_ins
        self.initUI(Main_ins)
    @staticmethod
    def showtext(text):
        QToolTip.showText(QCursor.pos(),text)
    @staticmethod
    def updatethread(self,skip=False,qt=None,Main_ins=None):
        if qt is not None:
            qt.setText('正在检查...')
            qt.setEnabled(False)
        self.update_thread=threading.Thread(target=checkupdate.check,args=(skip,qt,Main_ins))
        self.update_thread.start()
    def closeEvent(self,event):
        threads=[self.update_thread,self.version_thread]
        for i in threads:
            if i is not None and i.is_alive():
                i.join()
        event.accept()
    def initUI(self,Main_ins):
        from Msgbox import messagebox
        from Rwconfig import RwConfig,rwconfig
        from Main import getcolor
        import Main
        self.setWindowTitle('设置') 
        self.move(Main_ins.m_width+450,80)
        self.setFixedSize(400,535)
        self.setWindowIcon(QIcon('images/setting.png'))
        self.setStyleSheet('border-radius:15px')
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        center=QFrame(self)
        center.resize(self.width(),self.height())
        layout_center=QVBoxLayout(center)
        layout_center.setSpacing(0)
        layout_center.setContentsMargins(0,0,0,0)
        shapes=[
            {'type':11,'shape':1,'color':getcolor(),'last_time':6},
            {'type':21,'shape':3,'color':getcolor(),'last_time':5},
            {'type':31,'shape':1,'color':getcolor(),'last_time':7},
            {'type':41,'shape':2,'color':getcolor(),'last_time':8},
            {'type':12,'shape':1,'color':getcolor(),'last_time':9},
        ]
        label=BlurredLabel(center,shapes)
        banner=CustomBanner(self,'images/setting.png','设置',[1,3])
        layout_center.addWidget(banner)
        self.setCentralWidget(center)

        f1=QFrame()
        f1.setStyleSheet('background:rgba(0,0,0,0)')
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

        layout_blur=QVBoxLayout()
        l1=QLabel('模糊设置')
        cb1=QCheckBox('取消模糊')
        if RwConfig.blopen==2:
            cb1.setChecked(True)
        else:cb1.setChecked(False)
        cb1.stateChanged.connect(lambda state: blur_open(state,RwConfig.blradius))
        layout_blur1=QHBoxLayout()
        l2=QLabel('模糊程度:')
        t1=QLineEdit()
        t1.setText(str(RwConfig.blradius))
        t1.setFixedWidth(40)
        b1=QPushButton()
        b1.setIcon(QIcon('images/warm.png'))
        b1.clicked.connect(lambda:SettingWindow.showtext('数字越大性能开销越大!'))
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
                color=ColorDialog().opendialog()
                if color is not None:
                    self.mwbg.setStyleSheet('background:'+color)
                    self.htbg.setStyleSheet('background:'+color)
                    center.setStyleSheet('background:'+color)
                    b3.setStyleSheet(center.styleSheet()+';border-radius:8px')
            else:
                color=re.findall(Main_ins.find_color,b3.styleSheet())[0]
                rwconfig.wconfig('window','bg_color',color)
        b19=QPushButton()
        b19.setIcon(QIcon('images/warm.png'))
        b19.clicked.connect(lambda:SettingWindow.showtext('背景色的优先级大于主题样式,更改后注意保存'))
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
        def settheme():
            send=self.sender()
            color={'明亮':'white','暗黑':'black','默认':'default'}[send.text()]
            if color=='default':
                self.mwl1.setStyleSheet('color:black')
                self.mwbg.setStyleSheet('background:white')
                center.setStyleSheet('background:white')
                color1='rgba(215,215,215,0.3)'
                color2='rgba(5,5,5,0.5)'
                self.tq.setStyleSheet(f'background:{color1};border-radius:{RwConfig.qradius}px')  
                self.ba.setStyleSheet(f'background:{color1};border-radius:15px;color:{color2}')
            else:
                if color=='white':
                    self.mwl1.setStyleSheet('color:black')
                    self.mwbg.setStyleSheet('background:white')
                    center.setStyleSheet('background:white')
                    self.tq.setStyleSheet(f'background:rgba(255,255,255,0.5);border-radius:{RwConfig.qradius}px')
                    self.ba.setStyleSheet('background:rgba(200,200,200,0.5);border-radius:15px')
                else:
                    self.mwl1.setStyleSheet('color:white')
                    self.mwbg.setStyleSheet('background:black')
                    center.setStyleSheet('background:black')
                    self.tq.setStyleSheet(f'background:rgba(255,255,255,0.5);border-radius:{RwConfig.qradius}px')
                    self.ba.setStyleSheet('background:rgba(255,255,255,0.5);border-radius:15px')
            self.ta.setStyleSheet(self.tq.styleSheet().replace(re.findall(Main_ins.find_radius,self.tq.styleSheet())[0],str(RwConfig.aradius)))
            self.bc.setStyleSheet(self.ba.styleSheet())
            b3.setStyleSheet(center.styleSheet()+';border-radius:8px')
            rwconfig.wconfig('window','theme',color)
        b4=QRadioButton('明亮')
        b4.clicked.connect(settheme)
        b5=QRadioButton('暗黑')
        b5.clicked.connect(settheme)
        b6=QRadioButton('默认')
        b6.clicked.connect(settheme)
        for i in l5,b6,b4,b5:
            if i!=l5:btg1.addButton(i)
            layout_window2.addWidget(i)
        if RwConfig.bgtheme=='default':b6.click()
        elif RwConfig.bgtheme=='white':b4.click()
        else:b5.click()

        def setradius(zone,qt,num):
            try:
                a=int(num)
                style=qt.styleSheet()
                patten=re.findall(Main_ins.find_radius,style)[0]
                style=str(style).replace(patten,num)
                qt.setStyleSheet(style)
                rwconfig.wconfig('window',zone,a)
                if qt==self.tq:RwConfig.qradius=a
                else:RwConfig.aradius=a
            except ValueError:
                messagebox.showmsg('圆角应为整形(int)')
        layout_window3=QHBoxLayout()
        l6=QLabel('输入框圆角:')
        t2=QLineEdit()
        t2.setFixedWidth(40)
        t2.setText(str(RwConfig.qradius))
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
        t3.setText(str(RwConfig.aradius))
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
        t5.setText(str(RwConfig.opacity))
        setopacity(RwConfig.opacity)
        b20=QPushButton()
        b20.setIcon(QIcon('images/tip.png'))
        b20.clicked.connect(lambda:SettingWindow.showtext('数字越小越透明,仅支持0-1'))
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
                for i in Main.ml:
                    i.startAnimation(state,None)
            else:
                for i in Main.ml:
                    i.startAnimation(state,curve)
                    rwconfig.wconfig('dynamic','curve','QEasingCurve.'+str(curve_dict[combobox1.currentText()]))
            rwconfig.wconfig('dynamic','open',state)
        cb2=QCheckBox('关闭动效')
        if RwConfig.dnopen==2:
            cb2.setChecked(True)
        else:cb2.setChecked(False)
        cb2.stateChanged.connect(lambda state:setdynamic(state,eval(RwConfig.dncurve)))
        layout_dynamic1=QHBoxLayout()
        l9=QLabel('运动速度:')
        t4=QLineEdit()
        t4.setFixedWidth(40)
        t4.setText(str(RwConfig.dnspeed))
        def setspeed(num):
            try:
                a=int(num)
                for i in Main.ml:
                    i.animationSpeed(a)
                rwconfig.wconfig('dynamic','speed',a)
            except ValueError:
                messagebox.showmsg('运动速度应为整形(int)')
        b9=QPushButton()
        b9.setIcon(QIcon('images/warm.png'))
        b9.clicked.connect(lambda:SettingWindow.showtext('数字越大运动越慢,建议500-1000'))
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
            if str(value)==RwConfig.dncurve[13:]:
                combobox1.setCurrentText(key)
        b11=QPushButton()
        b11.setIcon(QIcon('images/tip.png'))
        b11.clicked.connect(lambda:SettingWindow.showtext(curve_des[combobox1.currentIndex()]))
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
            if value==RwConfig.interval:combobox2.setCurrentText(key)
        b14=QPushButton()
        b14.setIcon(QIcon('images/save.png'))
        b14.clicked.connect(lambda:setinterval(interval_dict[combobox2.currentText()]))
        for i in l12,combobox2,0,b14:
            if i==0:layout_update1.addStretch()
            else:layout_update1.addWidget(i)

        l13=QLabel('当前版本:'+str(Main_ins.VERSION))
        def setnewversion(qt):
            newversion=checkupdate.getdata()
            if newversion is None:result='检查失败!'
            else:result=str(newversion['version'])
            qt.setText('云端版本:'+result)
        Main_ins.l14=QLabel('云端版本:未知')
        self.version_thread=threading.Thread(target=setnewversion,args=(Main_ins.l14,))
        self.version_thread.start()
        Main_ins.l15=QLabel('检查时间:'+str(RwConfig.lasttime))
        layout_update2=QHBoxLayout()
        for i in l13,Main_ins.l14,Main_ins.l15:
            if i==0:layout_update2.addStretch()
            else:layout_update2.addWidget(i)
        b18=QPushButton('检查更新')
        b18.setMinimumHeight(30)
        b18.setStyleSheet('background:rgba(255,255,255,0.5);border-radius:10px')
        b18.clicked.connect(lambda:SettingWindow.updatethread(self,True,b18,Main_ins))
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
            RwConfig.apikey=key
            banner.reboot()
            
        layout_gemini=QVBoxLayout()
        l17=QLabel('API设置')
        layout_gemini1=QHBoxLayout()
        l18=QLabel('APIKEY:')
        t6=QLineEdit()
        t6.setFixedWidth(275)
        t6.setPlaceholderText('请在此填写您的APIKEY')
        t6.setText(RwConfig.apikey)
        b22=QPushButton()
        b22.setIcon(QIcon('images/warm.png'))
        b22.clicked.connect(lambda:SettingWindow.showtext('保存后将重启程序'))
        b23=QPushButton()
        b23.setIcon(QIcon('images/save.png'))
        b23.clicked.connect(lambda:setapi(t6.text()))
        for i in l18,t6,b22,b23:
            layout_gemini1.addWidget(i)

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

        for i in b1,b2,b7,b8,b9,b10,b11,b12,b13,b14,b19,b20,b21,b22,b23:
            i.setStyleSheet('background:rgba(0,0,0,0)')

        for i in layout_gemini,layout_blur,layout_window,layout_dynamic,layout_update:
            layout_f1.addLayout(i)
        layout_f1.addStretch(1)

        layout_center.addWidget(f1)
        self.mwbg.setStyleSheet('background:'+RwConfig.bgcolor)
        self.htbg.setStyleSheet('background:'+RwConfig.bgcolor)
        center.setStyleSheet('background:'+RwConfig.bgcolor)
        b3.setStyleSheet(center.styleSheet()+';border-radius:8px')
