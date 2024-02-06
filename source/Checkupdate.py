import datetime
import requests
from functools import partial


class CheckUpdate:
    def check(self,skip=False,qt=None,Main_ins=None):
        from Rwconfig import RwConfig
        if skip:
            self.checkUpdate(qt,Main_ins)
            return
        a=datetime.datetime.now()
        b=RwConfig.lasttime+datetime.timedelta(days=int(RwConfig.interval))
        if a<b:return
        self.checkUpdate(qt,Main_ins)
    def checkUpdate(self,qt=None,Main_ins=None):
        from Msgbox import messagebox
        try:
            data=self.get_data()
            if data is None:return
            new_version=data["version"]
            if Main_ins.VERSION<new_version:
                    messagebox.connectshow(partial(messagebox.showmsg,'当前版本:'+str(Main_ins.VERSION)
                                                    +'\n云端版本:'+str(new_version)+'\n更新说明:'+data["desc"]
                                                    +'\n更新地址:'+data["url"]+'\n点击OK将跳转下载','检测到更新'
                                                    ,'QMessageBox.Icon.Information',data["url"],True,qt))
            else:
                messagebox.connectshow(partial(messagebox.showmsg,'当前已是最新版本!\n'+str(new_version)
                                                +'更新日志:\n'+data["desc"],'通知','QMessageBox.Icon.Information',qt=qt))
            from Rwconfig import rwconfig
            rwconfig.wconfig('update','lasttime',datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            from Main import config
            lasttime=config['update']['lasttime']
            Main_ins.l14.setText('云端版本:'+str(new_version))
            Main_ins.l15.setText('检查时间:'+lasttime)
        except Exception as e:
            print(e)
            messagebox.connectshow(partial(messagebox.showmsg,f'原因:\n{type(e).__name__}:{e}','检查更新失败','QMessageBox.Icon.Warning',qt=qt))
        messagebox.messageSignal.emit('signal')
    def get_data(self):
        from Msgbox import messagebox
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