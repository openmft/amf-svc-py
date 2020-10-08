from amf import amfservice

import os

class ps(amfservice):
    """ IBM Sterling File Gateway Perimiter Server Components
    This service controls all local PS components """

    psfolders = ['/ibm/ssp_ps/sfg1', '/ibm/ssp_ps/sfg2']
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
