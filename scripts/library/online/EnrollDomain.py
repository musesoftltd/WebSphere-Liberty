import getopt
from java.io import FileInputStream
from java.lang import System
from java.util import Properties
import os
import sys

from com.muse.properties.secure import EncryptionUtils
from weblogic.management.scripting.utils.wlst import nmEnroll
from wlst.WlstWrapper import connect, disconnect


if __name__ == '__main__': 
    from wlstModule import *  # @UnusedWildImport
    



def usage():
    print "Usage:"
    print "EnrollDomain.py -t domainDir -p <properties> -n nodemgrHomeDir"

def getPassword(props, key):
    ENCRPYTED_VALUE_PREFIX = "::ENCRYPTED::"
    password = props.get(key)
    if password :
        passkey = props.get('security.passkey')

        if password.startswith(ENCRPYTED_VALUE_PREFIX):
            password = EncryptionUtils.decryptString(passkey, password[len(ENCRPYTED_VALUE_PREFIX):])

    return password

#=======================================================================================
# get domain properties.
#=======================================================================================

props = Properties()
domainDir = ""
properties = ""

try:
    opts, args = getopt.getopt(sys.argv[1:], "p:t:n:", ["domainDir=", "nodemgrHomeDir="])
except getopt.GetoptError, err:
    print str(err)
    usage()
    sys.exit(2)

for opt, arg in opts:
    if opt == "-t":
        domainDir = arg
    elif opt == "-p":
        properties = arg
    elif opt == "-n":
        nodemgrHomeDir = arg

if domainDir == "":
    print "Missing \"-t domainDir\" parameter."
    usage()
    sys.exit(2)

if properties == "":
    print "Missing \"-p Property File\" parameter."
    usage()
    sys.exit(2)

if nodemgrHomeDir == "":
    print "Missing \"-n nodemgrHomeDir\" parameter."
    usage()
    sys.exit(2)

propsInputStream = FileInputStream(properties)
props.load(propsInputStream)

adminUserName = props.get('adminUserName')
adminAddress = props.get('listenAddress')
domainName = props.get('domainName')

adminPassword = getPassword(props, 'adminPassword')

adminURL = 't3://' + adminAddress + ':' + props.get('listenPort')

connect(adminUserName, adminPassword, adminURL)
print "Connecting to admin server with url: " + adminURL
connect(adminUserName, adminPassword, adminURL)
nmEnroll(domainDir, nodemgrHomeDir)
disconnect()

print "Enroll returns SUCCESS"   

exit()


