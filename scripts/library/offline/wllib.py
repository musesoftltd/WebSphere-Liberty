# import weblogic.management.scripting.utils.wlst
# if __name__ == '__main__': 
#     from wlstModule import *#@UnusedWildImport
 
import jarray
from java.lang import String

import weblogic.management.scripting.utils.WLSTUtil as wlst
from wlstModule import *  # @UnusedWildImport


# import weblogic.management.scripting.utils.WLSTUtil. as wlst
def createUnixMachine(name, nmType, nmlistenPort):
    cmo = wlst.wlst.cd('/')
    cmo.createUnixMachine(name)

    cmo = wlst.cd('/Machines/' + name + '/NodeManager/' + name)
    cmo.setNMType(nmType)
    cmo.setListenPort(nmlistenPort)    
    
def createServer(serverName, port):
    # create server
    cmo = wlst.cd('/')
    cmo.createServer(serverName)
    
    cmo = wlst.cd('/Servers/' + serverName)
    # cmo.setListenAddress('')
    cmo.setListenPort(port)
    
def deleteServer(serverName):
    # create server
    cmo = wlst.cd('/Servers')
    wlst.delete(serverName, 'Server')    
    
def setServerRemoteStartArguments(serverName, options):
    print 'Setting remote server start options for : ' + serverName + '...'
    cmo = wlst.cd('/Servers/' + serverName + '/ServerStart/' + serverName)
    cmo.setArguments(options)
    print 'Setting remote server start options for : ' + serverName + '...end.'    

def assignServerToMachine(serverName, machineName):
    cmo = wlst.cd('/Servers/' + serverName)
    cmo.setMachine(wlst.getMBean('/Machines/' + machineName))
    
def createClusterUnicast(clusterName):
    # create cluster
    cmo = wlst.cd('/')
    cmo.createCluster(clusterName)
    
    cmo = wlst.cd('/Clusters/' + clusterName)
    cmo.setClusterMessagingMode('unicast')
    cmo.setClusterBroadcastChannel('')

def assignManagedServerToCluster(serverName, clusterName):
    cmo = wlst.cd('/Servers/' + serverName)
    cmo.setCluster(wlst.getMBean('/Clusters/' + clusterName))
    
def createOracleThinJDBCdataSource (
        dsName,
        dsURL,
        dsDriverName,
        dsJNDINames,
        dsUserName,
        dsPassword,
        dsDatabaseName,
        dsTestQuery,
        datasourceTarget
    ):
    
    print 'creating a OracleThin datasource...'
    
    print 'datasource name: ' + dsName
    
    cmo = wlst.cd('/')
    cmo.createJDBCSystemResource(dsName)
    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName)
    cmo.setName(dsName)
     
    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDataSourceParams/' + dsName)
    set('JNDINames', jarray.array(dsJNDINames, String))
     
    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDriverParams/' + dsName)
    cmo.setUrl(dsURL)
    cmo.setDriverName(dsDriverName)
    cmo.setPassword(dsPassword)
     
    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCConnectionPoolParams/' + dsName)
    cmo.setTestTableName(dsTestQuery)
    
    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDriverParams/' + dsName + '/Properties/' + dsName)
    cmo.createProperty('user')
    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDriverParams/' + dsName + '/Properties/' + dsName + '/Properties/user')
    cmo.setValue(dsUserName)
    
    if (dsDatabaseName != ''): 
        cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDriverParams/' + dsName + '/Properties/' + dsName)
        cmo.createProperty('databaseName')
     
        cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDriverParams/' + dsName + '/Properties/' + dsName + '/Properties/databaseName')
        cmo.setValue(dsDatabaseName)
     
    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDataSourceParams/' + dsName)
    cmo.setGlobalTransactionsProtocol('OnePhaseCommit')
 
    if (datasourceTarget != ''):
        cmo = wlst.cd('/SystemResources/' + dsName)
        set('Targets', datasourceTarget)

    print 'creating a OracleThin datasource...end.'

def targetOracleThinJDBCdataSource(dsName, datasourceTargets):
    print 'targetting: ' + dsName + ' to: ' + str(datasourceTargets) + '...'
    if (datasourceTargets != ''):
        cmo = wlst.cd('/SystemResources/' + dsName)
        set('Targets', datasourceTargets)    
    print 'targetting: ' + dsName + ' to: ' + str(datasourceTargets) + '...end.'
    
