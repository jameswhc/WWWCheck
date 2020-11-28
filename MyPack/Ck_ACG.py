#coding: utf-8
from time import sleep
from MyPack.MyCrab import MYSITE,crab
__all__ = ['ACG']

class ACG(crab):
    def check(self):
        aheaders = { 'Cookie': '__cfduid=daf56fbfbdd23f35e5d37891a102af8c11548041550; Hm_lvt_dfa59ae97c988b755b7dfc45bbf122ae=1569204591,1569206478; ftwwwacgsoucom=1; Hm_lpvt_dfa59ae97c988b755b7dfc45bbf122ae=1569206486'
                    ,'Host': 'www.36dm.club'
                    ,'Upgrade-Insecure-Requests': '1'
                    }
        aparams = { 'bound' : 'content'
                   ,'local' : '1'
                   ,'keyword': ''
                   ,'sort_id': '0'
                   ,'field' :'title'
                   ,'node_id' : '0'
                   ,'external' : 'google'
                   }
        CW = 'table#listTable tr.alt1 td'
        url = 'https://www.36dm.club/'
        if not crab.Config.has_section(self.secName) :
            self.logging ('\t未定義 {} Config\r\n'.format (self.secName))
            return 2
        #if len(self.Sec['keyword']) > 20:
        url = url+'search.php'
        aparams.clear()
        sleep(15)
        #--end if
        aparams['keyword']=self.Sec['keyword']
        Last_Update = self.Sec['Last Update']
        try :
            res = MYSITE (url , headers = aheaders ,params = aparams)
            tempD = res.soup.select(CW)[0]
            chkD = str(tempD.text)
            if chkD == Last_Update :
                self.logging('\t自{0}後，{1} 未有更新\n'.format(chkD,self.Sec['Name']))
                return 0
            else :
                msg = '{0} 於 {1} 發佈更新\n'.format(self.Sec['Name'],chkD)
                self.Sec['Last Update'] = chkD 
                self.notify(msg+'\n#影片發佈\n')
                self.logging('\t{}'.format(msg))
        except Exception as e:
            self.logging ('\t{}網站連結失敗\r\n'.format(self.secName))
        finally :
            pass

