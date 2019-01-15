import unittest

from ConfigureDomain import props
import PbCommon as pbc
from pb import PbWlstLib


class PbCommonTest(unittest.TestCase, props) :
    def getConnectionUrl(self, serverKey) :
        listenAddress = props.get("/Servers/" + serverKey + "/ListenAddress")
        if self.adminPortEnabled and serverKey == "AdminServer" :
            listenPort = props.get("admin.server.adminPort")
            connectionUrl = 't3s://' + listenAddress + ':' + listenPort
        elif self.sslEnabled :
            listenPort = props.get("/Servers/" + serverKey + "/SSL/" + serverKey + "/ListenPort")
            connectionUrl = 't3s://' + listenAddress + ':' + listenPort
        else:
            listenPort = props.get("/Servers/" + serverKey + "/ListenPort")
            connectionUrl = 't3://' + listenAddress + ':' + listenPort
        return connectionUrl

    def setUp(self, testContext) :
        self.adminListenAddress = testContext.props.get("server.admin.listen.address")
        self.adminListenPort = testContext.props.get("server.admin.listen.port")
        self.adminPassword = pbc.getDecryptedValue(testContext.props, "adminPassword")
        self.adminUserName = testContext.props.get("adminUserName")
        self.sslEnabled = pbc.getBoolFromString(testContext.props.get("SSLEnabled"))
        self.adminPortEnabled = pbc.getBoolFromString(testContext.props.get("admin.server.adminPortEnabled"))
        self.nodeManagerPort = testContext.props.get("nodemanager.listenPort")
        self.domainName = testContext.props.get("domainName")
        self.domainDir = testContext.props.get("domainHome")
        self.nmType = testContext.props.get("nodemanager.connectionType")
        self.jvmArgs = testContext.props.get("global._java_options")
        PbWlstLib.props = testContext.props