def deleteDataSource(dsName):
    cmo = wlst.cd('/JDBCSystemResources')
    wlst.delete(dsName, 'JDBCSystemResource')
    
    
def createSQLServerJDBCdataSource (
        dsName,
        dsURL,
        dsDriverName,
        dsJNDINames,
        dsUserName,
        dsPassword,
        dsDatabaseName,
        dsTestTable,
        datasourceTarget,
        dsPortNumber,
        dsServerName
    ):
    
    print 'creating a SQL Server datasource...'
    
    print 'datasource name: ' + dsName
    
    cmo = wlst.cd('/')
    cmo.createJDBCSystemResource(dsName)
    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName)
    cmo.setName(dsName)
     
    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDataSourceParams/' + dsName)
    set('JNDINames', jarray.array(dsJNDINames, String))
     
    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDriverParams/' + dsName)
    cmo.setUrl(dsURL)
    cmo.setDriverName(dsDriverName)
    cmo.setPassword(dsPassword)
     
    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCConnectionPoolParams/' + dsName)
    cmo.setTestTableName(dsTestTable)

    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDriverParams/' + dsName + '/Properties/' + dsName)
    cmo.createProperty('portNumber')
    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDriverParams/' + dsName + '/Properties/' + dsName + '/Properties/portNumber')
    cmo.setValue(dsPortNumber)
    
    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDriverParams/' + dsName + '/Properties/' + dsName)
    cmo.createProperty('serverName')
    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDriverParams/' + dsName + '/Properties/' + dsName + '/Properties/serverName')
    cmo.setValue(dsServerName)

    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDriverParams/' + dsName + '/Properties/' + dsName)
    cmo.createProperty('user')
    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDriverParams/' + dsName + '/Properties/' + dsName + '/Properties/user')
    cmo.setValue(dsUserName)

    if (dsDatabaseName != ''): 
        cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDriverParams/' + dsName + '/Properties/' + dsName)
        cmo.createProperty('databaseName')
     
        cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDriverParams/' + dsName + '/Properties/' + dsName + '/Properties/databaseName')
        cmo.setValue(dsDatabaseName)
     
    cmo = wlst.cd('/JDBCSystemResources/' + dsName + '/JDBCResource/' + dsName + '/JDBCDataSourceParams/' + dsName)
    cmo.setGlobalTransactionsProtocol('OnePhaseCommit')
 
    if (datasourceTarget != ''):
        cmo = wlst.cd('/SystemResources/' + dsName)
        set('Targets', datasourceTarget)

    print 'creating a SQL Server datasource...end.'

def targetSQLServerJDBCdataSource(dsName, datasourceTarget):
    if (datasourceTarget != ''):
        cmo = wlst.cd('/SystemResources/' + dsName)
        set('Targets', datasourceTarget)
        
def createFilestore(filestoreName, targets):
    # create file store
    cmo = wlst.cd('/')
    cmo.createFileStore(filestoreName)
    
    cmo = wlst.cd('/FileStores/' + filestoreName)
    set('Targets', targets)        
    cmo.setDirectory(filestoreName)
    cmo.setSynchronousWritePolicy('Direct-Write')

def deleteFilestore(filestoreName):
    cmo = wlst.cd('/FileStores')
    wlst.delete(filestoreName)


def createJMSModule(moduleName, targets):
    print 'Creating a JMS System module named : ' + moduleName + ' targetted to : ' + str(targets) + '...'
    cmo = wlst.cd('/')
    cmo.createJMSSystemResource(moduleName)
    
    cmo = wlst.cd('/SystemResources/' + moduleName)
    set('Targets', targets)
    print 'Creating a JMS System module named : ' + moduleName + ' targetted to : ' + str(targets) + '...end.'
    
def deleteJMSModule(moduleName):
    print 'Deleting a JMS System module named : ' + moduleName + '...'
    cmo = wlst.cd('/SystemResources')
    wlst.delete(moduleName, 'JMSSystemResource')
    print 'Deleting a JMS System module named : ' + moduleName + '...end.'

def createJMSServer(jmsServerName):
    cmo = wlst.cd('/JMSServers')
    cmo.createJMSServer(jmsServerName)
    
