
import getopt
from java.io import FileInputStream
from java.lang import System
from java.util import Properties
import os
import sys

import ConfigureJdbc
import ConfigureMachines
from wlst.WlstWrapper import readDomain, updateDomain, closeDomain


def usage():
    print "Usage:"
    print "ConfigureDomain.py -t <domainDir> -p <properties> -d <domain>"

#=======================================================================================
# get domain properties.
#=======================================================================================

props = Properties()
domainDir = ""
properties = ""

try:
    opts, args = getopt.getopt(sys.argv[1:], "p:d:t:")
except getopt.GetoptError, err:
    print str(err)
    usage()
    sys.exit(2)

for opt, arg in opts:
    if opt == "-d":
        domain = arg
    elif opt == "-p":
        properties = arg
    elif opt == "-t":
        domainDir = arg

if domain == "":
    print "Missing \"-d domain\" parameter."
    usage()
    sys.exit(2)

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

# get JDBC config from property file
url = props.get('rcu.jdbc.ConnectionUrl')

print 'JDBC parameters:'
print 'url = ' + url

#=======================================================================================
# Open the existing domain.
#=======================================================================================
readDomain(domainDir)

#=======================================================================================
# Create machine(s) and assign WebLogic servers to machines.
#=======================================================================================
result = ConfigureMachines.configureMachines(props, domain)
if not result :
    sys.exit(1)

#=======================================================================================
# apply config to each JDBC resource in turn
#=======================================================================================
result = ConfigureJdbc.configureJDBCResources(props, domain, url)
if not result :
    sys.exit(1)

#=======================================================================================
# Save the update domain.
#=======================================================================================
updateDomain()
closeDomain()
print "script returns SUCCESS"

#=======================================================================================
# Exit 
#=======================================================================================

sys.exit()
