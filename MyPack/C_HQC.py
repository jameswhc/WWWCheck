#coding: utf-8
from MyPack.MyDSM import MyDownloadStation as MyDS
from MyPack.MyCrab import MYSITE
from MyPack.MyCrab import crab
from MyPack.MyDB import CrabDB as HQCDB
from bs4 import BeautifulSoup
import requests
import os
__all__ = ['Crab_HQC']

class Crab_HQC (crab) :
    def check (self):
        if not crab.Config.has_section(self.secName) :
            self.logging('\t未定義 {} Config\r\n'.format (self.secName))
            return 2
        hd= { 'Host': 'www.gscq.me'
             ,'Upgrade-Insecure-Requests' : '1'
             ,'Cookie' :'bbs_token=RVz5QEmUkfLAIfn8RPO4egxAtbgGslmQr0Kc0M17Uz1aLZtm; bbs_sid=s1lemcj23bsbhgg9tfbt705r92'
            }
        url = 'https://{}/{}'.format(self.Sec['Site'],self.Sec['Page'])
        status = self.Sec['Site Status']
        try :
            with MYSITE (url,headers = hd) as res :
                tempD = res.soup.select (self.Sec['Crab word'])[self.Sec.getint('Crab raw')]
                chkD = str(tempD)
                #找 <fieldset>
                FileSets = res.soup.find_all ('fieldset')
            self.headers = res.headers.copy()
            uri = self.Sec['Last Uri']
            self.Sec['Site Status'] = 'OK'
        except :
            self.logging ('\t網站連結失敗\r\n')
            self.Sec['Site Status'] = 'Error'
        finally :
            chkName = self.Sec['Name']
            if self.Sec['Site Status'] == 'Error' :
            #若網站服務異常
#                if status == 'OK' :
                #若上次檢查時是好的
                try :
                    msgtxt = '{}網站服務異常'.format(self.secName)
                    self.logging ('\t{}\r\n'.format(msgtxt))
#                    self.notify (msgtxt)
                    del res
                except :
                    pass
                finally :
                    return 1
            else :
            #網站服務正常
                if status == 'Error':
                #若上次檢查時是異常
                    msgtxt = '{}網站服務恢復'.format(self.secName)
                    #列印日誌
                    self.logging ('\t{}\r\n'.format(msgtxt))
#                    self.notify (msgtxt)
                SLD         = self.Sec['Section Left Delimiter']
                SRD         = self.Sec['Section Right Delimiter']
                tempDD      = chkD.split(SLD)[self.Sec.getint('check Section')]
                DD          = '{}{}{}'.format(SLD,tempDD.split(SRD)[0],SRD)
                keyVal      = self.Sec['check word']
                LastUpdate  = self.Sec['Last Update']
                with MyDS() as MDS:
                    MDS.CONNECT(crab.dsm)
                    if keyVal == DD :
                    #無更新
                        if self.Sec['DL Status'] == 'downloading' :
                        #上次仍在下載中
                            if MDS.SID != '' :
                            #Download Station 己連上
                                crab.lock.acquire()
                                with HQCDB(crab.DBFile,self.secName) as tempDB:
                                    tasks = tempDB.GetNotFinished()
                                    if tasks != [] :
                                    #處理未完成更新的工作
                                        for task in tasks:
                                            #取得工作的狀態
                                            info = MDS.GetInfo(task[0])
                                            if info['success'] :
                                                DL_status = info['data']['tasks'][0]['status']
                                                #DL_uri = info['data']['tasks'][0]['additional']['detail']['uri']
                                                if (task[1] != 'Down') and (task[1] != DL_status) :
                                                #若狀態有變
                                                    #更新狀態
                                                    tempDB.UpdateStatus([task[0],DL_status])
                                            else :
                                                tempDB.UpdateStatus([task[0],'Down'])
                                        #重新取回所有工作狀態
                                        tasks = tempDB.GetNotFinished()
                                    if tasks == [] :
                                    #全部下載完成
                                        self.Sec['DL Status'] = 'finished'
                                        msgtxt = '{}{} 已下載完成'.format (chkName,DD)
#                                        self.notify (msgtxt)
                                        for task in tempDB.GetTasks().keys():
                                            tempDB.UpdateStatus ([task,'Down'])
                                            MDS.Delete(task)
                                        #列印日誌
                                        msgtxt = ('\t{}\r\n'.format(msgtxt))
                                    else :
                                    #下載中
                                        #列印日誌
                                        msgtxt =  ('\t{}{} 還有{}個下載排程\r\n'.format(chkName,DD,len(tasks)))
                                del tempDB
                                crab.lock.release()
                                self.logging (msgtxt)
                            else :
                            #無法連上Download Station
                                self.logging ('\t無法連結 NAS\r\n')
                        else :
                        #上次已完成下載
                            #列印日誌
                            self.logging ('\t自 {} 後，{} 沒有更新\r\n'.format(LastUpdate,chkName+DD))
                    else :
                    #有更新
                        if FileSets != [] :
                        # 取得HQC連結
                            FileSet = str(FileSets[0])
                            soupHref = BeautifulSoup(FileSet,'html.parser')
                            #挑出 <ul class='attachlist'> <li> <a>
                            Files = soupHref.select('ul.attachlist li a')
                            crab.lock.acquire()
                            try :
                                #用於計算新增多少個排程
                                tempcount = 0
                                with HQCDB(crab.DBFile,self.secName) as tempDB:
                                    if keyVal == '' :
                                        tempDB.ClearDB()
                                    #處理每一條連結
                                    for File in Files:
                                        uri = 'https://{}/{}'.format(self.Sec['Site'],File['href'])
                                        title = File.text.strip()
                                        if not tempDB.IsExistFile(uri) :
                                        #如果連結不存在於資料庫
                                            #設定檔案名稱
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
                                                res1 = requests.get(uri,headers = self.headers,verify = False ,timeout = 15)
                                                #torrent 存檔
                                                with open ( tfn,'wb') as ff :
                                                    ff.write (res1._content)                                                
                                                with open ( fn,'wb') as ff :
                                                    ff.write (res1._content)
                                            except Exception as e :
                                                print ('torrent get Exception:' ,e)
                                            del ff
                                            #將torrent 加入排程
                                            if MDS.AddTask (file = fn ,des = self.Sec['destination']) :
                                                tempcount += 1
                                                temptask = MDS.List()['data']['tasks'][-1]
                                                tempDB.AddFile ([uri,temptask['id'],temptask['status'],title])
                                    msgtxt = '{}{}已新增 {} 個下載排程'.format (chkName,DD,tempcount)
                                del tempDB
                            except Exception as e :
                                print (e)
                            crab.lock.release()
                            self.logging ('\t{}\r\n'.format (msgtxt))
                            if tempcount > 0 :
                                self.Sec['check word']  =  DD
                                self.Sec['Last Update'] = self.chk_date
                                self.Sec['Last Uri']    = uri
                                self.Sec['DL Status']   = 'downloading'
                            self.notify (msgtxt)
                        else :
                            msgtxt = '網頁服務異常'
                return 0

