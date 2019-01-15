import array
import getopt
import os
import sys
import unittest

import PlatformBuildBase as pbb
import Settings
import TestContextModule as tcm
import TestDeployments
import TestJDBCResource
import TestWeblogicMachine
import TestWeblogicServer


totals = array.array('i', [0, 0, 0])

def runSuite(suite, totals) :
    result = unittest.TextTestRunner().run(suite)
    if (result.testsRun) :
        totals[Settings.TOTAL_TESTS_RUN_INDEX] = totals[Settings.TOTAL_TESTS_RUN_INDEX] + result.testsRun
    if (result.errors) :
        totals[Settings.TOTAL_TESTS_ERRORED_INDEX] = totals[Settings.TOTAL_TESTS_ERRORED_INDEX] + len(result.errors)
    if (result.failures) :
        totals[Settings.TOTAL_TESTS_FAILED_INDEX] = totals[Settings.TOTAL_TESTS_FAILED_INDEX] + len(result.failures)


######################################################################
# Test Machines
loader = unittest.TestLoader()
suite = loader.loadTestsFromModule(TestWeblogicMachine)
global_suite = unittest.TestSuite([suite])

testContext = tcm.TestContext(pbb.properties)

machineNames = testContext.props.getChildBranches("/Machines")

for machineName in machineNames :
    testContext.setKey(machineName)
    TestWeblogicMachine.testContext = testContext
    runSuite(global_suite, totals)

######################################################################

######################################################################
# Test Weblogic Server
loader = unittest.TestLoader()
suite = loader.loadTestsFromModule(TestWeblogicServer)
global_suite = unittest.TestSuite([suite])

testContext = tcm.TestContext(pbb.properties)

serverNames = testContext.props.getChildBranches("/Servers")

for serverName in serverNames :
    testContext.setKey(serverName)
    TestWeblogicServer.testContext = testContext
    runSuite(global_suite, totals)

######################################################################

######################################################################
# Test JDBC Resources

loader = unittest.TestLoader()
suite = loader.loadTestsFromModule(TestJDBCResource)
global_suite = unittest.TestSuite([suite])

testContext = tcm.TestContext(pbb.properties)

jdbcNames = testContext.props.getChildBranches("/JDBCSystemResources")

for jdbcName in jdbcNames :
    testContext.setKey(jdbcName)
    TestJDBCResource.testContext = testContext
    runSuite(global_suite, totals)

#####
# old

loader = unittest.TestLoader()
suite = loader.loadTestsFromModule(TestJDBCResource)
global_suite = unittest.TestSuite([suite])

testContext = tcm.TestContext(pbb.properties)
TestJDBCResource.testContext = testContext
domain = testContext.props.get("DOMAIN")
i = 1
TestJDBCResource.testContext.setKey(domain + ".JDBCResource." + str(i) + ".")
dsName = TestJDBCResource.testContext.props.get(TestJDBCResource.testContext.key + "name")
while dsName :
    runSuite(global_suite, totals)
    i += 1
    TestJDBCResource.testContext.setKey(domain + ".JDBCResource." + str(i) + ".")
    dsName = TestJDBCResource.testContext.props.get(TestJDBCResource.testContext.key + "name")

######################################################################

######################################################################
# Test Deployments
loader = unittest.TestLoader()
suite = loader.loadTestsFromModule(TestDeployments)
global_suite = unittest.TestSuite([suite])

testContext = tcm.TestContext(pbb.properties)
TestDeployments.testContext = testContext
runSuite(global_suite, totals)

######################################################################

print("TestDomain: Total tests ran = " + str(totals[Settings.TOTAL_TESTS_RUN_INDEX]))
print("TestDomain: Total tests failed = " + str(totals[Settings.TOTAL_TESTS_FAILED_INDEX]))
print("TestDomain: Total tests in error = " + str(totals[Settings.TOTAL_TESTS_ERRORED_INDEX]))

if (totals[Settings.TOTAL_TESTS_RUN_INDEX] > 0 and (totals[Settings.TOTAL_TESTS_FAILED_INDEX] > 0 or totals[Settings.TOTAL_TESTS_ERRORED_INDEX] > 0)) :
    sys.exit(1)
sys.exit(0)
