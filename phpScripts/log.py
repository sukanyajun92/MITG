#!/usr/bin/python

__author__ = 'suksubra'
import  os

line = os.popen('tail -1 /etc/httpd/logs/access_log').read()
print "line =%s " %line

ip = line.split('"')
print ip[0]

if "&chassis" in ip[3]:
    chassis = ip[3].split('&chassis=')
    print "Chassis = " + chassis[1]

else:
    print "Not yet"