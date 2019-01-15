# A representation of a properties file that defines mappings between classifiers and attributes of the classifier.
from java.io import FileInputStream
import re
import types

from PbCommon import ENCRPYTED_VALUE_PREFIX, getDecryptedValue, getBoolFromString
from com.muse.fmw.platform import PbProperties
from entities import MBeanAttributeTypes


global TYPES
TYPES = PbProperties()

# A representation of the classifiers. This is the data that feeds the mechanism that establishes, given an MBean path,
# what 'class' that falls within.
global CLASSIFIERS
CLASSIFIERS = PbProperties()

def ensureTypeSystem(classifiersFileName, typesFileName) :
    if TYPES.isEmpty() :
        propsInputStream = FileInputStream(typesFileName)
        TYPES.load(propsInputStream)
    if CLASSIFIERS.isEmpty() :
        propsInputStream = FileInputStream(classifiersFileName)
        CLASSIFIERS.load(propsInputStream)


def constructPropertyPath(parts) :
    '''
    Helper function that takes an array of string parts and constructs a '/' separated string from them
    '''
    result = ""
    length = len(parts)
    for part in parts :
        result = result + part
        if part == parts[length - 1] :
            break
        result = result + PbProperties.SEPARATOR
    return result

def classify(path):
    '''
    Classify an mbean path.
    The path is compared against regular expressions from the CLASSIFIERS to establish what 'class' a path falls within
    The resultant value is a key into the TYPES data where python classes and specific attribute types are defined.
    '''
    keys = CLASSIFIERS.keySet()
    for key in keys :
        typeRegEx = CLASSIFIERS.get(key)
        if(re.match(typeRegEx, path)) :
            return key
    return None


def getMBeanAttribute(name, value, path):
    '''
    Helper method to get an MBeanAttribute object. This uses the type system to access the required MBeanAttribute type,
    if a type is not provided then the default is to use 'MBeanAttribute'.
    '''
    result = MBeanAttributeTypes.MBeanAttribute(name, value, path)
    classifier = classify(name)
    if classifier != None :
        pbTypeDict = getAttributeType(classifier)
        if pbTypeDict != None :
            attributeClass = getattr(MBeanAttributeTypes, pbTypeDict["pbAttributeType"])
            attributeObj = types.InstanceType(attributeClass)
            attributeObj.__init__(name, value, path)
            attributeObj.isOffline = getBooleanAttributeFromTypeDict(pbTypeDict, "isOffline")
            attributeObj.isPostConfig = getBooleanAttributeFromTypeDict(pbTypeDict, "isPostConfig")
            attributeObj.getAttribute()
            result = attributeObj

    result.mbeanAttributePath = getMBeanPath(name)
    return result

def getMBeanPropertyTypeString(key) :
    return getTypeString(key[1:])

def getAttributeFromTypeDict(dict, key) :
    try :
        val = dict[key]
        return val
    except KeyError:
        return None

def getBooleanAttributeFromTypeDict(dict, key) :
    val = getAttributeFromTypeDict(dict, key)
    getDecryptedValue
    return getBoolFromString(val)

def getAttributeTypeDict(keyParts) :
    result = dict()

    base = constructPropertyPath(keyParts)
    attributes = TYPES.getLeaves(base)
    for attribute in attributes :
        result[TYPES.getLeafName(attribute)] = TYPES.get(attribute)

    return result


def getAttributeType(key) :
    suffix = "/pbAttributeType"
    try :
        keyParts = re.split(PbProperties.SEPARATOR, key)
        property = constructPropertyPath(keyParts) + suffix
        attributeType = TYPES.get(property)

        if attributeType == None :
            while len(keyParts) > 0 :
                property = constructPropertyPath(keyParts) + suffix
                attributeType = TYPES.get(property)
                if attributeType != None :
                    break
                keyParts.pop()

        if attributeType == None :
            return None
        return getAttributeTypeDict(keyParts)
    except :
        return None


def getTypeString(key) :
    '''
    Helper function to obtain a type string. Taking the key input the key is deconstructed into its component parts
    (i.e. as it represents a path) and then reconstructed in reducing length until a match is found. The initial query
    just uses the key intact, subsequently as the key is reduced in length, when a match is not found, the string
    '.default' is also appended. So either the key must exist in its true form, or one of its descendants must exist
    with a '.default' suffix.
    '''
    try :
        keyParts = re.split(PbProperties.SEPARATOR, key)
        property = constructPropertyPath(keyParts)
        result = TYPES.get(property)
        suffix = ".default"
        if result == None :
            while len(keyParts) > 0 :
                property = constructPropertyPath(keyParts)
                result = TYPES.get(property + suffix)
                if result != None :
                    break
                keyParts.pop()
        return result
    except :
        return None

def getMBeanPath(key) :
    return getMBeanPathOnline(key)

def getMBeanPathOffline(key) :
    mbeanPath = getMBeanPathOnline(key)
    if not mbeanPath :
        return None
    route = mbeanPath[0]
    dest = mbeanPath[1]

    offlineRoute = getOfflineMBeanPath(route)
    if offlineRoute :
        route = offlineRoute
    return [route, dest]

def getMBeanPathOnline(key):
    '''
    Given a property key return the corresponding mbean path
    '''

    if key == PbProperties.SEPARATOR:
        return [key, ""]

    keyParts = re.split(PbProperties.SEPARATOR, key)
    if len(keyParts) < 1 :
        raise Exception("MBean Path must have at least 1 part : " + str(key))


    numOfParts = len(keyParts)
    lastKeyPart = keyParts[numOfParts - 1]
    path = ""
    for keyPart in keyParts :
        if keyPart != lastKeyPart :
            path = path + keyPart + "/"
    return [path, lastKeyPart]

def getPropertyValue(props, name) :
    '''
    Simply obtain a property vlaue from the supplied properties. This introduces the special value 'PB:None' which
    is translated as Python's 'None'. This allows explicit resetting of tracked mbean vlaues, as simply removing the
    property from being tracked means it will no longer be tracked and therefore not modified.
    '''
    propertyValue = props.get(name)
    if propertyValue == "PB:None" :
        propertyValue = None
    elif propertyValue == "PB:True" :
        propertyValue = True
    elif propertyValue == "PB:False" :
        propertyValue = False
    elif re.match(ENCRPYTED_VALUE_PREFIX, propertyValue):
        propertyValue = getDecryptedValue(props, name)

    return propertyValue

def getOfflineMBeanPath(onlineMBeanPath):
    regexKeys = TYPES.getSortedSubset("transform/input")
    for regexKey in regexKeys :
        result = re.match(TYPES.get(regexKey), onlineMBeanPath)
        if result :
            groupDict = result.groupdict()
            outputString = TYPES.get("transform/output" + regexKey[len("transform/input"):])
            return outputString % groupDict
    return None
