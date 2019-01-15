import jarray
from java.util.logging import Logger
from javax.management import ObjectName
from sets import Set

import PbCommon
from com.muse.fmw.platform import PbProperties
from entities.PbWlstEntity import PbWlstEntity
from pb import PbWlstWrappers
from WlstWrapper import assign, getMachineNames, pushd, \
    removeReferencesToBean, getMBean, destroyMachine


# from pb import PbTypes
LOGGER = Logger.getLogger("entities.PbWlstEntities")

__clusterToServersMap = dict()

def assignServersToClusters(clusterToServersMap) :
    LOGGER.info("About to assign servers to clusters")
    clusters = clusterToServersMap.keys()
    for cluster in clusters :
        serversSet = clusterToServersMap.get(cluster)
        serverCsv = PbCommon.getCsv(serversSet)
        LOGGER.info("Assigning to cluster " + cluster + " the following servers: " + serverCsv)
        assign("Server", serverCsv, "Cluster", cluster)

def getEntityCollection(func, prefix) :
    result = Set()
    collection = func()
    for entry in collection :
        result.add(prefix + entry)
    return result

class Domain(PbWlstEntity):
    pass

class Machine(PbWlstEntity):
    def exists(self):
        machines = getMachineNames()
        for machine in machines :
            if self.name == machine :
                LOGGER.fine("Machine exists: " + str(self.name))
                return True
        LOGGER.fine("Machine does not exist: " + str(self.name))
        return False

    def delete(self) :
        LOGGER.info("Deleting machine: " + str(self.name))
        pushd("/")
        try :
            removeReferencesToBean(getMBean(self.mbeanLocation))
            destroyMachine(getMBean(self.mbeanLocation))
            popd()
        except :
            LOGGER.severe("Unable to delete machine: " + str(self.name))
            popd()
            raise
        LOGGER.info("Deleted machine: " + str(self.name))


class MachineCollection:
    def getCollection(self) :
        return getEntityCollection(getMachineNames, "/Machines/")

class Server(PbWlstEntity):
    def setValue(self, mbeanAttribute, value) :
        name = mbeanAttribute.mbeanAttributePath[1]

        if name == "Cluster" :
            if value == None :
                self.removeAsTarget()
                setCluster(value)
            else :
                cluster = value.name
                server = self.name
                if len(__clusterToServersMap) == 0 :
                    PbWlstWrappers.addOfflineFunc("All", assignServersToClusters, __clusterToServersMap)
                #                assign("Server", self.name, "Cluster", value.name)

                serverSet = __clusterToServersMap.get(cluster)
                if not serverSet :
                    serverSet = Set()
                    __clusterToServersMap[cluster] = serverSet
                serverSet.add(server)

        elif name == "Machine" :
            assign("Server", self.name, "Machine", value.name)
        else :
            PbWlstEntity.setValue(self, mbeanAttribute, value)

    def delete(self) :
        LOGGER.info("Deleting server: " + str(self.name))
        pushd("/Servers")
        try :
            pushd(self.mbeanLocation)
            setCluster(None)
            setMachine(None)
            removeReferencesToBean(getMBean(self.mbeanLocation))
            popd()
            delete(self.name, "Server")
        except Exception, e:
            LOGGER.severe("Unable to delete server: " + str(self.name))
            popd()
            raise e
        LOGGER.info("Deleted server: " + str(self.name))

    def removeAsTarget(self) :
        LOGGER.fine("Entering entities.PbWlstEntities.Server.removeTarget")

        pushd('/Deployments')

        deployments = lsmap()

        for deployment in deployments :
            print deployment
            pushd(deployment)
            pushd("Targets")

            targets = lsmap()
            newTargets = []
            rePoint = False

            for target in targets :
                print("Target='" + target + "'")

                if target != self.name :
                    # find the type:
                    pushd(target)
                    type = get("Type")
                    newTargets.append(ObjectName("com.bea:Name=" + target + ",Type=" + type))
                    popd()
                else :
                    rePoint = True

            popd()
            print("New Targets: " + str(jarray.array(newTargets, ObjectName)))
            if rePoint :
                print("Repointing targets: " + str(jarray.array(newTargets, ObjectName)))
                set('Targets', jarray.array(newTargets, ObjectName))
            popd()
        popd()
        LOGGER.fine("Exiting entities.PbWlstEntities.Server.removeTarget")

class ServerCollection:
    def getCollection(self) :
        return getEntityCollection(getServerNames, "/Servers/")

class Cluster(PbWlstEntity):
    def exists(self):
        cluster = getCluster(self.name)
        return cluster != None

    def delete(self) :
        LOGGER.info("Deleting cluster: " + str(self.name))
        pushd('/Clusters')
        try :
            delete(self.name, "Cluster")
            popd()
        except Exception, e:
            LOGGER.severe("Unable to delete cluster: " + str(self.name))
            popd()
            raise e
        LOGGER.info("Deleted cluster: " + str(self.name))

class ClusterCollection:
    def getCollection(self) :
        return getEntityCollection(getClusterNames, "/Clusters/")


class JDBCSystemResource(PbWlstEntity):
    def delete(self) :
        LOGGER.info("Deleting JDBCSystemResource: " + str(self.name))
        pushd('/')
        try :
            delete(self.name, "JDBCSystemResource")
            popd()
        except Exception, e:
            LOGGER.severe("Unable to delete JDBCSystemResource: " + str(self.name))
            popd()
            raise e
        LOGGER.info("Deleted JDBCSystemResource: " + str(self.name))


class JDBCSystemResourceCollection:
    def getCollection(self) :
        func = divert(lsmap, "/JDBCSystemResources")
        return getEntityCollection(func, "/JDBCSystemResources/")


