#coding: utf-8
from MyPack.MyCrab import crab
import os
import socket
__all__ = ['Crab_GG']

class Crab_GG (crab):
    def check(self):
        ''' 
        return 0 : 網站服務正常
        return 2 : Config 未設定
        Config 參數如下
            Batch File = 輸出檔案
            host = 主機名
            IPs = 偵測到的IP
            Last Update = 上次發現新IP日期
            App Path 4 Windows = Windows下的輸出目錄
            App Path 4 Linux = Linux 下的輸出目錄
        '''
        if not crab.Config.has_section(self.secName):
            self.logging ('\t未定義 {} Config\r\n'.format (self.secName))
            return 2
        #===============參數設定==============================================
        ###===============================================
        if crab.plat_Linux :
            AppPath2 = self.Sec['App Path 4 Linux']
        else :
            AppPath2 = '{}\\'.format(os.getcwd())
    
        ###===============================================
        BatFileName = self.Sec['Batch File']
        host = self.Sec['host']
        cmdDelstr = 'netsh advfirewall firewall delete rule name="Block_GG"'
        cmdAddstr = 'netsh advfirewall firewall add rule name="Block_GG" dir=out action=block enable=yes remoteip={}'
        temp_ip = socket.gethostbyname(host)
        GG_IPs =  self.Sec['IPs']
        msgtxt = self.chk_date
        if temp_ip in GG_IPs :
            for ip in GG_IPs.split(','):
                if ip != temp_ip :
                    msgtxt +=  '\t' 
                else :
                    msgtxt += ' {}\r\n'.format( temp_ip)
                    break
#            self.logging ('\tGG沒有新IP.\r\n'.format(msgtxt))
        else:
            msg = 'GG 新增 {}'.format(temp_ip) 
            self.notify (msg)
            self.Sec['Last Update'] = self.chk_date
            self.Sec['IPs']         = '{},{}'.format(GG_IPs,temp_ip)
            msgtxt += '\t{}\r\n'.format(msg)
            self.logging (msgtxt)
        #Windows 用的檔案，換行必須使用 \r\n
        #===================================================================================
            '''#強制轉 Big5 碼寫入
            cmd = ''.encode('big5')
            cmd = cmd + '@rem 封鎖 Game Guard 回報 IPs\r\n'.encode('big5')
            cmd = cmd + '@rem 更新日期: {}\r\n'.format (chk_date).encode('big5')
            cmd = cmd + '@rem 刪除舊規則\r\n'.encode('big5')
            cmd = cmd + '{}\r\n'.format (cmdDelstr).encode('big5')
            cmd = cmd + '@rem 新增規則\r\n'.encode('big5')
            cmd = cmd + '{}\r\n'.format (cmdAddstr.format(Config.get(secName,'IPs'))).encode('big5')
            cmd = cmd + '@pause'.encode('big5')
            n_cmd = cmd.decode('big5')
            with open(AppPath2+BatFileName,'w',encoding = 'Big5') as BatFile :
                BatFile.write (n_cmd)
            '''
            cmd = ''
            cmd = cmd + 'rem 封鎖 Game Guard 回報 IPs\r\n'
            cmd = cmd + 'rem 更新日期: {}\r\n'.format (self.chk_date)
            cmd = cmd + 'rem 刪除舊規則\r\n'
            cmd = cmd + '{}\r\n'.format (cmdDelstr)
            cmd = cmd + 'rem 新增規則\r\n'
            cmd = cmd + '{}\r\n'.format (cmdAddstr.format(self.Sec['IPs']))
            cmd = cmd + 'timeout /T 10'
            with open(AppPath2+BatFileName,'w',encoding = 'utf-8' if crab.plat_Linux else 'big5') as BatFile :
                BatFile.write (cmd)
        #===================================================================================
        with open (crab.Config.get('LOG','GG Log File'),'a+') as log:
            log.write (msgtxt)
        return 0