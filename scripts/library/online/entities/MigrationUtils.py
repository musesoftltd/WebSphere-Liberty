import jarray
from java.lang import Exception
from java.util.logging import Logger
from javax.management import ObjectName

from pb.PbWlstLib import connectToAdminServer
from wlst.WlstWrapper import edit, startEdit, cd, ls, pushd, get, popd, save, \
    activate, cancelEdit


LOGGER = Logger.getLogger("entities.MigrationUtils")

def rePointAppTargets(userName, password, url, properties) :
    if connectToAdminServer(userName, password, url) :
        try :
            edit()
            startEdit()

            cmo = cd('AppDeployments')
            i = 1
            source = properties.get("migrate.target." + str(i) + ".source")
            while source :
                destination = properties.get("migrate.target." + str(i) + ".destination")
                destinationType = properties.get("migrate.target." + str(i) + ".type")
                deployments = ls(returnMap='true')

                for deployment in deployments :
                    print deployment
                    pushd(deployment + "/Targets")
                    targets = ls(returnMap='true')
                    newTargets = []
                    rePoint = False

                    for target in targets :
                        print("Target='" + target + "'")
                        theTarget = target
                        if target == source :
                            theTarget = destination
                            type = destinationType
                            rePoint = True
                        else :
                            # find the type:
                            pushd(target)
                            type = get("Type")
                        newTargets.append(ObjectName("com.bea:Name=" + theTarget + ",Type=" + type))

                    print("New Targets: " + str(jarray.array(newTargets, ObjectName)))
                    if rePoint :
                        print("Repointing targets: " + str(jarray.array(newTargets, ObjectName)))
                        set('Targets', jarray.array(newTargets, ObjectName))
                    popd()

                i = i + 1
                source = properties.get("migrate.target." + str(i) + ".source")

            save()
            activate()
        except Exception, e:
            LOGGER.severe("Caught Exception in migration : " + e)
            cancelEdit("y")
            raise e


