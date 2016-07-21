# -*- coding:utf-8 -*-
#author:hjd
import ConfigParser,json
import urllib2
from threading import Thread
from core import sendto
def checkurl(url,key,key2,host,websugarurl):

    url = url
    req = urllib2.Request(url=url)
    try:
        urllib2.urlopen(req)
    except:
        result=0
    else:
        result=1
    sendhandle=sendto.sendtowebsugar(websugarurl)
    sendhandle.send(host,key,result)
    sendhandle.send(host,key2,url)

def checkHTTP(conf_path):
    conf=ConfigParser.ConfigParser()
    conf.read(conf_path)
    hosts=conf.get('checkurlservers','hosts').split(',')
    websugarurl=conf.get('websugar','url')
    T_list=[]

    for host in hosts:
        keys = {"data": []}
        host_urls=conf.get('checkurlservers','_'.join([host,'urls'])).split(',')
        for i in xrange(len(host_urls)):
            url=host_urls[i].split('|')
            if len(url)==1:
                key='url_[{}]'.format(i)
                key2='urlpath_[{}]'.format(i)
                keys['data'].append({'{#URLNAME}':i})
                url=url[0]
            elif len(url)==2:
                key='url_[{}]'.format(url[0])
                key2 = 'urlpath_[{}]'.format(url[0])
                keys['data'].append({'{#URLNAME}':url[0]})
                url=url[1]
            if key:
                T=Thread(target=checkurl,args=(url,key,key2,host,websugarurl))
                T.start()
                T_list.append(T)
        if keys['data']:
            sendhandle=sendto.sendtowebsugar(websugarurl)
            sendhandle.send(host,'find_url',json.dumps(keys,sort_keys=True,indent=7,separators=(',',':')))
    for T in T_list:
        T.join()


