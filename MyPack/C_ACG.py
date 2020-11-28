#coding: utf-8
from MyPack.MyDSM import MyDownloadStation as MyDS
from MyPack.MyCrab import MYSITE
from MyPack.MyCrab import crab
from MyPack.MyDB import CrabDB as HQCDB
from time import sleep
import requests
import os
__all__ = ['Crab_ACG']

class Crab_ACG(crab):
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
            Crab raw : 解析欄位 (table 使用;否則為 0)
            Section Left Delimiter : 左邊界字元
            Section Right Delimiter : 右邊界字元
            check Section : 檢核區塊
            check word : 檢測字詞
            Last Update : 上次更新日期
            Site Status : 上次檢測狀態
            Last Uri : 前次的下載網址
            DL ID : 下載工作ID
            DL Status : 下載狀態
        '''
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
        if not crab.Config.has_section(self.secName) :
            self.logging ('\t未定義 {} Config\r\n'.format (self.secName))
            return 2
    #    url = Config.get (secName,'Url')
        urla = 'https://{}/'.format(self.Sec['Site'])
        #if len(self.Sec['keyword']) >20 :
        urla = urla+'search.php'
        aparams.clear()
        sleep (15)
        #---end if
        aparams['keyword']=self.Sec['keyword']
        status = self.Sec['Site Status']
        try :
            res = MYSITE (urla , headers = aheaders ,params = aparams)
#            res.get(urla,headers = self.headers ,params = self.params) 
            tempD = res.soup.select (self.Sec['Crab word'])[self.Sec.getint('Crab raw')]
            chkD = str(tempD.text)
            uri = self.Sec['Last Uri']
            self.Sec['Site Status'] = 'OK'
        except Exception as e:
            self.logging ('\t{}網站連結失敗\r\n'.format(self.secName))
            self.Sec['Site Status'] = 'Error'
        finally :
            chkName = self.Sec['Name']
            if self.Sec['Site Status'] == 'Error' :
            #若網站服務異常
#                if status == 'OK' :
                #若上次檢查時是好的
                msgtxt = '{}網站服務異常'.format(self.secName)
                self.logging ('\t{}\r\n'.format(msgtxt))
#                    self.notify (msgtxt)
                del res
                return 1
            else :
            #網站服務正常
                if status == 'Error':
                #若上次檢查時是異常
                    msgtxt = '{}網站服務恢復'.format(self.secName)
                    #列印日誌
                    self.logging ('\t{}\r\n'.format(msgtxt))
#                    self.notify (msgtxt)
                SLD = self.Sec['Section Left Delimiter']
                SRD = self.Sec['Section Right Delimiter']
                tempDD = chkD.split(SLD)[self.Sec.getint('check Section')]
                DD = '{}{}{}'.format(SLD,tempDD.split(SRD)[0],SRD)
                keyVal = self.Sec['check word']
                LastUpdate = self.Sec['Last Update']
                with MyDS() as MDS:
                    MDS.CONNECT(crab.dsm)
                    if keyVal == DD :
                    #無更新
                        if self.Sec['DL Status'] == 'downloading' :
                        #上次仍在下載中
                            if MDS.SID != '' :
                            #Download Station 己連上
                                TK_id = self.Sec['DL ID']
                                DL_Info = MDS.GetInfo (TK_id)
                                if DL_Info['success'] == True :
                                #找到任務
                                    if DL_Info['data']['tasks'][0]['status'] == 'finished' :
                                    #下載完成
                                        TK_Info = DL_Info['data']['tasks'][0]
                                        TK_status = TK_Info['status']
                                        TK_title = TK_Info['title'].strip()
                                        TK_uri = TK_Info['additional']['detail']['uri']
                                        crab.lock.acquire()
                                        with HQCDB(crab.DBFile,self.secName) as tempDB:
                                            if tempDB.IsExistTask(TK_id):
                                                tempDB.Update([TK_id,TK_uri,TK_status,TK_title])
#                                                tempDB.DelTask(TK_id)
                                        del tempDB
                                        crab.lock.release()
                                        del TK_Info
                                        msgtxt = '{}{} 已下載完成'.format (chkName,DD)
                                        MDS.Delete(self.Sec['DL ID'])
                                        self.Sec['DL ID'] = ''
                                        self.Sec['DL Status'] = 'finished'
#                                        self.notify (msgtxt)
                                        #列印日誌
                                        self.logging ('\t{}\r\n'.format(msgtxt))
                                    else :
                                    #下載中
                                        #列印日誌
                                        self.logging ('\t{}{} 下載中\r\n'.format(chkName,DD))
                                else :
                                #找不到任務
                                    crab.lock.acquire()
                                    with HQCDB(crab.DBFile,self.secName) as tempDB:
                                        if tempDB.IsExistTask(TK_id):
                                            tempDB.DelTask(TK_id)
                                    del tempDB
                                    crab.lock.release()
                                    self.Sec['DL ID'] = ''
                                    self.Sec['DL Status'] = ''
                                    self.logging ('\t{}{} NAS 任務已被手動移除\r\n'.format(chkName,DD))
                                del DL_Info
                            else :
                            #無法連上Download Station
                                self.logging  ('\t無法連結 NAS\r\n')
                        else :
                        #上次已完成下載
                            #列印日誌
                            self.logging ('\t自 {} 後，{} 沒有更新\r\n'.format(LastUpdate,chkName+DD))
                    else :
                    #有更新
                        #取得ACG資料磁力鏈結
                        try :
                            title = chkD.strip() + '.torrent'
                            res.get('http://{}/{}'.format(self.Sec['Site'],tempD['href']))
                            #挑出 <a id='magnet'>
                            uri = res.soup.select('a#magnet')[0]['href']
                            tUri = res.soup.select('a#download')[0]['href']
                            torrentURI = 'http://{}/{}'.format(self.Sec['Site'],tUri)

                            if crab.plat_Linux :
                                torrentPath = '/volume1/{}/{}'.format(self.Sec['destination'],'Torrent')
                                if not os.path.exists(torrentPath) :
                                    os.makedirs(torrentPath)
                                tfn = '{}/{}'.format(torrentPath,title)  
                                fn = '{}/{}.{}'.format(torrentPath,'HQC',title.split('.')[-1])
                            else :
                                try :
                                    torrentPath = '{}\\{}'.format(crab.Config['DEBUG']['Windows Work Path'],'Torrent')
                                except :
                                    torrentPath = 'C:\\MyCoding\\D_Check\\Torrent'
                                if not os.path.exists(torrentPath) :
                                    os.makedirs(torrentPath)
                                tfn = '{}\\{}'.format(torrentPath,title)
                                fn = '{}\\{}.{}'.format(torrentPath,'HQC',title.split('.')[-1])
                            #取得torrent連結
                            try :
                                res1 = requests.get(torrentURI,headers = aheaders,timeout = 15)
                                #torrent 存檔
                                with open ( tfn,'wb') as ff :
                                    ff.write (res1._content)                                                
                                with open ( fn,'wb') as ff :
                                    ff.write (res1._content)
                            except Exception as e :
                                print ('torrent get Exception:' ,e)
                            del ff
                        except :
                            self.logging ('\t{}無法取得磁力鏈結\r\n'.format(self.secName))
                        self.Sec['check word'] = DD
                        self.Sec['Last Update'] = self.chk_date
                        msgtxt = '{}{} 發佈'.format(chkName,DD)
                        if (uri != self.Sec['Last Uri']) and (MDS.SID != '') and (uri != '') :
                        ##Download Station 己連上 且 有新的連結
                            if MDS.AddTask(uri = uri,des = self.Sec['destination']) == True :
                            #成功加入 Download List
                                msgtxt = '{},已加入下載排程'.format(msgtxt)
                                TK_Info = MDS.List()['data']['tasks'][-1]
                                TK_status = TK_Info['status']
                                TK_id = TK_Info['id']
                                TK_title = tempD.text.strip()
                                TK_uri = TK_Info['additional']['detail']['uri']
                                crab.lock.acquire()
                                with HQCDB(crab.DBFile,self.secName) as tempDB:
                                    tempDB.AddFile([TK_uri,TK_id,TK_status,TK_title])
                                del tempDB
                                crab.lock.release()
                                del TK_Info
                                self.Sec['Last Uri']    = uri
                                self.Sec['DL ID']       = MDS.List()['data']['tasks'][-1]['id']
                                self.Sec['DL Status']   = 'downloading'
                        self.notify (msgtxt+'\n#影片發佈')
                        #列印日誌
                        self.logging ('\t{}\r\n'.format(msgtxt))
                del res
                return 0