def targetJMSServer(jmsServerName, targets):
    print 'Targetting JMS Server: ' + jmsServerName + ' to : ' + str(targets) + '...'
    cmo = wlst.cd('/Deployments/' + jmsServerName)
    set('Targets', targets)
    print 'Targetting JMS Server: ' + jmsServerName + ' to : ' + str(targets) + '...end.'
    
def deleteJMSServer(jmsServerName):
    cmo = wlst.cd('/JMSServers')
    wlst.delete(jmsServerName)
    
def assignPersistentStoreToJMSServer(jmsServerName, filestoreName):
    cmo = wlst.cd('/Deployments/' + jmsServerName)
    cmo.setPersistentStore(wlst.getMBean('/FileStores/' + filestoreName))
    
def createJMSSubDeployment(jmsModule, subDeploymentName, targets):    
    print 'Creating SubDeployment: ' + subDeploymentName + ', with targets: ' + str(targets) + '...'        
    cmo = wlst.cd('/SystemResources/' + jmsModule)
    cmo.createSubDeployment(subDeploymentName)
    
    cmo = wlst.cd('/SystemResources/' + jmsModule + '/SubDeployments/' + subDeploymentName)
    set('Targets', targets)
        
    print 'Creating SubDeployment: ' + subDeploymentName + ', with targets: ' + str(targets) + '...end.'        

def deleteJMSSubDeployment(jmsModule, subDeploymentName):
    cmo = wlst.cd('/SystemResources/' + jmsModule + '/' + 'SubDeployments')
    wlst.delete(subDeploymentName)
    
def createConnectionFactory(connectionFactoryName, jmsModule, targets, subDeploymentName):
    print 'Creating connection factory : ' + connectionFactoryName + '...'
    print ' NOTE: the factory name and its JNDI name are BOTH taken from the factory name'

    cmo = wlst.cd('/JMSSystemResources/' + jmsModule + '/JMSResource/' + jmsModule)
    cmo.createConnectionFactory(connectionFactoryName)
    
    cmo = wlst.cd('/JMSSystemResources/' + jmsModule + '/JMSResource/' + jmsModule + '/ConnectionFactories/' + connectionFactoryName)
    cmo.setJNDIName(connectionFactoryName)
    
    cmo = wlst.cd('/JMSSystemResources/' + jmsModule + '/JMSResource/' + jmsModule + '/ConnectionFactories/' + connectionFactoryName + '/SecurityParams/' + connectionFactoryName)
    cmo.setAttachJMSXUserId(False)
        
    if (subDeploymentName != '') :
        cmo = wlst.cd('/JMSSystemResources/' + jmsModule + '/JMSResource/' + jmsModule + '/ConnectionFactories/' + connectionFactoryName)
        cmo.setSubDeploymentName(subDeploymentName)    
        if (targets != '') :
            cmo = wlst.cd('/SystemResources/' + jmsModule + '/SubDeployments/' + subDeploymentName)
            set('Targets', targets)            
    else:
        if (targets != '') :
            set('Targets', targets)            

    print 'Creating connection factory : ' + connectionFactoryName + '...end.'

def createQueue(queueName, jmsModule, targets, subDeploymentName) :
    print 'Creating Queue : ' + queueName + '...'
    print ' NOTE: the factory name and its JNDI name are BOTH taken from the factory name'

    cmo = wlst.cd('/JMSSystemResources/' + jmsModule + '/JMSResource/' + jmsModule)
    cmo.createQueue(queueName)
    
    cmo = wlst.cd('/JMSSystemResources/' + jmsModule + '/JMSResource/' + jmsModule + '/Queues/' + queueName)
    cmo.setJNDIName(queueName)

    if (subDeploymentName != '') :
        cmo = wlst.cd('/JMSSystemResources/' + jmsModule + '/JMSResource/' + jmsModule + '/Queues/' + queueName)
        cmo.setSubDeploymentName(subDeploymentName)    
        if (targets != '') :
            cmo = wlst.cd('/SystemResources/' + jmsModule + '/SubDeployments/' + subDeploymentName)
            set('Targets', targets)            
    else:
        # this code path needs to change to target in the absence of a subDeployment
        if (targets != '') :
            cmo = wlst.cd('/SystemResources/' + jmsModule + '/SubDeployments/' + subDeploymentName)
            set('Targets', targets)            
    
    print 'Creating Queue : ' + queueName + '...end.'
    
