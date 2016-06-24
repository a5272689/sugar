# -*- coding:utf-8 -*-
#author:hjd
import os,ConfigParser,logging,sys,time
from multiprocessing import Process,freeze_support
from apscheduler.schedulers.blocking import BlockingScheduler
base_path=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_path)
from core import checkhost,checkurl,checkJVM,tuxedobbix,orapybbix,mysqlbbix
conf_path=os.path.join(os.path.join(base_path,'conf'),'sugar.ini')
log_path=os.path.join(os.path.join(base_path,'log'),'sugar.log')
sugarconf=ConfigParser.ConfigParser()
sugarconf.read(conf_path)
logging.basicConfig(level=logging.WARNING,filename=log_path,filemode='a',format='%(asctime)s %(levelname)s %(message)s',datefmt='%Y/%m/%d %H:%M:%S')

def cronsleep(func,sleeptime,args):
    scheduler = BlockingScheduler()
    scheduler.add_job(func=func,trigger='cron',args=args,minute='*/{}'.format(sleeptime))
    try:
        scheduler.start()
    except Exception as e:
        print e
def crontiming(func,timing,args):
    scheduler = BlockingScheduler()
    scheduler.add_job(func=func,trigger='cron',args=args,hour='{}'.format(timing))
    try:
        scheduler.start()
    except Exception as e:
        print e
if __name__ == '__main__':
    #freeze_support()
    P_list=[]
    if sugarconf.get('switch','orapybbix') == 'on':
        sleeptime1=int(sugarconf.get('orapybbixservers','sleeptime1'))
        orapybbix_P=Process(target=cronsleep,args=(orapybbix.StartOrapybbix,sleeptime1,(conf_path,base_path,'sleeptime1'),),name='orapybbix_s1')
        orapybbix_P.start()
        P_list.append(orapybbix_P)
        sleeptime2=int(sugarconf.get('orapybbixservers','sleeptime2'))
        orapybbix_P=Process(target=cronsleep,args=(orapybbix.StartOrapybbix,sleeptime2,(conf_path,base_path,'sleeptime2'),),name='orapybbix_s2')
        orapybbix_P.start()
        P_list.append(orapybbix_P)
        timing1=sugarconf.get('orapybbixservers','timing1')
        orapybbix_P=Process(target=crontiming,args=(orapybbix.StartOrapybbix,timing1,(conf_path,base_path,'sqlconftiming1'),),name='orapybbix_t1')
        orapybbix_P.start()
        P_list.append(orapybbix_P)
        timing2=sugarconf.get('orapybbixservers','timing2')
        orapybbix_P=Process(target=crontiming,args=(orapybbix.StartOrapybbix,timing2,(conf_path,base_path,'sqlconftiming2'),),name='orapybbix_t2')
        orapybbix_P.start()
        P_list.append(orapybbix_P)
    if sugarconf.get('switch','mysqlbbix') == 'on':
        sleeptime=int(sugarconf.get('mysqlbbixservers','sleeptime'))
        mysqlbbix_P=Process(target=cronsleep,args=(mysqlbbix.StartMysqlbbix,sleeptime,(conf_path,base_path,),),name='mysqlbbix')
        mysqlbbix_P.start()
        P_list.append(mysqlbbix_P)
    if sugarconf.get('switch','checkhost') == 'on':
        sleeptime=int(sugarconf.get('checkhostservers','sleeptime'))
        checkhost_P=Process(target=cronsleep, args=(checkhost.checkhost,sleeptime,(conf_path,),),name='checkhost')
        checkhost_P.start()
        P_list.append(checkhost_P)
    if sugarconf.get('switch','checkurl') == 'on':
        sleeptime=int(sugarconf.get('checkurlservers','sleeptime'))
        checkurl_P=Process(target=cronsleep, args=(checkurl.checkHTTP,sleeptime,(conf_path,),),name='checkurl')
        checkurl_P.start()
        P_list.append(checkurl_P)
    if sugarconf.get('switch','checkJVM') == 'on':
        sleeptime=int(sugarconf.get('checkJVMservers','sleeptime'))
        checkJVM_P=Process(target=cronsleep, args=(checkJVM.checkjava,sleeptime,(conf_path,),),name='checkJVM')
        checkJVM_P.start()
        P_list.append(checkJVM_P)
    if sugarconf.get('switch','tuxedopybbix') == 'on':
        sleeptime=int(sugarconf.get('tuxedopybbixservers','sleeptime'))
        tuxedopybbix_P=Process(target=cronsleep, args=(tuxedobbix.checktuxedo,sleeptime,(conf_path,),),name='tuxedopybbix')
        tuxedopybbix_P.start()
        P_list.append(tuxedopybbix_P)
    while True:
        time.sleep(600)
        for P in P_list:
            if not P.is_alive():
                P.start()
                logging.error('进程{}死掉已重启！'.format(P.name))
