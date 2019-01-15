from java.util.logging import Logger

from wlst.WlstWrapper import pushd, pwd, popd, lsChildMap, lsmap


LOGGER = Logger.getLogger("pb.Catalogue")

class CatalogueEntry :
    def __init__(self, name, dir, dirContents=None):
        self.name = name
        self.dir = dir
        self.branches = dict()
        self.dirContents = dirContents

    def catalogueEntryToString(self, entry):
        result = entry.dir + "\n"
        for child in entry.branches.values() :
            result = result + self.catalogueEntryToString(child)
        return result

    def __str__(self):
        return self.catalogueEntryToString(self)


def catalogueTree(catalogueEntry) :
    try :
        origDir = catalogueEntry.dir
        theContents = catalogueEntry.dirContents
        for dirEntry in catalogueEntry.dirContents :
            pushd(dirEntry)
            newDir = pwd()
            if(catalogueEntry.dir == newDir) :
                # dir has not moved - no other indicator!!
                popd()
                continue
            else :
                newDirContents = lsChildMap()
                newEntry = CatalogueEntry(dirEntry, newDir, newDirContents)
                catalogueEntry.branches[dirEntry] = newEntry
                catalogueTree(newEntry)
                entryDir = pwd()
                popd()
                exitDir = pwd()
    except Exception, e:
        LOGGER.severe("Caught Exception in cataloguing : " + str(e))
        raise e
    return catalogueEntry


def catalogue(dir) :
    pushd(dir)
    dirContents = lsmap()
    pwd = pwd()
    catalogueEntry = catalogueTree(CatalogueEntry("/", pwd, dirContents))
    return catalogueEntry

