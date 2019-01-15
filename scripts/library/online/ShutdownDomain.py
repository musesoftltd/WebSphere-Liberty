import getopt
from java.io import FileInputStream
from java.lang import System
from java.util import Properties
import os
import sys

from weblogic.management.scripting.core.utils.wlst_core import WLSTException
from wlst.WlstWrapper import connect, cd, shutdown, disconnect


if __name__ == '__main__': 
    from wlstModule import *  # @UnusedWildImport
    


def usage():
    print "Usage:"
    print "ShutdownDomain.py -t domainDir -p <properties>"

#=======================================================================================
# get domain properties.
#=======================================================================================

props = Properties()
domainDir = ""
properties = ""
nodemgrHomeDir = ""

try:
    opts, args = getopt.getopt(sys.argv[1:], "p:t:")
except getopt.GetoptError, err:
    print str(err)
    usage()
    sys.exit(2)

for opt, arg in opts:
    if opt == "-t":
        domainDir = arg
    elif opt == "-p":
        properties = arg

if domainDir == "":
    print "Missing \"-t domainDir\" parameter."
    usage()
    sys.exit(2)

if properties == "":
    print "Missing \"-p Property File\" parameter."
    usage()
    sys.exit(2)

propsInputStream = FileInputStream(properties)
props.load(propsInputStream)

print "Shutting down domain" + domainDir
try:
	connect(props.get('adminUserName'), props.get('adminPassword'), 't3://' + props.get('listenAddress') + ':' + props.get('listenPort'))
	cmo = cd('/')
	adminServerName = cmo.getAdminServerName()
	cmo = cd('/Servers')
	servers = cmo.getServers()
	# Shut down all managed servers first
	for server in servers:
		if (server.getName() != adminServerName):
			try:
				shutdown(server.getName(), block='true')
			except:
				print 'Unable to shutdown server ' + server.getName()

	# Now shutdown admin server
	shutdown(block='false')
	disconnect()
	print "Shutdown completed"
except WLSTException:
	print 'Unable to connect to admin server: domain may already have shut down'

exit()



