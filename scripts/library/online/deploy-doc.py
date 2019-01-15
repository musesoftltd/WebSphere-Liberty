
if __name__ == '__main__': 
    from wlstModule import *  # @UnusedWildImport
    
import getopt
from java.io import FileInputStream
from java.lang import System
import os

from com.muse.properties.secure import EncryptionUtils


def usage():
    print "Usage:"
    print "deployDoc -p <properties>"
	# '-all' actions are applied to admin server in addition to managed servers
	# Actions may be prefixed with "test-" to run them in test/simulation mode

def getPassword(props, key):
    ENCRPYTED_VALUE_PREFIX = "::ENCRYPTED::"
    password = props.get(key)
    if password :
        passkey = props.get('security.passkey')

        if password.startswith(ENCRPYTED_VALUE_PREFIX):
            password = EncryptionUtils.decryptString(passkey, password[len(ENCRPYTED_VALUE_PREFIX):])

    return password

#=======================================================================================
# get domain properties.
#=======================================================================================

props = Properties()
domainDir = ""
properties = ""
action = ""
serversToStart = ""
testMode = false

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

domainHome = props.get("domainHome")
jdbcDatabase = props.get("jdbcDatabase")
dirDocumakerHome = props.get("dirDocumakerHome")
jdbcAdminUsername = props.get("jdbcAdminUsername")
jdbcAdminPassword = props.get("jdbcAdminPassword")
jdbcDatabaseHost = props.get("jdbcDatabaseHost")
jdbcDatabasePort = props.get("jdbcDatabasePort")
jdbcDatabaseName = props.get("jdbcDatabaseName")
jdbcDatabaseNameType = props.get("jdbcDatabaseNameType")
jdbcAslineUsername = props.get("jdbcAslineUsername")
jdbcAslinePassword = props.get("jdbcAslinePassword")
ALID = props.get("ALID")

portAdminServer = props.get("portAdminServer")
portSoaServer = props.get("portSoaServer")
portIdmServer = props.get("portIdmServer")
portIdmSslServer = props.get("portIdmSslServer")
portDmkrServer = props.get("portDmkrServer")

# JMS account
jmsPrincipal = props.get("jmsPrincipal")
jmsCredential = props.get("jmsCredential")

weblogicUsername = props.get("weblogicUsername")
weblogicPassword = props.get("weblogicPassword")
weblogicDomain = props.get("weblogicDomain")

#=======================================================================================
dirDomain = domainHome

readDomain(dirDomain);

if jdbcDatabase == "Oracle" :
	dirDocumakerJ2ee = dirDocumakerHome + '/j2ee/weblogic/oracle11g';

if jdbcDatabase == "DB2" :
	dirDocumakerJ2ee = dirDocumakerHome + '/j2ee/weblogic/db2v97';

# =================== JDBC

