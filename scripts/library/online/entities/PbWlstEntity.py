from java.lang import IllegalStateException
from java.util.logging import Logger, Level

import entities.EntityUtils as entityUtils
from pb import PbTypes
from pb import PbWlstWrappers
from weblogic.management.scripting.core.utils.wlst_core import WLSTException
from wlst.WlstWrapper import pushd, popd, get, create


LOGGER = Logger.getLogger("entities.PbWlstEntity")

def applyChange(pbWlstEntity, mbeanAttribute) :
    requiredValue = pbWlstEntity.pbEntity.get(mbeanAttribute.name)
    try :
        pushd(mbeanAttribute.mbeanAttributePath[0])
    except WLSTException :
        # The value is not present as the parent is not present.
        LOGGER.warning("No path exists to set attribute. Path: '" + mbeanAttribute.mbeanAttributePath[0] + "',  Attribute: '" + mbeanAttribute.mbeanAttributePath[1] + "'. Ignoring.")
        return

    try :
        pbWlstEntity.setValue(mbeanAttribute, requiredValue)
        popd()
    except Exception, e:
        LOGGER.severe("Unable to set attribute identified by '" + mbeanAttribute.name + "', to value '" + str(requiredValue) + "'")
        popd()
        raise e

class PbWlstEntity :
    '''
    this class embodies the current state. It also maintains a reference to the target state (pbEntity) and therefore
    becomes the object of query when differences relating to a specific mbean are needed.
    This class contains methods to synchronise the existing state (which may change during a single run) as well as CRUD
    operations, specifically 'exists', 'update', 'create' and 'delete'.
    All but 'delete' have an implementation which may be overridden by sub classes.
    'create' has a dependency on the type system (see EntityUtils) and requires a 'targetType' to be set on the
    '''
    def __init__(self, pbEntity):
        self.map = dict()
        self.pbEntity = pbEntity
        mbeanSpec = PbTypes.getMBeanPath(pbEntity.path)
        self.mbeanPath = mbeanSpec[0]
        self.name = mbeanSpec[1]
        self.mbeanLocation = self.mbeanPath + self.name
        self.getCurrentValues(pbEntity)

    def addAttribute(self, name, value):
        self.map[name] = PbTypes.getMBeanAttribute(name, value, self.pbEntity.path)

    def getCurrentValues(self, pbEntity):
        if self.exists() :
            for key in pbEntity.keys() :
                # goto the corresponding path in wlst:
                pathSpec = PbTypes.getMBeanPath(key)

                try :
                    pushd(pathSpec[0])
                except WLSTException :
                    # The value is not present as the parent is not present.
                    LOGGER.warning("No attribute identified by '" + key + "' found.")
                    continue

                try :
                    value = get(pathSpec[1])
                    self.addAttribute(key, value)
                    popd()
                except Exception, e :
                    # The value is not present as the parent is not present.
                    LOGGER.severe("Unable to get attribute identified by '" + key + "'")
                    popd()

    def setValue(self, mbeanAttribute, value) :
        name = mbeanAttribute.mbeanAttributePath[1]
        key = mbeanAttribute.name

        try :
            set(name, value)
        except:
            LOGGER.error("Failed to set attribute: name=" + str(name) + ", value=" + str(value) + ", key=" + str(key))
            raise

    def sortChanges(self, changes):
        return changes

    def applyChanges(self, changes):
        changes = self.sortChanges(changes)
        appliedChanges = []
        for change in changes :
            mbeanAttribute = self.pbEntity.map[change]

            if mbeanAttribute.isPostConfig :
                if mbeanAttribute.isOffline :
                    PbWlstWrappers.addOfflinePostConfigFunc(applyChange, self, mbeanAttribute)
                else :
                    PbWlstWrappers.addOnlinePostConfigFunc(applyChange, self, mbeanAttribute)
            else :
                appliedChanges.append(change)
                if mbeanAttribute.isOffline :
                    PbWlstWrappers.addOfflineFunc("All", applyChange, self, mbeanAttribute)
                else :
                    applyChange(self, mbeanAttribute)
        return appliedChanges

    def exists(self):
        try :
            pushd(self.mbeanLocation)
            return True
        except WLSTException :
            # The value is not present as the parent is not present.
            LOGGER.warning("MBean path not found: " + self.mbeanLocation)
        return False

    def update(self):
        """
        Although there may be value in understanding Added and Removed items, we do not process these. Only changed
        items are modified. This stems from the premise that only keys found in the target property set are monitored,
        if a property is removed then it is simply not tracked anymore and will not show here. Similarly items that
        exist in the current state that are not tracked as property keys are not considered. Therefore Added and Removed
        sets in the 'DictDiffer' are always empty..
        """
        self.getCurrentValues(self.pbEntity)
        diffEntities = entityUtils.DictDiffer(self.map, self.pbEntity.map)
        return len(self.applyChanges(diffEntities.changed())) > 0

    def create(self):
        pushd("/")
        try :
            if self.pbEntity.targetType == None :
                raise IllegalStateException("pbEntity '" + self.pbEntity.path + "' does not have a target type. (see classifiers.properties and types.properties)")
            create(self.name, self.pbEntity.targetType)
            popd()
        except Exception, e :
            LOGGER.warning("Unable to create entity: " + self.name + ", type='" + self.pbEntity.targetType + "'")
            popd()
            raise e

    def delete(self) :
        pass

    def __str__(self):
        return "Current settings: <%s, %s>, target settings: %s" % (
        self.pbEntity.path, str(self.map), str(self.pbEntity))
