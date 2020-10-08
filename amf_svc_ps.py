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

import os

class ps(amfservice):
    """ IBM Sterling File Gateway Perimiter Server Components
    This service controls all local PS components """

    #Add your PS installation paths relative from $AMF_PS_HOME if there are more than one PS installations on the same server
    psfolders = []
    def __init__(self, svc, home):
        amfservice.__init__(self, svc, home)
        self.svc = svc
        self.home = home
           
    def start(self):
        """start local PS components"""
        status = 0
        self.printer.info("service starting")
        for folder in self.psfolders:
            if self.run(self.home+folder+'/startupPs.sh', printflag=False):
                if str(self.outbuf).find("already running") != -1:
                    self.printer.info("service %s already running" % folder)
                else:
                    status = 1
        if status:
            self.printer.error("service start failed")   
        return status 

    def stop(self):
        """stops local PS components"""
        status = 0
        for folder in self.psfolders:
            if self.run(self.home+folder+'/stopPs.sh'):
                status = 1
        if status:
            self.printer.error("service stop failed")   
        return status 

    def restart(self):
        """stops and starts local PS components"""
        status = self.stop()
        if status == 0:
            status = self.start()
        return status

    def status(self):
        """reports status on all local SFG components"""
        self.printer.info("checking service status")
        status = 0
        clist = []
        clist.append("%-35s%-12s%-10s" % ('PID FILE', 'PID', 'RUNNING'))
        clist.append('---------------------------------------------------------')
        self.run("ps -ef | grep java | cut -c1-30", printflag=False)
        pidfiles = []
        for folder in self.psfolders:
            pidfiles.append(self.home+folder+'/ps.pid')
        for fname in pidfiles:
            if os.path.exists(fname):
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
            clist.append("%-35s%-12s%-10s" % (fname, pid, found))
            if not found:
                status = 1 
        self.printer.info(clist)
        if status == 0:
            self.printer.info("ps services all running")
        else:
            self.printer.info("ps services not running")
        return status