def createJDBCDatasource(jdbcName, jdbcJNDIName, dbUser, dbPassword, dbHost, dbPort, dbName, dbNameType) :
    print('  ' + jdbcName);
    cmo = cd('/');

    create(jdbcName , 'JDBCSystemResource');

    cmo = cd('/JDBCSystemResources/' + jdbcName + '/JdbcResource/' + jdbcName);

    create('myJdbcDriverParams', 'JDBCDriverParams');
    cmo = cd('JDBCDriverParams/NO_NAME_0');

    if dbNameType == "ServiceName" :
        dbJdbcURL = 'jdbc:oracle:thin:@//' + dbHost + ':' + dbPort + '/' + dbName;
    else:
        dbJdbcURL = 'jdbc:oracle:thin:@' + dbHost + ':' + dbPort + ':' + dbName;

    set('DriverName', 'oracle.jdbc.xa.client.OracleXADataSource');
    set('URL', dbJdbcURL);
    set('PasswordEncrypted', dbPassword);
    set('UseXADataSourceInterface', 'true')

    create('myProps', 'Properties');
    cmo = cd('Properties/NO_NAME_0');
    create('user', 'Property');
    cmo = cd('Property/user');
    cmo.setValue(dbUser);

    cmo = cd('/JDBCSystemResources/' + jdbcName + '/JdbcResource/' + jdbcName);

    create('myJdbcDataSourceParams', 'JDBCDataSourceParams');
    cmo = cd('JDBCDataSourceParams/NO_NAME_0');
    set('JNDIName', jdbcJNDIName);


    cmo = cd('/JDBCSystemResources/' + jdbcName + '/JdbcResource/' + jdbcName);

    create('myJdbcConnectionPoolParams', 'JDBCConnectionPoolParams');
    cmo = cd('JDBCConnectionPoolParams/NO_NAME_0');
    set('TestTableName', 'SQL SELECT 1 FROM DUAL');
    set('MaxCapacity', 50);


    cmo = cd('/JDBCSystemResources/' + jdbcName + '/JdbcResource/' + jdbcName);

    create('myJdbcXAParams', 'JDBCXAParams');
    cmo = cd('JDBCXAParams/NO_NAME_0');
    set('KeepXaConnTillTxComplete', 1);

    cmo = cd('/JDBCSystemResources/' + jdbcName);
    set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1');


print('creating JDBC Data Sources');
createJDBCDatasource(jdbcAdminUsername, 'jdbc/' + jdbcAdminUsername, jdbcAdminUsername, jdbcAdminPassword, jdbcDatabaseHost, jdbcDatabasePort, jdbcDatabaseName, jdbcDatabaseNameType);
createJDBCDatasource(jdbcAslineUsername, 'jdbc/' + jdbcAslineUsername, jdbcAslineUsername, jdbcAslinePassword, jdbcDatabaseHost, jdbcDatabasePort, jdbcDatabaseName, jdbcDatabaseNameType);


print('creating JMS resources');
# =================== JMS Setup

alJMSModule = 'AL' + ALID + 'Module';
alJMSFileStore = 'AL' + ALID + 'FileStore';
alJMSServer = 'AL' + ALID + 'Server';

alJMSSubDeployment = 'AL' + ALID + 'Sub';

# =================== JMS FileStore

print('  FileStore for JMS : ' + alJMSFileStore);
cmo = cd('/');
create(alJMSFileStore, 'FileStore');
cmo = cd('/FileStores');
cmo = cd(alJMSFileStore);
set('Target', 'AdminServer');
set('Directory', alJMSFileStore);

# =================== JMS Server

print('  JMS Server : ' + alJMSServer);
cmo = cd('/');
create(alJMSServer, 'JMSServer');
cmo = cd('/JMSServers');
cmo = cd(alJMSServer);
set('Target', 'AdminServer');
set('PersistentStore', alJMSFileStore);

# =================== JMS Module

print('  JMS Module : ' + alJMSModule);
cmo = cd('/');
create(alJMSModule, 'JMSSystemResource');
cmo = cd('/JMSSystemResources');
cmo = cd(alJMSModule);
set('Target', 'AdminServer');

create(alJMSSubDeployment, 'SubDeployment');
cmo = cd('SubDeployments');
cmo = cd(alJMSSubDeployment);
set('Target', alJMSServer);


# =================== JMS QCF

print('  qcf : ' + 'AL' + ALID + 'QCF');
cmo = cd('/JMSSystemResources/' + alJMSModule + '/JmsResource/NO_NAME_0');

create('AL' + ALID + 'QCF', 'ConnectionFactory');
cmo = cd('ConnectionFactories/' + 'AL' + ALID + 'QCF');
set('Name', 'AL' + ALID + 'QCF');
set('SubDeploymentName' , alJMSSubDeployment);
set('JNDIName', 'jms.al' + ALID + '.qcf');

# =================== JMS Queues

