# coding: utf-8

import os
import sys
from datetime import datetime
from MyPack import *
today = datetime.now() 
weekday = today.strftime('%w')
tday = today.strftime('%Y-%m-%d')
debugging = False

def doCheck(ConfSec):
    global today 
    global weekday
    global tday
    todayD = today.strftime('%d')
    todayH = today.strftime('%H')
    Checkdays = ConfSec['Check Days'].split(',')
    lenCD = len(Checkdays)
    isMonthly = True if Checkdays[0] == 'M' else False
    if isMonthly :
        return True if  (todayH == '11') and (todayD in Checkdays)and(lenCD > 1) else False
    isWeekly = True if Checkdays[0] == 'W' else False
    if isWeekly :
        return True if  (todayH in ['11','18']) and (weekday in Checkdays)and(lenCD > 1) else False
    isDayly = True if Checkdays[0] == 'D' else False
    if isDayly :
        return True if (lenCD == 1) or (todayH in (Checkdays)) else False

    wd = (lambda x,y : (x - y) + (7 if x < y else 0))(int(weekday) , int(Checkdays[-1]))
    LastUpdate = datetime.strptime(ConfSec['Last Update'].split('(')[0],'%Y-%m-%d')
#    lw = datetime.strftime(LastUpdate,'%w')
    if 'downloading' in ConfSec['DL Status']:
        return True
    elif u'全' in ConfSec['check word'] :
        return False
    elif tday in ConfSec['Last Update']:
        return False
    elif int ((today-LastUpdate).days) > 7:
        return True
    elif weekday in ConfSec['Check Days']:
        return True
    elif int((today-LastUpdate).days) > wd:
        return True
    else :
        return False

def __main__ () :
    global debugging
    global today
    global weekday
    global tday
    from platform import platform
    plat =  platform()
    AppPath = ''
    ConfigFile = ''
    Ignore_Last_Update = False
    _log = MyLog()
    if len (sys.argv) > 1  :
        path = sys.argv[1]
        if (os.path.isdir(path)) :
            AppPath = path
        elif (os.path.isfile(path)):
            AppPath = os.path.abspath(path)
            ConfigFile = path         
    if AppPath == '' :
        if 'Windows' in plat :
            AppPath = '{}\\'.format(os.getcwd())
        elif 'Linux' in plat :
            AppPath = '/volume1/Tasks/WWWCheck/'
            if not os.path.exists(AppPath) :
                print ('程式路徑不存在')
                return 0
        else  :
            print ('未設定的作業系統: ',plat)
            return 0
    if ConfigFile == '':
        if (AppPath[-1] == '\\') or (AppPath[-1] == '/'):
            ConfigFile = '{}D_Check1.ini'.format(AppPath)
        else:
            ConfigFile = '{}\\D_Check.ini'.format(AppPath) if 'Windows' in plat else '{}/D_Check.ini'.format(AppPath)
    if not (os.path.exists (ConfigFile)) :
        print ('{}設定檔找不到'.format(ConfigFile))
        return 0
    Config = MyConfig(ConfigFile)
    debugging = Config.ckBool('debugging','DEBUG')
    Ignore_Last_Update = Config.ckBool('Ignore Last Update','DEBUG')
    _log.writable = Config.ckBool('Logging','LOG')
    crabs = list(filter(lambda x: Config.ckBool(x,'Crabs') ,Config.Options('Crabs')))
    def _split(kword,iter):
        _A = list(filter(lambda x: kword in x , iter))
        _B = list(filter(lambda x: x not in _A , iter))
        _C = list(filter(lambda x: doCheck(Config.Config[x]) , _A))
        return _A,_C,_B

    _Ck_ACG , __Ck_ACG  , _crabs = _split('Ck_ACG'  ,crabs )
    _ACG    , __ACG     , _crabs = _split('ACG'     ,_crabs)
    _HQC    , __HQC     , _crabs = _split('HQC'     ,_crabs)
    _BTDY   , __BTDY    , _crabs = _split("BTDY"    ,_crabs)
    _BT     , __BT      , _crabs = _split("BT"      ,_crabs)
    _Ck_BK  , __Ck_BK   , _crabs = _split("Ck_BK"   ,_crabs)
    _OK     , __OK      , _crabs = _split("OK"      ,_crabs)

    crr =       [ACG(Config , x)        for x in (_Ck_ACG if Ignore_Last_Update else __Ck_ACG)]
    crr = crr + [Crab_ACG(Config , x)   for x in (_ACG    if Ignore_Last_Update else __ACG)   ]
    crs =       [Crab_HQC(Config , x)   for x in (_HQC    if Ignore_Last_Update else __HQC)   ]
    crs = crs + [Crab_BTDY(Config , x)  for x in (_BTDY   if Ignore_Last_Update else __BTDY)  ]
    crs = crs + [Crab_BTDY1(Config , x) for x in (_BT     if Ignore_Last_Update else __BT)    ]
    crs = crs + [BOOK(Config , x)       for x in (_Ck_BK  if Ignore_Last_Update else __Ck_BK) ]
    crs = crs + [Crab_OK(Config , x)    for x in (_OK     if Ignore_Last_Update else __OK)    ]

    cnt,cnt1,cnt2 = 0,0,0
    cnt = len (crabs)
    cnt1 = len (crs)+len(crr)
    cnt2 = cnt - cnt1

    if crr != []:
        [x.run() for x in crr]
    if crs != []:
        [(x.start() if not debugging else x.run()) for x in crs]
        [(x.join() if not debugging else None) for x in crs]
    for cr in crr:
        del cr
    del crr
    for cr in crs:
        del cr
    del crs
    if cnt1 == 0 :
        _log.logging (datetime.now().strftime('%Y-%m-%d(%w)T%H:%MZ') + '\n')
    _log.logging ('\t總共 {0} 網頁被設定(僅檢測空值之前)\n'.format(cnt))
    _log.logging ('\t\t{0} 個網頁被檢測\n'.format(cnt1))
    #_log.logging ('\t\t{0} 個網頁今日已更新\n'.format(cnt3))
    _log.logging ('\t\t{0} 個網頁未達檢測時間\n\n'.format(cnt2))
    _log.WriteLog (Config.Config['LOG']['Log File'])
    del _log

if __name__ == '__main__' :
    __main__()