from java.util.logging import Logger
import unittest

from PbCommonTest import PbCommonTest
from wlst.WlstWrapper import connect, disconnect


LOGGER = Logger.getLogger("TestWebLogicServer")
testContext = None

class TestWebLogicServer(PbCommonTest):
    def setUp(self):
        PbCommonTest.setUp(self, testContext)

    def test_wlstConnect(self):
        try :
            connect(self.adminUserName, self.adminPassword, self.getConnectionUrl(testContext.key))
            disconnect()
        except :
            self.assert_(False, "Failed to connect to Weblogic server (" + testContext.key + ") : connectionUrl=" + 
                                str(self.getConnectionUrl(testContext.key)) + ", adminUserName=" + str(self.adminUserName))

if __name__ == '__main__':
    unittest.main()
