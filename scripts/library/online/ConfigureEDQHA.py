
import getopt
from java.io import FileInputStream
from java.lang import System
import os
import shutil
import sys

from WlstWrapper import connect
from weblogic.management.scripting.utils.wlst import *


def usage():
    print "Usage:"
    print "ConfigureEDQHA.py  -p <properties> "


#=======================================================================================
# get domain properties.
#=======================================================================================

props = Properties()
properties = ""

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
# Set all the script level variables to use 
#=======================================================================================

# Deployment related variables

installer_base = props.get('installers.PATH')
# deployable_dir=installer_base + '/../edq/deployable'
deployable_dir = props.get('edq.deployable.dir')
planFilLoc = installer_base + '/../edq/weblogic-plan.xml'
domainDir = props.get('domainHome')
deploymentsDir = domainDir + '/deployments'


# Admin Server related variables

AServerAddr = props.get('_Servers_AdminServer_ListenAddress')
AServerPort = props.get('_Servers_AdminServer_ListenPort')
AServerNm = props.get('_Servers_AdminServer_Name')
AdminPwd = props.get('adminPassword')
AdminUsr = props.get('adminUserName')


#=======================================================================================
# Connect to the Admin Server
#=======================================================================================
print 'Coneecting to the AdminServer:' + AServerAddr

try:
	connect(AdminUsr, AdminPwd, 't3://' + AServerAddr + ':' + AServerPort)
except:
	print 'Unable to connect to the Admin Server.'
	sys.exit(2)

# Get the list of servers in the domain
try:
	ServerNames = cmo.getServers()
except:
	print 'Unable to obtain the list of managed servers.'
	sys.exit(2)

domainRuntime()

#=======================================================================================
# Create Directory to be used to hold all deployment files
#=======================================================================================
if not os.path.exists(deploymentsDir):
	os.makedirs(deploymentsDir)

#=======================================================================================
# Start the managed servers in preparation for the EDQ deployment
#=======================================================================================

for srvr in ServerNames:
	srvrnm = srvr.getName()
	if not srvrnm == AServerNm:
		srvBean = getMBean('ServerRuntimes/' + srvrnm)
		if srvBean:
                        print 'Server ' + srvrnm + ' is in State ' + srvBean.getState() + ' Not needed to be Started..'
                else:
                        start(srvrnm, 'Server', block='true')


#=======================================================================================
# Perform the deployment of EDQ into individual Managed Servers
#=======================================================================================

for MServer in ServerNames:
	MServerNm = MServer.getName()
        
	if MServerNm == AServerNm:
		print 'Admin Server - Not processing'
	else:
		print 'Processing Managed Server - ' + MServerNm
		# ApplicationName='dndirector-'+MServerNm[-3:]
		ApplicationName = 'dndirector-' + MServerNm
                MSDeploymentDir = deploymentsDir + '/' + MServerNm
		print 'Going to copy the deployments to ' + MSDeploymentDir

		
		try:
			shutil.copytree(deployable_dir, MSDeploymentDir)
		except:
			print 'Unable to copy the deployable files into ' + MSDeploymentDir + '. Please check if the directory already exists..'
			sys.exit(2)			
                
		# Deploy the EDQ Application Tailored for the Managed Server

		print 'Going to deploy the application ' + ApplicationName
		edit()
                try:
			startEdit()
			deploy(ApplicationName, MSDeploymentDir + '/dndirector', targets=MServerNm, stageMode='nostage')
			save()
			activate()
			print 'Deployment Complete.. '
		except:
			stopEdit('y')
			print 'Deployment failed for ' + MServerNm
			sys.exit(2)		

		# Update the deployment plan with the EDQ specific plan file for the deployed Application

		try:
			stopApplication(ApplicationName)
		except:                
			print 'Error while stopping Application ' + ApplicationName			

		edit()
		
		try:
			startEdit()
			updateApplication(ApplicationName, MSDeploymentDir + '/dndirector/weblogic-plan.xml', targets=MServerNm, stageMode='nostage')
                        save()
			activate()
		except:
			stopEdit('y')
			print 'Update of weblogic-plan failed for ' + MServerNm

		try:
                        startApplication(ApplicationName)

                except:
                        print 'Error while Starting Application ' + ApplicationName

		try:		
			shutdown(MServerNm, block='true')
		except:
			print 'Unable to shutdown server ' + MServerNm


#=======================================================================================
# All done.. Disconnect from the Admin Server
#=======================================================================================

disconnect()

print "script returns SUCCESS.. Disconnected form the Admin server.."


#=======================================================================================
# Exit the Script.
#=======================================================================================

sys.exit()
