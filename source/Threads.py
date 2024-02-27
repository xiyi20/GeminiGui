from PyQt6.QtCore import QThread,pyqtSignal
from functools import partial

class ImgThread(QThread):
    imgsignal=pyqtSignal(str)
    def run(self):
        from Mainwindow import MainWindow
        from Msgbox import messagebox
        if MainWindow.img_a is not None:
            MainWindow.img_a=None
            MainWindow.checkimg(MainWindow.link)
            return
        messagebox.connectshow(partial(messagebox.showdialog,'file'))
        messagebox.messageSignal.emit('signal')
        
class AnswerThread(QThread):
    def __init__(self,MainWindow_ins):
        super().__init__()
        self.MainWindow_ins=MainWindow_ins
    def run(self):
        from Mainwindow import MainWindow
        question=self.MainWindow_ins.question
        t1=self.MainWindow_ins.t1
        code=self.MainWindow_ins.code
        question=t1.toPlainText()
        self.MainWindow_ins.answersignal.emit(2,'请等待回答...')
        MainWindow.setenable(self.MainWindow_ins,False)
        if MainWindow.img_a is not None:
            if question!='':question+=',语言请用简体中文'
            question_text=question
            self.MainWindow_ins.answersignal.emit(1,'我:\n')
            self.MainWindow_ins.answersignal.emit(3,'signal')
            self.MainWindow_ins.answersignal.emit(1,question_text)
        else:
            if (self.MainWindow_ins.state is None)and(question!=''):
                question+=',语言请用简体中文'
                self.MainWindow_ins.state=1
            question_text='我:\n'+question
            self.MainWindow_ins.answersignal.emit(1,question_text)
        keywords=['网页','博客','文章','帖子','Wiki','文档','教程','手册','报告','百科','简历',
                      '电子书','演讲稿','课件','规范','合同','论文','文章','新闻','计划','指南','说明',
                      '分析','笔记','词典','诗歌','小说','剧本','攻略','日志','论文','新闻','公告']
        if MainWindow.img_a is None:
            code=1
            for i in keywords:
                if i in question:
                    code=0
                    break
            answer=self.MainWindow_ins.gemini.get_content(code,question)
            answer_text='Gemini:\n'+answer+'\n'
            if code==0:self.MainWindow_ins.answersignal.emit(0,'<br>'+answer_text)
        else:
            answer=self.MainWindow_ins.gemini_visual.get_content(None,question,MainWindow.img_a)
            answer_text='Gemini:\n'+answer+'\n'
            MainWindow.img_a=None
        self.MainWindow_ins.answersignal.emit(1,answer_text)
        self.MainWindow_ins.clearsignal.emit('signal')
        MainWindow.checkimg(MainWindow.link)
        MainWindow.setenable(self.MainWindow_ins,True)
        
class UpdateThread(QThread):
    def __init__(self,skip=False,qt=None,Main_ins=None):
        super().__init__()
        self.skip=skip
        self.qt=qt
        self.Main_ins=Main_ins
    def run(self):
        from Checkupdate import checkupdate
        if self.qt is not None:
            self.qt.setText('正在检查...')
            self.qt.setEnabled(False)
        checkupdate.check(self.skip,self.qt,self.Main_ins)

class VersionThread(QThread):
    def __init__(self,l14):
        super().__init__()
        self.l14=l14
    def run(self):
        from Checkupdate import checkupdate
        newversion=checkupdate.getdata()
        if newversion is None:result='检查失败!'
        else:result=str(newversion['version'])
        self.l14.setText('云端版本:'+result)
        