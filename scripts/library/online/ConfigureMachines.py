
import os

from wlst.WlstWrapper import cd, create


# Function to create a Machine and its NodeManager. Return Machine as result
def configureMachine (machineName, listenAddress, listenPort):
	print 'creating machine ' + machineName
	cmo = cd('/')
	machine = create(machineName, 'UnixMachine')
	cmo = cd('Machines/' + machineName)
	create(machineName, 'NodeManager')
	cmo = cd('NodeManager/' + machineName)
	set('ListenAddress', listenAddress)
	set('ListenPort', int(listenPort))
	set('NMType', 'Plain')
	return machine

# Assign server to machine
def assignServer(serverName, machineName) :
	print 'assigning ' + serverName + ' to machineName'
	machine = cmo = cd('/Machines/' + machineName)
	cmo = cd('/Servers/' + serverName)
	set('Machine', machine)


#=======================================================================================
# Create machine(s) and assign WebLogic servers to machines.
#=======================================================================================
def configureMachines(props, domain):
    # 'Hardwire' name of admin machine: ultimately should be a domain property
    print 'configuring admin server'
    adminMachineName = 'AdminMachine'
    print "Configuring admin server with machine=" + str(adminMachineName) + ", listen address=" + str(props.get('listenAddress')) + ", listen port=" + str(props.get('wls.NODEMGR_PORT'))
    adminMachine = configureMachine(adminMachineName, props.get('listenAddress'), props.get('wls.NODEMGR_PORT'))
    assignServer('AdminServer', adminMachineName)

    print 'configuring managed servers'

    i = 1
    prefix = "managed.server."
    ms_name = props.get(prefix + str(i) + ".name")
    while (ms_name) :
        ms_host = props.get(prefix + str(i) + '.listenAddress')
        ms_port = props.get(prefix + str(i) + '.listenPort')
        print 'configuring server ' + ms_name
        if ms_host is None:
            print 'Host name for managed server ' + ms_name + ' missing from property file'
            return False
        if ms_port is None:
            print 'Port number for managed server ' + ms_name + ' missing from property file'
            return False

        print "Configuring " + ms_name + " with machine=" + str(adminMachineName) + ", listen address=" + str(ms_host) + ", listen port=" + str(ms_port)
        cmo = cd('/Servers/' + ms_name)
        set('ListenAddress', ms_host)
        set('ListenPort', int(ms_port))
        # For now, assign all servers to admin machine
        set('Machine', adminMachine)
        i = i + 1
        ms_name = props.get(prefix + str(i) + '.name')

    print 'configured ' + str(i - 1) + ' managed servers'
    return True


