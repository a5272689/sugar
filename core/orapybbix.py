# -*- coding:utf-8 -*-
#author:hjd
import cx_Oracle,ConfigParser,os,Queue,json,re
from threading import Thread
from core import sendto
from core.moduleslog import write_log
class UseCx_Oracle(object):
    def __init__(self,connstr,ErrorQ):
        self.ErrorQ=ErrorQ
        try:
            self.__conn = cx_Oracle.connect(connstr)
        except:
            self.connstatus=0
        else:
            self.dbversion=self.__conn.version
            self.connstatus=1
            self.__cur = self.__conn.cursor()
    def runsql(self,sql):
        if self.connstatus:
            try:
                exe = self.__cur.execute(sql)
            except:
                self.ErrorQ.put('执行SQL<{}>出错！'.format(sql))
                return []
            else:
                return exe.fetchall()
    def close(self):
        self.__cur.close()
        self.__conn.close()

def check_ora(host_connstr,host,websugarurl,ErrorQ,sqls_dic):
    ora=UseCx_Oracle(host_connstr,ErrorQ)
    sendhandle = sendto.sendtowebsugar(websugarurl)
    sendhandle.send(host, 'oraclalive', ora.connstatus)
    if ora.connstatus:
        sendhandle.send(host, 'dbversion',ora.dbversion)
        for sql,sendkeys in sqls_dic.items():
            sqlresult=ora.runsql(sendkeys['sql'])
            keys_list = sendkeys['keys']
            if sqlresult:
                if len(keys_list)==len(sqlresult[0]):
                    itemkeys=sendkeys.get('itemkeys')
                    rowkeys = sendkeys.get('rowkeys')
                    rowkey = sendkeys.get('rowkey')
                    rowvalue = sendkeys.get('rowvalue')
                    if itemkeys:
                        itemkeynames = sendkeys.get('itemkeynames')
                        macros = sendkeys.get('macros')
                        macrosname = sendkeys.get('macrosname')
                        if itemkeynames and macros and macrosname:
                            macros_keys = {"data": []}
                            for tmpresult in sqlresult:
                                for i in xrange(len(keys_list)):
                                    try:
                                        exec '{}={}'.format(keys_list[i], tmpresult[i])
                                    except:
                                        exec "{}='{}'".format(keys_list[i], tmpresult[i])
                                for itemkey, value in itemkeys.items():
                                    exec '{}={}'.format(itemkey, value)
                                realmacrosname=re.sub(r'[\$\/\=]','',eval(macrosname))
                                macros_keys['data'].append({macros: realmacrosname})
                                for realkey in itemkeys.keys():
                                    sendhandle.send(host, '{}[{}]'.format(realkey,realmacrosname), eval(realkey))
                            sendhandle.send(host,itemkeynames,json.dumps(macros_keys,sort_keys=True,indent=7,separators=(',',':')))
                        else:
                            for i in xrange(len(keys_list)):
                                try:
                                    exec '{}={}'.format(keys_list[i], sqlresult[0][i])
                                except:
                                    exec "{}='{}'".format(keys_list[i], sqlresult[0][i])
                            for itemkey, value in itemkeys.items():
                                exec '{}={}'.format(itemkey, value)
                            for realkey in itemkeys.keys():
                                sendhandle.send(host,realkey,eval(realkey))
                    elif rowkeys and rowkey and rowvalue:
                        for i in xrange(len(rowkeys)):
                            try:
                                exec '{}={}'.format(rowkeys[i], sqlresult[i][0])
                            except:
                                exec "{}='{}'".format(rowkeys[i], sqlresult[i][0])
                        sendhandle.send(host, rowkey, eval(rowvalue))
                    else:
                        for i in xrange(len(keys_list)):
                            sendhandle.send(host,keys_list[i],sqlresult[0][i])
                else:
                    ErrorQ.put('sql<{}>获取的列数跟配置的keys个数不一致！'.format(sql))
            else:
                if len(keys_list)!=1:
                    ErrorQ.put('sql<{}>获取不到数据！'.format(sql))
                else:
                    sendhandle.send(host, keys_list[0], 'none')
        ora.close()
def make_sqls_dic(base_path,cron_conf,ErrorQ):
    ora_conf=ConfigParser.ConfigParser()
    ora_conf.read(os.path.join(os.path.join(base_path,'conf'),'orapybbix.ini'))
    try:
        sqls_list=ora_conf.get(cron_conf,'sqls').split(',')
    except:
        sqls_list=[]
    sqls={}
    for sql in sqls_list:
        try:
            sqls[sql]={'sql':ora_conf.get(cron_conf,'{}_sql'.format(sql)),'keys':ora_conf.get(cron_conf,'{}_keys'.format(sql)).split(',')}
        except:
            ErrorQ.put('{}_sql或者{}_keys获取失败！'.format(sql,sql))
        else:
            itemkeys_str = False
            try:
                itemkeys={}
                itemkeys_str=ora_conf.get(cron_conf,'{}_itemkeys'.format(sql))
                for itemkey in itemkeys_str.split(','):
                    itemkeys[itemkey]=ora_conf.get(cron_conf,itemkey)
            except:
                if itemkeys_str:
                    ErrorQ.put('itemkeys<{}>获取失败！'.format(itemkeys_str))
            else:
                sqls[sql]['itemkeys']=itemkeys
            itemkeynames=False
            macros=False
            macrosname=False
            try:
                itemkeynames=ora_conf.get(cron_conf,'{}_itemkeynames'.format(sql))
                macros=ora_conf.get(cron_conf,'{}_macros'.format(sql))
                macrosname=ora_conf.get(cron_conf,'{}_macrosname'.format(sql))
            except:
                if itemkeynames or macros or macrosname:
                    ErrorQ.put('{}_itemkeynames或者{}_macros或者{}_macrosname获取失败！'.format(sql, sql,sql))
            else:
                sqls[sql]['itemkeynames']=itemkeynames
                sqls[sql]['macros'] = macros
                sqls[sql]['macrosname'] = macrosname
            rowkeys=False
            rowkey=False
            rowvalue=False
            try:
                rowkeys=ora_conf.get(cron_conf,'{}_rowkeys'.format(sql)).split(',')
                rowkey=ora_conf.get(cron_conf,'{}_rowkey'.format(sql))
                rowvalue = ora_conf.get(cron_conf, '{}_rowvalue'.format(sql))
            except:
                if rowkeys or rowkey or rowvalue:
                    ErrorQ.put('{}_rowkeys或者{}_rowkey或者{}_rowvalue 获取失败！'.format(sql, sql, sql))
            else:
                sqls[sql]['rowkeys'] = rowkeys
                sqls[sql]['rowkey'] = rowkey
                sqls[sql]['rowvalue'] = rowvalue
    return sqls
def StartOrapybbix(conf_path,base_path,cron_conf):
    conf=ConfigParser.ConfigParser()
    conf.read(conf_path)
    hosts = conf.get('orapybbixservers', 'hosts').split(',')
    orapybbixlogfile=conf.get('orapybbixservers', 'orapybbixerrorlog')
    websugarurl = conf.get('websugar', 'url')
    T_list = []
    ErrorQ=Queue.Queue()
    sqls_dic = make_sqls_dic(base_path,cron_conf,ErrorQ)
    for host in hosts:
        host_connstr=conf.get('orapybbixservers', host)
        T = Thread(target=check_ora, args=(host_connstr,host, websugarurl,ErrorQ,sqls_dic))
        T.start()
        T_list.append(T)
    for T in T_list:
        T.join()
    write_log(orapybbixlogfile,ErrorQ)


