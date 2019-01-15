from java.io import FileInputStream
from java.util import Properties
from java.util.logging import Logger

from com.muse.properties.secure import EncryptionUtils


global ENCRPYTED_VALUE_PREFIX
ENCRPYTED_VALUE_PREFIX = "::ENCRYPTED::"

global LOGGER
LOGGER = Logger.getLogger("PbCommon")

def getBoolFromString(str) :
    return (str == "true" or str == "True")

def getDecryptedValue(props, key):
    password = props.get(key)
    if password :
        passkey = props.get('security.passkey')

        if password.startswith(ENCRPYTED_VALUE_PREFIX):
            password = EncryptionUtils.decryptString(passkey, password[len(ENCRPYTED_VALUE_PREFIX):])

    return password


def decryptfunc(obj) :
    pass

# Load properties file in java.util.Properties
def loadJavaProperties(propertyFileName):
    inStream = FileInputStream(propertyFileName)
    properties = Properties()
    properties.load(inStream)

    return properties


# Return all keys and values of properties file in csv list
def serialiseJavaPropertiesAsCsv(properties):
    keys = properties.keySet()
    result = ""
    for key in keys:
        value = properties.getProperty(key)
        if value :
            if len(result) > 0 :
                result = result + ","
            result = result + key + "=" + value

    return result

def getCsv(objSet) :
    result = ""
    i = 0
    objArray = []
    for obj in objSet :
        objArray.append(obj)

    while i < len(objArray) :
        result = result + str(objArray[i])
        i = i + 1
        if i < len(objArray) :
            result = result + ","
    return result
