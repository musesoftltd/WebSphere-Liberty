import getopt
from java.io import FileInputStream
from java.lang import System
from java.util import Properties
import os
import sys

from weblogic.management.scripting.utils.offline_nonsupported import addTemplate
from wlst.WlstWrapper import readDomain, updateDomain, closeDomain


if __name__ == '__main__': 
    from wlstModule import *  # @UnusedWildImport
    


def usage():
    print "Usage:"
    print "ExtendDomain.py -t domainDir -p <properties> <template-files>"

#=======================================================================================
# get domain properties.
#=======================================================================================

props = Properties()
domainDir = ""
properties = ""
template = ""

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

# The list of template files should now be in args
print "Template files to extend domain are: "
print args

propsInputStream = FileInputStream(properties)
props.load(propsInputStream)

#=======================================================================================
# Apply domain extension templates in turn
#=======================================================================================

readDomain(domainDir)
for template in args:
	print "Applying extension template " + template
	addTemplate(template)

updateDomain()
closeDomain()
print "script returns SUCCESS"   

#=======================================================================================
# Exit 
#=======================================================================================

exit()


