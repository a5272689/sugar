# -*- coding:utf-8 -*-
#author:hjd
import subprocess,ConfigParser
from threading import Thread
from core import sendto
def checkping(ip,count,host,websugarurl):
    a=subprocess.Popen('ping {} -c {} -W 1'.format(ip,count),shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    result = a.stdout.readlines()
    result = result[len(result) - 2].split()
    if '%' in result[5]:
        result=result[5].split(b'%')[0]
    else:
        result=result[7].split(b'%')[0]
    sendhandle=sendto.sendtowebsugar(websugarurl)
    sendhandle.send(host,'packet_loss',result)

def checkhost(conf_path):
    conf=ConfigParser.ConfigParser()
    conf.read(conf_path)
    hosts=conf.get('checkhostservers','hosts').split(',')
    pingcount=int(conf.get('checkhostservers','pingcount'))
    websugarurl=conf.get('websugar','url')
    T_list=[]
    for host in hosts:
        T=Thread(target=checkping,args=(conf.get('checkhostservers','_'.join([host,'ip'])),
                                        pingcount,host,websugarurl,
                                        ))
        T.start()
        T_list.append(T)
    for T in T_list:
        T.join()


