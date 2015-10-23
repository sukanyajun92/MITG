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
chassisLog = "/tmp/poll/access_log.txt"

csvPath = os.environ.get('SYSENG_CSV')
data = {'csv' : csvPath}
with open(fileName, 'w') as json_file:
    json.dump(data, json_file)

id= re.findall('\d+' , hostName)
length = len(id)
host = '10.84.18.' + id[length-1]

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
lines = buff.split('\n')

crashLog = ""
for line in lines:
    if "show crash list" not in line and "show crash all" not in line:
        crashLog += line

with open(logFile, "w") as log:
    log.write(crashLog+"\n\n\n\n#")

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

lines = buff.split('\n')
srpLog = ""
for line in lines:
    if "show srp info" not in line:
        srpLog += line

with open(logFile, "a") as log:
    log.write(srpLog+"\n\n\n\n#")

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

child.sendline ('show diameter peers | grep Endpoint')
child.expect (prompt)
buff = child.before
#print buff + "\n"
lines = buff.split('\n')

peerLog = "Context " + " EndPoint " + " T/O/C/I"
peerLog+= "\n________________________"
with open(logFile, "a") as log:
    log.write(peerLog+"\n")

for line in lines:
   # print line + "\n"
    if "Endpoint:" in line:
        endPoint = line.split(':')[2].rstrip()
        context = line.split(':')[1].split(" ")[1].strip('\r')
        child.sendline ('show diameter peers full endpoint ' + endPoint)
        child.expect (prompt)
        buff = child.before
        matchPeers=re.search(r'Total peers matching specified criteria:\s*(\w+)',buff)
        matchOpenPeers=re.search(r'Peers in OPEN state:\s*(\w+)',buff)
        matchClosedPeers=re.search(r'Peers in CLOSED state:\s*(\w+)',buff)
        matchInterPeers=re.search(r'Peers in intermediate state:\s*(\w+)',buff)

        try:
            peerLog= context + " " + endPoint+ " " +  matchPeers.group(1) + '/' + matchOpenPeers.group(1) + '/' + matchInterPeers.group(1)+ '/' + matchClosedPeers.group(1)

        except AttributeError:
            peerLog = endPoint+" " + ' Info not found'

        with open(logFile, "a") as log:
            log.write(peerLog+"\n")

    else:
        continue

with open(logFile, "a") as log:
    log.write('\n\n\n\n#')

child.sendline ('show task resources | grep -v good')
child.expect (prompt)
buff = child.before

taskLog = ""
lines = buff.split('\n')
for line in lines:
    if "Total " not in line and "show task resources" not in line:
        taskLog += line

with open(logFile, "a") as log:
    log.write(taskLog + '\n\n\n\n#')

log.close()

line = os.popen('tail -1 /etc/httpd/logs/access_log').read()
ip = line.split('"')

if "&chassis" in ip[3]:
    chassis = ip[3].split('&chassis=')
    log_text = ip[0] + " monitoring chassis = " + chassis[1] + "\n"

else:
    log_text = ip[0] + "\n"

with open(chassisLog, "a") as clog:
     clog.write(log_text)

clog.close()
child.sendline ('exit')