def createJMSQueue(queueName, queueJNDIName, queueType='eq') :
    print('  queue : ' + queueName);
    cmo = cd('/JMSSystemResources/' + alJMSModule + '/JmsResource/NO_NAME_0');
    create(queueName + 'R' + queueType , 'Queue');
    cmo = cd('Queues/' + queueName + 'R' + queueType);
    set('Name', queueName + 'R' + queueType);
    set('SubDeploymentName', alJMSSubDeployment)
    set('JNDIName', 'jms.al' + ALID + '.' + queueJNDIName + 'r' + queueType);

createJMSQueue('Archiver', 'archiver');
createJMSQueue('Assembler', 'assembler');
createJMSQueue('Distributor', 'distributor');
createJMSQueue('Identifier', 'identifier');
createJMSQueue('Presenter', 'presenter');
createJMSQueue('Publisher', 'publisher');
createJMSQueue('PubNotifier', 'pubnotifier');

createJMSQueue('Receiver', 'receiver', 'eq');
createJMSQueue('Receiver', 'receiver', 'es');

createJMSQueue('IDS', 'ids', 'eq');
createJMSQueue('IDS', 'ids', 'es');

# =================== JRF

print('deploying JRF to required servers');
cmo = cd('/AppDeployments');

cmo = cd('DMS Application#11.1.1.1.0');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('wsil-wls');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
 
cmo = cd('/Libraries');

cmo = cd('oracle.jrf.system.filter');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('oracle.wsm.seedpolicies#11.1.1@11.1.1');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('oracle.jsp.next#11.1.1@11.1.1');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('oracle.dconfig-infra#11@11.1.1.1.0');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('orai18n-adf#11@11.1.1.1.0');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('adf.oracle.domain#1.0@11.1.1.2.0');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('oracle.adf.dconfigbeans#1.0@11.1.1.2.0');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('oracle.adf.management#1.0@11.1.1.2.0');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('adf.oracle.domain.webapp#1.0@11.1.1.2.0');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('jsf#1.2@1.2.9.0');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('jstl#1.2@1.2.0.1');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('UIX#11@11.1.1.1.0');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('ohw-rcf#5@5.0');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('ohw-uix#5@5.0');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('oracle.pwdgen#11.1.1@11.1.1.2.0');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 



cmo = cd('/ShutdownClasses');
 
cmo = cd('DMSShutdown');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('JOC-Shutdown');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 



cmo = cd('/StartupClasses');

cmo = cd('JRF Startup Class');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('JPS Startup Class');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('ODL-Startup');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('Audit Loader Startup Class');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('AWT Application Context Startup Class');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('JMX Framework Startup Class');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('DMS-Startup');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 
cmo = cd('..');
cmo = cd('JOC-Startup');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 

cmo = cd('/WLDFSystemResources/Module-FMWDFW');
set('Target', 'AdminServer,idm_cluster1,dmkr_cluster1'); 


print('deploying Documaker Applications');

# =================== Applications
print('  deploying Document Factory Dashboard');
print('    ear location : ' + dirDocumakerJ2ee + '/dashboard/ODDF_Dashboard.ear');

cmo = cd('/');
create('ODDF_Dashboard#V2.0', 'AppDeployment');
cmo = cd('/AppDeployments/ODDF_Dashboard#V2.0');
set('Target', 'dmkr_cluster1'); 
set('ModuleType', 'ear'); 
set('DeploymentOrder', 100); 
set('SourcePath', dirDocumakerJ2ee + '/dashboard/ODDF_Dashboard.ear'); 
set('SecurityDDModel', 'DDOnly'); 

print('  deploying Dashboard Help');
print('    war location : ' + dirDocumakerJ2ee + '/dashboard/ODDF_Dashboard_Help.war');
cmo = cd('/');
create('ODDF_Dashboard_Help', 'AppDeployment');
cmo = cd('/AppDeployments/ODDF_Dashboard_Help');
set('Target', 'dmkr_cluster1'); 
set('ModuleType', 'war'); 
set('DeploymentOrder', 100) ; 
set('SourcePath', dirDocumakerJ2ee + '/dashboard/ODDF_Dashboard_Help.war'); 
set('SecurityDDModel', 'DDOnly'); 

