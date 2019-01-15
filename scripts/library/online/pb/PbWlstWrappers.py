from java.util.logging import Logger
from javax.management import MBeanException
import sys
import traceback

from ConfigureDomain import properties
import PbCommon
import java.lang as lang
from pb import PbWlstLib as pbwl, PbTypes
from weblogic.management.scripting.core.utils.wlst_core import WLSTException
from WlstWrapper import shutdown, readDomain, updateDomain, closeDomain, \
    edit, startEdit, save, activate, silent, divert, X_getMachines, X_getServers, \
    X_getClusters, X_getMachineNamesOffline, cd, cancelEdit, getServerNames, \
    DOMAIN_DIR, nmConnect, startNodeManager, nmStart, assign, unassign, decrypt


class OfflineFunctionCalls:
    def __init__(self, server):
        self.functionCalls = []
        self.name = server

class functionCall :
    def __init__(self, func, args):
        self.func = func
        self.args = args

global OfflineServerFunctionCallDict
OfflineServerFunctionCallDict = dict()

global OfflinePostConfigFunctionCalls
OfflinePostConfigFunctionCalls = []

global OnlinePostConfigFunctionCalls
OnlinePostConfigFunctionCalls = []

global LOGGER
LOGGER = Logger.getLogger("PbWlstWrappers")

global functionCalls
functionCalls = []

def addOfflineFunc(server, func, *args):
    getOfflineFunctionCalls(server).functionCalls.append(functionCall(func, args))

def registerOfflineFunc(server, func):
    def wrapper(*args) :
        getOfflineFunctionCalls(server).functionCalls.append(functionCall(func, args))
    return wrapper

def getOfflineFunctionCalls(server) :
    result = None
    try :
        result = OfflineServerFunctionCallDict.get(server)
    except KeyError :
        pass

    if not result :
        result = OfflineFunctionCalls(server)
        OfflineServerFunctionCallDict[server] = result

    return result

def addOnlinePostConfigFunc(func, *args):
    OnlinePostConfigFunctionCalls.append(functionCall(func, args))

def addOfflinePostConfigFunc(func, *args):
    OfflinePostConfigFunctionCalls.append(functionCall(func, args))


def exit(exitValue):
    lang.System.exit(exitValue)

def switchToOffline() :
    if pbwl.connectToAdminServer() :
#        try :
#            onlineCloseEditSession()
#        except Exception, e :
#            LOGGER.warning("Got Exception in trying to close edit session: " + str(e))
        shutdown()

def switchServerStateToOffline(server) :
    try :
        shutdown(server)
    except WLSTException, e :
        LOGGER.info("Server already shutdown " + server)


def primeOfflineEditSession() :
    domainDir = pbb.properties.get("domainHome")
    primeOfflineCalls(domainDir)
    readDomain(domainDir)

def completeOfflineEditSession() :
    updateDomain()
    closeDomain()

def primeOnlineEditSession() :
    primeOnlineCalls()  # TODO - this is cyclic with runOnline - is that needed?
    edit()
    startEdit()

def completeOnlineEditSession() :
    save()
    activate()

def primeOnlineCalls() :
    PbTypes.getMBeanPath = PbTypes.getMBeanPathOnline

    pbwl.catalogue = runInOnline(pbwl.catalogue)
    getMachines = silent(divert(X_getMachines, "/Machines"))
    getServers = silent(divert(X_getServers, "/Servers"))
    getClusters = silent(divert(X_getClusters, "/Clusters"))
    getMachineNames = divert(X_getMachineNamesOffline, "/Machines")

def primeOfflineCalls(domainDir) :
    PbTypes.getMBeanPath = PbTypes.getMBeanPathOffline

    pbwl.catalogue = runInOffline(pbwl.catalogue, domainDir)

    getMachines = silent(divert(X_getMachines, "/AnyMachine"))
    getServers = silent(divert(X_getServers, "/Server"))
    getClusters = silent(divert(X_getClusters, "/Cluster"))
    getMachineNames = divert(X_getMachineNamesOffline, "/AnyMachine")


def switchToOnline() :
    if not pbwl.connectToAdminServer() :
        startAdminServer()
        if not pbwl.connectToAdminServer() :
            LOGGER.error("Unable to connect to Admin Server")
            raise Exception("Unable to connect to Admin Server")
    primeOnlineEditSession()


def runInOffline(func, location) :
    def wrapper(*args) :
        try :
            primeOfflineEditSession()
            cmo = cd(location)
            result = func(*args)
            completeOfflineEditSession()
            LOGGER.info(str(func) + " returned '" + str(result) + "'")
            return result
        except Exception, e:
            print "Unexpected error in runInOffline: ", sys.exc_info()[0], sys.exc_info()[1]
            tb = sys.exc_info()[2]
            traceback.print_tb(tb)
            raise e
    return wrapper

def runInOnline(func) :
    def wrapper(*args) :
        try :
            switchToOnline()
            result = func(*args)
            completeOnlineEditSession()
            return result
        except Exception, e:
            print "Unexpected error in runInOnline: ", sys.exc_info()[0], sys.exc_info()[1]
            tb = sys.exc_info()[2]
            traceback.print_tb(tb)
            if pbwl.connectToAdminServer() :
                try :
                    cancelEdit("y")
                except MBeanException :
                    LOGGER.error("Failed to stop edit session.")
            raise e
    return wrapper

def emptyList(list) :
    while len(list) > 0 :
        list.pop()

def executeFunctionList(functionList) :
    for functionCall in functionList :
        result = functionCall.func(*functionCall.args)
        LOGGER.info(str(functionCall.func) + " returned '" + str(result) + "'")
    emptyList(functionList)


