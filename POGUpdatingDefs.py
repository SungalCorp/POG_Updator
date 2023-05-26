# this gets updated after KC's changes
import datetime
from DBUtils import *

def addShelves(self,apiServer,storeID,POGDict,tableList):
    # adds shelves to the database. If shelf exists in the tableList but not in the 
    # POG from the database, it is added to the database in this def
    
    print(" in add Shelves")
    print("POGDict =",POGDict)
    addedShelfs = {}
    previousLevel = -1
    currentLevel = 0
    previousGondolaID = -1
    currentGondolaID = 0
    
    for i in range(len(tableList)):                         
        try:
            # print("POGDict[tableList[i]['gondola']]=", POGDict[tableList[i]['gondola']])
            if tableList[i]['shelf'].upper() != 'NONE':
                tryit = POGDict[tableList[i]['gondola']][int(tableList[i]['shelf'])]
        except:
            # here is where we add all added shelves
            # currentGondolaID = getGondolaIDByGondolaName(apiServer,storeID,tableList[i]['gondola'])
            currentGondolaID = POGDict[tableList[i]['gondola']]["gondolaID"]
            currentLevel = tableList[i]['shelf']
            # if we added a shelf record we don't want to add another one if the shelf
            # has already been added            
            if currentGondolaID != previousGondolaID or currentLevel != previousLevel:
                previousGondolaID = currentGondolaID
                previousLevel = currentLevel
                addShelfRecord(apiServer,["displayfixtureID","level"],[currentGondolaID,currentLevel])
                print("Shelves added @ : Gondola: ",tableList[i]['gondola']," GondolaID = ", currentGondolaID)



def addFacings(self,apiServer,storeID,POGDict,tableList):
    # adds facings to the database. If facing exists in the tableList but not in the 
    # POG from the database, it is added to the database in this def

    print("in add Facings")

    addedFacings = {}
    shelfID = 0
    gondolaID = 0
    productDict = getDictionary(apiServer,"products","upc")
    for i in range(len(tableList)):
        
        try:
            if tableList[i]['facing'].upper() != 'NONE':
                tryit = POGDict[tableList[i]['gondola']][int(tableList[i]['shelf'])][int(tableList[i]['facing'])]
        except:
            # here is where we add all added facings
            print("facing added @ : Gondola: ",tableList[i]['gondola']," shelf:",tableList[i]['shelf']," facing:",tableList[i]['facing'])
            # gondolaID = getGondolaIDByGondolaName(apiServer,storeID,tableList[i]['gondola'])
            gondolaID = POGDict[tableList[i]['gondola']]["gondolaID"]
            # shelfID =   getShelfIDByGondolaIDAndLevel(apiServer,gondolaID,tableList[i]['shelf'])
            shelfID =   POGDict[tableList[i]['gondola']][int(tableList[i]['shelf'])]["shelfID"]
            upc = str(tableList[i]['UPC'])
            # facingID  = getFacingIDByShelfIDandRelativeShelfAddress(apiServer,shelfID,tableList[i]['facing'])
            # productID = getProductIDByUPC(apiServer,upc)
            productID = productDict[upc]["productID"]

            fromDate  = str(datetime.datetime.now())

            print("fromDate = ", fromDate)
            print('upc = ' ,upc)
            print("addFacingRecord(",apiServer,',["shelfID","shelfRelativeAddress"],[',shelfID,",",str(tableList[i]['facing']),"])]",")")

            addFacingRecord(apiServer,["shelfID","shelfRelativeAddress"],[shelfID,str(tableList[i]['facing'])])
            facingID  = getFacingIDByShelfIDandRelativeShelfAddress(apiServer,shelfID,tableList[i]['facing'])

            addfacingmerchandiselinksRecord(apiServer,["facingID","productID", "fromDate"],[facingID,productID,fromDate])

# INSERT INTO `lpogdbtest`.`facingmerchandiselinks` (`facingID`, `productID`, `fromDate`) VALUES ('12', '14', '2022-11-10 22:00:00');
def deleteShelvesAndFacings(self,apiServer,storeID,tableDict,currentPOG):

    print("in deleteShelvesAndFacings()")
    deletedShelfs = {}

    shelfID = 0
    gondolaID = 0

    for i in range(len(currentPOG)):
        try:
            # 
            if currentPOG[i]['shelf'] != None and currentPOG[i]['facing'] != None:
                tryit = tableDict[currentPOG[i]['gondola']][str(currentPOG[i]['shelf'])][str(currentPOG[i]['facing'])]
        except:
            # here is wwhere we delete all deleted facings
            print("facing deleted @ : Gondola: ",currentPOG[i]['gondola']," shelf:",currentPOG[i]['shelf']," facing:",currentPOG[i]['facing'])

            # get gondola ID which will be displayfixture where storeID = storeID and displayfixtureIDForUser = currentPOG[i]['gondola']
            # get shelf ID which will be shelf  where displayfixtureID = gondolaID and level = currentPOG[i]['shelf']
            gondolaID = getGondolaIDByGondolaName(apiServer,storeID,currentPOG[i]['gondola'])
            shelfID =   getShelfIDByGondolaIDAndLevel(apiServer,gondolaID,currentPOG[i]['shelf'])
            filter = 'shelfID=' + str(shelfID) + ' AND shelfRelativeAddress=' + str(currentPOG[i]['facing'])
            deleteFacingRecord(apiServer,filter)

        # now do for shelfs what we did for facings
        newGondola = currentPOG[i]['gondola']
        newShelf  = ""
        try:
            if currentPOG[i]['shelf'] != None:
                newShelf = str(currentPOG[i]['shelf'])
                tryit = tableDict[newGondola][newShelf]
        except:
            # here is where we delete all deleted shelfs
            try:
                tryit = deletedShelfs[newGondola+"$"+newShelf]
            except:
                print("shelf deleted @ : Gondola: ",newGondola," shelf:",newShelf)
                # we need displayFixtureID here to get filter
                gondolaID = getGondolaIDByGondolaName(apiServer,storeID,currentPOG[i]['gondola'])
                shelfID =   getShelfIDByGondolaIDAndLevel(apiServer,gondolaID,currentPOG[i]['shelf'])
                filter = 'shelfID=' + str(shelfID) 
                deleteShelfRecord(apiServer,filter)

                deletedShelfs[newGondola+"$"+newShelf] = 1

def updateUPCS(self,apiServer,storeID,POGDict,tableList):
    for i in range(len(tableList)): 
            if tableList[i]['facing'].upper() =='NONE' or tableList[i]['shelf'].upper() == 'NONE':
                continue

            POGUPC = POGDict[tableList[i]['gondola']][int(tableList[i]['shelf'])][int(tableList[i]['facing'])]
            tableUPC = tableList[i]['UPC']
            if POGUPC != tableUPC:
                # add record to facingmerchandiselinks table
                productID = getProductIDByUPC(apiServer,tableUPC)
                fromDate  = str(datetime.datetime.now())
                gondolaID = getGondolaIDByGondolaName(apiServer,storeID,tableList[i]['gondola'])
                shelfID =   getShelfIDByGondolaIDAndLevel(apiServer,gondolaID,tableList[i]['shelf'])
                facingID  = getFacingIDByShelfIDandRelativeShelfAddress(apiServer,shelfID,tableList[i]['facing'])
                addfacingmerchandiselinksRecord(apiServer,["facingID","productID", "fromDate"],[facingID,productID,fromDate])

                