print('  deploying Documaker Administrator');
print('    ear location : ' + dirDocumakerJ2ee + '/documaker_administrator/documakerAdmin.ear');
cmo = cd('/');
create('documakerAdmin#V2.0', 'AppDeployment');
cmo = cd('/AppDeployments/documakerAdmin#V2.0');
set('Target', 'dmkr_cluster1'); 
set('ModuleType', 'ear'); 
set('DeploymentOrder', 100); 
set('SourcePath', dirDocumakerJ2ee + '/documaker_administrator/documakerAdmin.ear'); 
set('SecurityDDModel', 'DDOnly'); 

print('  deploying Documaker Administrator Help');
print('    war location : ' + dirDocumakerJ2ee + '/documaker_administrator/documakerAdmin_Help.war');
cmo = cd('/');
create('documakerAdmin_Help', 'AppDeployment');
cmo = cd('/AppDeployments/documakerAdmin_Help');
set('Target', 'dmkr_cluster1'); 
set('ModuleType', 'war'); 
set('DeploymentOrder', 100) ; 
set('SourcePath', dirDocumakerJ2ee + '/documaker_administrator/documakerAdmin_Help.war'); 
set('SecurityDDModel', 'DDOnly'); 


print('  deploying DWS');
print('    ear location : ' + dirDocumakerJ2ee + '/DWS.ear');
cmo = cd('/');
create('DWS', 'AppDeployment');
cmo = cd('/AppDeployments/DWS');
set('Target', 'dmkr_cluster1'); 
set('ModuleType', 'ear'); 
set('DeploymentOrder', 100) ; 
set('SourcePath', dirDocumakerJ2ee + '/DWS.ear'); 
set('SecurityDDModel', 'DDOnly'); 

print('  deploying Weblogic JPS Query tool');
print('    war location : ' + dirDocumakerJ2ee + '/jpsquery.war');
cmo = cd('/');
create('jpsquery', 'AppDeployment');
cmo = cd('/AppDeployments/jpsquery');
set('Target', 'AdminServer'); 
set('ModuleType', 'war'); 
set('DeploymentOrder', 100); 
set('SourcePath', dirDocumakerJ2ee + '/jpsquery.war'); 
set('SecurityDDModel', 'DDOnly'); 

print('  deploying Documaker Interactive : Correspondence');
print('    ear location : ' + dirDocumakerJ2ee + '/idocumaker_correspondence/idm.ear');
cmo = cd('/');
create('idm#V2.0', 'AppDeployment');
cmo = cd('/AppDeployments/idm#V2.0');
set('Target', 'idm_cluster1'); 
set('ModuleType', 'ear'); 
set('DeploymentOrder', 100); 
set('SourcePath', dirDocumakerJ2ee + '/idocumaker_correspondence/idm.ear'); 
set('SecurityDDModel', 'DDOnly'); 

print('  deploying BPEL Passthrough');
print('    war location : ' + dirDocumakerJ2ee + '/idocumaker_correspondence/BPELPassthroughService-BPELService-context-root.war');
cmo = cd('/');
create('BPELPassthroughService-BPELService-context-root', 'AppDeployment');
cmo = cd('/AppDeployments/BPELPassthroughService-BPELService-context-root');
set('Target', 'idm_cluster1'); 
set('ModuleType', 'war'); 
set('DeploymentOrder', 100); 
set('SourcePath', dirDocumakerJ2ee + '/idocumaker_correspondence/BPELPassthroughService-BPELService-context-root.war'); 
set('SecurityDDModel', 'DDOnly'); 


updateDomain();

print('Finished');
