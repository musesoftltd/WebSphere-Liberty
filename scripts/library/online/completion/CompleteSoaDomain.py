# Script to perform HA configuration of JTA and JMS in SOA domain

import jarray
from java.lang import String
from java.util.logging import Logger
from javax.management import ObjectName
import sys
import traceback

from pb import PbWlstLib as pbwl
from pb import SystemControl
from weblogic.management.scripting.utils.wlst import *


global props
global online

online = False

LOGGER = Logger.getLogger("CompleteDomain")

def connect():
    global online
    if (online):
        return True
    else:
        online = pbwl.connectToAdminServer()
        return online

def disconnect():
    global online
    if (online):
        disconnect()
        online = False

def startOnlineEditSession():
    edit()
    startEdit()
    return True

def completeOnlineEditSession():
    global online
    if (online):
        save()
        activate()

def cancelOnlineEditSession():
    global online
    if (online):
        cancelEdit('y')

def createMigrationLeasingDS ():
    # TBD: Create property names for these vars
    dsName = "Leasing"
    dsJndiName = "jdbc/Leasing"

    if (getMBean("/JDBCSystemResources/" + dsName) != None):
        LOGGER.info("Leasing DataSource already exists")
        return

    cmo = cd("/")
    cmo.createJDBCSystemResource(dsName)

    cmo = cd("/JDBCSystemResources/" + dsName + "/JDBCResource/" + dsName)
    cmo.setName(dsName)

    cmo = cd("/JDBCSystemResources/" + dsName + "/JDBCResource/" + dsName + "/JDBCDataSourceParams/" + dsName)
    set("JNDINames", jarray.array([String(dsJndiName)], String))

    cmo = cd("/JDBCSystemResources/" + dsName + "/JDBCResource/" + dsName + "/JDBCDriverParams/" + dsName)
    cmo.setUrl(props.get("rcu.jdbc.ConnectionUrl"))
    cmo.setDriverName("oracle.jdbc.OracleDriver")
    cmo.setPassword(props.get("schema.LEASING.Password"))

    cmo = cd("/JDBCSystemResources/" + dsName + "/JDBCResource/" + dsName + "/JDBCDriverParams/" + dsName + "/Properties/" + dsName)
    cmo.createProperty("user")

    cmo = cd("/JDBCSystemResources/" + dsName + "/JDBCResource/" + dsName + "/JDBCDriverParams/" + dsName + "/Properties/" + dsName + "/Properties/user")
    cmo.setValue(props.get("schema.name.LEASING"))

    cmo = cd("/JDBCSystemResources/" + dsName + "/JDBCResource/" + dsName + "/JDBCOracleParams/" + dsName)
    cmo.setFanEnabled(True)
    cmo.setOnsNodeList(props.get("database.scanEndPoint"))

    # Target at all clusters
    osbCluster = getMBean("/Clusters/osb_Cluster")
    soaCluster = getMBean("/Clusters/soa_Cluster")
    cmo = cd("/JDBCSystemResources/" + dsName)
    cmo.addTarget(osbCluster)
    cmo.addTarget(soaCluster)

def setClusterMigrationDataSources():
    # TBD: Create property names for this var
    dsName = "Leasing"
    leasingDataSource = getMBean("/JDBCSystemResources/" + dsName)
    cmo = cd('/')
    clusters = cmo.getClusters()
    for c in clusters:
        c.setMigrationBasis("database")
        c.setDataSourceForAutomaticMigration(leasingDataSource)

