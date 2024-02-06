import json
import datetime
class RwConfig:
    adminkey=apikey=blopen=blradius=bgcolor=bgtheme=qradius=\
    aradius=opacity=dnopen=dnspeed=dncurve=interval=lasttime=None
    def __init__(self):  
        try:
            from Msgbox import messagebox
            import Main
            with open('config.json') as f:
                Main.config=json.load(f)
                self.rconfig(Main.config)
        except FileNotFoundError:
            messagebox.showmsg('配置文件不存在或路径错误!')
            exit()
        except json.decoder.JSONDecodeError:
            messagebox.showmsg('配置文件不是有效的JSON格式!')
            exit()
        except PermissionError:
            messagebox.showmsg('没有足够权限读取或写入配置文件!')
            exit()
    @classmethod
    def rconfig(cls,config):
        #密钥配置
        cls.adminkey=config['admin']['key']
        #API配置
        cls.apikey=config['gemini']['apikey']
        #模糊配置
        cls.blopen=config['blur']['open']
        cls.blradius=config['blur']['blur_radius']
        #界面配置
        cls.bgcolor=config['window']['bg_color']
        cls.bgtheme=config['window']['theme']
        cls.qradius=config['window']['q_radius']
        cls.aradius=config['window']['a_radius']
        cls.opacity=config['window']['opacity']
        #动效配置
        cls.dnopen=config['dynamic']['open']
        cls.dnspeed=config['dynamic']['speed']
        cls.dncurve=config['dynamic']['curve']
        #更新配置
        cls.interval=config['update']['interval']
        cls.lasttime=datetime.datetime.strptime(config['update']['lasttime'],'%Y-%m-%d %H:%M:%S')
    def wconfig(self,zone,name,value):
        try:
            with open('config.json','w') as f:
                import Main
                Main.config[zone][name]=value
                json.dump(Main.config,f,indent=4)
        except PermissionError:
            from Msgbox import messagebox
            messagebox.showmsg('没有足够权限读取或写入配置文件!')
            exit()

rwconfig=RwConfig()