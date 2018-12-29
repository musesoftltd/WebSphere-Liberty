from javax.management import ObjectName
from library.restConnector import JMXRESTConnector

connector = JMXRESTConnector()
connector.trustStore = "wsTrustStore.jks"
connector.trustStorePassword = "admin123#"

connector.connectBasic("localhost", 9443, "admin", "adminpwd")
mBeanServerConnection = connector.getMBeanServerConnection()
mbeans = mBeanServerConnection.queryNames(ObjectName("*:*"), None).toArray()

type(mbeans)

mbeans[0]

type(mbeans[0])

for i in mbeans: print i