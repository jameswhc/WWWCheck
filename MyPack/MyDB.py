# coding: utf-8
import sqlite3 as lite
__all__ = ['CrabDB']

class CrabDB ():
    Create_CMD = '''CREATE TABLE IF NOT EXISTS {} (     
                                    file	  TEXT,
                                    taskid	TEXT NOT NULL UNIQUE,
                                    status	TEXT,
                                    title	  TEXT,
                                    PRIMARY KEY( taskid ));'''
    
    CreateHis_CMD = '''CREATE TABLE IF NOT EXISTS History (     
                                    file	  TEXT NOT NULL UNIQUE,
                                    taskid	TEXT NOT NULL,
                                    status	TEXT,
                                    title	  TEXT,
                                    PRIMARY KEY( file ));'''
    Create_Index_CMD = '''CREATE INDEX IF NOT EXISTS index_{}_status ON {} (status) ;'''
    Insert_CMD = '''INSERT INTO {0} VALUES ("{1}","{2}","{3}","{4}");'''
    Update_CMD = '''UPDATE {} SET status = "{}" WHERE taskid = "{}" ;'''

    def __init__(self,lite_file,project):
        self.lite_file = lite_file
        self.project = project
        self.con = lite.connect(lite_file)
        self.cursor = self.con.cursor()
        ###  專案資料表
        self.cursor.execute(CrabDB.Create_CMD.format (self.project))
        self.cursor.execute(CrabDB.CreateHis_CMD)
        self.cursor.execute(CrabDB.Create_Index_CMD.format(self.project,self.project))

    def GetTask (self,value,table = ''):
        '''
        傳回工作(排除 Down)的Dictionary
        {taskid:{'file': uri
                 'status':'finished' / 'downloading' 
                 'title' : 檔案名稱
                }
        }
        '''
        TB = self.project
        if table != '' :
            TB = table
        self.cursor.execute ('''Select file,taskid,status,title From {} Where taskid = "{}";'''.format (TB,value))
        a = self.cursor.fetchone()
        return {a[1]:{'file':a[0],'status':a[2],'title':a[3]}}

    def GetTasks (self,table = ''):
        '''
        傳回所有工作(排除 Down)的Dictionary
        {taskid:{'file': uri
                 'status':'finished' / 'downloading' 
                 'title' : 檔案名稱
                }
        }
        '''
        TB = self.project
        if table != '':
            TB = table
        self.cursor.execute ('''Select file,taskid,status,title From {} Where status != 'Down';'''.format (TB))
        c = {}
        for a in self.cursor.fetchall() :
            c.update({a[1]:{'file':a[0],'status':a[2],'title':a[3]}})
        return c

    def GetNotFinished (self,X_finished = True,X_Down = True):
        '''
        X_finished = True : 要濾除finished
        X_Down = True : 要濾除 Down
        傳回所有未完成(排除 finished、Down)工作的LIST
        [[taskid,status],....]
        '''
        
        if (X_finished) and (X_Down) :
            Select_CMD = '''SELECT taskid , status From {} Where (status != 'finished') and (status != 'Down')  ; '''
        elif (X_finished) :
            Select_CMD = '''SELECT taskid , status From {} Where status != 'finished'  ; '''
        elif (X_Down) :
            Select_CMD = '''SELECT taskid , status From {} Where status != 'Down'  ; '''
        else :
            Select_CMD = '''SELECT taskid , status From {} ; '''
        self.cursor.execute (Select_CMD.format(self.project))
        c = []
        for a in self.cursor.fetchall() :
            c.append ([a[0],a[1]])
        return c

    def IsExistFile (self,value):
        self.cursor.execute('''SELECT count(*) FROM {} WHERE file = "{}";'''.format(self.project,value))
        return False if self.cursor.fetchone()[0] == 0 else True           

    def IsExistTask (self,value):
        self.cursor.execute('''SELECT count(*) FROM {} WHERE taskid = '{}';'''.format(self.project,value))
        return False if self.cursor.fetchone()[0] == 0 else True           

    def _IsExistHis (self,file):
        self.cursor.execute('''select count(*) from History where file = "{}";'''.format(file))
        return False if self.cursor.fetchone()[0] == 0 else True

    def _HisUpsert (self,value):
        TK_file     = value[0]
        TK_id       = value[1]
        TK_status   = value[2]
        TK_title    = value[3]
        # PostgreSQL mssql sqllite-3.24專屬語法
        cmd = CrabDB.Insert_CMD[:-1]+ ''' ON CONFLICT(file) DO UPDATE SET
                                            taskid = "{2}" ,
                                            status = "{3}" ,
                                            title  = "{4}";'''
        cmd = cmd.format ('History',TK_file,TK_id,TK_status,TK_title)
        try:
            self.cursor.execute(cmd)
        except Exception as e:            
            if self._IsExistHis(TK_file):
                #Update 程式
                self.cursor.execute('''
                    update History  
                        set taskid = "{}",
                            status = "{}",
                            title  = "{}"
                        where file = "{}"
                        ;'''.format(TK_id,TK_status,TK_title,TK_file))
            else:
                #Insert 程式
                self.cursor.execute(CrabDB.Insert_CMD.format ('History' , TK_file , TK_id , TK_status , TK_title))
        finally :
            self.con.commit()

    def AddFile (self,value):
        if (len(value) > 3)and(type(value) is type([])) :
            TK_file     = value[0]
            TK_id       = value[1]
            TK_status   = value[2]
            TK_title    = value[3]
            try : 
                self.cursor.execute(CrabDB.Insert_CMD.format (self.project , TK_file , TK_id , TK_status , TK_title))
                self.con.commit()
                self._HisUpsert([TK_file,TK_id,TK_status,TK_title])
                return True
            except:
                return False

    def AddFiles (self,values):
        try :
            for value in values :
                self.AddFile(value)
            return True
        except :
            return False

    def UpdateStatus(self,value):
        if (len(value) > 1)and(type(value) is type([])) :
            TK_id       = value[0]
            TK_status   = value[1]
            if self.IsExistTask(TK_id):
                self.cursor.execute(CrabDB.Update_CMD.format (self.project,TK_status,TK_id))
                self.con.commit()
                TK = self.GetTask(TK_id)[TK_id]
                TK_file = TK['file']
                TK_title= TK['title']
                self._HisUpsert([TK_file,TK_id,TK_status,TK_title])
                return True
        return False

    def Update(self,value):
        if (len(value) > 2)and(type(value) is type([])) :
            TK_id       = value[0]
            TK_file     = value[1]
            TK_status   = value[2]
            if len (value) == 4:
                TK_title = value[3]
            else :
                TK = self.GetTask(TK_id)[TK_id]
                TK_title= TK['title']
            if self.IsExistTask(TK_id):
                self.cursor.execute('''
                        update {} 
                            set file    = "{}" ,
                                status  = "{}" ,
                                title   = "{}"
                            where taskid = "{}"
                        ;'''.format (self.project,TK_file,TK_status,TK_title,TK_id))
                self.con.commit()
                self._HisUpsert([TK_file,TK_id,TK_status,TK_title])
                return True
        return False

    def ClearDB (self):
        self.cursor.execute('''insert into History(file,taskid,status,title) select A.file,A.taskid,'Down',A.title from {} A where A.file not in (select file from History);'''.format(self.project))
        self.con.commit()
        self.cursor.execute('''DELETE FROM {};'''.format(self.project))
        self.con.commit()

    def DelTask (self,value,force = False):
        if self.IsExistTask(value):
            TK_id = value
            TK = self.GetTask(TK_id)[TK_id]
            TK_file     = TK['file']
            TK_status   = 'Down'
            TK_title    = TK['title']
            if not force :
                self._HisUpsert([TK_file,TK_id,TK_status,TK_title])
            self.cursor.execute('''Delete From {} Where taskid = '{}' ;'''.format(self.project,TK_id))
            self.con.commit()

    def close (self):
        try :
            self.con.close()
        except:
            pass

    def __enter__ (self) :
        return self

    def __exit__(self, exc_ty, exc_val, tb) :
        try :
            self.con.close()
        except:
            pass

    def __del__ (self) :
        try :
            self.con.close()
        except:
            pass