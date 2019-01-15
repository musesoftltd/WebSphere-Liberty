import PbCommon
import javax.management.ObjectName as ObjectName
from wlst.WlstWrapper import getCluster, getMachine, encrypt, decryptBytes


class MBeanAttribute:
    def __init__(self, name, value, path):
        self.name = name
        self.value = value
        self.path = path
        self.mbeanAttributePath = None
        self.isOffline = False
        self.isPostConfig = False

    def __eq__(self, other):
        return ((self.name, str(self.value), self.path) == 
                (other.name, str(other.value), other.path))

    def __ne__(self, other):
        return not self.__eq__(other)

    def getAttribute(self):
        return self.value

    def __str__(self):
        return "[name=" + self.name + ", value=" + self.value + "]"

    def presentValue(self):
        return self.getAttribute()

class MBeanObjectAttribute(MBeanAttribute) :
    """
    Constructor for an mbean assignment to another mbean.
    This constructor can be invoked with a string value detailing the name of the mbean or an 'ObjectName' embodying
    the mbean object itself. This needs to be normalised as comparisons are done against target and current states.
    """
    def __init__(self, name, value, path):
        if isinstance(value, ObjectName) :
            value = value.getKeyProperty("Name")
        MBeanAttribute.__init__(self, name, value, path)


class MBeanServerClusterAttribute(MBeanObjectAttribute):
    def __init__(self, name, value, path):
        MBeanObjectAttribute.__init__(self, name, value, path)

    def getAttribute(self):
        cluster = getCluster(self.value)
        return cluster

class MBeanServerMachineAttribute(MBeanObjectAttribute):
    def __init__(self, name, value, path):
        MBeanObjectAttribute.__init__(self, name, value, path)

    def getAttribute(self):
        machine = getMachine(self.value)
        return machine

class MBeanIntegerAttribute(MBeanAttribute):
    def __init__(self, name, value, path):
        MBeanAttribute.__init__(self, name, int(value), path)


class MBeanEncryptedAttribute(MBeanObjectAttribute):
    def __init__(self, name, value, path):
        MBeanObjectAttribute.__init__(self, name, value, path)
        if isinstance(value, str) :
            self.encryptedTextToSet = encrypt(self.value)
        elif value:
            self.value = decryptBytes(value)
            self.encryptedTextToSet = encrypt(self.value)
        else:
            self.encryptedTextToSet = None

    def getAttribute(self):
        if self.encryptedTextToSet :
            return self.encryptedTextToSet
        return MBeanObjectAttribute.getAttribute(self)

    def __eq__(self, other):
        return MBeanObjectAttribute.__eq__(self, other)

class MBeanBooleanAttribute(MBeanAttribute):
    def __init__(self, name, value, path):
        if PbCommon.getBoolFromString(value) or value == True or value == 1 or value == "1" :
            MBeanAttribute.__init__(self, name, True, path)
        else :
            MBeanAttribute.__init__(self, name, False, path)


class MBeanBooleanIntegerAttribute(MBeanBooleanAttribute):
    def getAttribute(self):
        if self.value :
            return 1
        else :
            return 0

    def presentValue(self):
        if self.value :
            return "true"
        else :
            return "false"