def createPersistentStoreDS (schemaName, dsName, dsJndiName):
    dataSource = getMBean("/JDBCSystemResources/" + dsName)
    if (dataSource != None):
        LOGGER.info("TLog DataSource " + dsName + " already exists")
    else:
        cmo = cd("/")
        dataSource = cmo.createJDBCSystemResource(dsName)

        cmo = cd("/JDBCSystemResources/" + dsName + "/JDBCResource/" + dsName)
        cmo.setName(dsName)

        cmo = cd("/JDBCSystemResources/" + dsName + "/JDBCResource/" + dsName + "/JDBCDataSourceParams/" + dsName)
        set("JNDINames", jarray.array([String(dsJndiName)], String))
        cmo.setGlobalTransactionsProtocol("None")

        cmo = cd("/JDBCSystemResources/" + dsName + "/JDBCResource/" + dsName + "/JDBCDriverParams/" + dsName)
        cmo.setUrl(props.get("rcu.jdbc.ConnectionUrl"))
        cmo.setDriverName("oracle.jdbc.OracleDriver")
        password = props.get("schema." + schemaName + ".Password")
        cmo.setPassword(password)

        cmo = cd("/JDBCSystemResources/" + dsName + "/JDBCResource/" + dsName + "/JDBCDriverParams/" + dsName + "/Properties/" + dsName)
        cmo.createProperty("user")

        cmo = cd("/JDBCSystemResources/" + dsName + "/JDBCResource/" + dsName + "/JDBCDriverParams/" + dsName + "/Properties/" + dsName + "/Properties/user")
        cmo.setValue(schemaName)

        cmo = cd("/JDBCSystemResources/" + dsName + "/JDBCResource/" + dsName + "/JDBCOracleParams/" + dsName)
        cmo.setFanEnabled(True)
        cmo.setOnsNodeList(props.get("database.scanEndPoint"))
    return dataSource

def createTransactionLogDS (serverName, schemaName):
    # TBD: Create property names for these vars
    dsName = "TLogDS_" + serverName
    jndiName = "jdbc/" + dsName

    dataSource = createPersistentStoreDS(schemaName, dsName, jndiName)

    # target DataSource at cluster for server
    server = getMBean("/Servers/" + serverName)
    cluster = server.getCluster()
    cmo = cd("/JDBCSystemResources/" + dsName)
    LOGGER.info("Setting DataSource " + dsName + " target to cluster: " + cluster.getName())
    cmo.addTarget(cluster)

    # return the DataSource object
    return cmo

def configureDefaultStore (serverName, schemaName):
    # TBD: Create property names for these vars
    storeName = "Tlog_" + serverName

    # create a datasource
    dataSource = createTransactionLogDS(serverName, schemaName)

    # create JDBCStore and link DataSource to it
    cmo = cd("/")
    store = getMBean("/JDBCStores/" + storeName)
    if (store == None):
        store = cmo.createJDBCStore(storeName)
    else:
        LOGGER.info("JDBC Persistent Store" + storeName + " already exists")

    store.setDataSource(dataSource)
    store.setPrefixName(serverName + "TLOG")

    # target JDBCStore at cluster of the server
    server = getMBean("/Servers/" + serverName)
    store.addTarget(server)

    # establish JDBCStore as Transaction Log for server
    cmo = cd("/Servers/" + serverName + "/TransactionLogJDBCStore/" + serverName)
    cmo.setDataSource(dataSource)
    cmo.setEnabled(True)

def setJtaMigrationPolicy (serverName):
    cmo = cd('/Servers/' + serverName + '/JTAMigratableTarget/' + serverName)
    cmo.setMigrationPolicy('failure-recovery')
    cmo.setStrictOwnershipCheck(True)

def configureDefaultStores ():
        tlogSchemaName = props.get("schema.name.SOATLOG")
        cmo = cd('/')
        adminServerName = cmo.getAdminServerName()
        servers = cmo.getServers()
        for svr in servers:
            serverName = svr.getName()
            if (serverName == adminServerName):
                    continue
            LOGGER.info("Configuring default persistent store for server " + serverName)
            configureDefaultStore(serverName, tlogSchemaName)

def configureJTAMigrationPolicy ():
        cmo = cd('/')
        adminServerName = cmo.getAdminServerName()
        servers = cmo.getServers()
        for svr in servers:
            serverName = svr.getName()
            if (serverName == adminServerName):
                    continue
            LOGGER.info("Setting JTA migration policy for server " + serverName)
            setJtaMigrationPolicy(serverName)

def configureHAJta ():
        LOGGER.info("Configuring cluster leasing DataSource")
        startOnlineEditSession()
        createMigrationLeasingDS()
        completeOnlineEditSession()

        LOGGER.info("Setting cluster migration basis")
        startOnlineEditSession()
        setClusterMigrationDataSources()
        completeOnlineEditSession()

        LOGGER.info("Configuring server default stores")
        startOnlineEditSession()
        configureDefaultStores()
        completeOnlineEditSession()

        LOGGER.info("Configuring JTA automatic failover")
        startOnlineEditSession()
        configureJTAMigrationPolicy()
        completeOnlineEditSession()

