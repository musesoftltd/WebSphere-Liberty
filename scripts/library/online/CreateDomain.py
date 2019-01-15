import getopt
from java.io import FileInputStream
from java.lang import System
import os

from com.muse.properties.secure import EncryptionUtils
from weblogic.management.scripting.utils.offline_nonsupported import readTemplate, \
    setOption, writeDomain, closeTemplate
from weblogic.management.scripting.utils.wlst import *


if __name__ == '__main__': 
    from wlstModule import *  # @UnusedWildImport
    



def usage():
    print "Usage:"
    print "CreateDomain.py -p domainPropertyFile"

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
domainPropertyFile = ""

try:
    opts, args = getopt.getopt(sys.argv[1:], ":p:",
        ["domainPropertyFile="])
except getopt.GetoptError, err:
    print str(err)
    usage()
    sys.exit(2)

for opt, arg in opts:
    if opt == "-p":
        domainPropertyFile = arg

if domainPropertyFile == "":
    print "Missing \"-p domainPropertyFile\" parameter."
    usage()
    sys.exit(2)

propsInputStream = FileInputStream(domainPropertyFile)
props.load(propsInputStream)

listenAddress = props.get("listenAddress")
listenPort = props.get("listenPort")
sslListenPort = props.get("sslListenPort")
securityRealm = props.get("securityRealm")
username = props.get("adminUserName")


domainHome = props.get("domainHome")

domainTemplate = props.get("templateDomain")

adminPassword = getPassword(props, 'adminPassword')

#=======================================================================================
# Open a domain template.
#=======================================================================================

readTemplate(domainTemplate)

#=======================================================================================
# Configure the Administration Server listen address and ports.
#=======================================================================================

cmo = cd('Servers/AdminServer')
set('ListenAddress', listenAddress)
set('ListenPort', int(listenPort))

create('AdminServer', 'SSL')
cmo = cd('SSL/AdminServer')
set('Enabled', 'True')
set('ListenPort', int(sslListenPort))

#=======================================================================================
# Define the user password for weblogic.
#=======================================================================================

cmo = cd('/')
cmo = cmo = cd('Security/base_domain/User/' + username)
cmo.setPassword(adminPassword)

#=======================================================================================
# Write the domain and close the domain template.
#=======================================================================================

setOption('OverwriteDomain', 'true')
writeDomain(domainHome)
closeTemplate()
print "script returns SUCCESS"   

#=======================================================================================
# Exit 
#=======================================================================================

exit()

