
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

print('creating users');
atnr.createUser('Alan Abrams', jmsCredential, 'Alan Abrams');
atnr.createUser('Bob Babbit', jmsCredential, 'Bob Babbit');
atnr.createUser('Clive Chan', jmsCredential, 'Clive Chan');
atnr.createUser('Debra Delany', jmsCredential, 'Debra Delany');
atnr.createUser('Emily Evans', jmsCredential, 'Emily Evans');
atnr.createUser('Frank Fish', jmsCredential, 'Frank Fish');
atnr.createUser('Gilbert Gold', jmsCredential, 'Gilbert Gold');
atnr.createUser('Hilda Hinton', jmsCredential, 'Hilda Hinton');

atnr.createUser('Ian Ivanoff', jmsCredential, 'Ian Ivanoff');
atnr.createUser('Jake James', jmsCredential, 'Jake James');
atnr.createUser('Karen Kane', jmsCredential, 'Karen Kane');
atnr.createUser('Linda Lamas', jmsCredential, 'Linda Lamas');

print('creating groups');
atnr.createGroup('Associate Typist', 'Associate Typist');
atnr.createGroup('Typist', 'Typist');
atnr.createGroup('Mgr', 'Manager');
atnr.createGroup('VP', 'Vice President');
atnr.createGroup('IT', 'Information Technology Administrators');

print('adding users to groups');
atnr.addMemberToGroup('Associate Typist', 'Alan Abrams');
atnr.addMemberToGroup('Associate Typist', 'Bob Babbit');

atnr.addMemberToGroup('Typist', 'Clive Chan');
atnr.addMemberToGroup('Typist', 'Debra Delany');
atnr.addMemberToGroup('Typist', 'Emily Evans');
atnr.addMemberToGroup('Typist', 'Frank Fish');
atnr.addMemberToGroup('Typist', 'Gilbert Gold');

atnr.addMemberToGroup('Mgr', 'Frank Fish');
atnr.addMemberToGroup('Mgr', 'Gilbert Gold');
atnr.addMemberToGroup('Mgr', 'Hilda Hinton');
atnr.addMemberToGroup('Mgr', 'Ian Ivanoff');

atnr.addMemberToGroup('VP', 'Jake James');
atnr.addMemberToGroup('VP', 'Karen Kane');

atnr.addMemberToGroup('IT', 'Linda Lamas');

print('Finished');
