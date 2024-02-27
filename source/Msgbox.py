import sys
import PIL.Image
import webbrowser
from PyQt6.QtGui import QIcon,QImage
from PyQt6.QtCore import Qt,QObject,pyqtSignal,pyqtSlot
from PyQt6.QtWidgets import QMessageBox,QInputDialog,QFileDialog

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
                from Rwconfig import rwconfig
                rwconfig.wconfig('gemini','apikey',api)
                rwconfig.apikey=api
            else:sys.exit()
        if mode=='file':
            from Mainwindow import MainWindow
            MainWindow.image,_=QFileDialog.getOpenFileName(None, "选择图片", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
            if MainWindow.image:
                MainWindow.img_a=PIL.Image.open(MainWindow.image)
                MainWindow.img_t=QImage(MainWindow.image)
                MainWindow.img_t=MainWindow.img_t.scaled(int(MainWindow.img_t.width()/10),int(MainWindow.img_t.height()/10), 
                                                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio
                                                ,transformMode=Qt.TransformationMode.SmoothTransformation) 
                MainWindow.checkimg(MainWindow.link)
    def onAccepted(self,url,open):
        if open:webbrowser.open(url)

messagebox=MessageBox()