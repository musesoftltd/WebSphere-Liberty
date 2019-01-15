import os

import PbCommon as pbc
from com.muse.properties.secure import EncryptionUtils
from weblogic.management.scripting.core.utils.wlst_core import WLSTException
from wlst.WlstWrapper import cd


# Script to configure named JDBC resource: sets connection URL, username, password and driverClass
def configureJDBCResource (resName, url, username, password, driverClass):
    try :
        cmo = cd('/JDBCSystemResource/' + resName + '/JdbcResource/' + resName + '/JDBCDriverParams/NO_NAME_0')
        set('PasswordEncrypted', password)
        set('DriverName', driverClass)
        set('URL', url)
        cmo = cd('Properties/NO_NAME_0/Property/user')
        set('Value', username)
    except WLSTException :
        return False
    return True

#=======================================================================================
# apply config to each JDBC resource in turn
#=======================================================================================
def configureJDBCResources(props, domain, url):
    print "Configuring JDBC Resources ..."
    i = 1;
    prefix = domain + ".JDBCResource."
    dsName = props.get(prefix + str(i) + "." + "name")
    result = True
    while (dsName and result) :
        print 'configuring ' + dsName

        schema = props.get("datasource.user." + dsName)

        driverClass = props.get(prefix + str(i) + "." + "driverclass")
        if(driverClass == None or len(driverClass) == 0):
            driverClass = 'oracle.jdbc.OracleDriver'

        password = pbc.getDecryptedValue(props, 'datasource.password.' + dsName)
        if not password :
            password = pbc.getDecryptedValue(props, 'rcu.jdbc.Password')

        result = configureJDBCResource(dsName, url, schema, password, driverClass)
        i = i + 1
        dsName = props.get(prefix + str(i) + "." + "name")
    if (result) :
        print "JDBC Resources configured successfully."
    else :
        print "Failed in seting up JDBC Resource"
    return result
