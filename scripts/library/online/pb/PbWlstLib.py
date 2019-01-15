from java.util.logging import Logger

import Catalogue
import PbCommon
from com.muse.fmw.platform import PbProperties
from entities.EntityUtils import ConfigurableCollection
import entities.EntityUtils as eu
from wlst.WlstWrapper import connect, cd, getMBean, setCluster, assign


LOGGER = Logger.getLogger("PbWlstLib")

global connected
connected = False
requiresRestart = False

global props


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
        password = PbCommon.getDecryptedValue(props, "adminPassword")
        listenAddress = props.get("admin.server.listenAddress")
        listenPort = props.get("admin.server.listenPort")
        sslPort = props.get("admin.server.ssl.listenPort")
        adminPort = props.get("admin.server.adminPort")
        sslEnabled = props.get("SSLEnabled")
        adminPortEnabled = props.get("admin.server.adminPortEnabled")

        connectionUrls = []
        if PbCommon.getBoolFromString(adminPortEnabled):
            if adminPort:
                connectionUrls.append("t3s://" + listenAddress + ":" + adminPort)
        if PbCommon.getBoolFromString(sslEnabled):
            if sslPort :
                connectionUrls.append("t3s://" + listenAddress + ":" + sslPort)
        if listenPort :
            connectionUrls.append("t3://" + listenAddress + ":" + listenPort)

        global connected
        connected = conectToAdminServerOnAnyUrl(connectionUrls, userName, password)

        return connected

def populateClusterOnline(clusterName) :
    serverName = props.get("managed.server.1.name")
    LOGGER.info("Adding " + str(serverName) + " to cluster " + str(clusterName))
    cmo = cd('/Servers/' + str(serverName))
    cluster = getMBean('/Clusters/' + str(clusterName))
    result = setCluster(cluster)
    LOGGER.info("the result = " + str(result))
    LOGGER.info("populateClusterOnline complete. " + str(serverName) + " to cluster " + str(clusterName))

def populateClusterOffline(clusterName) :
    serverName = props.get("managed.server.1.name")
    LOGGER.info("Adding " + str(serverName) + " to cluster " + str(clusterName))
    cmo = cd('/')
    result = assign("server", serverName, "Cluster", clusterName)
    LOGGER.info("result = " + str(result))
    LOGGER.info("Added " + str(serverName) + " to cluster " + str(clusterName))

def doConfigure(entityType) :
    LOGGER.fine("Entering PbWlstLib.doConfigure")
    configurableCollection = ConfigurableCollection(PbProperties.SEPARATOR + entityType)
    configurableCollection.createNew()
    configurableCollection.updateExisting()
    configurableCollection.removeOld()
    LOGGER.fine("Exiting PbWlstLib.doConfigure")
    return configurableCollection.modificationsPresent

def initialise() :
    LOGGER.fine("Entering PbWlstLib.initialise")

    LOGGER.info("Configuring Machines")
    cmResult = doConfigure("Machines")

    LOGGER.info("Configuring Clusters")
    ccResult = doConfigure("Clusters")

    LOGGER.info("Configuring Servers")
    csResult = doConfigure("Servers")

    LOGGER.info("Configuring JDBCSystemResources")
    cjResult = doConfigure("JDBCSystemResources")

    LOGGER.fine("Exiting PbWlstLib.configure")
    return cmResult or csResult or ccResult or cjResult


def configure() :
    LOGGER.fine("Entering PbWlstLib.configure")

    cdResult = False
    LOGGER.info("Configuring Domain level attributes")
    entity = eu.getEntityFactory().createDomainEntity()
    if (entity != None and eu.checkEntityChanged(entity)) :
        LOGGER.info("Making Domain level attribute changes")
        cdResult = entity.update()

    LOGGER.info("Configuring Machines")
    cmResult = doConfigure("Machines")

    LOGGER.info("Configuring Clusters")
    ccResult = doConfigure("Clusters")

    LOGGER.info("Configuring Servers")
    csResult = doConfigure("Servers")

    LOGGER.info("Configuring JDBCSystemResources")
    cjResult = doConfigure("JDBCSystemResources")

    LOGGER.fine("Exiting PbWlstLib.configure")
    return cdResult or cmResult or csResult or ccResult or cjResult

def configureOffline() :
    LOGGER.fine("Entering PbWlstLib.configureOffline")

    cdResult = False
    LOGGER.info("Configuring Domain level attributes")
    entity = eu.getEntityFactory().createDomainEntity()
    if (entity != None and eu.checkEntityChanged(entity)) :
        LOGGER.info("Making Domain level attribute changes")
        cdResult = entity.update()

    LOGGER.fine("Exiting PbWlstLib.configureOffline")
    return cdResult

def catalogue() :
    LOGGER.fine("Entering PbWlstLib.catalogue")
    result = Catalogue.catalogue("/")
    LOGGER.fine("Exiting PbWlstLib.catalogue")
    return result



