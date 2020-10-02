#!/usr/bin/python
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
import os, sys, json
import subprocess
import traceback


class amf_print:
    '''Utiity class for printing json or non json output '''

    def __init__(self, svc):
        self.svc = svc
        self.uiflag = '-u' in sys.argv  # ui flag to write json
        self.verbose = '-v' in sys.argv # make output more verbose
        
    def error(self, data):
        self.write('ERROR', data)
        
    def info(self, data):
        self.write('INFO', data)
        
    def write(self, level, data):
        if self.uiflag:
            # use json when ui flag is set
            if self.verbose or level != 'INFO':
                vals = {'LEVEL':level, 'SVC': self.svc.upper(), 'DATA': data}
                print(json.dumps(vals))
        else:
            if type(data) is list:
                # put >>> in front of listed items
                for line in data:
                    print('>>>\t', line)
            else:
                if level:
                    # print level if specified
                    print(level+':\t', data)
                else:
                    print(data)
                
class amfservice:
    '''
    Implement a subclass of pyservice to create a module to manage a specific application.
    Name the module after the application name.  For example: sfg.py, seas.py, etc.
 
    '''
    
    def __init__(self, service, home):
        self.home = home
        self.service = service
        self.verbose = '-v' in sys.argv
        self.printer = amf_print(service)

    def run(self, command, printflag=True, noWait=False):
        self.outbuf = []  # buffer for stdout
        self.errbuf = []  # buffer for stderr
        # launch process
        if noWait:
            process = subprocess.Popen(command, shell=True, stdout=None, stderr=None)
            process.wait()
            return process.returncode
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # save output in buffer for possible search later
        for line in process.stdout:
            line = line.strip()
            if printflag and self.verbose:
                self.printer.info(line)
            self.outbuf.append(line)
        for line in process.stderr:
            line = line.strip()
            if printflag and self.verbose:
                self.printer.error(line)
            self.errbuf.append(line)
        # wait for process to end
        process.wait()
        # printflag set, print out buffers to help identify problem
        if printflag and process.returncode != 0:
            self.printer.error('%s failed, return code: %d' % (command, process.returncode))
            if not self.verbose:
                self.printer.info('dumping standard output...')
                self.printer.write('STDOUT', self.outbuf)
                self.printer.info('dumping standard error...')
                self.printer.write('STDERR', self.errbuf)
        return process.returncode

