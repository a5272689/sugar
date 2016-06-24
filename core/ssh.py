# -*- coding:utf-8 -*-
#author:hjd
import paramiko
def sshrun(user,passwd,ip,port,cmd):
    try:
        # 测试连接
        transport = paramiko.Transport((ip, port))
        transport.connect(username=user, password=passwd)
    except:
        pass
    else:
        ssh = paramiko.SSHClient()
        ssh._transport = transport
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result=stdout.readlines()
        transport.close()
        return result
def sshrunerr(user,passwd,ip,port,cmd):
    try:
        # 测试连接
        transport = paramiko.Transport((ip, port))
        transport.connect(username=user, password=passwd)
    except:
        pass
    else:
        ssh = paramiko.SSHClient()
        ssh._transport = transport
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result=stderr.readlines()
        transport.close()
        return result