
import getopt
from java.io import FileInputStream
from java.lang import System
from java.util import Properties
import os
import sys


def usage():
    print "Usage:"
    print "ConfigureIAMDomain.py -t <domainDir> -p <properties> -d <domain>"

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

print "ConfigureIAMDomain started"

iam_home_dir = props.get("IAM_HOME")

print "IAM_HOME=" + iam_home_dir

sys.exit()

