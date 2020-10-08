from amf import amfservice
import time

class sspcm(amfservice):
    """
    IBM SSPCM
    This service controls SSPCM.
    """
    
    def __init__(self, svc, home):
        amfservice.__init__(self, svc, home)
        self.svc = svc
        self.home = home
           
    def start(self):
        """start SSPCM"""
        status = self.run("ps -ef | grep -v grep | grep java| grep sspcm", printflag=False)
        if status == 0:
            self.printer.error("sspcm is already running")
        else:
            self.printer.info("service starting")
            status = self.run(self.home+"/bin/startCM.sh >/dev/null 2>&1", noWait=True)
            if status:
                self.printer.error("service start failed")   
            else:
                while True:
                    time.sleep(3)
                    status = self.run("ps -ef|grep -v grep|grep sspcm|grep -c java", printflag=False)
                    val = self.outbuf[0]
                    if val > 0:
                        break
                return status 

    def stop(self):
        """stop SSPCM"""
        status = 0
        self.printer.info("service stopping")
        if self.run(self.home+"/bin/stopCM.sh mode=auto"): 
            self.printer.info("killing service")
            self.run("kill -9 `ps -ef|grep -v grep|grep sspcm|grep java|awk '{ print $2 }'` >/dev/null 2>&1; echo")
        return status 

    def restart(self):
        """stops and starts SSPCM"""
        status = self.stop()
        time.sleep(60)
        if status == 0:
            status = self.start()
        return status
    
    def status(self):
        """reports status on SSPCM"""
        self.printer.info("checking service status")
        status = 0
        found = False
        clist = []
        clist.append("%-20s%-12s%-10s" % ('PID FILE', 'PID', 'RUNNING'))
        clist.append('------------------------------------------')
        self.run("ps -ef | grep -v grep | grep sspcm | grep java| cut -c1-30", printflag=False)
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
            self.printer.info("sspcm is running")
        else:
            self.printer.info("sspcm is not running")
            status = 1
        return status
