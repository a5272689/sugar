# -*- coding:utf-8 -*-
#author:hjd
import subprocess,ConfigParser,re,json,paramiko
from threading import Thread
from core import sendto,ssh
def bbptmadmin(result,websugarurl,host):
    for i in xrange(len(result)):
        if re.findall(r'> Bulletin Board Parameters:',result[i]):
            sendhandle = sendto.sendtowebsugar(websugarurl)
            sendhandle.send(host, 'MAXSERVERS',result[i+1].strip().split()[1])
            sendhandle.send(host, 'MAXSERVICES', result[i + 2].strip().split()[1])
            sendhandle.send(host, 'MAXACCESSERS', result[i + 3].strip().split()[1])
            break
def bbstmadmin(result,websugarurl,host):
    for i in xrange(len(result)):
        if re.findall(r'> Current Bulletin Board Status:',result[i]):
            sendhandle = sendto.sendtowebsugar(websugarurl)
            sendhandle.send(host, 'Current_number_of_servers',result[i+1].strip().split(':')[1].strip())
            sendhandle.send(host, 'Current_number_of_services', result[i + 2].strip().split(':')[1].strip())
            sendhandle.send(host, 'Current_number_of_request_queues', result[i + 3].strip().split(':')[1].strip())
            sendhandle.send(host, 'Current_number_of_server_groups', result[i + 4].strip().split(':')[1].strip())
            sendhandle.send(host,'Current_number_of_interfaces',result[i + 5].strip().split(':')[1].strip())
            break

def tmadminV(result,websugarurl,host):
    # print result
    result=result[0].split(',')
    sendhandle = sendto.sendtowebsugar(websugarurl)
    sendhandle.send(host, 'tuxedoversion', result[1].strip())
    sendhandle.send(host, 'tuxedobit', result[2].strip())

def pqtmadmin(result,websugarurl,host):
    # total=0
    # wktotal=0
    # for i in result:
    #     i=i.split()
    #     if i[0]=='-':
    #         i[0]=0
    #     total += int(i[1])
    #     wktotal += int(i[0])
    # sendhandle = sendto.sendtowebsugar(websugarurl)
    # sendhandle.send(host,'queuedcount',str(total))
    # sendhandle.send(host,'queuedcount',str(wktotal))
    # if wktotal:
    #     sendhandle.send(host,'queuedcountp',float(total)/float(wktotal)*100)
    # else:
    #     sendhandle.send(host, 'queuedcountp', 0)
    keys = {"data": []}
    sendhandle = sendto.sendtowebsugar(websugarurl)
    for i in result:
        i=i.split()
        tempkey='|'.join([i[0],i[1],i[6]])
        keys["data"].append({'{#T_Q_NAME}':tempkey})
        for num in xrange(3,6):
            if i[num]=='-':
                i[num]=0
            else:
                i[num]=int(i[num])
        sendhandle.send(host,'WkQueued_[{}]'.format(tempkey),i[3])
        sendhandle.send(host, 'TQQueued_[{}]'.format(tempkey), i[4])
        sendhandle.send(host, 'TQavgLen_[{}]'.format(tempkey), i[5])
    sendhandle.send(host, 'tuxedo_queue', json.dumps(keys,sort_keys=True,indent=7,separators=(',',':')))


def psctmadmin(result,websugarurl,host):
    keys = {"data": []}
    sendhandle = sendto.sendtowebsugar(websugarurl)
    for i in result:
        i=i.split()
        tempkey='|'.join([i[0],i[1],i[3],i[4]])
        keys["data"].append({'{#TUXEDOIDNAME}':tempkey})
        sendhandle.send(host,'done_[{}]'.format(tempkey),int(i[6]))
        if i[7]=='AVAIL':
            i[7]=1
        else:
            i[7]=0
        sendhandle.send(host, 'status_[{}]'.format(tempkey), i[7])
    sendhandle.send(host, 'tuxedoservice_name', json.dumps(keys,sort_keys=True,indent=7,separators=(',',':')))


def remotecheck(host,websugarurl,user,passwd,ip,port):
    bbptmadminresult=ssh.sshrun(user,passwd,ip,port,'source /etc/profile&&source $HOME/.bash_profile&&echo bbp|tmadmin -r')
    bbptmadmin(bbptmadminresult,websugarurl,host)
    # bbstmadminresult=ssh.sshrun(user,passwd,ip,port,'source /etc/profile&&source $HOME/.bash_profile&&echo bbs|tmadmin -r')
    # bbstmadmin(bbstmadminresult,websugarurl,host)
    tmadminvresult=ssh.sshrunerr(user,passwd,ip,port,'source /etc/profile&&source $HOME/.bash_profile&&tmadmin -v')
    tmadminV(tmadminvresult,websugarurl,host)
    pqtmadminresult=ssh.sshrun(user,passwd,ip,port,
                                "source /etc/profile&&source $HOME/.bash_profile&&echo pq|tmadmin -r|grep -Ev '^>|^$|^-'")
    pqtmadmin(pqtmadminresult,websugarurl,host)
    psctmadminresult=ssh.sshrun(user,passwd,ip,port,
                                "source /etc/profile&&source $HOME/.bash_profile&&echo psc|tmadmin -r|grep -Ev '^>|^$|^-'")
    psctmadmin(psctmadminresult,websugarurl,host)

def localcheck(host,websugarurl):
    bbptmadminresult = subprocess.Popen('echo bbp|tmadmin -r',
                                        shell=True, stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
    bbptmadmin(bbptmadminresult.stdout.readlines(),websugarurl,host)
    # bbstmadminresult = subprocess.Popen('echo bbs|tmadmin -r',
    #                                     shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    #                                     stderr=subprocess.PIPE)
    # bbstmadmin(bbstmadminresult.stdout.readlines(),websugarurl,host)
    tmadminvresult = subprocess.Popen('tmadmin -v',
                                        shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
    tmadminV(tmadminvresult.stderr.readlines(),websugarurl,host)
    pqtmadminresult=subprocess.Popen("echo pq|tmadmin -r|grep -Ev '^>|^$|^-'",
                               shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    pqtmadmin(pqtmadminresult.stdout.readlines(),websugarurl,host)
    psctmadminresult=subprocess.Popen("echo psc|tmadmin -r|grep -Ev '^>|^$|^-'",
                                shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    psctmadmin(psctmadminresult.stdout.readlines(),websugarurl,host)

def checktuxedo(conf_path):
    conf=ConfigParser.ConfigParser()
    conf.read(conf_path)
    hosts=conf.get('tuxedopybbixservers','host')
    websugarurl=conf.get('websugar','url')
    try:
        user = conf.get('tuxedopybbixservers', 'user')
        passwd = conf.get('tuxedopybbixservers', 'passwd')
        ip = conf.get('tuxedopybbixservers', 'ip')
        port = int(conf.get('tuxedopybbixservers', 'port'))
    except:
        host=hosts.split(',')[0]
        localcheck(host,websugarurl)
    else:
        T_list=[]
        for host in hosts.split(','):
            T = Thread(target=remotecheck, args=(host,websugarurl,user,passwd,ip,port,))
            T.start()
            T_list.append(T)
            # remotecheck(host,websugarurl,user,passwd,ip,port)
        for T in T_list:
            T.join()


