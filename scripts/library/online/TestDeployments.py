from java.util.logging import Logger
import unittest

from PbCommonTest import PbCommonTest
from pb import PbWlstLib
from weblogic.management.scripting.core.utils.wlst_core import WLSTException
from wlst.WlstWrapper import domainConfig, cd, lsmap, domainRuntime, \
    getCurrentState, getAppDeployments


LOGGER = Logger.getLogger("TestDeployments")
testContext = None

def verifyDeployment (self, appDeployment):
    try:
        domainConfig()
        cmo = cd('/AppDeployments/' + appDeployment.getName() + '/Targets')
        targets = lsmap()
        domainRuntime()
        cmo = cd('AppRuntimeStateRuntime')
        cmo = cd('AppRuntimeStateRuntime')
        for target in targets:
            state = getCurrentState(appDeployment.getName(), target)
            if state != "STATE_ACTIVE":
                self.assert_(False, "State of Deployment not ACTIVE: " + appDeployment.getName() + ", state=" + state)
                if state == "STATE_NEW":
                    LOGGER.info("Ensure managed servers are started")

    except WLSTException:
        self.assert_(False, "Unable to get state of Deployment: " + appDeployment.getName())


class TestDeployments(PbCommonTest):
    def setUp(self):
        PbCommonTest.setUp(self, testContext)
        self.assert_(PbWlstLib.connectToAdminServer())

    def test_Deployments(self):
        cmo = cd('/AppDeployments')
        appDeployments = getAppDeployments()
        for appDeployment in appDeployments:
            verifyDeployment(self, appDeployment)

if __name__ == '__main__':
    unittest.main()
