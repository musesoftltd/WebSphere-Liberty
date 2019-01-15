from java.io import FileInputStream
from java.lang import IllegalStateException
from java.util.logging import Logger, Level
import new
from sets import Set

import PbWlstEntities
from com.muse.fmw.platform import PbProperties
from entities.PbEntity import PbEntity
import pb.PbTypes as PbTypes


# The entity factories (currently only one exists)
LOGGER = Logger.getLogger("entities.EntityUtils")

global ENTITY_FACTORIES
ENTITY_FACTORIES = dict()

def getEntityFactoryWithSource(source) :
    try :
        result = ENTITY_FACTORIES[source]
    except KeyError :
        result = EntityFactory(source)
        ENTITY_FACTORIES[source] = result
    return result

def getEntityFactory() :
    if len(ENTITY_FACTORIES) > 0:
        return ENTITY_FACTORIES.items()[len(ENTITY_FACTORIES) - 1][1]
    raise IllegalStateException("No entity factory has been created!")


def checkEntityChanged(theEntity) :
    diffEntities = DictDiffer(theEntity.map, theEntity.pbEntity.map)
    changed = diffEntities.changed()
    if len(changed) > 0 :
        LOGGER.info("*** Entity to be changed: " + theEntity.pbEntity.path + " : " + str(changed))
    elif LOGGER.isLoggable(Level.FINE) :
        LOGGER.fine("*** Entity Unchanged: " + theEntity.pbEntity.path + " : " + str(diffEntities.unchanged()))
    return len(changed) > 0

class ConfigurableCollection :
    '''
    This class embodies the idea of a collection of objects that are of the same type that need to be configured.
    This introduces the ability to add and remove items that are not tracked. Therefore this operates at the Entity
    level (not the entity attribute level which cannot monitor additions and deletions).
    This comes with CRUD like operations 'createNew', 'removeOld' and 'updateExisting' which do what they suggest.
    '''
    def __init__(self, path):
        self.entities = dict()
        entityFactory = getEntityFactory()
        props = entityFactory.getProperties()

        keys = props.getChildNodes(path)
        for key in keys :
            entity = entityFactory.createEntity(key)
            if(entity.exists()):
                self.entities[key] = entity

        currentCollection = entityFactory.createCurrentCollection(path)
        targetCollection = entityFactory.createTargetCollection(path)
        toAdd = targetCollection - currentCollection
        toRemove = currentCollection - targetCollection
        candidatesToChange = currentCollection.intersection(targetCollection)

        self.entitiesToAdd = []
        for entityPath in toAdd :
            self.entitiesToAdd.append(entityFactory.createCurrentStateEntityFromPath(entityPath))
        if len(self.entitiesToAdd) > 0 :
            for entity in self.entitiesToAdd :
                LOGGER.info("*** Entity to be added:: " + str(entity))

        self.entitiesToRemove = []
        for entityPath in toRemove :
            self.entitiesToRemove.append(entityFactory.createCurrentStateEntityFromPath(entityPath))
        if len(self.entitiesToRemove) > 0 :
            for entity in self.entitiesToRemove :
                LOGGER.info("*** Entity to be removed:: " + str(entity))


        self.entitiesToChange = []
        for candidateEntityPath in candidatesToChange :
            theEntity = self.entities[candidateEntityPath]
            if checkEntityChanged(theEntity) :
                self.entitiesToChange.append(theEntity)

        self.modificationsPresent = False

    def createNew(self):
        for entity in self.entitiesToAdd :
            LOGGER.fine("Creating Entity : " + str(entity))
            entity.create()
            LOGGER.fine("Created Entity : " + str(entity))
            self.modificationsPresent = True
            self.entitiesToChange.append(entity)

    def removeOld(self):
        for entity in self.entitiesToRemove :
            LOGGER.fine("Removing Entity : " + str(entity))
            entity.delete()
            LOGGER.fine("Removed Entity : " + str(entity))
            self.modificationsPresent = True

    def updateExisting(self):
        changesApplied = False
        for entity in self.entitiesToChange :
            LOGGER.fine("Changing Entity : " + str(entity))
            changesApplied = entity.update()
            if changesApplied :
                LOGGER.fine("Changed Entity : " + str(entity) + " (Changes applied: " + str(changesApplied) + ")")
                self.modificationsPresent = True
        return changesApplied