global executeOfflineRegisteredFunctionCalls
def executeOfflineRegisteredFunctionCalls() :
    # execute all offline functions
    servers = OfflineServerFunctionCallDict.keys()
    for server in servers :
        LOGGER.info("Executing functions for server in offline mode. (server=" + server + ")")
        executeFunctionList(OfflineServerFunctionCallDict.get(server).functionCalls)

def doOfflineRegisteredFunctionCalls() :
    # Ascertain which machines need to go offline:
    servers = OfflineServerFunctionCallDict.keys()
    serversToSwitchOffline = []

    # Swtich those required offline, leaving AdminServer to last
    for server in servers :
        if server == "All":
            serversToSwitchOffline = getServerNames()
            break
        else:
            serversToSwitchOffline.append(server)

    adminServerName = None
    for server in serversToSwitchOffline :
        if server == "AdminServer":
            adminServerName = server
        else :
            LOGGER.info("Switching server into offline mode to execute offline only functions (" + server + ")")
            switchServerStateToOffline(server)

    if adminServerName :
        switchServerStateToOffline(adminServerName)
        global executeOfflineRegisteredFunctionCalls
        executeOfflineRegisteredFunctionCalls = runInOffline(executeOfflineRegisteredFunctionCalls, DOMAIN_DIR)
    else :
        global executeOfflineRegisteredFunctionCalls
        executeOfflineRegisteredFunctionCalls = runInOnline(executeOfflineRegisteredFunctionCalls)

    try :
        executeOfflineRegisteredFunctionCalls()
    except Exception, e:
        print "Unexpected error in executeOfflineRegisteredFunctionCalls: ", sys.exc_info()[0], sys.exc_info()[1]
        tb = sys.exc_info()[2]
        traceback.print_tb(tb)
        raise e


def doOfflinePostConfigFunctions() :

    try :
        switchToOffline()
        f = runInOffline(executeFunctionList, DOMAIN_DIR)
        f(OfflinePostConfigFunctionCalls)
    except :
        print "Unexpected error in executeFunctionList: ", sys.exc_info()[0], sys.exc_info()[1]
        tb = sys.exc_info()[2]
        traceback.print_tb(tb)
        raise

def doOnlinePostConfigFunctions() :
    try :
        f = runInOnline(executeFunctionList)
        f(OnlinePostConfigFunctionCalls)
    except :
        print "Unexpected error in executeFunctionList: ", sys.exc_info()[0], sys.exc_info()[1]
        tb = sys.exc_info()[2]
        traceback.print_tb(tb)
        raise

def doConnectToNodeManager(userName, password, adminListenAddress, nodemgrPort, domainName, domainDir,
                           nodeManagerConnectionType) :
    jsseEnabled = pbwl.props.get("JSSEEnabled")
    if PbCommon.getBoolFromString(jsseEnabled) :
        jsseJvmArgs = pbwl.props.get("javaOptions.jsse")
        print "Trying to connect to Node Manager: userName=" + userName + ", adminListenAddress=" + adminListenAddress + ", nodemgrPort=" + nodemgrPort + ", domainName=" + domainName + ", domainDir" + domainDir + ", nodeManagerConnectionType=" + nodeManagerConnectionType + ", jsseJvmArgs=" + jsseJvmArgs
        nmConnect(userName, password, adminListenAddress, nodemgrPort, domainName, domainDir,
            nodeManagerConnectionType, jsseJvmArgs)
    else:
        nmConnect(userName, password, adminListenAddress, nodemgrPort, domainName, domainDir,
            nodeManagerConnectionType, "")


def connectToNodeManager(userName, password, adminListenAddress, nodemgrPort, domainName, domainDir,
                         nodemgrHome, nodeManagerConnectionType) :
    secureListener = "false"
    if nodeManagerConnectionType == "SSL":
        secureListener = "true"

    try:
        doConnectToNodeManager(userName, password, adminListenAddress, nodemgrPort, domainName, domainDir,
                               nodeManagerConnectionType)
    except WLSTException, e:
        try:
            # todo - check we are on the server - if not need a remote call!
            print "Starting NodeManager with home at " + nodemgrHome
            startNodeManager(nodemgrHome, nodemgrPort, secureListener, adminListenAddress)
            doConnectToNodeManager(userName, password, adminListenAddress, nodemgrPort, domainName, domainDir,
                nodeManagerConnectionType)
        except WLSTException, e:
            LOGGER.severe("Unable to start Node Manager: nmHome=" + nodemgrHome + ", nmPort=" + nodemgrPort)
            raise  e


def startAdminServer() :
    userName = pbwl.props.get("adminUserName")
    password = PbCommon.getDecryptedValue(pbwl.props, "adminPassword")
    adminListenAddress = pbwl.props.get("admin.server.listenAddress")
    domainName = pbwl.props.get("domainName")
    domainDir = pbwl.props.get("domainHome")
    nodemgrPort = pbwl.props.get("wls.NODEMGR_PORT")
    adminServerName = pbwl.props.get("admin.server.name")
    nodemgrHome = pbwl.props.get("wls.NODEMGR_HOME")
    nodeManagerConnectionType = pbwl.props.get("nodemanager.connectionType")

    if not nodeManagerConnectionType:
        nodeManagerConnectionType = "Plain"

    connectToNodeManager(userName, password, adminListenAddress, nodemgrPort, domainName, domainDir,
        nodemgrHome, nodeManagerConnectionType)

    nmStart(adminServerName, domainDir)

def setUp(domainDir) :
    pbwl.configure = runInOnline(pbwl.configure)
    pbwl.configureOffline = runInOffline(pbwl.configureOffline, domainDir)
    assign = registerOfflineFunc("All", assign)
    unassign = registerOfflineFunc("All", unassign)
    DOMAIN_DIR = domainDir
    PbCommon.decryptfunc = decrypt


