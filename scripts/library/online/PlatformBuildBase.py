import getopt
from java.lang import Boolean
import sys

from com.muse.fmw.platform import PlatformPropertyBuilder
from pb import SystemControl


def usage():
    print "Usage:"
    print "-c <conf location> -e <env> -d <domain> [optional: -o <property-override-filename>"
    SystemControl.exitOnUsage()

try:
    opts, args = getopt.getopt(sys.argv[1:], "c:d:e:o:")
except getopt.GetoptError, err:
    print str(err)
    usage()

mode = "online"
overridesFile = None
properties = ""
for opt, arg in opts:
    if opt == "-c":
        confLoc = arg
    if opt == "-e":
        env = arg
    if opt == "-d":
        domain = arg
    if opt == "-o":
        overridesFile = arg
    if opt == "-m":
        mode = arg

if confLoc == "" or env == "" or domain == "":
    usage()

platformPropertyBuilder = PlatformPropertyBuilder()
properties = platformPropertyBuilder.buildProperties(confLoc, env, domain, Boolean.FALSE, overridesFile)

# Include wlst module paths
beaHome = properties.get("wls.BEAHOME")
weblogicHome = properties.get("wls.WLS_INSTALL_DIR")
sys.path.append(weblogicHome + "/common/wlst/modules")
sys.path.append(beaHome + "/oracle_common/util/jython/Lib")

