import os
import os.path

from weblogic.management.scripting.utils.wlst import *


adminUrl = 't3://ha-as:7001'
adminUser = 'weblogic'
adminPassword = 'jmspoc_jms'

transactionLogFilesHome = '/u01/app/oracle/runtime/stores/tlog'

def configureDefaultStore (serverName):
	# Where set at default value, set the dir of a managed server's default store to a shared directory
	# and if necessary create an appropriate shared directory
	cmo = cd('/Servers/' + serverName + '/DefaultFileStore/' + serverName) 
	if (cmo.getDirectory() == None):
		print 'Setting new default store directory for server ' + serverName
		logDir = transactionLogFilesHome + '/' + serverName
		if not os.path.exists(logDir):
			print 'Creating directory ' + logDir + ' for transaction logs for server ' + serverName
			os.makedirs(logDir)
		cmo = cd('/Servers/' + serverName + '/DefaultFileStore/' + serverName)
		cmo.setDirectory(logDir)
	else:
		print 'Server ' + serverName + ' already has non-default folder for default store'

def setJtaMigrationPolicy (serverName):
	cmo = cd('/Servers/' + serverName + '/JTAMigratableTarget/' + serverName)
	jta = cmo
	if (jta.getMigrationPolicy() == 'failure-recovery'):
		print 'JTA migration policy for server ' + serverName + ' is already set to "failure-recovery"'
	else:
		print 'Setting JTA migration policy "failure-recovery" for server ' + serverName
		jta.setMigrationPolicy('failure-recovery')
	if (jta.isSet('StrictOwnershipCheck')):
		print 'Disabling strict ownership for JTA in ' + serverName
		jta.setStrictOwnershipCheck(false)
	else:
		print 'Strict ownership already disabled for JTA in ' + serverName

def createHAJtaConfig ():
	# Set migration policy for all migratable targets
	cmo = cd('/')
	targets = cmo.getMigratableTargets()
	for mt in targets:
		if (mt.getMigrationPolicy() == 'exactly-once'):
			print 'Migration policy for migratable target ' + mt.getName() + ' is already set to "exactly-once"'
		else:
			print 'Setting migration policy "exactly once" for migratable target ' + mt.getName()
			mt.setMigrationPolicy('exactly-once')
	# Enable migration of each managed server's transaction recover service and
	# set default stores to a shared directory
	cmo = cd('/')
	adminServerName = cmo.getAdminServerName()
	print "Admin server name is " + adminServerName
	servers = cmo.getServers()
	managedServerNames = []
	for svr in servers:
		if (svr.getName() != adminServerName):
			managedServerNames.append(svr.getName())
	print "Managed servers are: " + ', '.join(managedServerNames)
	for serverName in managedServerNames:
		configureDefaultStore(serverName)
		setJtaMigrationPolicy(serverName)
	# Set all clusters to use Consensus leasing
	cmo = cd('/')
	clusters = cmo.getClusters()
	for c in clusters:
		if (c.getMigrationBasis() == 'consensus'):
			print 'Migration basis for cluster ' + c.getName() + ' is already set to "consensus"'
		else:
			print 'Setting consensus migration basis for cluster ' + c.getName()
			c.setMigrationBasis('consensus')
		
cmo.connect(adminUser, adminPassword, adminUrl)
edit()
startEdit()

createHAJtaConfig()

activate()
disconnect()
