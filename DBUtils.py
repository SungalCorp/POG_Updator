
# example of how this def would be called

#updateDatabaseTable(apiServer,"batches",['factoryID','deviceTypeID','mfDate'],
#                                         [1,210,'10/12/2022'])

import json,requests
from Messageboxes import showDialog
timeoutForGetRequests = 3
# POG_FILTER = "filter=storeid=4"


# def updateDatabaseTable(apiServer,tableName,fields,fieldVals,filter):

# 	updateBatchURL = apiServer + "dbUpdate?tablename=" + tableName + '&fields={' 
# 	for i in range(len(fields)):
# 		updateBatchURL += ('"' + fields[i] + '":"' + str(fieldVals[i]) + '",')

# 	updateBatchURL = updateBatchURL[:len(updateBatchURL)-1] + "}&filter="	+ filter

# 	print(updateBatchURL)

def getProductIDByUPC(apiServer,upc):
	filter = "filter=upc="+str(upc)
	rTable = getTable(apiServer,"products",filter)
	if  len(rTable) > 0:
		return rTable[0]["productID"]

	return -1


def getGondolaIDByGondolaName(apiServer,storeID,gondolaName):
	filter = "filter=storeID="+str(storeID)+ " AND displayfixtureIDForUser='" + gondolaName.strip() + "'"
	rTable = getTable(apiServer,"displayfixtures",filter)
	if  len(rTable) > 0:
		return rTable[0]["displayfixtureID"]

	return -1

def getShelfIDByGondolaIDAndLevel(apiServer,gondolaID,level):
	filter = "filter=displayfixtureID="+str(gondolaID)+ " AND level=" + str(level)
	rTable = getTable(apiServer,"shelfs",filter)
	if  len(rTable) > 0:
		return rTable[0]["shelfID"]
		
	return -1

def getFacingIDByShelfIDandRelativeShelfAddress(apiServer,shelfID,shelfRelativeAddress):
	filter = "filter=shelfID="+str(shelfID)+ " AND shelfRelativeAddress=" + str(shelfRelativeAddress)
	rTable = getTable(apiServer,"facings",filter)
	if  len(rTable) > 0:
		return rTable[0]["facingID"]
		
	return -1

def deleteRecord(apiServer,tableName,filter):
	url = apiServer + "dbExecuteSQL?sqlstatement=delete from " + tableName 
	if len(filter) > 0:
		url += (" where " + filter)
	resultTable = json.loads(requests.get(url).text)
	return resultTable
	

def deleteFacingRecord(apiServer,filter):
	return deleteRecord(apiServer,"facings",filter)

def deleteShelfRecord(apiServer,filter):
	return deleteRecord(apiServer,"shelfs",filter)


def addRecord(apiServer,tableName,fields,fieldVals):
    
	url = apiServer + "dbInsert?tablename=" + tableName + "&fields={"
	URLAddon=""
	for i in range(len(fields)):
		URLAddon += ('"' + fields[i] + '":"' + str(fieldVals[i]) + '",')

	URLAddon = URLAddon[:len(URLAddon)-1]
	url += (URLAddon + "}")
	return json.loads(requests.get(url).text)

def addShelfRecord(apiServer,fields,fieldVals):
	addRecord(apiServer,"shelfs",fields,fieldVals)

def addFacingRecord(apiServer,fields,fieldVals):
	addRecord(apiServer,"facings",fields,fieldVals)

def addfacingmerchandiselinksRecord(apiServer,fields,fieldVals):
	addRecord(apiServer,"facingmerchandiselinks",fields,fieldVals)	

def getPOG(apiServer,filter):
	return getTable(apiServer,"planogram",filter)

def getProductUPCs(apiServer):
	resultTable =  getTable(apiServer,"productUPCs","")
	return [productItem["UPC"] + " " + productItem["productName"]for productItem in resultTable]
	
def getTable(apiServer,tableName,filter):
	#?filter=deviceTypeID<3000&orderby=batchID'
	resultTable = []
	url = apiServer + 'dbGet_' + tableName 
	if len(filter) > 0:
		url += '?' + filter
	try:
		resultTable = json.loads(requests.get(url, timeout= timeoutForGetRequests).text)
	except:
		# showDialog("info","Database Unavailble, check your internet connection or contact a technician if the situation persists","Error Connecting To Database")
		return  []
	
	return [p for p in resultTable ]

def getDictionary(apiServer,tableName,keyField):
	rVal = {}
	resultDataSet = getTable(apiServer,tableName,"")
	for record in resultDataSet:
		rVal[str(record[keyField])] = record           
	return rVal



