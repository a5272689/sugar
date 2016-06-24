# -*- coding:utf-8 -*-
#author:hjd
import urllib, urllib2


class sendtowebsugar(object):
    def __init__(self, url):
        self.url = url

    def send(self, hostname, key, value):
        self.textmod = {'hostname': hostname, 'key': key, 'value': value}
        self.textmodcode = urllib.urlencode(self.textmod)
        try:
            self.req = urllib2.Request(url=self.url, data=self.textmodcode)
        except:
            return '5'
        else:
            try:
                self.res = urllib2.urlopen(self.req).read()
            except:
                return '5'
            else:
                if self.res == '3' or self.res == '0' or self.res == '4':
                    return self.res
                else:
                    return '5'