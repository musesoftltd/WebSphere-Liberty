from java.lang import String
from java.lang import System
import re
import sys

from com.muse.fmw.platform import NullPrintStream
import weblogic.management.scripting.utils.WLSTInterpreter as wlst
from weblogic.management.scripting.utils.online_append import *
from weblogic.management.scripting.utils.wlst import *
from weblogic.management.scripting.utils.wlst_common import *
from weblogic.security.internal import SerializedSystemIni
from weblogic.security.internal.encryption import ClearOrEncryptedService


global STATE_MAPS
STATE_MAPS = dict()

# WLSTException = WLSTException
# global WLSTException


global DOMAIN_DIR
DOMAIN_DIR = ""

class DevNull(NullPrintStream):
    def nothing(self):
        print ""


class DirStackEntry :
    def __init__(self, path):
        if(re.match("^/", path)) :
            self.absolutePath = path
        else:
            # build an absolute path based on the stack
            topStackEntry = getDirStack().peek()
            self.absolutePath = topStackEntry.absolutePath + "/" + path


class Stack:
    def __init__(self):
        self.__storage = []

    def isEmpty(self):
        return len(self.__storage) == 0

    def push(self, p):
        self.__storage.append(p)

    def pop(self):
        return self.__storage.pop()

    def peek(self):
        result = self.pop()
        self.push(result)
        return result

global DIR_STACK
DIR_STACK = Stack()

def newWLSTException(message):
    return WLSTException(message)

def getStateMap(name) :
    try :
        result = STATE_MAPS[name]
    except KeyError :
        result = dict()
        STATE_MAPS[name] = result
    return result

def getDirStack() :
    return DIR_STACK

def activate() :
    try :
        activate()
    except WLSTException, e:
        dumpStack()
        raise e

def assign(type, name, toType, toName) :
    return assign(type, name, toType, toName)

def cancelEdit(ans) :
    cancelEdit(ans)

def closeDomain() :
    closeDomain()

def connect(adminUser, password, url) :
    connect(adminUser, password, url)

def create(name, type) :
    return create(name, type)

def delete(name, type) :
    return delete(name, type)

def decrypt(encryptedText):
    encryptionService = SerializedSystemIni.getEncryptionService(DOMAIN_DIR)
    ces = ClearOrEncryptedService(encryptionService)
    clear = ces.decrypt(encryptedText)
    return clear

def decryptBytes(bytes):
    encryptionService = SerializedSystemIni.getEncryptionService(DOMAIN_DIR)
    ces = ClearOrEncryptedService(encryptionService)
    clear = ces.decryptBytes(bytes)
    return str(String(clear))

def destroyMachine(machine):
    return cmo.destroyMachine(machine)

def disconnect() :
    disconnect()

def domainConfig():
    return domainConfig()

def domainRuntime():
    return domainRuntime()

def edit() :
    edit()

def encrypt(obj) :
    return encrypt(obj, DOMAIN_DIR)

def get(name) :
    return get(name)

def getAppDeployments() :
    return cmo.getAppDeployments()

def X_getClusters() :
    return cmo.getClusters()

def getClusterNames() :
    result = []
    clusters = getClusterNames()
    for cluster in clusters:
        result.append(cluster.getName())
    return result

def getCluster(name) :
    clusters = getClusterNames()
    for cluster in clusters :
        if name == cluster.getName() :
            return cluster
    return None

def getCurrentState(obj, targetinst) :
    return cmo.getCurrentState(obj, targetinst)

def X_getMachines() :
    return cmo.getMachines()

def getMachineNames() :
    machines = getMachineNames()
    result = []
    for machine in machines :
        result.append(machine.getName())
    return result

def X_getMachineNamesOffline() :
    return lsmap()

def getMachine(name) :
    machines = getMachineNames()
    for machine in machines :
        if name == machine.getName() :
            return machine
    return None

def getMBean(path) :
    return getMBean(path)

def X_getServers() :
    return cmo.getServers()

def getServerNames() :
    result = []
    servers = getServerNames()
    for server in servers :
        result.append(server.getName())
    return result

