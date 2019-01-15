# 2015.03.10 - Initial version.

import weblogic.management.scripting.utils.WLSTUtil as wlst
from wllib import *
from wlstModule import *  # @UnusedWildImport
    
from library.offline.wllib import *  # @UnusedWildImport

print 'starting the script ....'

# for local test use below...
username = 'weblogic'
password = 'weblogic1'
url = 't3://localhost:7001'
#  
# createDomain('C:\\bea10.3.3\\wlserver_10.3\\common\\templates\\domains\\wls.jar', 'C:\\bea10.3.3\\user_projects\\domains\\base_domain', 'weblogic', 'weblogic1')
# startServer('AdminServer', 'base_domain', url, username, password, 'C:\\bea10.3.3\\user_projects\\domains\\base_domain', 'true', 15000, 'false', 'true', '/log.txt', '', '-Xms256m -Xmx256m -XX:MaxPermSize=256m', 'true')
# for local test use below...end.

sliceName = 'aServerSlice'

try:
    
    wlst.connect(username, password, url)

    wlst.edit()
    wlst.startEdit()
       
    print 'Sub Deployments...'
    deleteJMSSubDeployment('JMSModule' + sliceName + '_SystemModule', sliceName + '_SubDeployment')
    print 'Sub Deployments...end.'

    print 'JMS Modules...' 
    deleteJMSModule('JMSModule' + sliceName + '_SystemModule')
    print 'JMS Modules...end.'

    print 'JMS Servers for every managed server...'
    deleteJMSServer('JMSServer' + sliceName)
    print 'JMS Servers for every managed server...end.'

    print 'Filestores...'
    deleteFilestore('FileStore' + sliceName)
    print 'Filestores...end.'

    print 'datasources...'
    deleteDataSource('oraclePool_' + sliceName)
    print 'datasources...end.'
        
    print 'servers...'    
    deleteServer(sliceName)
    print 'servers...end.'
                    
except Exception, e:
    print e
    print "Error while trying to execute the script"
    wlst.dumpStack()
    raise 

try:
    wlst.save()
    wlst.activate(block="true")
    print "script returns SUCCESS"   
except Exception, e:
    print e 
    print "Error while trying to save and/or activate!!!"
    wlst.dumpStack()
    raise 
    
