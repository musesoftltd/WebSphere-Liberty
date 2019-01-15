import getopt
from java.io import FileInputStream
from java.lang import System
import os

from com.muse.properties.secure import EncryptionUtils
from weblogic.management.scripting.utils.wlst import *
from wlst.WlstWrapper import connect, readDomain, closeDomain, nmConnect, \
    nmStart, nmDisconnect


if __name__ == '__main__':
    from wlstModule import *  # @UnusedWildImport




def usage():
    print "Usage:"
    print "ControlDomain.py -z [ admin | start | stop | stop-all | start-nm ] -p <properties>"

# '-all' actions are applied to admin server in addition to managed servers
# Actions may be prefixed with "test-" to run them in test/simulation mode

def getPassword(props, key):
    ENCRPYTED_VALUE_PREFIX = "::ENCRYPTED::"
    password = props.get(key)
    if password:
        passkey = props.get('security.passkey')

        if password.startswith(ENCRPYTED_VALUE_PREFIX):
            password = EncryptionUtils.decryptString(passkey, password[len(ENCRPYTED_VALUE_PREFIX):])

    return password

def getBoolFromString(str) :
    return (str == "true" or str == "True")


#=======================================================================================
# get domain properties.
#=======================================================================================

props = Properties()
domainDir = ""
properties = ""
global targetHost
targetHost = ""
action = ""
serversToStart = ""
testMode = false

try:
    opts, args = getopt.getopt(sys.argv[1:], "p:z:h:")
except getopt.GetoptError, err:
    print str(err)
    usage()
    sys.exit(2)

for opt, arg in opts:
    if opt == "-z":
        action = arg
    elif opt == "-p":
        properties = arg
    elif opt == "-h":
        targetHost = arg

testMode = action.startswith("test-")

if testMode:
    # we're in test mode
    # drop the 'test-' prefix
    action = action[5:]

if action == "":
    print "Missing \"-z <action>\" parameter."
    usage()
    sys.exit(2)
elif action == "start":
    serversToStart = args
    action = "start"
elif (action != "admin") and (action != "stop") and (action != "stop-all") and (action != "start-nm"):
    print "Invalid \"-z <action>\" parameter '" + action + "'"
    usage()
    sys.exit(2)

if properties == "":
    print "Missing \"-p Property File\" parameter."
    usage()
    sys.exit(2)

propsInputStream = FileInputStream(properties)
props.load(propsInputStream)

adminUserName = props.get('adminUserName')
listenAddress = props.get('listenAddress')
listenPort = props.get('listenPort')
sslPort = props.get('admin.server.ssl.listenPort')
adminPort = props.get('admin.server.adminPort')
sslEnabled = props.get("SSLEnabled")
adminPortEnabled = props.get("admin.server.adminPortEnabled")

connectionUrls = []
if getBoolFromString(adminPortEnabled):
    if adminPort:
        connectionUrls.append("t3s://" + listenAddress + ":" + adminPort)
if getBoolFromString(sslEnabled):
    if sslPort :
        connectionUrls.append("t3s://" + listenAddress + ":" + sslPort)
if listenPort :
    connectionUrls.append("t3://" + listenAddress + ":" + listenPort)



nmPropertiesFileName = props.get("wls.NODEMGR_PROPERTIES")

domainName = props.get("domainName")
domainDir = props.get("domainHome")
nodemgrPort = props.get("wls.NODEMGR_PORT")
nodemgrHome = props.get("wls.NODEMGR_HOME")
nodeManagerConnectionType = props.get("nodemanager.connectionType")
secureListener = "false"
if nodeManagerConnectionType == "SSL":
    secureListener = "true"

if not nodeManagerConnectionType:
    nodeManagerConnectionType = "Plain"

adminPassword = getPassword(props, 'adminPassword')

def connectAdminServer():
    connected = false
    for connectionUrl in connectionUrls :
        try :
            print "Trying to connect to " + connectionUrl
            connect(adminUserName, adminPassword, connectionUrl)
            connected = true
            print "Connected to " + connectionUrl
            break
        except:
            pass

    return connected


