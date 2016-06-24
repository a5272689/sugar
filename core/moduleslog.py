# -*- coding:utf-8 -*-
#author:hjd
from datetime import datetime
def write_log(logfile,ErrorQ):
    with open(logfile,'a') as fp:
        for i in range(ErrorQ.qsize()):
            fp.write('{} WARNING {}\n'.format(datetime.now(),ErrorQ.get()))