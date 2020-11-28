#coding: utf-8
'''
本模組用來爬取網站資料
class MyConfig : 用來存取 .ini 檔
class MyCrypt : 用來加解密字串
class MYSITE : 用來解析一個網站
class MyLog  : 用來填寫執行中的紀錄
class Telegram : 可用來發訊Telegram Bot訊息
class crab   :基礎的爬取類別,可以多執行緒方式爬取
function LINE_notify :用LINE Notify來發送訊息
function send_email  :用E-mail來發送訊息
'''
import requests , threading , smtplib
from platform import platform
from functools import reduce
from base64 import b64encode as ENCRYP
from base64 import b64decode as DECRYP
from configparser import ConfigParser as CP
from datetime import datetime
from bs4 import BeautifulSoup
from email.mime.text import MIMEText

__all__ = ['MyCrypt','MYSITE','MyLog','crab','Telegram','LINE_notify','send_email','MyConfig']

class MyConfig ():
    def __init__(self,_filename):
        self._filename = _filename
        self.Config = CP(allow_no_value=True)
        self.Config.optionxform = str
        self.Config.read(_filename,encoding='utf-8')

    @property
    def Sections(self):
        return [x for x in self.Config.sections()]

    def ckBool (self,option,Sec):
        try :
            return self.Config.getboolean(Sec , option)
        except :
            return False
    
    def Options(self,_Sec):
        return [x for x in self.Config[_Sec].keys()] if self.Config.has_section(_Sec) else None

    def __del__(self):
        self.Config.write(open (self._filename,'w+',encoding='utf-8'))

class MyCrypt ():
    def __init__ (self,key = ''):
        if key == '' :
            self.__key = ''
            self.__eValue = ''
        else:
            self.__key = key
            self.__eValue = ENCRYP(ENCRYP(self.__key.encode())).decode()

    @property
    def eValue(self):
        return self.__eValue

    @property
    def Value(self):
        return self.__key

    @Value.setter
    def Value(self,key):
        self.__key = key
        self.__eValue = ENCRYP(ENCRYP(self.__key.encode())).decode()

    def encrypt (self,key = ''):
        if (key != '' ):
            self.__key = key
            self.__eValue = ENCRYP(ENCRYP(self.__key.encode())).decode() 
        return self.__eValue

    def decrypt (self,dkey = ''):
        if dkey != '' : 
            self.__eValue = dkey               
            self.__key = str(DECRYP(DECRYP(dkey.encode())).decode())
        return self.__key

class MYSITE ():
    __headers  = {\
               'Accept':'text/html,application/xhtml;q=0.9,image/webp,*/*;q=0.8' , \
               'Accept-Encoding':'gzip, deflate' ,\
               'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3' ,\
               'Connection':'keep-alive' ,\
               'User-Agent':'Mozilla/5.0 (Windows NT 10.0; ) Gecko/20100101 Firefox/65.0' \
                }
    def __init__(self,siteurl,encoding = 'utf-8',headers = None , params = None):
        self.session = requests.session()
        self.headers = MYSITE.__headers.copy()
        if headers != None :
            self.headers.update(headers)
        if siteurl != '':
            self.url = siteurl
            self.ressite = self.session.get(self.url,headers = self.headers, params = params,timeout = 15)
            self.ressite.encoding = encoding
            self.get_soup()
    def get_soup(self):
        self.soup = BeautifulSoup(self.ressite.text,'html.parser')
        return self.soup
    def set_encoding (self,encoding) :
        self.ressite.encoding = encoding
        self.get_soup()
    def get (self,siteurl,headers = None,params = None) :
        if headers == None :
            headers = self.headers.copy()
        if siteurl != '':
            self.url = siteurl
            self.ressite = self.session.get(self.url, headers = headers, params = params, timeout = 15)
            self.get_soup()
    def __enter__(self) :
        return self
    def __exit__(self, exc_ty, exc_val, tb) :
        try :
            self.session.close()
        except :
            pass
    def __del__(self):
        try :
            self.session.close()
        except :
            pass

