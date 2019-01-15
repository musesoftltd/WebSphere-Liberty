import os

from wlst.WlstWrapper import cd


# Function to enabled or disabled the Admin Port offline
def enabledAdminPort (adminPortEnabled, AdminPort, listenPort):
        cmo = cd('/')
        set('AdministrationPortEnabled', adminPortEnabled)
        set('AdministratorPort', int(listenPort))
        return