def startAdminServer():
    global adminServerName
    if connectAdminServer():
        print "Admin server already started"
        return true
    try:
        print "Getting admin server name from domain at " + domainDir
        readDomain(domainDir)
        cmo = cd('/')
        adminServerName = cmo.getAdminServerName()
        print "Admin server name is " + adminServerName
        closeDomain()
    except:
        print "Unable to get admin server name from domain"
        return false
    try:
        print "Starting admin server with NodeManager"
        print "Connect to NodeManager at " + listenAddress + ":" + nodemgrPort + " as " + adminUserName
        print "...for domain " + props.get("domainName") + " at " + domainDir

        jsseEnabled = props.get("JSSEEnabled")
        if getBoolFromString(jsseEnabled) :
            jsseJvmArgs = props.get("javaOptions.jsse")
            nmConnect(adminUserName, adminPassword, listenAddress, nodemgrPort, props.get("domainName"), domainDir,
                nmType=nodeManagerConnectionType, jvmArgs=jsseJvmArgs)
        else:
            nmConnect(adminUserName, adminPassword, listenAddress, nodemgrPort, props.get("domainName"), domainDir,
                nmType=nodeManagerConnectionType)

        nmStart(adminServerName, domainDir)
        nmDisconnect()
    except:
        print 'Unable to connect to NodeManager for machine ' + listenAddress + ' on port ' + nodemgrPort
        return false
    return true


def stopAdminServer():
    result = true
    # Need to be online to invoke this function
    cmo = cd('/')
    adminServerName = cmo.getAdminServerName()
    try:
        shutdown(adminServerName, block='false')
    except:
        print 'Unable to shutdown admin server ' + adminServerName
        # result = false
        # todo - check if server is running first and return false if cannot shut it down!

    return result


def startAllManagedServers():
    result = true
    # Need to be online to invoke this function
    cmo = cd('/')
    adminServerName = cmo.getAdminServerName()
    cmo = cd('/Servers')
    servers = cmo.getServers()
    # Start all managed servers
    for server in servers:
        if (server.getName() != adminServerName):
            try:
                start(server.getName(), block='true')
            except:
                print 'Unable to start server ' + server.getName()
                result = false
    return result


def startManagedServers():
    result = true
    if serversToStart == []:
        result = startAllManagedServers()
    else:
        # Start named managed servers
        for server in serversToStart:
            cmo = cd('/')
            adminServerName = cmo.getAdminServerName()
            if (server != adminServerName):
                try:
                    start(server, block='true')
                except:
                    print 'Unable to start server ' + server
                    result = false

    return result


def stopManagedServers():
    result = true
    # Need to be online to invoke this function
    cmo = cd('/')
    adminServerName = cmo.getAdminServerName()
    cmo = cd('/Servers')

    servers = cmo.getServers()
    # Shut down all managed servers
    for server in servers:
        if (server.getName() != adminServerName):
            try:
                shutdown(server.getName(), block='true')
            except:
                print 'Unable to shutdown server ' + server.getName()
                # result = false
                # todo - check if server is running first and return false if cannot shut it down!
    return result

def startNM():
    # Try to connect to NodeManager to determine if it is running
    started = false
    try:
        global targetHost
        if targetHost == "":
            targetHost = listenAddress
        print "Attempting to connect to node manager with adminUserName:" + adminUserName + ", ListenAddress:" + targetHost + ", nodemgrPort:" + nodemgrPort + ", domainName: " + domainName + ", domainDir:" + domainDir + ", nmType=" + nodeManagerConnectionType
        nmConnect(adminUserName, adminPassword, targetHost, nodemgrPort, domainName, domainDir,
            nmType=nodeManagerConnectionType)
        # and immediately disconnect, if successful
        nmDisconnect()
        started = true
        print "NodeManager is already started"
    except:
        # Unable to connect to NodeManager, so try to start it up
        started = false

    if not started:
        print "Starting NodeManager with home at " + nodemgrHome + " listening on port " + nodemgrPort
        try:
            startNodeManager(NodeManagerHome=nodemgrHome, ListenPort=nodemgrPort, SecureListener=secureListener, StartScriptEnabled='true', ListenAddress=targetHost)
            started = true
            print "NodeManager start returns SUCCESS"
        except:
            # Unable to start NodeManager
            print "NodeManager start FAILED"
    return started


def startAll():
#    print "Starting Node Manager"
#    if startNM() :
    print "Starting servers"
    if startAdminServer():
        if connectAdminServer():
            if startManagedServers():
                return true
    return false


def stopManagedOnly():
    print "Shutting down all managed servers"
    if startAdminServer():
        if stopManagedServers() :
            return true
    return false


def stopAll():
    print "Shutting down all domain servers"
    if startAdminServer():
        if stopManagedServers() :
            if stopAdminServer() :
                return true
    return false

# Mapping from parameter to function	
invoke = {'admin': startAdminServer, 'start': startAll, 'stop': stopManagedOnly, 'stop-all': stopAll,
          'start-nm': startNM}

# Invoke appropriate function
result = invoke[action]()
if result == false:
    print "Failed!"
    lang.System.exit(1)
lang.System.exit(0)






