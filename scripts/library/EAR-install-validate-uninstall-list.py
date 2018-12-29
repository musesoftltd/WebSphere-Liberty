#
# Author: Barry Searle
#
# (C) Copyright IBM Corp. 2004,2007 - All Rights Reserved.
# DISCLAIMER:
# The following source code is sample code created by IBM Corporation.
# This sample code is not part of any standard IBM product and is provided
# to you solely for the purpose of assisting you in the development of your
# applications. The code is provided 'AS IS', without warranty or condition
# of any kind. IBM shall not be liable for any damages arising out of your
# use of the sample code, even if IBM has been advised of the possibility of
# such damages.
#
# Change History:
# 3.0 (25apr2007) added support for installOptions, removed hardcoded "-nodeployejb"
# 2.0 (10feb2006) initial Jython version
# 1.1 (17nov2004) initial shipped version
#

def validateEAR (appPath):
        global ScriptLocation
        execfile(ScriptLocation + "/Definitions.py")
        log(INFO_, "validateEAR: FUTURE: installed EAR-FILE validation")
# endDef

def installEAR (action, appPath, appName, clusterName, nodeName, serverName, installOptions):
        global ScriptLocation
        execfile(ScriptLocation + "/Definitions.py")
        update = ""
        if (action == "update"):
                update = "-update -appname " + appName + " "
        # endIf
        if (serverName != "" and nodeName != ""):
                highlight(MAJOR_, "installEAR: " + action + " node=" + nodeName + " server=" + serverName + " appName=" + appName + " appPath=" + appPath + " installOptions=" + `installOptions` + " ...")
                try:
                        _excp_ = 0
                        options = update + "-verbose -node " + nodeName + " -server " + serverName + " -distributeApp " + installOptions
                        installed = AdminApp.install(appPath, options)
                except:
                        _type_, _value_, _tbck_ = sys.exc_info()
                        log(ERROR_, "AdminApp.install Exception=" + `_value_`)
                        _excp_ = 1
                # endTry
                temp = _excp_
                if (temp != 0):
                        msg = "Exception installing EAR " + appPath + " to " + nodeName + " " + serverName
                        fail(msg)
                # endIf
        # endIf
        elif (clusterName != ""):
                highlight(MAJOR_, "installEAR: " + action + " cluster=" + clusterName + " appName=" + appName + " appPath=" + appPath + " installOptions=" + `installOptions` + " ...")
                try:
                        _excp_ = 0
                        installed = AdminApp.install(appPath, update + " -verbose -cluster " + clusterName + "               -distributeApp " + installOptions)
                except:
                        _type_, _value_, _tbck_ = sys.exc_info()
                        log(ERROR_, "AdminApp.install Exception=" + `_value_`)
                        _excp_ = 1
                # endTry
                temp = _excp_
                if (temp != 0):
                        msg = "Exception installing EAR " + appPath + " to " + clusterName
                        fail(msg)
                # endIf
        # endIf
        else:
                msg = "ERROR: installEAR: no serverName/nodeName nor clusterName specified"
                fail(msg)
        # endElse
        if (len(installed) > 0):
                log(INFO_, installed)
        # endIf
        appExists = checkIfAppExists(appName)
        if (appExists):
                pass
        else:
                fail("failed to installEAR application=" + appName)
        # endElse
        log(VERBOSE_, "InstallEAR: DONE.")
# endDef

def uninstallEAR (appName):
        global ScriptLocation
        execfile(ScriptLocation + "/Definitions.py")
        log(MAJOR_, "UninstallEAR: " + appName + "...")
        uninstalled = AdminApp.uninstall(appName)
        log(INFO_, uninstalled)
        appExists = checkIfAppExists(appName)
        if (appExists):
                fail("failed to uninstallEAR application=" + appName)
        # endIf
        log(VERBOSE_, "UninstallEAR: DONE.")
# endDef
