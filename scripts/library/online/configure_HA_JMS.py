import os
import os.path

from weblogic.management.scripting.utils.wlst import *


adminUrl = 't3://ha-as:7001'
adminUser = 'weblogic'
adminPassword = 'jmspoc_jms'

persistentStoresHome = '/u01/app/oracle/runtime/stores'

def createFilestore (storeName, storeDir, migratableTargetName):
	# Ensure that the store directory exists
	if not os.path.exists(storeDir):
		print 'Creating directory ' + storeDir + ' for persistent store'
		os.makedirs(storeDir)
	cmo = cd('/')
	cmo.createFileStore(storeName)
	cmo = cd('/FileStores/' + storeName)
	cmo.setDirectory(storeDir)
	set('Targets', jarray.array([ObjectName('com.bea:Name=' + migratableTargetName + ',Type=MigratableTarget')], ObjectName))
	cmo = cd('/FileStores/' + storeName)
	return cmo

def createHAJMSConfig ():
	# Create persistent stores for JMS servers
	jmservers = cmo.getJMSServers()
	for svr in jmservers:
		# Get the JMS Server's name
		sName = svr.getName()
		print 'Configuring JMS Server ' + sName
		# Get the target managed server 
		target = svr.getTargets()[0]
		# And construct migratable target name from its name
		mtName = target.getName() + ' (migratable)'
		print 'Migratable target for JMS Server and its store will be ' + mtName
		storeName = ''
		if (svr.getPersistentStore() == None):
			storeName = sName + 'Store'
			print 'Creating persistent store fot JMS Server; store name is ' + storeName
			# Create a filestore persistent store for the JMS server and target the migratable target
			store = createFilestore(storeName, persistentStoresHome + '/' + sName, mtName)
			# Now allocate the persistent store to the jms server
			svr.setPersistentStore(store)
		# Target the store (whether just-created or not) at the migratable target
		storeName = svr.getPersistentStore().getName()
		print 'Setting migratable target for peristent store ' + storeName + ' to ' + mtName
		cmo = cd('/FileStores/' + storeName)
		set('Targets', jarray.array([ObjectName('com.bea:Name=' + mtName + ',Type=MigratableTarget')], ObjectName))
		# And finally target the JMS server at the migratable target
		print 'Setting migratable target for JMSServer ' + sName + ' to ' + mtName
		cmo = cd('/JMSServers/' + sName)
		set('Targets', jarray.array([ObjectName('com.bea:Name=' + mtName + ',Type=MigratableTarget')], ObjectName))
		# Get the cluster of the migrationable target and set its migration basis to 'consensus'
		cmo = cd('/MigratableTargets/' + mtName)
		cluster = cmo.getCluster()
		print 'Setting migration basis for cluster ' + cluster.getName()
		cluster.setMigrationBasis('consensus')
		# Set the server migration policy to auto-exactly-once the JMS Servers's migratable target
		print 'Setting migration policy for migratable target ' + mtName
		cmo = cd('/FileStores/' + storeName)
		cmo = cd('/MigratableTargets/' + mtName)
		cmo.setMigrationPolicy('exactly-once')

cmo.connect(adminUser, adminPassword, adminUrl)
edit()
startEdit()

createHAJMSConfig()

activate()
disconnect()
