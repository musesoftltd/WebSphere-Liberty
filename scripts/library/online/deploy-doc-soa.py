
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
listenAddress1 = props.get("Servers.soa_server1.ListenAddress")
listenPort1 = props.get("Servers.soa_server1.ListenPort")
listenAddress2 = props.get("Servers.soa_server2.ListenAddress")
listenPort2 = props.get("Servers.soa_server2.ListenPort")
# JMS account
jmsPrincipal = props.get("jmsPrincipal")
jmsCredential = props.get("jmsCredential")

weblogicUsername = props.get("weblogicUsername")
weblogicPassword = props.get("weblogicPassword")
weblogicDomain = props.get("weblogicDomain")

if jdbcDatabase == "Oracle" :
	dirDocumakerJ2ee = dirDocumakerHome + '/j2ee/weblogic/oracle11g';

if jdbcDatabase == "DB2" :
	dirDocumakerJ2ee = dirDocumakerHome + '/j2ee/weblogic/db2v97';

sca_deployComposite('http://' + listenAddress1 + ':' + listenPort1, dirDocumakerJ2ee + '/bpel/sca_iDMkr_Correspondence_rev1.0.jar', true, adminUserName, adminPassword);
sca_deployComposite('http://' + listenAddress1 + ':' + listenPort1, dirDocumakerJ2ee + '/bpel/sca_iDMkrApprovalRulesProj_rev1.0.jar', true, adminUserName, adminPassword);

sca_deployComposite('http://' + listenAddress2 + ':' + listenPort2, dirDocumakerJ2ee + '/bpel/sca_iDMkr_Correspondence_rev1.0.jar', true, adminUserName, adminPassword);
sca_deployComposite('http://' + listenAddress2 + ':' + listenPort2, dirDocumakerJ2ee + '/bpel/sca_iDMkrApprovalRulesProj_rev1.0.jar', true, adminUserName, adminPassword);
