# -*- coding:utf-8 -*-
#author:hjd
import MySQLdb,ConfigParser,Queue,os
from threading import Thread
from core import sendto
from moduleslog import write_log
class UseMySQLdb(object):
    def __init__(self,connlist,ErrorQ):
        self.ErrorQ=ErrorQ
        try:
            self.__conn = MySQLdb.connect(host=connlist[0],port=int(connlist[1]),
                                          user=connlist[2],passwd=connlist[3],charset=connlist[4])
        except:
            self.connstatus=0
        else:
            self.dbversion = self.__conn.get_server_info()
            self.connstatus = 1
            self.__cur = self.__conn.cursor()

    def runsql(self, sql):
        if self.connstatus:
            try:
                self.__cur.execute(sql)
            except:
                self.ErrorQ.put('执行SQL<{}>出错！'.format(sql))
                return []
            else:
                return self.__cur.fetchall()

    def msyqlstatus(self):
        statusdic={}
        for status in self.runsql('show status'):
            statusdic[status[0]]=status[1]
        return statusdic

    def close(self):
        self.__cur.close()
        self.__conn.close()

def check_ora(host_connlist,host,websugarurl,check_status_list,ErrorQ):
    mysql=UseMySQLdb(host_connlist,ErrorQ)
    sendhandle = sendto.sendtowebsugar(websugarurl)
    sendhandle.send(host, 'mysqlalive', mysql.connstatus)
    if mysql.connstatus:
        sendhandle.send(host,'mysqlinfo',mysql.dbversion)
        mysqlstatusdic=mysql.msyqlstatus()
        for check_status in check_status_list:
            sendhandle.send(host,check_status,mysqlstatusdic[check_status])
        mysql.close()

def StartMysqlbbix(conf_path,base_path):
    conf=ConfigParser.ConfigParser()
    conf.read(conf_path)
    hosts = conf.get('mysqlbbixservers', 'hosts').split(',')
    orapybbixlogfile=conf.get('mysqlbbixservers', 'mysqlbbixerrorlog')
    websugarurl = conf.get('websugar', 'url')
    mysql_conf=ConfigParser.ConfigParser()
    mysql_conf.read(os.path.join(os.path.join(base_path,'conf'),'mysqlbbix.ini'))
    check_status_list=mysql_conf.get('status','list').split(',')
    T_list = []
    ErrorQ=Queue.Queue()
    for host in hosts:
        host_connlist=conf.get('mysqlbbixservers', host).split(',')
        if len(host_connlist)==5:
            T = Thread(target=check_ora, args=(host_connlist,host, websugarurl,check_status_list,ErrorQ))
            T.start()
            T_list.append(T)
        else:
            ErrorQ.put('主机<{}>的连接信息有问题！'.format(host))
    for T in T_list:
        T.join()
    write_log(orapybbixlogfile,ErrorQ)