def deleteQueue(queueName, jmsModule):
    print 'Deleting Uniform Distributed Queue : ' + queueName + '...'
    cmo = wlst.cd('/JMSSystemResources/' + jmsModule + '/JMSResource/' + jmsModule + '/Queues/')
    cmo.wlst.delete(queueName)
    
    print 'Deleting Uniform Distributed Queue : ' + queueName + '...end.'

def createDistributedQueue(queueName, jmsModule, targets, subDeploymentName, loadBalancingPolicy) :
    print 'Creating Uniform Distributed Queue : ' + queueName + '...'
    print ' NOTE: the factory name and its JNDI name are BOTH taken from the factory name'

    cmo = wlst.cd('/JMSSystemResources/' + jmsModule + '/JMSResource/' + jmsModule)
    cmo.createUniformDistributedQueue(queueName)
    
    cmo = wlst.cd('/JMSSystemResources/' + jmsModule + '/JMSResource/' + jmsModule + '/UniformDistributedQueues/' + queueName)
    cmo.setJNDIName(queueName)

    cmo.setLoadBalancingPolicy(loadBalancingPolicy)
            
    if (subDeploymentName != '') :
        cmo = wlst.cd('/JMSSystemResources/' + jmsModule + '/JMSResource/' + jmsModule + '/UniformDistributedQueues/' + queueName)
        cmo.setSubDeploymentName(subDeploymentName)    
        if (targets != '') :
            cmo = wlst.cd('/SystemResources/' + jmsModule + '/SubDeployments/' + subDeploymentName)
            set('Targets', targets)            
    else:
        # this code path needs to change to target in the absense of a subDeployment
        if (targets != '') :
            cmo = wlst.cd('/SystemResources/' + jmsModule + '/SubDeployments/' + subDeploymentName)
            set('Targets', targets)            

    print 'Creating Uniform Distributed Queue : ' + queueName + '...end.'

def deleteDistributedQueue(queueName, jmsModule):
    print 'Deleting Uniform Distributed Queue : ' + queueName + '...'
    cmo = wlst.cd('/JMSSystemResources/' + jmsModule + '/JMSResource/' + jmsModule + '/UniformDistributedQueues/')
    cmo.wlst.delete(queueName)
    
    print 'Deleting Uniform Distributed Queue : ' + queueName + '...end.'
    
def SetQRedeliveryOptions(systemModule, queueName, backupQueueName):
    print 'Setting Queue redelivery options for : ' + queueName + '... at System Module: ' + systemModule + '...'

    cmo = wlst.cd('/JMSSystemResources/' + systemModule + '/JMSResource/' + systemModule + '/UniformDistributedQueues/' + queueName + '/DeliveryFailureParams/' + queueName)

    cmo.setErrorDestination(wlst.getMBean('/JMSSystemResources/' + systemModule + '/JMSResource/' + systemModule + '/UniformDistributedQueues/' + backupQueueName))
    cmo.setRedeliveryLimit(1)
    cmo.setExpirationPolicy('Discard')
    
    cmo = wlst.cd('/JMSSystemResources/' + systemModule + '/JMSResource/' + systemModule + '/UniformDistributedQueues/' + queueName + '/DeliveryParamsOverrides/' + queueName)
    cmo.setRedeliveryDelay(120000)
    
    print 'Setting Queue redelivery options for : ' + queueName + '... at System Module: ' + systemModule + '...end.'
        
def SetQFailureOptions(systemModule, queueName, backupQueueName):
    print 'Setting Queue Failure options for : ' + queueName + '... at System Module: ' + systemModule + '...'

    cmo = wlst.cd('/JMSSystemResources/' + systemModule + '/JMSResource/' + systemModule + '/UniformDistributedQueues/' + queueName + '/DeliveryFailureParams/' + queueName)

    cmo.setErrorDestination(wlst.getMBean('/JMSSystemResources/' + systemModule + '/JMSResource/' + systemModule + '/UniformDistributedQueues/' + backupQueueName))
    cmo.setRedeliveryLimit(24)
    cmo.setExpirationPolicy('Discard')
    
    cmo = wlst.cd('/JMSSystemResources/' + systemModule + '/JMSResource/' + systemModule + '/UniformDistributedQueues/' + queueName + '/DeliveryParamsOverrides/' + queueName)
    cmo.setRedeliveryDelay(120000)
    
    print 'Setting Queue Failure options for : ' + queueName + '... at System Module: ' + systemModule + '...end.'
        
