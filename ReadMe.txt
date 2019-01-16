########################################################
# For WLP Scripting
########################################################
Use the example listFeatures script as a base.

Right-click it and Run, once you have a valid server to
connect to.
########################################################

After defining/installing the Server Ensure you add:
    Basic User Registry
    Administrator
View the file libertyServerConfig.PNG to see a typical configuration 
for the Liberty Server 
    
You must add the server certificate chain to the wsTrustStore.jks trust store 
  (password admin123#) 
  Download KeyExplorer to achieve this:
        https://sourceforge.net/projects/keystore-explorer/

########################################################            
