#coding: utf-8 
import requests
from MyPack.MyCrab import MYSITE
from MyPack.MyCrab import crab
__all__ = ['Crab_D']

class Crab_D (crab):
    def check(self): 
        '''
        return 0 : 程式正常完成
        return 1 : 網站服務異常
        return 2 : Config 未設定
        Config 參數如下
            Url : 爬取網址
            update date : 資料更新日期
            version : 資料版本
            S_Link : 轉址位址
            Site Status : 上次檢測時網站狀態
        '''
        if not crab.Config.has_section(self.secName):
            self.logging ('\t未定義 {} Config\r\n'.format (self.secName))
            return 2
        temp_hd = {\
                   'Accept':'text/html,application/xhtml;q=0.9,image/webp,*/*;q=0.8' , \
                   'Accept-Encoding':'gzip, deflate' ,\
                   'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3' ,\
                   'Connection':'keep-alive' ,\
                   'Cookie':'ASPSESSIONIDSCQSTABC=LIFMIBDAKCPBIMNMLEMMPHHB' ,\
                   "Host":'www.ucppweb.com' ,\
                   'Upgrade-Insecure-Requests':'1' ,\
                   'User-Agent':'Mozilla/5.0 (Windows NT 10.0; ) Gecko/20100101 Firefox/65.0' \
                  }
        #===============程式起始==============================================
        status = self.Sec['Site Status']
        try :
            with MYSITE (self.Sec['Url']) as DD :
                ver = DD.soup.select('table#ProceM1_dalist1_ctl00_dalist2 tr td tr td')[1].text
    #            update_date = DD.soup.select('table#ProceM1_dalist1_ctl00_dalist2 tr td tr td')[3].text
                tempURL = DD.soup.select('table#ProceM1_dalist1_ctl00_dalist2 tr td tr td a')[0]['href']
            with requests.get (tempURL , headers = temp_hd , allow_redirects = False ,timeout = 10 ) as temp_res:
                S_Link = str (temp_res.headers['Location'])
            self.Sec['Site Status'] = 'OK'
        except :
            self.Sec['Site Status'] = 'Error'
        finally :
            if self.Sec['Site Status'] == 'Error' :
                self.logging ('\t{}網站服務異常\r\n'.format (self.secName))
                if status == 'OK' :
                    self.notify ('{} 網站服務異常'.format(self.secName))
                return 1
            else :
                if status == 'Error':
                    self.logging ('\t{}網站服務恢復\r\n'.format (self.secName))
                    self.notify ('{} 網站服務恢復'.format(self.secName))
                DocName = ver
                update_in_DB = self.Sec['update date']
                Doc_in_DB = self.Sec['version']
                link_in_DB = self.Sec['S_Link']
                if S_Link == link_in_DB :
                    self.logging ('\t自 {} 後，大D沒有更新\r\n'.format (update_in_DB))
                else :
                    if Doc_in_DB == DocName :
                        tempDoc = '子版大D'
                    else :
                        tempDoc = DocName
                    self.Sec['update date'] = self.chk_date
                    self.Sec['version']     = DocName
                    self.Sec['S_Link']      = S_Link
                    msgtxt = '{} 發佈'.format (tempDoc)
                    self.logging ('\t{}\r\n'.format(msgtxt))
                    self.notify (msgtxt)
                return 0
