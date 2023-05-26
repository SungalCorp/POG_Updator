from PyQt5 import QtCore, QtGui, QtWidgets
from configparser import ConfigParser
from DBUtils import getPOG, getDictionary,getProductUPCs
from Messageboxes import msgButtonClick
from POGUpdatorUI import setupUILayout,retranslateUi
from PyQt5.QtWidgets import QMessageBox,QComboBox
from PyQt5.QtGui import QIcon
from Messageboxes import *
from POGUpdatingDefs import * # deleteShelvesAndFacings,addFacings,addShelves
import tkinter as tk
# import json, requests
import os

configFilePath = r'config.ini'  #ini file path
cfg = ConfigParser()
cfg.read(configFilePath)
apiServer = cfg.get('URLs', 'apiServer')
storeID = cfg.get('storedata','storeID')
productDict = {} 
columnsInPOGtable = 4
gondolaColumn = 0
shelfColumn = 1
facingColumn = 2
upcColumn = 3

storewideFilterString = "filter=storeid="+str(storeID)
changesMadeSinceLastUpdate = False

class NoWheelEventComboBox(QComboBox):
    def wheelEvent(self, event):
        pass


class Ui_MainWindow(object):
    def productSelectionChanged(self):
        self.changesMadeSinceLastUpdate = True
        

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        setupUILayout(self,MainWindow)
        retranslateUi(self,MainWindow)

    def showPOGTable(self):
        try:
            dataSource = getPOG(apiServer,"filter=storeid="+str(storeID))
        except:
            return False

        return self.showTable(dataSource,columnsInPOGtable)


    # show a noneditable table
    def showTable(self,dataSource,numberOfColums):

        if len(dataSource) == 0:
            return False

        backColors = [QtGui.QColor(200,200,200),QtGui.QColor(150,150,150)]
        backColorsForCombo = ["rgb(200,200,200)","rgb(150,150,150)"]

        textColors = [QtGui.QColor(0,0,200),QtGui.QColor(102,0,102)]
        textColorsForCombo = ["rgb(0,0,200)","rgb(102,0,102)"]

        self.tableWidget.setRowCount(len(dataSource))
        self.tableWidget.setColumnCount(numberOfColums)
        # .... dbGet_productUPCs
        row = 0
        i = 0
        j = 0
        previousGondola = ""
        previousShelf =  -1

        for item in dataSource:
            currentGondola = item['gondola']
            currentShelf = item['shelf']
            if previousGondola != currentGondola or previousShelf != currentShelf:
                i+=1
                if previousGondola != currentGondola:
                    j+=1

            # previous Gondola became current Gondola
            previousGondola = currentGondola
            previousShelf = currentShelf

            col = 0
            self.table_header = []    
            for attribute, value in item.items():
 
                if col > columnsInPOGtable - 1:
                    break

                self.table_header.append(attribute) 
                
                if col == upcColumn:
                    # cb = QtWidgets.QComboBox()
                    cb = NoWheelEventComboBox()
                    cb.addItems(productList)
                    cb.currentIndexChanged.connect(self.productSelectionChanged)
                    cb.setStyleSheet("QComboBox"
                                     "{"
                                     "background-color: " + backColorsForCombo[i%2] + ";"
                                     "color: " + textColorsForCombo[j%2] + ";"
                                     "}")
                    try:
                        # saveChangeStatus = self.changesMadeSinceLastUpdate
                        cb.setCurrentText(productDict[str(value)]["upc"]+ " " + productDict[str(value)]["productName"])
                        self.changesMadeSinceLastUpdate = False
                    except:
                        continue

                    self.tableWidget.setCellWidget(row,col,cb) 
                
                else:
                    self.tableWidget.setItem(row,col, QtWidgets.QTableWidgetItem(str(value)))
                    self.tableWidget.item(row,col).setBackground(backColors[i%2])
                    self.tableWidget.item(row,col).setForeground(textColors[j%2])


                col += 1
            row += 1

        self.tableWidget.setHorizontalHeaderLabels(self.table_header)  

        header = self.tableWidget.horizontalHeader()       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)    
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)      
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)  
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.ResizeToContents) 

        # self.tableWidget.horizontalHeader().resizeSections
        self.tableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        return True


    def onPushButtonAddFacing(self):
        # don't do this if there is no selected shelf, meaning that the currently 
        # selected row has a None value for shelf (gondola with no shelves)
        if self.tableWidget.item(self.POGRowSelected,shelfColumn).text().upper() =='NONE':
            showDialog("info","Gondola has no shelves, Add a shelf to the Gondola before adding facings","Problem Adding Shelf")
            return False
        try:
            if self.tableWidget.item(self.POGRowSelected,facingColumn).text().upper() =='NONE':
                self.tableWidget.setItem(self.POGRowSelected,facingColumn,QtWidgets.QTableWidgetItem("1"))
                self.onTableCellClicked(self.POGRowSelected)
                cb = QtWidgets.QComboBox()
                cb.addItems(productList)
                cb.setCurrentText(productList[0])
                self.tableWidget.setCellWidget(self.POGRowSelected,upcColumn,cb) 
                 
                return True

            self.insertFacing(self.POGRowSelected)
            self.reorderItemsFollowing("FACING",self.POGRowSelected,1)
            self.onTableCellClicked(self.POGRowSelected+1)
        except: 
            print("Error Inserting Row, No row selected")
            self.noticeLabel.setText("Error Inserting Row, No row selected")
            self.noticeLabel.setStyleSheet("QLabel {  color : red; }")   
            return False
        
        self.changesMadeSinceLastUpdate = True
        return True
 
    def onPushButtonAddShelf(self):
        # try:
        # no shelfs  on  this gondola, just  modify the row to represent
        # a shelf  by changing shelf value from 'None' to '1'

        if self.shelfSelected.upper() =='NONE':
            self.tableWidget.setItem(self.POGRowSelected,shelfColumn,QtWidgets.QTableWidgetItem("1"))
            self.tableWidget.setItem(self.POGRowSelected,facingColumn,QtWidgets.QTableWidgetItem("None"))
            self.onTableCellClicked(self.POGRowSelected)
            return

        # if we're on the last row of the table, just add the shelf after
        # the last row and continue
        if self.POGRowSelected == self.tableWidget.rowCount()-1:
            self.insertShelf(self.POGRowSelected+1)
            return
        
        newShelfRow = self.findRowToInsertShelf(self.POGRowSelected)
        self.insertShelf(newShelfRow)        
        self.reorderItemsFollowing("SHELF",newShelfRow,1)

        self.onTableCellClicked(newShelfRow)

                
        print("shelf added!")

        # except: 
        #     self.noticeLabel.setText("Error Inserting Row, No row selected")
        #     self.noticeLabel.setStyleSheet("QLabel {  color : red; }")
        self.changesMadeSinceLastUpdate = True       
        return    
 
    def findRowToInsertShelf(self,row):

            for j in range(row+1,self.tableWidget.rowCount()):

                isNewGondola = self.tableWidget.item(j,gondolaColumn).text() != self.gondolaSelected
                isEndOfTable = (j ==self.tableWidget.rowCount())
                isNewShelf = not isNewGondola and self.tableWidget.item(j,shelfColumn).text() != self.shelfSelected
                # if isEndOfTable:
                foundRow = j
                # if hit the different shelf or Gondola we insert a new row below with new shelfID (1 digit bigger than the shelfID we selected) and facingID#1
                if isNewGondola  or isNewShelf or isEndOfTable:
                    if isEndOfTable:
                        foundRow += 1                    
                    break            
            return foundRow

    def reorderItemsFollowing(self,mode,selectedRow,incrementAmount):

        for k in range(selectedRow+1,self.tableWidget.rowCount()):
            
            isNewGondola = self.tableWidget.item(k,gondolaColumn).text() != self.gondolaSelected
            breakingCondition = False
            if mode.upper() == "SHELF":
                breakingCondition = isNewGondola
                reorderedColumn = shelfColumn
                color = QtGui.QColor(200,200,200)
            if mode.upper() == "FACING":
                isNewShelf = self.tableWidget.item(k,shelfColumn).text() != self.shelfSelected
                breakingCondition = isNewGondola or isNewShelf
                reorderedColumn = facingColumn
                color = QtGui.QColor(150,100,200)
    
            if breakingCondition :   # except gondola changed
                break
            self.tableWidget.setItem(k,reorderedColumn,QtWidgets.QTableWidgetItem(str(int(self.tableWidget.item(k,reorderedColumn).text())+incrementAmount)))
            # self.tableWidget.item(k,reorderedColumn).setBackground(color)
        return

    def onPushButtonDeleteFacing(self):
        try:
            wasRowDeleted = self.deleteFacing(self.POGRowSelected)
            # select next row after deleting
            if self.POGRowSelected==0:
                self.POGRowSelected = 1

            if wasRowDeleted:
                self.onTableCellClicked(self.POGRowSelected-1)
            else:
                self.onTableCellClicked(self.POGRowSelected)

        except:
            self.noticeLabel.setText("Error Deleting Facing, No Facing selected")
            self.noticeLabel.setStyleSheet("QLabel {  color : red; }")
            return    
        self.changesMadeSinceLastUpdate = True      

    def onPushButtonDeleteShelf(self):
        try:
            self.deleteShelf(self.gondolaSelected,self.shelfSelected)

        except:
            self.noticeLabel.setText("Error Deleting Shelf, No Shelf selected")
            self.noticeLabel.setStyleSheet("QLabel {  color : red; }")
            return 
        
        self.changesMadeSinceLastUpdate = True  

    def isLastShelfForGondola(self,tableWidget,row):
        lastRowInTable = row == tableWidget.rowCount()-1
        firstRowInTable = row == 0
        differentGondolaBefore = firstRowInTable or tableWidget.item(row,gondolaColumn).text() != tableWidget.item(row-1,gondolaColumn).text()
        differentGondolaAfter = lastRowInTable or tableWidget.item(row,gondolaColumn).text() != tableWidget.item(row+1,gondolaColumn).text()
        return differentGondolaBefore and differentGondolaAfter

    def  deleteShelf(self,selectedGondola,selectedShelf):
        try:
            lastDeletedRow = 0
            while True:
                foundShelf = False

                for j in range(0,self.tableWidget.rowCount()):
                    
                    if self.tableWidget.item(j,shelfColumn).text() == selectedShelf and \
                       self.tableWidget.item(j,gondolaColumn).text() == selectedGondola:
                            if not self.isLastShelfForGondola(self.tableWidget, j) :
                                self.tableWidget.removeRow(j)
                            else:
                                print("will not remove row for last shelf of gondola, just change shelf field value")
                                self.tableWidget.setItem(j,shelfColumn,QtWidgets.QTableWidgetItem('None'))
                                self.tableWidget.setItem(j,facingColumn,QtWidgets.QTableWidgetItem('None'))
                                self.onTableCellClicked(lastDeletedRow)
                                return True

                            lastDeletedRow = j-1
                            foundShelf = True
                            break
                
                if not foundShelf:
                    break
            
            self.reorderItemsFollowing("SHELF",lastDeletedRow,-1)

            if lastDeletedRow < 0:
                lastDeletedRow+=1

            self.onTableCellClicked(lastDeletedRow)
            # self.tableWidget.selectRow(lastDeletedRow)
            print("row: "+str(lastDeletedRow)+" selected")
            print("Shelf deleted!")

        except:
            self.noticeLabel.setText("Error Deleting Row, No row selected")
            self.noticeLabel.setStyleSheet("QLabel {  color : red; }")
            return False

        return True 

    
    def deleteFacing(self,row):
            gondolaSelected = self.tableWidget.item(row,gondolaColumn).text()
            shelfSelected = self.tableWidget.item(row,shelfColumn).text()
            facingSelected = self.tableWidget.item(row,facingColumn).text()
            print("gondolaSelected:",gondolaSelected)
            print("shelfSelected:",shelfSelected)
            print("POGRowSelected:",row)
            isLastRow = row == self.tableWidget.rowCount() - 1

            if (facingSelected =='1' or facingSelected.upper() =='NONE') and \
               (isLastRow or gondolaSelected!=self.tableWidget.item(row+1,gondolaColumn).text() or \
                shelfSelected !=self.tableWidget.item(row+1,shelfColumn).text()): 
                
                self.tableWidget.setItem(row,facingColumn,QtWidgets.QTableWidgetItem('None'))
                return False
           
            self.tableWidget.removeRow(row)

            for j in range(row,self.tableWidget.rowCount()):
                if not (self.tableWidget.item(j,gondolaColumn).text() == gondolaSelected and self.tableWidget.item(j,shelfColumn).text() == shelfSelected):
                    break
                self.tableWidget.setItem(j,facingColumn,QtWidgets.QTableWidgetItem(str(int(self.tableWidget.item(j,facingColumn).text())-1)))
            
            return True

    def insertShelf(self,rowSelected):
        
        self.insertFacing(rowSelected-1)

        newShelfNum = 0
        
        try:
            newShelfNum = int(self.tableWidget.item(rowSelected,shelfColumn).text()) + 1
        except:
            # we're in the except because shelf == None
            newShelfNum = 1
    
        self.tableWidget.setItem(rowSelected,shelfColumn,QtWidgets.QTableWidgetItem(str(newShelfNum)))
        self.tableWidget.setItem(rowSelected,facingColumn,QtWidgets.QTableWidgetItem('1'))


    def insertFacing(self,rowSelected):
        # insert a row after the selected row of the table
            
        print("gondolaSelected:",self.gondolaSelected)
        print("shelfSelected:",self.shelfSelected)
        print("POGRowSelected:",rowSelected)
        rowSelected  += 1
        self.tableWidget.insertRow(rowSelected)

        colCount = self.tableWidget.columnCount()

        for j in range(colCount):
            # if not QtWidgets.QTableWidgetItem(self.tableWidget.item(rowCount-2,j)) is None:
            if j == upcColumn:
                cb = QtWidgets.QComboBox()
                cb.addItems(productList)
                try:
                    cb.setCurrentText(self.tableWidget.cellWidget(rowSelected-1,j).currentText())
                except:
                    cb.setCurrentText('')
                self.tableWidget.setCellWidget(rowSelected,j,cb) 
                
            self.tableWidget.setItem(rowSelected,j,QtWidgets.QTableWidgetItem(self.tableWidget.item(rowSelected-1,j)))
            # self.tableWidget.item(rowSelected,2).setBackground(QtGui.QColor(150,100,200))

            
 
    def onTableCellClicked(self,row):
        print("clicked:r="+str(row))
        self.POGRowSelected = row
        self.gondolaSelected = self.tableWidget.item(row,gondolaColumn).text()

        # row may not have a shelf, facing or upc
        self.shelfSelected = '0'
        self.facingSelected = '0'
        self.upcSelected = "00000 0000"
        try:
            self.shelfSelected = self.tableWidget.item(row,shelfColumn).text()
            self.facingSelected = self.tableWidget.item(row,facingColumn).text()
            self.upcSelected = self.tableWidget.cellWidget(row,upcColumn).currentText()
        except:
            print("") # do nothing

        self.tableWidget.selectRow(row)
        self.noticeLabel.setText("Selected:    Gondola: "+ self.gondolaSelected + "     Shelf: "+self.shelfSelected + "             Facing: " + self.facingSelected + "                    Product: "+ self.upcSelected.split(" ",1)[1])
        self.noticeLabel.setStyleSheet("QLabel {  color : green; }")


    def convertListToDict(self,POGList): 
        # POGList looks like:
        # [{'gondola': 'G-00111', 'shelf': '1', 'facing': '1', 'UPC': '9421021171424'}, {'gondola': 'G-00111', 'shelf': '1', 'facing': '2', 'UPC': '9421021171424'}]
        
        currentGondola = ""
        currentShelf = '0'

        mDict = {}
        for i in range(len(POGList)):
            isNewGondola = POGList[i]["gondola"]!= currentGondola
            if isNewGondola:
                mDict[ POGList[i]["gondola"]] = {}
                mDict[ POGList[i]["gondola"]]["gondolaID"] = POGList[i]["displayfixtureID"]
                currentGondola = POGList[i]["gondola"]

            # we have a new shelf, create a sub dictionary of facings in mDict
            if POGList[i]["shelf"] != currentShelf or isNewGondola:
                mDict[ POGList[i]["gondola"]][ POGList[i]["shelf"]] = {}
                mDict[ POGList[i]["gondola"]][ POGList[i]["shelf"]]["shelfID"] = POGList[i]["shelfID"]
                currentShelf = POGList[i]["shelf"]
            
            # print("POGList[i]['gondola'] = ",POGList[i]["gondola"],'POGList[i]["shelf"]=',POGList[i]["shelf"],'POGList[i]["facing"]=',POGList[i]["facing"])
            # print("mDict=",mDict)
            mDict[POGList[i]["gondola"]][ POGList[i]["shelf"]][POGList[i]["facing"]] =  POGList[i]["UPC"]
        return mDict
    # end of update to KC's


    def generateListFromTable(self):
        updatedList = []
        for row in range(self.tableWidget.rowCount()):
            # fieldValueList = []
            updatedDic = {}
            for col in range(columnsInPOGtable):
                fillVal = ""
                if col == upcColumn:
                    try:
                        fillVal = self.tableWidget.cellWidget(row,col).currentText().split()[0]
                    except:
                        fillVal = "0000"
                else:
                    fillVal = self.tableWidget.item(row,col).text()
                
                updatedDic[self.table_header[col]] = fillVal
            updatedDic["shelfID"] = 0
            updatedDic["displayfixtureID"] = 0

            updatedList.append(updatedDic) 
            
        # print("UPC LIST========\n\n\n\n",updatedList)
        return updatedList

        #
    def refreshPOG(self):
        if showDialog("question","This will restore everything to state of your last update, press OK to refresh.","Notice"):
            self.showPOGTable()
            showDialog("info","POG data refreshed from database","Refresh from Database?")
            self.changesMadeSinceLastUpdate = False

    def updatePOG(self):

        tableDict = self.convertListToDict(self.generateListFromTable())
        currentPOG = getPOG(apiServer,storewideFilterString)
        POGDict = self.convertListToDict(currentPOG)

        # first find any and all deleted shelves and facings and delete them
        deleteShelvesAndFacings(self,apiServer,storeID,tableDict,currentPOG)

        # add shelves and facings that are currently not in the planogram
        mList = self.generateListFromTable()
        addShelves(self,apiServer,storeID,POGDict,mList)
    
        tableDict = self.convertListToDict(mList)
        currentPOG = getPOG(apiServer,storewideFilterString)
        POGDict = self.convertListToDict(currentPOG)

        addFacings(self, apiServer,storeID,POGDict,mList)

        # changeUPCs()
        
        tableDict = self.convertListToDict(self.generateListFromTable())
        currentPOG = getPOG(apiServer,storewideFilterString)
        POGDict = self.convertListToDict(currentPOG)

        updateUPCS(self,apiServer,storeID,POGDict,self.generateListFromTable())
        
        tableDict = self.convertListToDict(self.generateListFromTable())
        currentPOG = getPOG(apiServer,storewideFilterString)
        POGDict = self.convertListToDict(currentPOG)
        self.showPOGTable()
        showDialog("info","POG updated","Notice")
        # showModal()
        self.changesMadeSinceLastUpdate = False
        return

    def exitApp(self):
        if self.changesMadeSinceLastUpdate:
            if showDialog("question","You have made changes that will be lost..Continue to exit APP?","Exit APP?"):
                QtWidgets.QApplication.quit()
        else:
            QtWidgets.QApplication.quit()
                
        
if __name__ == "__main__":
    
    import sys
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyle('Windows')
    app.setStyle('macintosh')
    path = os.path.join(os.path.dirname(sys.modules[__name__].__file__), 'logo.png')
    app.setWindowIcon(QIcon(path))
   
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    
    productDict = getDictionary(apiServer,"products","upc")
    if productDict == {}:
        showDialog("info","There is a problem connecting to the Database, please notify support personel","CONNECTION ERROR")
        sys.exit()
    else:
        MainWindow.show()
        productList = getProductUPCs(apiServer)
        ui.showPOGTable()
        ui.onTableCellClicked(0)
        changesMadeSinceLastUpdate = False
    sys.exit(app.exec_())