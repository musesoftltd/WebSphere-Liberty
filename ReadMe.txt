########################################################
# For WebLogic Scripting
########################################################

This part of the scripting environment will target WebLogic.

We cannot ship Oracle Binaries or Samples. We have provided a WebLogic API
as a base to begin scripting. This software has been designed for the WebLogic
Server Tools to be downloaded and installed from the Oracle Download Site.

Download and install Oracle WebLogic Server 12.x
Use Oracle Download Site to obtain the WebLogic Server Tools.
In Eclipse, Help | Install New Software...
Add a new download site...
http://download.oracle.com/otn_software/oepe/12.2.1.7/oxygen/repository/
Name it WebLogicWLST
Select the download site.
Install Tools | Oracle WebLogic Scripting Tools  
NOTE: You will be notified of alternative solutions, because PyDev is already installed. 
      You should choose to update your current configuration to be compatible. 
      This will then indicate the current PyDev installation will be removed.
      Ignore this warning and continue.                                           
                            
In the J2EE view within Eclipse:
    Create a new 12.x server definition
    
With the WebLogic project, right click it and choose Properties.
Choose WebLogic 12.x as the targeted runtime.
Right click the existing WebLogic Project and apply the WLST Scripting Facet,
via the Project Facets option. 
Right click the Project and choose PyDev Interpreter / Grammar.
Ensure the new Project has WebLogic as the interpreter.

Once this is installed you should be able to script successfully 
with Jython against a 12.x Server.

Right click the .PY file you wish to execute and use RunAs WLSTRun.

You can click the server view, at the bottom of the jee perspective and
add server. Then choose Oracle and WebLogic related items.
With a WebLogic server installed, you can then script against it locally.
########################################################
