
if __name__ == '__main__': 
    from wlstModule import *  # @UnusedWildImport
    
import getopt
from java.io import FileInputStream
from java.lang import System
import os

from com.muse.properties.secure import EncryptionUtils


def usage():
    print "Usage:"
    print "deployDoc -p <properties>"
	# '-all' actions are applied to admin server in addition to managed servers
	# Actions may be prefixed with "test-" to run them in test/simulation mode

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
action = ""
serversToStart = ""
testMode = false

try:
    opts, args = getopt.getopt(sys.argv[1:], "p:")
except getopt.GetoptError, err:
    print str(err)
    usage()
    sys.exit(2)

for opt, arg in opts:
    if opt == "-p":
		properties = arg
	
if properties == "":
    print "Missing \"-p Property File\" parameter."
    usage()
    sys.exit(2)

propsInputStream = FileInputStream(properties)
props.load(propsInputStream)
#=======================================================================================

domainHome = props.get("domainHome")
jdbcDatabase = props.get("jdbcDatabase")
dirDocumakerHome = props.get("dirDocumakerHome")
adminUserName = props.get("adminUserName")
adminPassword = props.get("adminPassword")
listenAddress = props.get("listenAddress")
listenPort = props.get("listenPort")
# JMS account
jmsPrincipal = props.get("jmsPrincipal")
jmsCredential = props.get("jmsCredential")

weblogicUsername = props.get("weblogicUsername")
weblogicPassword = props.get("weblogicPassword")
weblogicDomain = props.get("weblogicDomain")

print('connecting to weblogic with...')
print(' username:' + adminUserName)
print(' password:' + adminPassword)
print(' listenAddress:' + listenAddress)
print(' listenPort:' + listenPort)
connect(adminUserName, adminPassword, 't3://' + listenAddress + ':' + listenPort)

atnr = cmo.getSecurityConfiguration().getDefaultRealm().lookupAuthenticationProvider('DefaultAuthenticator');

print('Creating User : documaker');
atnr.createUser('documaker', jmsCredential, 'Documaker Admin');

print('Creating Group : Documaker Administrators');
atnr.createGroup('Documaker Administrators', 'Documaker Administrators');

print('Adding documaker to Documaker Administrators');
atnr.addMemberToGroup('Documaker Administrators', 'documaker');

try:
    print('Creating User : ' + jmsPrincipal);
    atnr.createUser(jmsPrincipal, jmsCredential, 'JMS Account');
except:
    print(jmsPrincipal + ' accout exists, skipping');
    

print('Finished');
