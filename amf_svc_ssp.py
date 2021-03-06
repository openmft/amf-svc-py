'''
##################################################################################
# License: MIT
# Copyright 2018 Agile Data Inc
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of 
# this software and associated documentation files (the "Software"), to deal in 
# the Software without restriction, including without limitation the # rights to 
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
# the Software, and to permit persons to whom the Software is furnished to do so, 
# subject to the following conditions:
# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE # AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
# OR THE USE OR OTHER DEALINGS IN  # THE SOFTWARE.
##################################################################################
'''
from amf import amfservice
import time

class ssp(amfservice):
    """
    IBM SSP
    This service controls SSP.
    """
    
    def __init__(self, svc, home):
        amfservice.__init__(self, svc, home)
        self.svc = svc
        self.home = home
           
    def start(self):
        """start SSP"""
        self.printer.info("service starting")
        status = self.run(self.home+"/bin/startEngine.sh >/dev/null 2>&1", noWait=True)
        if status:
            self.printer.error("service start failed")   
        else:
            while True:
                time.sleep(3)
                status = self.run("ps -ef|grep -v grep|grep SSPPlatformFactory|grep -c java", printflag=False)
                val = self.outbuf[0]
                if val > 0:
                    break
        return status 

    def stop(self):
        """stop SSP"""
        self.printer.info("service stopping")
        self.run(self.home+"/bin/stopEngine.sh mode=auto") 
        time.sleep(15)
        self.run("kill -9 `ps -ef|grep -v grep|grep SSPPlatformFactory|grep java|awk '{ print $2 }'` >/dev/null 2>&1; echo", printflag=False)

    def restart(self):
        """stops and starts SSP"""
        self.stop()
        status = self.start()
        return status
    
    def status(self):
        """reports status SSP"""
        self.printer.info("checking service status")
        status = 0
        found = False
        clist = []
        clist.append("%-20s%-12s%-10s" % ('PID FILE', 'PID', 'RUNNING'))
        clist.append('------------------------------------------')
        self.run("ps -ef | grep -v grep | grep SSPPlatformFactory| cut -c1-30", printflag=False)
        line = self.outbuf
        pid = 'unknown'
        for line in self.outbuf:
            vals = line.split()
            if len(vals) > 1:
                if vals[0] == 'admin':
                    found = True
                    pid = vals[1]
                    break
        clist.append("%-20s%-12s%-10s" % ('NA', pid, found))
        self.printer.info(clist)
        if found:
            self.printer.info("SSP is running")
        else:
            self.printer.info("SSP is not running")
            status = 1
        return status
