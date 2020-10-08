# Service Manager to start, stop, restart or check status -> amf-svc-py

Service management is part of an overall application framework Agile Message Framework (AMF) and this code base is a subset of a larger infrastructure that is made available as OpenSource under MIT License.  

This has been envisioned to be a generic start, stop, restart processs with pluggable modules for each system or sub-system in any environment.   This was created in the context of Managed File Transfer during our experience with IBM customers using Sterling File Gategway and Axway customers, but could be used for any platform by creating new modules.

# Install

* Clone  or download this repository from https://github.com/openmft/amf-svc-py.git to a directory of your choice.
* Create a symbolic link for amf.py -> ln -s amf.py amf
* Create an environment variable per module. For example, for the module amf_svc_sfg.py, create an Environment variable called AMF_SFG_HOME, which is the base path of Sterling File Gateway (SFG).
* For GM module amf_svc_gm.py, create an Environment variable called AMF_GM_HOME, which is the base path of GM Pre-requisites (Cassandra, Zookeeper, etc)
* Either create an alias for amf or put the path of amf.py in PATH
* If a particular node is an External Purge node, just add an Environment variable called SFG_EXTERNAL_PURGE=true and external purge will automatically be managed for that node in the cluster.
* For PS module amf_svc_ps.py, create an Environment variable called AMF_PS_HOME, which is the base path of Perimeter Server

# Operation

## Start examples
* amf start sfg
* amf start gm
* amf start ps

## Stop examples
* amf stop sfg
* amf stop gm
* amf stop ps

## Restart examples
* amf restart sfg
* amf restart gm
* amf restart ps

## Status examples
* amf status sfg
* amf status gm
* amf status ps
