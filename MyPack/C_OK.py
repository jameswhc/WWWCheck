#coding: utf-8
import requests , os 
from configparser import ConfigParser
from threading import Thread ,RLock
from bs4 import BeautifulSoup as BS
from MyPack.MyCrab import crab, MYSITE , MyLog
from MyPack.MyDSM import MyDownloadStation as MyDS
__all__ = ['DPLfile','Crab_OK']

class DPLfile():
    import re
    tpl= '{}*file*{}\n'
    tpr= re.compile('[0-9]{1,3}\*file\*')
    tphead =[   'DAUMPLAYLIST\n',
                'playname=\n',
                'playtime=0\n',
                'topindex=0\n',
                'saveplaypos=0\n'
            ]

    def __init__(self,Filename):
        self.Filename = Filename
        self.f = open (Filename,'a+',encoding='utf-8')
        self.f.close()
        self.f = open (self.Filename,'r+',encoding='utf-8')
        self.f.seek(0,0)
        self.lines = self.f.readlines()
        if (lambda x : True if x==[] else ('DAUMPLAYLIST' not in x[0]))(self.lines):
            self.f.seek(0,0)
            self.f.truncate(0)
            self.f.writelines(DPLfile.tphead)
            self.lines = DPLfile.tphead
    
    def isexist(self,_link):
        A = list( filter( lambda x: _link in x , self.lines ) )
        return True if A != [] else False

    def getlast (self):
        B = list(filter(lambda x:DPLfile.tpr.match(x)is not None, self.lines))
        return  B[-1] if B != [] else []
    
    def append (self,Link):
        A = self.getlast()
        self.f.seek(0,2)
        _L = DPLfile.tpl.format((int(A.split('*')[0]) if A != [] else 0) + 1,Link)
        self.f.writelines(_L)
        self.lines.append(_L)
        
    def bypass(self):
        pass
    
    def toTXT(self):
        p ,n = os.path.splitext(self.Filename)
        n = '.txt'
        _links = list(filter(lambda x: DPLfile.tpr.match(x) is not None , self.lines))
        links = [x.split('*')[-1] for x in _links]
        with open (p+n,'w',encoding='utf-8') as t :
            t.writelines(links)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.f.close()
        self.f = None
        self.lines.clear()
        self.lines = None

class Crab_OK (crab):
    __headers  = {\
               'Accept':'text/html,application/xhtml;q=0.9,image/webp,*/*;q=0.8' , \
               'Accept-Encoding':'gzip, deflate' ,\
               'Accept-Language':'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3' ,\
               'Connection':'keep-alive' ,\
               'User-Agent':'Mozilla/5.0 (Windows NT 10.0; ) Gecko/20100101 Firefox/65.0' \
                }
    @property
    def GenTXT(self):
        return self.ckBool('Generate TXT')

    @GenTXT.setter
    def GenTXT(self,value):
        if value in ['yes','no','True','False']:
            try :
                self.secName['Generate TXT'] = value
            except :
                crab.Config.set(self.secName,'Generate TXT','False')
    @property
    def url (self):
        return 'https://{}/?m={}'.format(self.Sec['Site'],self.Sec['Page'])

    def check(self):
        ''' 
        return 0 : 網站服務正常
        return 1 : 網站服務異常
        return 2 : Config 未設定
        Config 參數如下
            Site : 網站
            Page : 網頁
            Name : 名稱
            Crab word : 解析字詞
            check word : 檢測字詞
            Last Update : 上次更新日期
            Last Uri : 前次的下載網址
            Generate TXT : 產生link文字檔
            DL Path : 下載影片檔的路徑
        '''
        if not crab.Config.has_section(self.secName) :
            self.logging ('\t未定義 {} Config\r\n'.format (self.secName))
            return 2
        
        res = MYSITE(self.url)
        ep = res.soup.select('div.vodh span')[0].text
        if self.Sec['keyword'] not in res.soup.select('div.vodh h2')[0].text:
            self.logging("{}\t找不到資源\n".format(self.chk_date))
            return 0
        if ep == self.Sec['check word']:
            self.logging("\t{},沒有更新\n".format(self.Sec['Name']))
            return 0
        _uris = [ x['value'] for x in res.soup.select(self.Sec['Crab word']) ]
        '''
        _uris = list (map(lambda x: x['value'] , res.soup.select(self.Sec['Crab word'])))
        將元素(x)的特定值('value')輸出重新組成(map(express,iterator))新的列表(list())
        * map()的輸出是疊代器(iterator)
        '''
        _indexNew = (_uris.index(self.Sec['Last Uri'])+1) if self.Sec['Last Uri'] in _uris else 0
        if _indexNew < (len(_uris)) :
            with DPLfile(self.Sec['destination']) as DPL:
                def appendx(x):
                    crab.lock.acquire()
                    DPL.append(x)
                    _DPL = DPLfile(crab.Config['LOG']['OK Log File'].format(self.chk_date.split('(')[0]))
                    _DPL.append(x)
                    del _DPL
                    crab.lock.release()
                list( map (lambda x : appendx(x) if not DPL.isexist(x) else DPL.bypass() ,_uris[_indexNew:])) 
                '''
                如果檔案中不存在x連結(not DPL.isexist(x))就新增連結(DPL.append(x))，否則略過(DPL.bypass())
                DPL.append(x) if not DPL.isexist(x) else DPL.bypass()
                * lambda 組成的函式，可以立刻輸入參數執行 (lambda : param1,param2.. : express(param1,param2..))(input1,input2..)
                '''
                if self.GenTXT :
                    DPL.toTXT()
                    self.GenTXT = 'no'
            msg = '{},已增加連結'.format(self.Sec['Name'])
            msgs = ['[新連結{}]({})'.format(i+1,x) for (i,x) in enumerate(_uris[_indexNew : ])]
            self.Sec['check word'] = ep     
            self.Sec['Last Update'] = self.chk_date
            self.Sec['Last Uri'] = _uris[-1]
            self.logging ('\t'+msg+'\n')
            self.notify(msg)
            [self.notify(x) for x in msgs] if self.ShowLink else None
            if 'DL Path' in [x for x in self.Sec.keys()]:
            #if crab.Config.has_option(self.secName,'DL Path'):
                if self.Sec['DL Path'] != '':
                    with MyDS() as MDS:
                        MDS.CONNECT(crab.dsm)
                        [MDS.AddTask(uri=x,des=self.Sec['DL Path']) for x in _uris[_indexNew :]]
        else :
            self.logging("\t{}沒有更新\n".format(self.Sec['Name']))
        return 0
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++《，
