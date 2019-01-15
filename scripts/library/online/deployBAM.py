import getopt
from java.io import FileInputStream
from java.lang import System
import os
import shutil
import sys

from weblogic.management.scripting.utils.wlst import *
from wlst.WlstWrapper import connect


def usage():
    print "Usage:"
    print "deployBAM  -p <properties> "


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

listenAddress = props.get('server.admin.listen.address')
listenPort = props.get('server.admin.listen.port')
adminUser = props.get('adminUserName')
adminPassword = props.get('adminPassword')



#=======================================================================================
# Connect to the Admin Server
#=======================================================================================
print 'Connecting to the AdminServer:' + listenAddress

try:
        connect(adminUser, adminPassword, 't3://' + listenAddress + ':' + listenPort)
except:
        print 'Unable to connect to the Admin Server.'
        sys.exit(2)

#===============================================================================================
# Create BAM subdeployments  		
#===================================================================================================		

edit()
startEdit()
cd ('/AppDeployments/oracle-bam#11.1.1/SubDeployments')


print 'create subdeployment /oracle/bam'
cmo.createSubDeployment('/oracle/bam')

print 'create subdeployment oracle-bam-adc-ejb.jar'
cmo.createSubDeployment('oracle-bam-adc-ejb.jar')

print 'create subdeployment oracle-bam-ems-ejb.jar'
cmo.createSubDeployment('oracle-bam-ems-ejb.jar')

print 'create subdeployment oracle-bam-eventengine-ejb.jar '
cmo.createSubDeployment('oracle-bam-eventengine-ejb.jar')

print 'create subdeployment oracle-bam-reportcache-ejb.jar '
cmo.createSubDeployment('oracle-bam-reportcache-ejb.jar')

print 'create subdeployment oracle-bam-statuslistener-ejb.jar'
cmo.createSubDeployment('oracle-bam-statuslistener-ejb.jar')

print 'create subdeployment sdpmessagingclient-ejb.jar'
cmo.createSubDeployment('sdpmessagingclient-ejb.jar')

print 'create subdeployment OracleBAM'
cmo.createSubDeployment('OracleBAM')

print 'create subdeployment OracleBAMWS'
cmo.createSubDeployment('OracleBAMWS')


print('Finished');

#===================================================================================
#
# Set Targets for BAM SUbDeployments 
#==================================================================================

print 'Target /oracle/bam to bam_server1'
cmo = cd('/AppDeployments/oracle-bam#11.1.1/SubDeployments//oracle/bam')
set('Targets', jarray.array([ObjectName('com.bea:Name=bam_server1,Type=Server')], ObjectName))


print 'Target oracle-bam-adc-ejb.jar to bam_server1'

cmo = cd('/AppDeployments/oracle-bam#11.1.1/SubDeployments/oracle-bam-adc-ejb.jar')
set('Targets', jarray.array([ObjectName('com.bea:Name=bam_server1,Type=Server')], ObjectName))

print 'Target oracle-bam-ems-ejb.jar to bam_server1'

cmo = cd('/AppDeployments/oracle-bam#11.1.1/SubDeployments/oracle-bam-ems-ejb.jar')
set('Targets', jarray.array([ObjectName('com.bea:Name=bam_server1,Type=Server')], ObjectName))


print 'Target oracle-bam-eventengine-ejb.jar to bam_server1'
cmo = cd('/AppDeployments/oracle-bam#11.1.1/SubDeployments/oracle-bam-eventengine-ejb.jar')
set('Targets', jarray.array([ObjectName('com.bea:Name=bam_server1,Type=Server')], ObjectName))


print 'Target oracle-bam-reportcache-ejb.jar to bam_server1'
cmo = cd('/AppDeployments/oracle-bam#11.1.1/SubDeployments/oracle-bam-reportcache-ejb.jar')
set('Targets', jarray.array([ObjectName('com.bea:Name=bam_server1,Type=Server')], ObjectName))

print 'Target oracle-bam-statuslistener-ejb.jar to bam_server1'
cmo = cd('/AppDeployments/oracle-bam#11.1.1/SubDeployments/oracle-bam-statuslistener-ejb.jar')
set('Targets', jarray.array([ObjectName('com.bea:Name=bam_server1,Type=Server')], ObjectName))


print 'Target sdpmessagingclient-ejb.jar to bam_server1'
cmo = cd('/AppDeployments/oracle-bam#11.1.1/SubDeployments/sdpmessagingclient-ejb.jar')
set('Targets', jarray.array([ObjectName('com.bea:Name=bam_server1,Type=Server')], ObjectName))


print 'Target OracleBAM to bam_cluster'
cmo = cd('/AppDeployments/oracle-bam#11.1.1/SubDeployments/OracleBAM')
set('Targets', jarray.array([ObjectName('com.bea:Name=bam_cluster1,Type=Cluster')], ObjectName))


print 'Target OracleBAMWS to bam_cluster'
cmo = cd('/AppDeployments/oracle-bam#11.1.1/SubDeployments/OracleBAMWS')
set('Targets', jarray.array([ObjectName('com.bea:Name=bam_cluster1,Type=Cluster')], ObjectName))

print('Finished');

save()
activate()
disconnect()
