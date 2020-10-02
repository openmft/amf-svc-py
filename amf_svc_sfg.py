'''
##################################################################################
# License: MIT
# Copyright 2018 Agile Data Inc
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the # rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN  # THE SOFTWARE.
##################################################################################
'''
from amf import amfservice
import os
import json

class sfg(amfservice):
    '''
    IBM Sterling File Gateway
    This service controls all local components for SFG, GM, and CLA2
    '''
           
    def start(self):
        '''start SFG, GM, and CLA2 components'''
        self.suppress_output = True
        running = self.status()
        if running == 0:
            self.printer.info('SFG service is already running.')
        else:
            self.printer.info('SFG service is starting')   
            status = 0
            if self.run(self.home+'/bin/run.sh', printflag=False):
                if str(self.outbuf).find('Run hardstop.sh to kill the corresponding processes') != -1:
                    self.printer.info('SFG service is already running, quiting')
                elif str(self.outbuf).find('Server SIServer started with process ID') != -1:
                    self.printer.info('Sfg service started successfully.')
                else:
                    status = 1
            if 'SFG_EXTERNAL_PURGE' in os.environ:
                if os.environ['SFG_EXTERNAL_PURGE'].upper() == 'TRUE':
                    print('Starting external purge')
                    if self.run(self.home+'/bin/control_extpurge.sh start',printflag=False):
                        if str(self.outbuf).find('already running') != -1:
                            print('External purge already started')
                        elif str(self.outbuf).find('External Purge started') == -1:
                            print('Failed to start External Purge')
                            status = 1
                        else:
                            print('External purge started successfully')
            if status:
                self.printer.error('service start failed')   
            return status 

    def stop(self):
        '''stops SFG, GM, and CLA2 components'''
        status = 0
        #self.run(self.home+'/bin/hardstop.sh')
        if self.run(self.home+'/bin/hardstop.sh', printflag=False):
            if str(self.outbuf).find('kill: usage:') != -1:
                status = 1
        if 'GlobalMailbox' in os.environ:
            if self.run(self.home+'/MailboxUtilities/bin/stopGM.sh', printflag=False):
                if str(self.outbuf).find('is not running') != -1:
                    status = 1
        if 'SFG_EXTERNAL_PURGE' in os.environ:
            if os.environ['SFG_EXTERNAL_PURGE'].upper() == 'TRUE':
                print('Stopping external purge')
                if self.run(self.home+'/bin/control_extpurge.sh stop',printflag=False):
                    if str(self.outbuf).find('your Purge does not appear to be running') != -1:
                        print('External purge does not appear to be running')
                    elif str(self.outbuf).find('killing external purge') == -1:
                        status = 1
        if status:
            self.printer.info('service is not running')   
        #return status 
        return 0

    def restart(self):
        '''stops and starts SFG, GM, and CLA2 components'''
        status = self.stop()
        if status == 0:
            status = self.start()
        return status
    
    def status(self):
        '''reports status on all local SFG components'''
        self.printer.info('checking service status')
        status = 0
        count = 0
        clist = []
        clist.append('%-50s%-12s%-10s' % ('PID FILE', 'PID', 'RUNNING'))
        clist.append('---------------------------------------------------------')
        self.run('ps -ef | grep java | cut -c1-30', printflag=False)
        pidfiles = []
        for fname in os.listdir(self.home):
            if not fname.endswith('.pid') or fname.startswith('gis') or fname.startswith('ext'):
                continue
            pidfiles.append(self.home+'/'+fname)

        for filename in ['ops.pid','noapp.pid']:
            if self.home+'/'+filename not in pidfiles:
                pidfiles.append(self.home+'/'+filename)

        for fname in pidfiles:
            if os.path.exists(fname):
                count += 1
                f = open(fname)
                pid = f.read().strip()
                f.close()
            else:
                pid = 'not found'
            found = False
            for line in self.outbuf:
                vals = line.split()
                if vals[1] == pid:
                    found = True
                    break
            clist.append('%-50s%-12s%-10s' % (fname, pid, found))
            if not found:
                status = 1 
        if 'GlobalMailbox' in os.environ:
            self.run("ps -ef | grep mailboxui | grep -v grep | awk '{print $2}'",printflag=True) 
            mailboxui_pid = str(self.outbuf).replace('[','').replace("'","").replace(']','')
            if mailboxui_pid != "":
                clist.append('%-50s%-12s%-10s' % ("mailboxui", mailboxui_pid , True))
            else:
                self.printer.info('Global Mailbox UI Service is not running')
                status = 1

        if 'SFG_EXTERNAL_PURGE' in os.environ:
            if os.environ['SFG_EXTERNAL_PURGE'].upper() == 'TRUE':
                self.run("ps -ef | grep purge | grep hpp | grep -v grep | awk '{print $2}'",printflag=True) 
                extpurge_pid = str(self.outbuf).replace('[','').replace("'","").replace(']','')
                if extpurge_pid != "":
                    if extpurge_pid.find(",") != -1:
                        extpurge_pid  = extpurge_pid.split(',')[0]
                    clist.append('%-50s%-12s%-10s' % ("extpurge", extpurge_pid , True))
                else:
                    self.printer.info('External Purge is not running')
                    status = 1

        if not hasattr(self,'suppress_output'):
            if count > 0:
                self.printer.info(clist)
            else:
                status = 1
                self.printer.info('no sfg service pid files found')
            if status == 0:
                self.printer.info('all sfg services are running')
            else:
                self.printer.info('not all sfg services are running ')
        return status
