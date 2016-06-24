# -*- coding:utf-8 -*-
#author:hjd
import subprocess,ConfigParser
from core import sendto,ssh
def checkjstat(host,jpsname,websugarurl):
    jps=subprocess.Popen('jps|grep {}'.format(jpsname),shell=True,stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    jpspid = jps.stdout.readline()
    if jpspid:
        jpspid = jpspid.split()[0]
        jstat = subprocess.Popen('jstat -gc {}'.format(jpspid), shell=True, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        jstat = jstat.stdout.readlines()
        sendjstatresult(host,jstat,websugarurl)

def sendjstatresult(host,jstat,websugarurl):
    keys = jstat[0].split()
    values = jstat[1].split()
    for i in xrange(len(keys)):
        key = 'gc_{}'.format(keys[i])
        sendhandle = sendto.sendtowebsugar(websugarurl)
        sendhandle.send(host, key, values[i])

def remotecheckjstat(host,jpsname,websugarurl,user,passwd,ip,port):
    jpspid=ssh.sshrun(user,passwd,ip,port,'source /etc/profile&&source $HOME/.bash_profile&&jps|grep {}'.format(jpsname))
    if jpspid:
        jpspid = jpspid[0].split()[0]
        jstat=ssh.sshrun(user,passwd,ip,port,'source /etc/profile&&source $HOME/.bash_profile&&jstat -gc {}'.format(jpspid))
        sendjstatresult(host, jstat, websugarurl)


def checkjava(conf_path):
    conf=ConfigParser.ConfigParser()
    conf.read(conf_path)
    hosts=conf.get('checkJVMservers','host')
    jpsname = conf.get('checkJVMservers', 'jpsname')
    websugarurl=conf.get('websugar','url')
    try:
        user = conf.get('checkJVMservers', 'user')
        passwd = conf.get('checkJVMservers', 'passwd')
        ip = conf.get('checkJVMservers', 'ip')
        port = int(conf.get('checkJVMservers', 'port'))
    except:
        host=hosts.split(',')[0]
        checkjstat(host,jpsname,websugarurl)
    else:
        for host in hosts.split(','):
            remotecheckjstat(host,jpsname,websugarurl,user,passwd,ip,port)


