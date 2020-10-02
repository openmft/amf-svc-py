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
import time

class gm(amfservice):
    '''
    IBM Sterling File Gateway
    This service controls all local components for GM
    '''
    pidfiles = ['/apache-cassandra/bin/cassandra.pid']
    zoofiles = ['/zookeeper/data/zookeeper_server.pid',
                '/zookeeper/watchdog/bin/watchdog.pid']
           
    def __init__(self, svc, home):
        amfservice.__init__(self, svc, home)
        val = os.getenv('USE_ZOOKEEPER')
        if val and val.lower() == "true":
            self.pidfiles.extend(self.zoofiles)

    def start(self):
        self.suppress_output = True
        status = 0
        self.printer.info('GM service is starting')   
        if self.run(self.home+'/MailboxUtilities/bin/startGM.sh', printflag=False):
            if str(self.outbuf).find('Starting Cassandra ... STARTED') != -1:
                if str(self.outbuf).find('Cassandra Reaper ... ... ... STARTED') != -1:
                    if str(self.outbuf).find('Starting ZooKeeper ... STARTED') != -1:
                        if str(self.outbuf).find('Starting WatchDog ... STARTED') != -1:
                            pass
                        else:
                            print('WatchDog failed to start')
                            status = 1
                    else:
                        print('Zookeeper failed to start')
                        if str(self.outbuf).find('Starting WatchDog ... STARTED') == -1:
                            print('WatchDog failed to start')
                        status = 2
                else:
                    print('Cassandra Reeper failed to start')
                    if str(self.outbuf).find('Starting ZooKeeper ... STARTED') == -1:
                        print('Zooker failed to start')

                    if str(self.outbuf).find('Starting WatchDog ... STARTED') == -1:
                        print('WatchDog failed to start')
                    status = 3
            else:
                print('Cassandra failed to start')
                if str(self.outbuf).find('Cassandra Reaper ... ... ... STARTED') == -1:
                    print('Cassandra Reaper failed to start')
                if str(self.outbuf).find('Starting ZooKeeper ... STARTED') == -1:
                        print('Zooker failed to start')

                if str(self.outbuf).find('Starting WatchDog ... STARTED') == -1:
                    print('WatchDog failed to start')
                status = 4
        if status:
            print('Failed to start some or all of GM service(s)')
        else:
            print('GM Services started successfully')
        return status

    def stop(self):
        status = 0
        self.printer.info('GM service is starting')   
        if self.run(self.home+'/MailboxUtilities/bin/stopGM.sh', printflag=False):
            if str(self.outbuf).find('Stopping Cassandra ... ... STOPPED ') != -1:
                if str(self.outbuf).find('Stopping Cassandra Reaper ... ... STOPPED ') != -1:
                    if str(self.outbuf).find('Stopping ZooKeeper ... ... STOPPED') != -1:
                        if str(self.outbuf).find('Stopping WatchDog ... ... STOPPED') != -1:
                            pass
                        else:
                            status = 1
                            print('Failed to stop WatchDog')
                    else:
                        print('Failed to stop Zookeeper')
                        if str(self.outbuf).find('Stopping WatchDog ... ... STOPPED') == -1:
                            print('Failed to WatchDog')
                        status = 2
                else:
                    print('Failed to stop Cassandra Reeper')
                    if str(self.outbuf).find('Stopping ZooKeeper ... ... STOPPED') == -1:
                        print('Failed to stop Zookeeper')
                    if str(self.outbuf).find('Stopping WatchDog ... ... STOPPED') == -1:
                        print('Failed to WatchDog')
                    status = 3
            else:
                print('Failed to stop Cassandra')
                if str(self.outbuf).find('Stopping Cassandra Reaper ... ... STOPPED ') == -1:
                    print('Failed to stop Cassandra Reaper')
                if str(self.outbuf).find('Stopping ZooKeeper ... ... STOPPED') == -1:
                    print('Failed to stop Zookeeper')
                if str(self.outbuf).find('Stopping WatchDog ... ... STOPPED') == -1:
                    print('Failed to WatchDog')
                status = 4
        if status:
            print('Failed to stop some or all GM Service(s)')
        return status


    def restart(self):
        self.stop()
        time.sleep(10)
        self.start()


    def status(self):
        """reports status of all local GM components"""
        self.printer.info("checking service status")
        status = 0
        count = 0
        clist = []
        clist.append("%-60s%-12s%-10s" % ('PID FILE', 'PID', 'RUNNING'))
        clist.append('-------------------------------------------------------------------------------')
        self.run("ps -ef | grep java | cut -c1-30", printflag=False)
        for fname in self.pidfiles:
            found = False
            pid = ''
            if os.path.exists(self.home+fname):
                count += 1
                f = open(self.home+fname)
                pid = f.read().strip()
                f.close()
                for line in self.outbuf:
                    vals = line.split()
                    if vals[1] == pid:
                        found = True
                        break
            clist.append("%-60s%-12s%-10s" % (fname, pid, found))
            if not found:
                status = 1 
        if count == 0: status = 1
        self.printer.info(clist)
        if status == 0:
            self.printer.info("gm status is good")
        else:
            self.printer.info("gm status is bad")
        return status