class MyLog ():
    def __init__ (self,Log = '',writable = True):
        self._log = []
        self.writable = writable
        if Log != '' :
            self.Log = Log
    @property
    def Log(self):
        return self._log
    @Log.setter
    def Log(self,tmplog):
        self._log = self._log + (tmplog if type(tmplog) is list else [tmplog,])

    def logging (self,msg):
        self.Log = msg

    def PrintLog (self):
        if len(self.Log) > 0:
            for l in self.Log :
                print (l)
            self._log.clear()

    def append (self,msg):
        self.Log = msg

    def WriteLog (self,LogFile):
        if self.writable :
            if len(self.Log) > 0 :
                try :
                    with open (LogFile,'a',encoding = 'utf-8') as l:
                        l.writelines(self.Log)
                except Exception as e :
                    print (u'{}無法開啟或寫入Log檔'.format(e))
        else :
            print (self.Log)

    def notify (self,token,chat_id = '',p_mode = 'Markdown'):
        if len(self.Log) > 0 :
            msgtxt = reduce (lambda x,y: x+y , self.Log)
            #msgtxt = ''
            #for msg in self.Log:
            #    msgtxt = msgtxt + msg
            if chat_id == '':
                LINE_notify(token,msgtxt)
            else :
                T = Telegram(token)
                for cid in chat_id.split(','):
                    if cid != '':
                        T.chat_id = cid
                        T.notify(msgtxt,p_mode = p_mode)

    def clear (self):
        self._log.clear()

    def __del__ (self):
        self._log.clear()

class crab (threading.Thread):
    dsun = MyCrypt()
    dspw = MyCrypt()
    count = 0
    plat_Linux = True
    Config = None
    lock = None
    LOG = None
    MSG = None
    Logging = True
    DBFile = ''
    dsm = {}

    @property
    def ShowLink(self):
        return self.ckBool('Show Link','Notify')

    def __init__ (self,_Config = None,secName = ''):
        '''
        Config : 傳入設定物件
        secName : 傳入要使用的區塊
        通用區塊 [Notify] :
            Notify : yes / no 設定是否要通知
            Token : 指定使用的 token
        通用區塊 [LOG]
            Logging : yes / no 設定是否要寫入 log
            Log File : 指定要寫入的 LOG 檔
            GG Log File : 指定檢測 Game Guard 時用的 LOG 檔(不論Logging的值為何)
        '''
        super(crab,self).__init__()
        crab.count += 1
        self.chk_date = ''
        self.secName = secName
        if crab.count == 1 :
            crab.plat_Linux = False if 'Windows' in platform() else True
            #crab.dsm.update(crab.__dsms['Linux'] if crab.plat_Linux else crab.__dsms['Windows'])
            crab.lock = threading.Lock()
            crab.Config = _Config.Config
            self.SetConfigFile(_Config)
            cDSM = crab.Config['DSM']
            if cDSM.getboolean('encrypt') :
                crab.dsun.decrypt(cDSM['username'])
                crab.dspw.decrypt(cDSM['password'])
            else :
                crab.dsun.Value = cDSM['username']
                crab.dspw.Value = cDSM['password']
                crab.Config['DSM']['username']=crab.dsun.eValue
                crab.Config['DSM']['password']=crab.dspw.eValue
                crab.Config['DSM']['encrypt']='True'
            crab.dsm.update({   'host':cDSM['ip'],
                                'port':cDSM['port'],
                                'https': cDSM.getboolean('https'),
                                'username':crab.dsun.Value,
                                'password':crab.dspw.Value})
        self.Sec = crab.Config[self.secName]
    def SetConfigFile(self,__Config):
        if __Config is not None:
            try :
                crab.Logging = __Config.ckBool('Logging','LOG')
                crab.LOG = MyLog(writable = crab.Logging)
                crab.MSG = MyLog(writable = False)
                crab.DBFile = __Config.Config['LOG']['SQLITE File']
                self.logging ('{}\r\n'.format (datetime.now().strftime('%Y-%m-%d(%w)T%H:%MZ' )))
                self.Sec = __Config.Config[self.secName]
                return True
            except Exception as e:
                print (e)
                crab.Logging = True
                crab.DBFile = ''
                crab.LOG.Log.clear()
                self.logging ('\tConfig ,參數設定錯誤,無法設定 Config 檔\r\n')
                return False

    def run (self):
        try :
            self.chk_date = datetime.now().strftime('%Y-%m-%d(%w)T%H:%MZ')
            if crab.Config is not None:
                self.check()
        except Exception as e:
            self.logging('\tCheck {} 錯誤 ------ \r\n\t\t{}\r\n'.format(self.secName,e))

    def check(self):
        pass

    def ckBool (self,option,Sec = ''):
        try :
            return crab.Config.getboolean(self.secName if Sec == '' else Sec , option) 
        except :
            return False

    def logging (self,msg):
        crab.lock.acquire()
        crab.LOG.logging(msg)
        crab.lock.release()

    def notify (self, msg):
        crab.MSG.logging('{}\n'.format(msg))
        
    def _notify (self):
        if self.has_option ('Notify','Notify'):
            if 'Teleg' in crab.Config['Notify']['Notify']:
                chat_ids = crab.Config['Notify']['Teleg Chat ID']
                for chat_id in chat_ids.split(','):
                    if chat_id != '':
                        token   = crab.Config['Notify']['Teleg Token']
                        crab.MSG.notify (token , chat_id)
            if 'Line' in chat_ids.split(','):
                token = crab.Config['Notify']['Line Token']
                if token != '':
                    crab.MSG.notify (token)
        else :
            print ('[Notify][Notify]不存在於ini檔')

    def has_option(self, _Sec, _Option):
        return True if crab.Config.has_option(_Sec,_Option) else False

    def has_section(self, _Sec):
        return True if crab.Config.has_section(_Sec) else False

    def __del__ (self) :
        crab.count -= 1
        if crab.count == 0 :
            crab.LOG.WriteLog(crab.Config['LOG']['Log File'])
            if crab.MSG.Log != [] :
                self._notify()

    def close (self):
        pass
    def __enter__ (self) :
        return self
    def __exit__(self, exc_ty, exc_val, tb) :
        pass