def createJMSStoreDS (jmsServerName, schemaName):
    # TBD: Create property names for these vars
    dsName = "JMSDS_" + jmsServerName
    jndiName = "jdbc/" + dsName

    dataSource = createPersistentStoreDS(schemaName, dsName, jndiName)

    # target DataSource at cluster for server
    jmsServer = cmo = cd("/JMSServers/" + jmsServerName)
    server = jmsServer.getTargets()[0]
    cluster = server.getCluster()
    LOGGER.info("Setting DataSource " + dsName + " target to cluster: " + cluster.getName())
    cmo = cd("/JDBCSystemResources/" + dsName)
    cmo.addTarget(cluster)

    # return the DataSource object
    return dataSource

def createJMSPersistentStore (jmsServerName, schemaName, migratableTargetName):
    storeName = "JDBCStore_" + jmsServerName

    # create a datasource
    dataSource = createJMSStoreDS(jmsServerName, schemaName)

    # create JDBCStore and link DataSource to it
    cmo = cd("/")
    store = getMBean("/JDBCStores/" + storeName)
    if (store == None):
        LOGGER.info("Creating JDBC Persistent Store" + storeName)
        store = cmo.createJDBCStore(storeName)
    else:
        LOGGER.info("JDBC Persistent Store" + storeName + " already exists")

    store.setDataSource(dataSource)
    store.setPrefixName(jmsServerName)

    # target JDBCStore at migraratable target (of the JMS Server)
    cmo = cd("/JDBCStores/" + storeName)
    set('Targets', jarray.array([ObjectName('com.bea:Name=' + migratableTargetName + ',Type=MigratableTarget')], ObjectName))
    return store

def configureJmsServers ():
    # Create persistent stores for JMS servers
    jmsStoreSchemaName = props.get("schema.name.SOAJMS")
    cmo = cd("/")
    jmsServers = cmo.getJMSServers()
    mtName = ""
    for svr in jmsServers:
        # Get the JMS Server's name
        sName = svr.getName()
        LOGGER.info('Configuring JMS Server ' + sName)
        # Ensure JMS server targetted at migratable target
        target = svr.getTargets()[0]
        mtName = target.getName()
        if (target.getType() != 'MigratableTarget'):
            # Construct migratable target name from current (managed server) target name
            mtName = target.getName() + ' (migratable)'
            LOGGER.info('Setting migratable target for JMSServer ' + sName + ' to ' + mtName)
            cmo = cd('/JMSServers/' + sName)
            set('Targets', jarray.array([ObjectName('com.bea:Name=' + mtName + ',Type=MigratableTarget')], ObjectName))
        cmo = cd('/MigratableTargets/' + mtName)
        if (cmo.getMigrationPolicy() == 'failure-recovery'):
            LOGGER.info('Migration policy for MigratableTarget ' + mtName + " already set to 'failure-recovery'")
        else:
            LOGGER.info('Setting Migration policy for MigratableTarget ' + mtName + " to 'failure-recovery'")
            cmo.setMigrationPolicy('failure-recovery')
        # Create and target JDBC persistent store for server
        store = svr.getPersistentStore()
        if (store == None or store.getType() == 'FileStore'):
            LOGGER.info('Creating persistent store for JMSServer ' + sName)
            store = createJMSPersistentStore(sName, jmsStoreSchemaName, mtName)
            # establish JDBCStore as store for server
            cmo = cd("/JMSServers/" + sName)
            svr.setPersistentStore(store)
        else:
            LOGGER.info('Custom persistent store for JMSServer ' + sName + ' already set ')

def configureHAJms ():
        startOnlineEditSession()
        configureJmsServers()
        completeOnlineEditSession()

def completeSoaDomain (properties):
    LOGGER.info("Starting CompleteSoaDomain")
    global props
    props = properties
    ha_enabled = props.get("soa.ha_config_enabled")
    if (ha_enabled == "true"):
        ha_enabled = True
    else:
        ha_enabled = False

    try:
        if (ha_enabled):
            try:
                connect()
                configureHAJta()
                configureHAJms()
                disconnect()
            except:
                cancelOnlineEditSession()
                disconnect()
                raise
    except :
        print "Unexpected error in CompleteSoaDomain.py: ", sys.exc_info()[0], sys.exc_info()[1]
        tb = sys.exc_info()[2]
        traceback.print_tb(tb)
        SystemControl.exitOnError()

