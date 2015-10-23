#!/usr/bin/python

__author__ = 'suksubra'
import json
import pexpect
import re
import os
import sys,time,math


hostName = os.environ.get('SYSENG_DUT');
#prompt = "(\[^ \r\n]\[^\r\n]*\[#>\$] ?|\# \[%])$"
prompt = '\[local](.*)#'

fileName = "/tmp/poll/json/" + hostName +".json"
logFile = "/tmp/poll/log/" + hostName +".log"
chassisLog = "/tmp/poll/access_log.txt"

csvPath = os.environ.get('SYSENG_CSV')
data = {'csv' : csvPath}
with open(fileName, 'w') as json_file:
    json.dump(data, json_file)

id= re.findall('\d+' , hostName)
length = len(id)
host = '10.84.18.' + id[length-1]

print "host = %s"%host

child = pexpect.spawn ('telnet ' + host)
child.expect ('login: ')
child.sendline ('staradmin')
child.expect ('password:')
child.sendline ('starent')
child.expect (prompt)


### Image Version:
child.sendline ('show version')
child.expect (prompt)
buff = child.before
match1=re.search(r'\s*Image Version:\s*(\w+\.\w+.\w+.\w+)',buff)
try:
    version ={'version' : match1.group(1)}
except AttributeError:
    version ={'version' : 'null'}

data.update(version)
print "data = %s"%data

child.sendline ('exit')