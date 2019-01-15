from java.net import InetAddress
from java.util.logging import *
from java.util.logging import Logger
import sys


logger = Logger.getLogger("scratch")

print "" + InetAddress.getLocalHost().getHostName()
