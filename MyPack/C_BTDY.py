#coding: utf-8
from MyPack.MyDSM import MyDownloadStation as MyDS
from MyPack.MyCrab import MYSITE
from MyPack.MyCrab import crab
from MyPack.MyDB import CrabDB as HQCDB
__all__ = ['Crab_BTDY','Crab_BTDY1']

class Crab_BTDY (crab) :
    def check (self):
        if not crab.Config.has_section(self.secName) :
            self.logging('\t未定義 {} Config\r\n'.format (self.secName))
            return 2
        url = 'http://{}/{}'.format(self.Sec['Site'],self.Sec['Page'])
        url_ = 'http://{}/vidlist/{}'.format(self.Sec['Site'],self.Sec['Page'].split('btdy/dy')[1])
        status = self.Sec['Site Status']
        try :
            res = MYSITE (url)
            tempD = res.soup.select (self.Sec['Crab word'])[self.Sec.getint('Crab raw')]
            chkD = tempD.text
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
                #找 <fieldset>
                uri = self.Sec['Last Uri']
                DD = chkD
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
                                                #DL_title = info['data']['tasks'][0]['title']
                                                DL_uri = info['data']['tasks'][0]['additional']['detail']['uri']
                                                if (task[1] != 'Down') and (task[1] != DL_status) :
                                                #若狀態有變
                                                    #更新狀態
                                                    tempDB.Update([task[0],DL_uri,DL_status])
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
                        # 取得連結
                        Files = []
                        res.get(url_)
                        tempf = res.soup.select('div.p_list li span a.d1')
                        tempt = res.soup.select('div.p_list li a.ico_1')
                        for i in range (len(tempf)):
                            Files.append([tempf[i]['href'],tempt[i]['title'].strip()])
#                            for file in res.soup.select('div.p_list li span a.d1'):
#                                Files.append(file['href'])
                        if Files != [] :
                            crab.lock.acquire()
                            with HQCDB(crab.DBFile,self.secName) as tempDB:
                                if keyVal == '' :
                                    tempDB.ClearDB()
                                tempcount = 0
                                for File in Files:
                                    uri = File[0]
                                    title = File[1].strip()
                                    if not tempDB.IsExistFile(uri) :
                                        if MDS.AddTask(uri=uri,des = self.Sec['destination']) :
                                            tempcount += 1
                                            temptask = MDS.List()['data']['tasks'][-1]
                                            tempDB.AddFile ([uri,temptask['id'],temptask['status'],title])
                            if tempcount > 0 :
                                msgtxt = '{}{}已新增 {} 個下載排程'.format (chkName,DD,tempcount)
                                self.Sec['DL Status'] = 'downloading'
                            else :
                                msgtxt = '{}{}已更新，但無新增下載連結'.format(chkName,DD)
                            del tempDB
                            crab.lock.release()
                            self.logging ('\t{}\r\n'.format (msgtxt))
                            self.Sec['check word']  = DD
                            self.Sec['Last Update'] = self.chk_date
                            self.Sec['Last Uri']    = uri
                            self.notify (msgtxt)
                        else :
                            msgtxt = '網頁服務異常'
                        del Files
                del res
                del MDS
                return 0

class Crab_BTDY1 (crab) :
    def check (self):
        if not crab.Config.has_section(self.secName) :
            self.logging('\t未定義 {} Config\r\n'.format (self.secName))
            return 2
        url = 'http://{}/{}'.format(self.Sec['Site'],self.Sec['Page'])
        status = self.Sec['Site Status']
        try :
            res = MYSITE (url)
            tempD = res.soup.select (self.Sec['Crab word'])[self.Sec.getint('Crab raw')]
            chkD = tempD.text
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
                #找 <fieldset>
                uri = self.Sec['Last Uri']
                DD = chkD
                keyVal = self.Sec['check word']
                LastUpdate = self.Sec['Last Update']
                if keyVal == DD :
                #無更新
                    pass
                else :
                #有更新
                    # 取得連結
                    msgtxt = '{}{}已更新'.format(chkName,DD)
                    self.logging ('\t{}\r\n'.format (msgtxt))
                    self.Sec['check word']  = DD
                    self.Sec['Last Update'] = self.chk_date
                    self.notify (msgtxt)
                del res
                return 0