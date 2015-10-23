#!/usr/bin/python

__author__ = 'suksubra'
import json
import pexpect
import re
import os
import sys,time,math


hostName = os.environ.get('SYSENG_DUT');
chassis = hostName
#prompt = "(\[^ \r\n]\[^\r\n]*\[#>\$] ?|\# \[%])$"
prompt = '\[local](.*)#'
print chassis

fileName = "/tmp/poll/json/" + hostName +".json"
logFile = "/tmp/poll/log/" + hostName +".log"

csvPath = os.environ.get('SYSENG_CSV')
data = {'csv' : csvPath}
with open(fileName, 'w') as json_file:
    json.dump(data, json_file)

id= re.findall('\d+' , hostName)
host = '10.84.18.' + id[0]

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
with open(fileName, 'w') as json_file:
    json.dump(data, json_file)

### Crash Info:
child.sendline ('show crash list')
child.expect (prompt)
buff = child.before
#log the lines to hostName.log
with open(logFile, "w") as log:
    log.write(buff+"\n/#/#/")

match2=re.search(r'Total Crashes\s*:\s*(\w+)',buff)
try:
    crashes =  match2.group(1)
except AttributeError:
    crashes ='0'

crash = {'Crashes' : crashes}
data.update(crash)
with open(fileName, 'w') as json_file:
    json.dump(data, json_file)

###Chasssis Uptime:
child.sendline ('show system uptime')
child.expect (prompt)
buff = child.before
match3=re.search(r'System uptime:\s*(\w+\s*\w+\s*\w+)',buff)
try:
   uptime = {'Uptime' : match3.group(1)}
except AttributeError:
    uptime = {'Uptime' : 'null'}

data.update(uptime)
with open(fileName, 'w') as json_file:
    json.dump(data, json_file)

###Chasssis Name:
try:
    chassisInfo = {'name' : hostName}
except AttributeError:
    chassisInfo = {'name' : 'null'}

data.update(chassisInfo)
with open(fileName, 'w') as json_file:
    json.dump(data, json_file)

### SRP State
child.sendline ('show srp info')
child.expect (prompt)
buff = child.before
match4=re.search(r'Chassis State:\s*(\w+)',buff)
match5=re.search(r'Chassis Mode:\s*(\w+)',buff)
match6=re.search(r'Peer State:\s*(\w+)',buff)
match7=re.search(r'Peer Mode:\s*(\w+)',buff)

try:
    srpState = {'SRP_State' :  match5.group(1) + '-' + match4.group(1) + '/' + match7.group(1) + '-' + match6.group(1)}

except AttributeError:
	srpState = {'SRP_State' : "SRP not Configured"}

data.update(srpState)
with open(fileName, 'w') as json_file:
    json.dump(data, json_file)


### Diameter Peers:
child.sendline ('show diameter peers full all')
child.expect (prompt)
buff = child.before
matchPeers=re.search(r'Total peers matching specified criteria:\s*(\w+)',buff)
matchOpenPeers=re.search(r'Peers in OPEN state:\s*(\w+)',buff)
matchClosedPeers=re.search(r'Peers in CLOSED state:\s*(\w+)',buff)
matchInterPeers=re.search(r'Peers in intermediate state:\s*(\w+)',buff)
try:
        DiameterPeers = {'Diameter_Peers' : matchPeers.group(1) + '/' + matchOpenPeers.group(1) + '/' + matchInterPeers.group(1)+ '/' + matchClosedPeers.group(1)}
except AttributeError:
        DiameterPeers = {'Diameter_Peers(T/O/I/C)' : "Information not available"}

data.update(DiameterPeers)
with open(fileName, 'w') as json_file:
    json.dump(data, json_file)

child.sendline ('show diameter peers full all| grep Peers')
child.expect (prompt)
buff = child.before
with open(logFile, "a") as log:
    log.write(buff+"\n/#/#/")

child.sendline ('show srp info')
child.expect (prompt)
buff = child.before
with open(logFile, "a") as log:
    log.write(buff+"\n/#/#/")

log.close()

child.sendline ('exit')
