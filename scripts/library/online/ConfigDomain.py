from java.util.logging import *
from java.util.logging import Logger
import sys
import traceback

import PlatformBuildBase as pbb
import entities.EntityUtils as eu
from pb import PbTypes
from pb import PbWlstLib as pbwl
from pb import SystemControl
import pb.PbWlstWrappers as pbwrappers
from wlst.WlstWrapper import isRestartRequired


LOGGER = Logger.getLogger("ConfigDomain")

try :
    entityFactory = eu.getEntityFactoryWithSource(pbb.properties)
    domainHome = entityFactory.props.get("domainHome")

    LOGGER.info("Setting up type system and factories")
    PbTypes.ensureTypeSystem("../resources/classifiers.properties", "../resources/types.properties")
    pbwl.props = entityFactory.getProperties()

    LOGGER.info("Setting up online and offline function wrappers")
    pbwrappers.setUp(domainHome)
    exitValue = SystemControl.EXIT_NORMALLY

    LOGGER.info("Configuring domain : " + domainHome)
    if pbb.mode == "offline" :
        result = pbwrappers.pbwl.configureOffline()
        offlinePostOps = len(pbwrappers.OfflinePostConfigFunctionCalls) > 0
        if exitValue == SystemControl.EXIT_NORMALLY and offlinePostOps :
            if offlinePostOps :
                pbwrappers.doOfflinePostConfigFunctions()
            exitValue = SystemControl.EXIT_ON_MODIFICATION
    elif pbb.mode == "online" :
        result = pbwrappers.pbwl.configure()
        if result :
            LOGGER.info("Modifications detected, should be re-run.")
            exitValue = SystemControl.EXIT_ON_MODIFICATION
            pbwrappers.doOfflineRegisteredFunctionCalls()
        else :
            # Do something else - i.e. Machines, servers Clusters and JDBC are set up - now ready for HA adaption
            pass

        if isRestartRequired() :
            pbwrappers.switchToOffline()
            exitValue = SystemControl.EXIT_ON_MODIFICATION

        offlinePostOps = len(pbwrappers.OfflinePostConfigFunctionCalls) > 0
        onlinePostOps = len(pbwrappers.OnlinePostConfigFunctionCalls) > 0
        if exitValue == SystemControl.EXIT_NORMALLY and (offlinePostOps or onlinePostOps) :
            if onlinePostOps :
                pbwrappers.doOnlinePostConfigFunctions()
            if offlinePostOps :
                pbwrappers.doOfflinePostConfigFunctions()
            exitValue = SystemControl.EXIT_ON_MODIFICATION

        SystemControl.exit(exitValue)
except :
    print "Unexpected error in ConfigDomain.py: ", sys.exc_info()[0], sys.exc_info()[1]
    tb = sys.exc_info()[2]
    traceback.print_tb(tb)
    SystemControl.exitOnError()

