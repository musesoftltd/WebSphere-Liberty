import pb.PbTypes as PbTypes


class PbEntity :
    '''
    Class that represents the target state of an entity
    '''
    def __init__(self, path):
        self.path = path
        self.map = dict()

    def addAttribute(self, name, value):
        self.map[name] = PbTypes.getMBeanAttribute(name, value, self.path)

    def keys(self):
        return self.map.keys()

    def get(self, name) :
        return self.map[name].presentValue()

    def __str__(self):
        return "<%s, %s>" % (str(self.path), str(self.map.keys()))
