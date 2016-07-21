# -*- coding:utf-8 -*-
#author:hjd
import subprocess,ConfigParser,os,re
from threading import Thread
from core import sendto,ssh
def checkjstat(host,jpsname,websugarurl):
    jps=subprocess.Popen('jps|grep {}'.format(jpsname),shell=True,stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    jpspid = jps.stdout.readline()
    javaversion = subprocess.Popen('java -version'.format(jpsname), shell=True, stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    javaversion = javaversion.stderr.readline()
    if javaversion:
        javaversion = re.findall(r'\"(.+?)\"', javaversion)[0]
    javapath= subprocess.Popen('which java'.format(jpsname), shell=True, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    javapath=javapath.stdout.readline()
    if javapath:
        javapath = os.path.dirname(os.path.dirname(javapath))
    if jpspid:
        jpspid = jpspid.split()[0]
        jstat = subprocess.Popen('jstat -gc {}'.format(jpspid), shell=True, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        jstat = jstat.stdout.readlines()
        sendjstatresult(host,jstat,websugarurl,javaversion,javapath)
    else:
        sendjstatresult(host, ['',''], websugarurl,javaversion,javapath)

def sendjstatresult(host,jstat,websugarurl,javaversion,javapath):
    hostname, jbossname, jbossversion = host.split('|')
    sendhandle = sendto.sendtowebsugar(websugarurl)
    if jstat[0] and jstat[1]:
        sendhandle.send(hostname, 'jbossjavastatus', 1)
    else:
        sendhandle.send(hostname, 'jbossjavastatus', 0)
    sendhandle.send(hostname, 'jbossversion',jbossversion)
    sendhandle.send(hostname,'jbossname',jbossname)
    sendhandle.send(hostname,'jbossjavaversion',javaversion)
    sendhandle.send(hostname,'jbossjavapath',javapath)
    keys = jstat[0].split()
    values = jstat[1].split()
    for i in xrange(len(keys)):
        key = 'jbossgc_{}'.format(keys[i])
        sendhandle.send(hostname, key, values[i])



def remotecheckjstat(host,jpsname,websugarurl,user,passwd,ip,port):
    jpspid=ssh.sshrun(user,passwd,ip,port,'source /etc/profile&&source $HOME/.bash_profile&&jps|grep {}'.format(jpsname))
    javaversion=ssh.sshrunerr(user,passwd,ip,port,'source /etc/profile&&source $HOME/.bash_profile&&java -version')
    if javaversion:
        javaversion=re.findall(r'\"(.+?)\"',javaversion[0])[0]
    javapath = ssh.sshrun(user, passwd, ip, port, 'source /etc/profile&&source $HOME/.bash_profile&&which java')
    if javapath:
        javapath=os.path.dirname(os.path.dirname(javapath[0].strip()))
    if jpspid:
        jpspid = jpspid[0].split()[0]
        jstat=ssh.sshrun(user,passwd,ip,port,'source /etc/profile&&source $HOME/.bash_profile&&jstat -gc {}'.format(jpspid))
        sendjstatresult(host, jstat, websugarurl,javaversion,javapath)
    else:
        sendjstatresult(host,['',''],websugarurl,javaversion,javapath)


def checkjava(conf_path):
    conf=ConfigParser.ConfigParser()
    conf.read(conf_path)
    hosts=conf.get('checkJbossServers','host').split(',')
    jpsname = conf.get('checkJbossServers', 'jpsname').split(',')
    websugarurl=conf.get('websugar','url')
    try:
        user = conf.get('checkJbossServers', 'user')
        passwd = conf.get('checkJbossServers', 'passwd')
        ips = conf.get('checkJbossServers', 'ip').split(',')
        port = int(conf.get('checkJbossServers', 'port'))
    except:
        checkjstat(hosts[0],jpsname[0],websugarurl)
    else:
        T_list=[]
        for i in xrange(len(hosts)):
            T = Thread(target=remotecheckjstat, args=(hosts[i],jpsname[i],websugarurl,user,passwd,ips[i],port,))
            T.start()
            T_list.append(T)
            #remotecheckjstat(host,jpsname,websugarurl,user,passwd,ip,port)
        for T in T_list:
            T.join()


