#coding: utf-8
import requests,re
from bs4 import BeautifulSoup as BS
from time import sleep
from MyPack.MyCrab import MYSITE,crab
__all__ = ['BOOK','Book1']

class BOOK(crab):
    '''
    本模組用來檢查小說網站是否有更新資料
    '''
    def check(self):
        config = self.setConfig()
        aheaders = {'Host':'m.twfanti.com'}
        #aparams = { 'sort':'desc'}
        CW = self.Sec['check word']
        if not crab.Config.has_section(self.secName) :
            self.logging ('\t未定義 {} Config\r\n'.format (self.secName))
            return 2
        #if len(self.Sec['keyword']) > 20:
        url = self.Sec['Href']
        #--end if
        try :
            res = MYSITE (url , headers = aheaders)
            tempD = res.soup.select('span')[1]
            chkD = str(tempD.text.strip())
            if chkD == CW :
                self.logging('\t{0} {1} 未有更新\n'.format(self.Sec['Name'],chkD))
                return 0
            else :
                msg = '{0} 發佈更新 {1}\n'.format(self.Sec['Name'],chkD)
                A = Book1(config)
                A.getChapters()
                bkhref = config['bsurl']+config['sUrl'].format(str(config['startChptr']))
                self.notify('{0} 發佈更新 [{1}]({2})\n#小說更新 #{3}\n'.format(self.Sec['Name'],chkD, bkhref , config['title']))
                self.logging('\t{}'.format(msg))
                self.Sec['check word'] = chkD
                self.Sec['Last Update'] = self.chk_date
        except Exception as e:
            print (e)
            self.logging (str(e))
            self.logging ('\t{}網站連結失敗\r\n'.format(self.secName))
        finally :
            pass
    
    def setConfig (self):
        r = re.compile('[0-9]{1,5}')
        m = r.search(self.Sec['check word'])
        config = {'title':self.Sec['Name'],
                'saveto':self.Sec['saveto'],
                'startChptr':(int (m.group(0))+ 1 ) if m is not None else 0,
                'bsurl':self.Sec['bsurl'],
                'sUrl':self.Sec['sUrl'],
                'soup select':self.Sec['soup select'],
                'multi pages':self.ckBool('multi pages')}
        return config

class Book1():
    from platform import platform
    plat =  platform()
    '''
    本模組用來抓取小說內文
    '''
    def __init__(self,config):
        self.title = config['title']
        self.startChptr = config['startChptr']
        self.saveto = config['saveto']
        self.bsurl = config['bsurl']
        self.sUrl = config['sUrl']
        self.sl = config['soup select']
        self.mpage=config['multi pages']
        self._p1 = re.compile('/read_[0-9]{1,5}_?p?[0-9]?.html$')

    def getContents(self,url):
        res = requests.get (url)
        soup = BS(res.text,'html.parser')
        a = soup.select(self.sl)
        nexturl = self.bsurl+a[0]['href']
        cts = soup.select('div#pt-pop p')
        contents = soup.select('body div div')[0].text + '\n'
        for ct in cts:
            if ('節內容不對' not in ct.text) :
                contents += '{}\n'.format(ct.text.split('本章未完')[0])
        contents += '\n'
        return contents,nexturl

    def _getChapters(self,startChptr):
        if startChptr == 0 :
            return 1
        if startChptr%100 < 51:
            endChapter = int (startChptr/100)*100+50
        else :
            endChapter = int (startChptr/100)*100+100
        starturl = self.bsurl+self.sUrl.format(str(startChptr))
        stopCharpter = '第{}章'.format(str(endChapter))
        _fn = self.saveto + '{}-{}.txt'.format(self.title,str(endChapter-49))
        fn = ('/volume1' if  'Linux' in Book1.plat else '') + _fn 
        url = starturl
        last = False
        with open(fn ,'a+',encoding='utf8') as f :
            while last == False:
                contents ,nexturl = self.getContents(url)
                f.writelines(contents)
                if self._p1.search(nexturl) is None:
                    #已到目錄
                    last = True
                    break
                if stopCharpter in contents:
                    if self.mpage :
                        contents ,nexturl = self.getContents(nexturl)
                        f.writelines(contents)        
                        url = nexturl
                    break
                url = nexturl
        if last == True :
            return 1
        else :
            self.startChptr = endChapter + 1
            return 0

    def getChapters(self):
        while self._getChapters(self.startChptr) == 0:
            pass