class Telegram():
    '''
    發送 Telegram 訊息
    token 是發行權杖
    chat_id 是要發送的聊天室id
    '''
    def __init__(self,token,chat_id = ''):
        self.token = token
        self.chat_id = chat_id
        
    @property 
    def token (self):
        return self.__token
    
    @token.setter
    def token (self,val):
        self.__token = val
        self.url = 'https://api.telegram.org/bot{}'.format(val)

    @property 
    def chat_id (self):
        return self.__chat_id
    @chat_id.setter
    def chat_id (self,val):
        self.__chat_id = val
        
    def getUpdate(self):
        url = self.url+'/getUpdates'
        a = requests.get(url).json()
        if a['ok']==True:
            results = a['result']
            d = []
            for r in results:
                id = r['message']['from']['id']
                dt = r['message']['date']
                txt = r['message']['text']
                if txt != '/help':
                    #print (str(int(time.time())))
                    d.append([dt,id,txt])
                    #self.chat_id = id
                    #self.notify(u'請輸入指令,謝謝')
            return d
        pass
    def notify(self, msg,disable_web_page_preview = True , disable_notification = False ,p_mode = 'Markdown'):
        '''
        發送 Telegram 訊息
        msg 是要發送的訊息
        disable_web_page_preview True=關閉網頁預覽
        disable_notification True=不發送通知
        p_mode in ['Markdown' , 'HTML']
        return  : 400 網頁服務正常
                : 200 網頁服務異常
                : 1   程式錯誤
        '''
        url = self.url+'/sendMessage'
        payload = {'chat_id': '{0}'.format (self.chat_id) ,
                   'text'   : '{0}'.format (msg),
                   'parse_mode' : p_mode,
                   'disable_web_page_preview' : disable_web_page_preview ,
                   'disable_notification' : disable_notification}
        try :
            with requests.post(url, data = payload,timeout = 15) as r:
                res = r.status_code
            return res
        except Exception as e:
            print (e)
            return 1
       
def LINE_notify (token, msg):
    '''
    發送 Line Notify 訊息
    token 是發行權杖
    msg 是要發送的訊息
    return  : 400 網頁服務正常
            : 200 網頁服務異常
            : 1   程式錯誤
    '''
    url = "https://notify-api.line.me/api/notify"
    headers = {
                "Authorization": "Bearer {}".format(token), 
                "Content-Type" : "application/x-www-form-urlencoded"
              }
        
    payload = {'message': msg}
    try :
        with requests.post(url, headers = headers, params = payload,timeout = 15) as r:
            res = r.status_code
        return res
    except :
        return 1

def send_email(user, pwd, recipient, subject, body):
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['From']     = user
    msg['To']       = recipient
    msg['Subject']  = subject
    try:
    #server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd) 
        server.sendmail(user, recipient, msg.as_string())
    except:
        print ('failed to send mail')
    finally :
        server.close()
