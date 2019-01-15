# 2015.03.10 - Initial version.
import jarray
from java.lang import String
from javax.management import ObjectName

from scripts.library.offline.wllib import *  # @UnusedWildImport
import weblogic.management.scripting.utils.WLSTUtil as wlst
from weblogic.management.scripting.utils.online_append import dumpStack
from weblogic.management.scripting.utils.wlst import save, activate, edit, \
    startEdit
from wllib import *
from wlstModule import *  # @UnusedWildImport


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
sliceNamePort = 4001

try:
    
    wlst.connect(username, password, url)

    wlst.edit()
    wlst.startEdit()
       
    print 'create servers and their filestores...'    

    createServer(sliceName, sliceNamePort)
    createFilestore('FileStore' + sliceName, jarray.array([ObjectName('com.bea:Name=' + sliceName + ',Type=Server')], ObjectName))
    setServerRemoteStartArguments(sliceName, '-XX:MaxPermSize=4g -Xms4g -Xmx4g -XX:MaxPermSize=4g -XX:+UseCodeCacheFlushing -XX:+CMSClassUnloadingEnabled -XX:+AggressiveHeap')
    
    print 'create servers and their filestores...end.'    
    
#     save()
#     activate()
# 
#     edit()
#     startEdit()
        
    print 'create PL datasources...'
    createOracleThinJDBCdataSource('oraclePool_' + sliceName,
                         'jdbc:oracle:thin:@hostname:1521:sid',
                         'oracle.jdbc.OracleDriver',
                         [String('oraclePool_' + sliceName), String('jdbc.aDatasource'), String('usertracking.jdbc.DataSource'), String('oraclePool'), String('dataSource'), String('jdbc.mappingdatasource')],
                         'user',
                         'pass',
                         'db',
                         'SQL SELECT * FROM DUAL',
                        jarray.array([ObjectName('com.bea:Name=' + sliceName + ',Type=Server')], ObjectName))        
    
    # create tracust ds

    print 'create PL datasources...end.'

    print 'JMS Modules...' 
    createJMSModule('JMSModule' + sliceName + '_SystemModule', jarray.array([ObjectName('com.bea:Name=' + sliceName + ',Type=Server')], ObjectName))
    print 'JMS Modules...end.'
     
    print 'JMS Servers for every managed server...'
    createJMSServer('JMSServer' + sliceName + '')
    targetJMSServer('JMSServer' + sliceName + '', jarray.array([ObjectName('com.bea:Name=' + sliceName + ',Type=Server')], ObjectName))
    print 'JMS Servers for every managed server...end.'

    print 'Assign persistent store to JMS servers...'
    assignPersistentStoreToJMSServer('JMSServer' + sliceName + '', 'FileStore' + sliceName + '')
    print 'Assign persistent store to JMS servers...end.'
     
#     save()
#     activate(block="true")
#  
#     edit() 
#     startEdit()

    print 'Q factories and Qs - for ' + sliceName + ' server...'
    createJMSSubDeployment('JMSModule' + sliceName + '_SystemModule', sliceName + '_SubDeployment', jarray.array([ObjectName('com.bea:Name=JMSServer' + sliceName + ',Type=JMSServer')], ObjectName))
    createConnectionFactory('jms/myFirstJMSQueueConnectionFactory', 'JMSModule' + sliceName + '_SystemModule', jarray.array([ObjectName('com.bea:Name=JMSServer' + sliceName + ',Type=JMSServer')], ObjectName), sliceName + '_SubDeployment')    

#     save()
#     activate(block="true")
#   
#     edit() 
#     startEdit()

    createQueue('jms/myFirstJMSQueue', 'JMSModule' + sliceName + '_SystemModule', jarray.array([ObjectName('com.bea:Name=JMSServer' + sliceName + ',Type=JMSServer')], ObjectName), sliceName + '_SubDeployment')
    createQueue('jms/myFirstJMSBackupQueue', 'JMSModule' + sliceName + '_SystemModule', jarray.array([ObjectName('com.bea:Name=JMSServer' + sliceName + ',Type=JMSServer')], ObjectName), sliceName + '_SubDeployment')
    createDistributedQueue('jms/myFirstJMSDistributedQueue', 'JMSModule' + sliceName + '_SystemModule', jarray.array([ObjectName('com.bea:Name=JMSServer' + sliceName + ',Type=JMSServer')], ObjectName), sliceName + '_SubDeployment', 'Round-Robin')
    print 'Q factories and Qs - for ' + sliceName + ' server...end.'    

#     print 'Setting Q redelivery options...'
#     SetQRedeliveryOptions('JMSModule' + sliceName + '_SystemModule', 'jms/myFirstJMSQueue', 'jms/myFirstJMSBackupQueue')
#     print 'Setting Q redelivery options...end.'

# ## new function test area...                    
    save()
    activate(block="true")

    edit()
    startEdit()
# ## new function test script...
                     
# ## new function test script...end.

# ## new function test area...end.                    

                    
except Exception, e:
    print e
    print "Error while trying to execute the script"
    dumpStack()
    raise 

try:
    save()
    activate(block="true")
    print "script returns SUCCESS"   
except Exception, e:
    print e 
    print "Error while trying to save and/or activate!!!"
    dumpStack()
    raise 
    
