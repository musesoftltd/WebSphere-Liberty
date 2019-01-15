from java.util.logging import Logger
import unittest

from PbCommonTest import PbCommonTest
from pb import PbWlstLib
from wlst.WlstWrapper import getServerRuntimes


LOGGER = Logger.getLogger("TestDeployments")
testContext = None

class TestJDBCResource(PbCommonTest):
    def setUp(self):
        PbCommonTest.setUp(self, testContext)
        self.assert_(PbWlstLib.connectToAdminServer())

    def test_jdbcConnection(self):
        allServers = getServerRuntimes()
        if (len(allServers) > 0):
            for tempServer in allServers:
                jdbcServiceRT = tempServer.getJDBCServiceRuntime()
                dataSources = jdbcServiceRT.getJDBCDataSourceRuntimeMBeans()
                if (len(dataSources) > 0):
                    for dataSource in dataSources:
                        if dataSource.getName() == testContext.key :
                            print "testing " + str(dataSource)
                            result = (None == dataSource.testPool())
                            self.assert_(result, "Datasource failed testPool: " + dataSource.getName())

if __name__ == '__main__':
    unittest.main()

