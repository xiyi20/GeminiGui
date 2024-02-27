from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel,QGraphicsBlurEffect

class BlurredLabel(QLabel):
    def __init__(self,parent=None,items=[]):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet('background:rgba(0,0,0,0)')
        self.setGeometry(0,0,parent.width(),parent.height())
        ml=[]
        for item in items:
            type=item.get('type',11)
            color=item.get('color','red')
            last_time=item.get('last_time',3)
            shape=item.get('shape',1)
            from Movelabel import MoveLabel
            ml.append(MoveLabel(self,type=type,color=color,last_time=last_time,shape=shape))
        import Main
        Main.ml.append(ml)
        from Rwconfig import rwconfig
        self.blur(rwconfig.blopen,rwconfig.blradius)
    def blur(self,state,num):
        if state==0:
            blur_effect=QGraphicsBlurEffect()
            blur_effect.setBlurRadius(num)
            self.setGraphicsEffect(blur_effect)
        else:
            self.setGraphicsEffect(None)