def getServerRuntimes() :
    return domainRuntimeService.getServerRuntimes()

def isRestartRequired(attr=None) :
    return isRestartRequired(attr)

def ls(propertySet) :
    return ls(propertySet)

def lsmap() :
    result = ls(returnMap='true')
    return result

def lsAttrMap() :
    result = ls(returnMap='true', returnType='a')
    return result

def lsChildMap() :
    result = ls(returnMap='true', returnType='c')
    return result

def lsOpMap() :
    result = ls(returnMap='true', returnType='o')
    return result

def nmConnect(adminUserName, adminPassword, adminListenAddress, nodemgrPort, domainName, domainDir , type, jvmArguments) :
    if jvmArguments :
        nmConnect(adminUserName, adminPassword, adminListenAddress, nodemgrPort, domainName, domainDir, nmType=type, jvmArgs=jvmArguments)
    else :
        nmConnect(adminUserName, adminPassword, adminListenAddress, nodemgrPort, domainName, domainDir, nmType=type)

def nmDisconnect() :
    nmDisconnect()

def nmKill(serverName) :
    nmKill(serverName)

def nmServerStatus(serverName) :
    return nmServerStatus(serverName)

def nmStart(serverName, domainDir) :
    nmStart(serverName, domainDir)

def popd() :
    dirStack = getDirStack()
    if not dirStack.isEmpty() :
        dirStack.pop()
        if not dirStack.isEmpty() :
            dest = dirStack.peek()
            try :
                cmo = cd(dest.absolutePath)
                return cmo
            except :
                pass
    cmo = cd("/")
    return cmo 

def pushd(path) :
    stackEntry = DirStackEntry(path)
    getDirStack().push(stackEntry)
    try :
        dir = cmo = cd(stackEntry.absolutePath)
        return dir
    except Exception, e :
        popd()
        raise e

def pwd() :
    return pwd()

def readDomain(domainDir) :
    readDomain(domainDir)

def removeReferencesToBean(mbean) :
    editService.getConfigurationManager().removeReferencesToBean(mbean)

def save() :
    save()

def set(name, value):
    set(name, value)

def setCluster(cluster) :
    cmo.setCluster(cluster)

def setClusterMessagingMode(type) :
    cmo.setClusterMessagingMode(type)

def setFanEnabled(value) :
    cmo.setFanEnabled(value)

def setMachine(machine) :
    cmo.setMachine(machine)

def shutdown(serverName=None) :
    shutdown(name=serverName, block="true")

def startEdit() :
    startEdit()

def startNodeManager(nodemgrHome, nodemgrPort, secureListener, listenAddress, jvmArgs='-Dweblogic.security.SSL.enableJSSE=true') :
    startNodeManager(NodeManagerHome=nodemgrHome, ListenPort=nodemgrPort, SecureListener=secureListener, StartScriptEnabled='true', ListenAddress=listenAddress, jvmArgs=jvmArgs)

def unassign(sourceType, sourceName, destType, destName) :
    return unassign(sourceType, sourceName, destType, destName)

def updateDomain() :
    updateDomain()

# USE WITH CAUTION - todo - remove
def getCmo() :
    return cmo

def divert(func, location) :
    def wrapper(*args) :
        pwd = pwd()
        cmo = cd(location)
        result = func(*args)
        cmo = cd(pwd)
        return result
    return wrapper

def silent(func) :
    def wrapper(*args) :
        sysout = sys.stdout
        syserr = sys.stderr
        javaOut = System.out
        javaErr = System.err
        sys.stdout = DevNull()
        sys.stderr = DevNull()
        System.setOut(DevNull())
        System.setErr(DevNull())
        result = func(*args)
        sys.stdout = sysout
        sys.stderr = syserr
        System.setOut(javaOut)
        System.setErr(javaErr)
        return result
    return wrapper

cd = silent(cd)
ls = silent(ls)
lsmap = silent(lsmap)
domainConfig = silent(domainConfig)
domainRuntime = silent(domainRuntime)