class EntityFactory:
    '''
    Factory class to create entities. Entities are high level objects (such as Server, Machine and Cluster)
    '''
    def __init__(self, source):
        if type(source) == str:
            self.props = PbProperties()
            propsInputStream = FileInputStream(source)
            self.props.load(propsInputStream)
        else :
            self.props = PbProperties(source)

    def createTargetStateEntity(self, path):
        # Leaves are the attributes that hang off this path directly.
        leaves = self.props.getLeaves(path)
        entity = PbEntity(path)
        for leaf in leaves :
            entity.addAttribute(leaf, PbTypes.getPropertyValue(self.props, leaf))

        # Children are also attributes, but they exist not directly off the path but further down, possibly on some
        # other entity. Currently these children are handled exactly as leaves, but there may come a time when the
        # interveining entity requires some special processing, and hence they are in a separate loop.
        # e.g. Machines/AdminMachine/NodeManager/AdminMachine/ListenAddress
        # Here AdminMachine is the entity, but NodeManager/AdminMachine could represent a NodeManager entity, however
        # as NodeManagers and Machines are in the same lifecycle these can be treated as extended attributes of the
        # Machine.
        children = self.props.getChildren(path)
        for child in children :
            entity.addAttribute(child, PbTypes.getPropertyValue(self.props, child))

        entity.targetType = PbTypes.getMBeanPropertyTypeString(path)
        return entity

    def createCurrentStateEntity(self, pbEntity):
        classifier = PbTypes.classify(pbEntity.path)
        pbEntityType = PbTypes.getTypeString(PbTypes.constructPropertyPath([classifier, "pbentityType"]))
        entityClass = getattr(PbWlstEntities, pbEntityType)
        entity = new.instance(entityClass)
        entity.__init__(pbEntity)
        return entity

    def createCurrentStateEntityFromPath(self, path):
        return self.createCurrentStateEntity(self.createTargetStateEntity(path))

    def createEntity(self, path):
        pbEntity = self.createTargetStateEntity(path)
        result = self.createCurrentStateEntity(pbEntity)
        return result

    def createDomainEntity(self):
        result = None
        leaves = self.props.getLeaves("/")
        pbEntity = PbEntity("/")

        if leaves.size() > 0 :
            for leaf in leaves :
                pbEntity.addAttribute(leaf, PbTypes.getPropertyValue(self.props, leaf))

            result = self.createCurrentStateEntity(pbEntity)
        return result

    def createTargetCollection(self, path) :
        result = Set()
        for key in self.props.getChildNodes(path) :
            result.add(key)
        return result

    def createCurrentCollection(self, path):
        classifier = PbTypes.classify(path)
        pbCollectionType = PbTypes.getTypeString(PbTypes.constructPropertyPath([classifier, "pbcollectionType"]))
        collectionClass = getattr(PbWlstEntities, pbCollectionType)
        coll = new.instance(collectionClass)
        return coll.getCollection()

    def getProperties(self):
        return self.props


class DictDiffer(object):
    """
    Utility class to work out the difference in two maps / dictionaries
    works out:
     items added
     items removed
     keys same in both but changed values
     keys same in both and unchanged values
    """
    def __init__(self, current_dict, target_dict):
        self.current_dict, self.target_dict = current_dict, target_dict
        self.current_keys = Set(current_dict.keys())
        self.target_keys = Set(target_dict.keys())
        self.intersect = self.current_keys.intersection(self.target_keys)

    def added(self):
        return self.current_keys - self.intersect

    def removed(self):
        return self.target_keys - self.intersect

    def changed(self):
        result = Set()
        for o in self.intersect :
            if self.target_dict[o] != self.current_dict[o] :
                result.add(o)
        return result

    def unchanged(self):
        result = Set()
        for o in self.intersect :
            if self.target_dict[o] == self.current_dict[o] :
                result.add(o)
        return result
