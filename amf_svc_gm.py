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
    zoofiles = ['/zookeeper/watchdog/bin/watchdog.pid']
           
    def __init__(self, svc, home):
        amfservice.__init__(self, svc, home)
        val = os.getenv('USE_ZOOKEEPER')
        self.zookeeper_exists = False
        if val and val.lower() == "true":
            self.zookeeper_exists = True
            self.pidfiles.extend(self.zoofiles)
            zmap = self.get_zookeeper_properties()
            if 'dataDir' in zmap:
                dataDir  = zmap['dataDir']
                self.pidfiles.extend([dataDir+'/zookeeper_server.pid'])
        val = os.getenv('USE_REAPER')
        self.reaper_exists = False
        if val and val.lower() == "true":
            self.reaper_exists = True



    def get_zookeeper_properties(self):
        pmap = {}
        pfile = os.environ["AMF_GM_HOME"]+"/zookeeper/conf/zoo.cfg"
        if os.path.isfile(pfile):
            d = open(pfile, 'r').read()
            for line in d.split('\n'):
                line = line.strip()
                if line.startswith("#"):
                    continue
                vals = line.split("=", 1)
                if len(vals) == 2:
                    key = vals[0].strip()
                    val = vals[1].strip()
                    pmap[key] = val
        return pmap


    def start(self):
        self.suppress_output = True
        status = 0
        self.printer.info('GM service is starting')   
        if self.run(self.home+'/MailboxUtilities/bin/startGM.sh', printflag=False):
            if str(self.outbuf).find('Starting Cassandra ... STARTED') != -1:
                if self.reaper_exists and str(self.outbuf).find('Cassandra Reaper ... ... ... STARTED') != -1:
                    if self.zookeeper_exists and str(self.outbuf).find('Starting ZooKeeper ... STARTED') != -1:
                        if str(self.outbuf).find('Starting WatchDog ... STARTED') != -1:
                            pass
                        else:
                            print('WatchDog failed to start')
                            status = 1
                    elif self.zookeeper_exists:
                        print('Zookeeper failed to start')
                        if str(self.outbuf).find('Starting WatchDog ... STARTED') == -1:
                            print('WatchDog failed to start')
                        status = 2
                elif self.reaper_exists:
                    print('Cassandra Reeper failed to start')
                    if self.zookeeper_exists and str(self.outbuf).find('Starting ZooKeeper ... STARTED') == -1:
                        print('Zooker failed to start')

                    if self.zookeeper_exists and str(self.outbuf).find('Starting WatchDog ... STARTED') == -1:
                        print('WatchDog failed to start')
                    status = 3
                else:
                    if self.zookeeper_exists and str(self.outbuf).find('Starting ZooKeeper ... STARTED') != -1:
                        if str(self.outbuf).find('Starting WatchDog ... STARTED') != -1:
                            pass
                        else:
                            print('WatchDog failed to start')
                            status = 1
                    elif self.zookeeper_exists:
                        print('Zookeeper failed to start')
                        if str(self.outbuf).find('Starting WatchDog ... STARTED') == -1:
                            print('WatchDog failed to start')
                        status = 2
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
            print('GM pre-requisite services started successfully')
        return status

    def stop(self):
        status = 0
        self.printer.info('GM pre-requisite services are stopping')   
        if self.run(self.home+'/MailboxUtilities/bin/stopGM.sh', printflag=False):
            if str(self.outbuf).find('Stopping Cassandra ... ... STOPPED') != -1:
                if str(self.outbuf).find('Stopping Cassandra Reaper ... ... STOPPED') != -1:
                    if str(self.outbuf).find('Stopping ZooKeeper ... ... STOPPED') != -1:
                        if str(self.outbuf).find('Stopping WatchDog ... ... STOPPED') != -1:
                            pass
                        else:
                            status = 1
                            print('Failed to stop WatchDog')
                    elif self.zookeeper_exists:
                        print('Failed to stop Zookeeper')
                        if str(self.outbuf).find('Stopping WatchDog ... ... STOPPED') == -1:
                            print('Failed to WatchDog')
                        status = 2
                elif self.reaper_exists:
                    print('Failed to stop Cassandra Reeper')
                    if self.zookeeper_exists and str(self.outbuf).find('Stopping ZooKeeper ... ... STOPPED') == -1:
                        print('Failed to stop Zookeeper')
                    if self.zookeeper_exists and str(self.outbuf).find('Stopping WatchDog ... ... STOPPED') == -1:
                        print('Failed to WatchDog')
                    status = 3
                else:
                    if self.zookeeper_exists and str(self.outbuf).find('Stopping ZooKeeper ... ... STOPPED') != -1:
                        if str(self.outbuf).find('Stopping WatchDog ... ... STOPPED') != -1:
                            pass
                        else:
                            status = 1
                            print('Failed to stop WatchDog')
                    elif self.zookeeper_exists:
                        print('Failed to stop Zookeeper')
                        if str(self.outbuf).find('Stopping WatchDog ... ... STOPPED') == -1:
                            print('Failed to WatchDog')
                        status = 2
            else:
                print('Failed to stop Cassandra')
                if str(self.outbuf).find('Stopping Cassandra Reaper ... ... STOPPED') == -1:
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
            self.printer.info("GM pre-requisite services are up")
        else:
            self.printer.info("GM pre-requisite services are down")
        return status


