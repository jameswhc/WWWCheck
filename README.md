用來檢測網站是否有更新資源
#BD、GG 已完成階段任務，沒再繼續使用
#ACG 用來檢查 簡單動漫 網站上的資源
#BTDY 用來檢查 BT天堂 網站上的資源
#BOOK 用來檢查 繁體小說網 網站上的資源
#OK 用來檢查 OK資源網 網站上的資源
在 CMD.exe 中使用 "python Ck_Programs.py Config.ini" 來執行程式，也可以加入排程 

在Config.ini中需要有下面Sections
============================================================================
[DEBUG]
debugging = <在除錯模式下執行[yes,no]>
Windows Work Path = < Windows下的預設工作目錄>
Ignore Last Update = <是否忽略最後的更新日期(強制檢查)) [yes,no]>

[LOG]
Logging = <是否要把log存檔[yes,no]>
Log File = < Log檔的檔名[/你的路徑/你的檔名])>
OK Log File = < OK資源網轉存DPL的檔案格式[/你的路徑/{}.dpl]>
SQLITE File = <存放URI的資料庫檔[/你的路徑/你的檔名]>

[Notify]
Notify = <你要的通知App，可以是[Teleg,LINE]2個任一或全部>
Teleg Chat ID = <你在Telegram中想對話的 chat ID>
Teleg Token = <你的Telegram token>
Line Token = <你的Line token>
Show Link = <是否要將網站連結一併傳送給App[yes,no]>

[DSM]
encrypt = <帳號、密碼是否已被加密[yes,no]>
https = <是否以HTTPS方式連結DSM[yes,no]>
ip = < DSM的IP[IPv4]>
port = < DSM的port>
username = < DSM的帳號 [username]>
password = < DSM的帳號 [password]>

[Crabs]
<要被檢測的網站類型及編號[網站類型及編號]> = <是否要檢測[yes,no]>
OK1 = no
OK2 = yes
BTDY1 = yes

[OK2]
Check Days = W,1,4  # 周1,4(上午11時、18時)檢查
Site = www.okzy.co  #網站
Page = vod-detail-id-59464.html #頁面
keyword = 独步逍遥 #主題文字
Name = OK 獨步逍遙 #訊息、紀錄使用的名字
Crab word = div#down_1 ul li input #網頁解析文字
check word = 更新至50集 #目前更新狀況
Last Update = 2020-11-26(4)T11:30Z #最後更新日期
Last Uri = http://xxx.yyy.zzz/aaaaaaaaaaaaaa #最後1筆 URI
Generate TXT = no #是否將URI產製文字檔
destination = /你的路徑/你的檔名.dpl #DPL檔

[BTDY1]
Check Days = 5 # 周5(不分時間)檢查
Site = btbtdy2.com #網站
Page = btdy/dy31679.html #頁面
Name = BT 九尾狐傳 #主題文字
Crab word = dl dd #網頁解析文字
Crab raw = 1 #網頁解析區段
Section Left Delimiter = [  #更新集數分析之左字元
Section Right Delimiter = ] #更新集數分析之右字元
check Section = 3 #更新集數分析之區段
check word = 共16集,更新至14集 #目前更新狀況
Last Update = 2020-11-27(5)T11:30Z #最後更新日期
Site Status = OK  #網站狀態
Last Uri = magnet:?xt=urn:btih:aaaaaaaaaaaaaa #最後1筆 URI
DL ID =   #DSM的工作ID
DL Status = finished #DSM的工作狀態
destination = /你的路徑
============================================================================