class amf:
    '''Help page for AMF v0.1

Usage:  AMF  <command> <service> (options)

Where required 'command' is one of the following:
    help    - will display this information
    list    - list services and service commands    
    
Where required 'service' is either a valid service name or 'all'  
When 'all' is specified, the command will apply to all services.
    
The following optional parameters are supported:
    -v verbose
    -u support ui interactions, returns output in json.

Optional parameters must not contain a space after the hyamfen '-', the options
may be anywhere in the command line.  Here are some examples.  Options may not 
be combined.  Some of the options like -u and all are not implemented yet.
    
    Examples of correct formats: 
        AMF start all -v   
        AMF start -v all
        AMF -v start all
        AMF -v -u start all        
        
    Examples of incorrect formats:
        AMF start all -vu
        AMF start - v all
        
examples of usage:
    'AMF list all' will list all services
    'AMF list sfg' will list all commands supported for sfg
    'AMF start sfg' will start sfg
    'AMF start all' will start all services supporting the 'start' command
    'AMF start sfg -v' will start sfg with verbose output
    'AMF restart sfg' will restart sfg
    'AMF status sfg' will show status for sfg.
    
notes:    
    Commands and services are not case sensitive.
                    
'''    
    GET_HELP = 'type "AMF help" for help'

    def get_parms(self):
        self.printer = amf_print('main')
        command = None
        service = 'all'
        self.svclist = {}
        # skip first parm containing program name
        for arg in sys.argv[1:]:
            # skip flags starting with -
            if arg.startswith('-'): 
                continue
            else:
                # expect service name, then command name
                # flags with - can be anywhere on command line
                if not command:
                    command = arg.lower() 
                else:
                    service = arg.lower()
        if command and service:   
            searchparm = 'AMF_'
            if service != 'all':
                searchparm += service.upper() + '_'
            # find all modules configured in .profile
            # configured using AMF_HOME where ?? is module name 
            # in upper case
            for parm in os.environ.keys():
                if not parm.startswith(searchparm):
                    continue
                svc = parm[4:parm.rindex('_')].lower()
                if svc != '':
                    self.svclist[svc] = os.environ.get(parm)
        return command, service

    def do_list(self, service):
        status = 0
        # for each service home found, list supported commands for service
        if service == 'all':
            self.printer.info('listing all services')
        # for each module, load module, get attributes
        for svc in self.svclist.keys():
            self.printer.info('service [%s]' % svc)
            try:
                # import module
                module = __import__('amf_svc_'+svc)
            except ImportError:
                print(traceback.format_exc())
                self.printer.error('list failed, module not installed [%s.py]' % svc)
                status = 1
                continue
            # get class definition
            myclass = getattr(module, svc)
            # get public class methods
            clist = []
            self.printer.info('service description')
            # get instance of class
            clazz = myclass('amf_svc_'+svc, self.svclist[svc])
            # get class doc string for printing dpc strings
            self.format(clist, clazz)
            # print class info
            self.printer.info(clist)
            clist = []
            self.printer.info('service commands...')
            # get class methods for printing dpc strings
            methods = myclass.__dict__
            mlist = methods.keys()
            mlist.sort()
            for method in mlist:
                # add info for each method
                self.format(clist, clazz, method)
            self.printer.info(clist)
            # this just to suppress warning that myclazz not used
            myclass = clazz 
        return status
    
    def format(self, clist, clazz, method=None):
        if method:
            # if method not special method
            if not method.startswith('_'):
                # get doc string for the method
                strval = eval('clazz.'+method+'.__doc__')
                lines = strval.split('\n')
                clist.append(method + '\t- %s' % lines[0])
                if len(lines) > 1:
                    for line in lines[1:]:
                        if line.strip():
                            clist.append('\t  %s' % line.strip())
        else:
            # get doc string for the class
            for line in clazz.__doc__.split('\n'):
                if line.strip():
                    clist.append('%s' % line.strip())
            
        
    def do_command(self, command, service):
        status = 0
        # svclist is a list of local services supported
        # e.g.  SFG,SEAS
        for svc in self.svclist.keys():
            self.printer.info('processing command - %s %s' % (svc, command))
            try:
                # import service module
                module = __import__('amf_svc_'+svc)
            except ImportError:
                self.printer.error('%s failed, module not installed [%s.py]' % (command, svc))
                status = 1
                continue
            # get class definition
            myclass = getattr(module, svc)
            # create instance of the class
            clazz = myclass(svc, self.svclist[svc])
            # perform specified operation on the class
            # get public class methods
            methods = myclass.__dict__
            # check if method is supported
            method = methods.get(command)
            if not method:
                self.printer.error('%s service does not support command [%s]' % (svc, command))
                status = 1
            else:
                # else run class method
                if eval('clazz.' + command + '()'):
                    status = 1
                # the following to avoid warnings for unused clazz variable
                module = clazz
        return status
    
    def run(self):
        status = 1
        command, service = self.get_parms()
        if not command:
            self.printer.error('no command specified')
            self.printer.write(None, self.GET_HELP)
        elif command == 'help':
            self.printer.write('', self.__doc__)
            status = 0
        elif len(self.svclist) == 0:
            if service == 'all':
                self.printer.error('no services configured in the environment')
            else:
                self.printer.error('service not configured [%s]' % service)
            self.printer.error(self.GET_HELP)   
        elif not command:
            self.printer.error('command not specified')
            self.printer.write('', self.GET_HELP)
        elif not service:        
            self.printer.error('service not specified')
            self.printer.write(None, self.GET_HELP)
        elif command == 'list':
            status = self.do_list(service)
        else:
            status = self.do_command(command, service)
        if command != 'help':
            text = 'FAILED'
            if status == 0:
                text = 'SUCCESS'
            self.printer.write('STATUS', text)
        return status

if __name__ == '__main__':
    amf = amf()
    status = amf.run()
    sys.exit(status)
