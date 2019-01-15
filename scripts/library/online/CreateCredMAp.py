import getopt
from java.io import FileInputStream
from java.lang import System
from java.util.logging import Logger
import os
import sys

from com.muse.properties.secure import EncryptionUtils
from WlstWrapper import connect


if __name__ == '__main__':
    from wlstModule import *  # @UnusedWildImport




global connected
connected = False

global LOGGER
LOGGER = Logger.getLogger("CreateCredMap")

def usage():
    print "Usage:"
    print "ConfigureDomain.py -t <domainDir> -p <properties> -d <domain>"

def getDecryptedValue(props, key):
    ENCRPYTED_VALUE_PREFIX = "::ENCRYPTED::"
    password = props.get(key)
    if password:
        passkey = props.get('security.passkey')

        if password.startswith(ENCRPYTED_VALUE_PREFIX):
            password = EncryptionUtils.decryptString(passkey, password[len(ENCRPYTED_VALUE_PREFIX):])

    return password

def getBoolFromString(str) :
    return (str == "true" or str == "True")


def conectToAdminServerOnAnyUrl(connectionUrls, userName, password) :
    connected = False
    for connectionUrl in connectionUrls :
        try :
            LOGGER.info("Trying to connect to " + connectionUrl)
            connect(userName, password, connectionUrl)
            connected = True
            LOGGER.info("Connected to " + connectionUrl)
            break
        except:
            LOGGER.info("Failed to connect as: " + str(userName) + " to " + str(connectionUrl))

    return connected

def connectToAdminServer() :
    global connected
    if connected :
        return True
    else:
        userName = props.get("adminUserName")
        password = getDecryptedValue(props, "adminPassword")
        listenAddress = props.get("admin.server.listenAddress")
        listenPort = props.get("admin.server.listenPort")
        sslPort = props.get("admin.server.ssl.listenPort")
        adminPort = props.get("admin.server.adminPort")
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

        global connected
        connected = conectToAdminServerOnAnyUrl(connectionUrls, userName, password)

        return connected


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

credMapName = props.get(domain + ".credmap.name")
credMapKey = props.get(domain + ".credmap.key")
credMapUser = props.get(domain + ".credmap.user")
credMapPassword = props.get(domain + ".credmap.password")
credMapDescription = props.get(domain + ".credmap.desc")

connectToAdminServer()
createCred(map=credMapName, key=credMapKey, user=credMapUser, password=credMapPassword, desc=credMapDescription)
disconnect()

#=======================================================================================
# Exit 
#=======================================================================================

sys.exit()
