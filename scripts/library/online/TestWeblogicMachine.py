from java.util.logging import Logger
import unittest

from PbCommonTest import PbCommonTest
from wlst.WlstWrapper import nmConnect, nmDisconnect


LOGGER = Logger.getLogger("TestWeblogicMachine")
testContext = None

class TestWeblogicMachine(PbCommonTest):
    def setUp(self):
        PbCommonTest.setUp(self, testContext)

    def test_NodeManagerRunning(self):
        try :
            listenAddress = testContext.props.get("/Machines/" + testContext.key + "/NodeManager/" + testContext.key + "/ListenAddress")
            nmConnect(self.adminUserName, self.adminPassword, listenAddress, self.nodeManagerPort, self.domainName, self.domainDir, self.nmType, self.jvmArgs)
            nmDisconnect()
        except :
            self.assert_(False, "Failed to connect to NodeManager : host=" + str(listenAddress) + ", port=" + str(self.nodeManagerPort) + 
                                ", domainName=" + str(self.domainName) + ", domainDir=" + str(self.domainDir) + ", nmType=" + str(self.nmType) + 
                                ", jvmArgs=" + str(self.jvmArgs))

if __name__ == '__main__':
    unittest.main()
