#!/usr/bin/python2.4

########################################
#Author: Sripada Rao (sriprao@cisco.com)
#Initial Version: 12/1/2011
########################################

import pexpect
import re
import time,sys,math


if len(sys.argv) < 3:
  print 'Usage: %s <host> <option to display>' %(sys.argv[0])
  sys.exit(1)

host= sys.argv[1]
option=int(sys.argv[2])

def main():
  child = pexpect.spawn ('telnet ' + host)
  child.expect ('login: ')
  child.sendline ('staradmin')
  child.expect ('password:')
  child.sendline ('starent')
  child.expect ('\[local](.*)#')

  child.sendline ('show version')
  child.expect ('\[local](.*)#')
  buff = child.before

  match=re.search(r'\s*Image Version:\s*(\w+\.\w+.\w+.\w+)',buff)

  child.sendline ('show crash list')
  child.expect ('\[local](.*)#')
  buff = child.before

  for lines in buff:
      a= buff.split('\n')
  match1=re.search(r'No crash record found',buff)
  if option==0:
      if (match1):
        print "\nNo crashes observed during the run\n"
      else:
        match2=re.search(r'Total Crashes\s*:\s*(\w+)',buff)
        print "Total crashes observed during the run: %s\n"%(match2.group(1))
        for line in a:
	    if (re.search(r'%s'%(match.group(1)),line)):
	       print '%s'%(line)    

  else:
      child.sendline ('show crash list')
      child.expect ('\[local](.*)#')
      buff = child.before

      print buff

      child.sendline ('show crash all')
      child.expect ('\[local](.*)#')
      buff = child.before
  
      print buff       


  child.sendline ('exit')





if __name__ == "__main__":
    main()






