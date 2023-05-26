
from PyQt5.QtWidgets import QMessageBox
from Messageboxes import *

def showBanner():
   print('showing banner')

def showDialog(mode,msgText,msgTitle):
   
   msgBox = QMessageBox()
   
   
   if mode.upper() == "INFO":
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setStandardButtons(QMessageBox.Ok)

   if mode.upper() == "QUESTION":
        msgBox.setIcon(QMessageBox.Question)  
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

   msgBox.setText(msgText)
   msgBox.setWindowTitle(msgTitle)
   msgBox.buttonClicked.connect(msgButtonClick)

   returnValue = msgBox.exec()
   
   if returnValue == QMessageBox.Ok:
      print('OK clicked')
      
   else:
      print("Canceled!")

   return returnValue == QMessageBox.Ok
   
def msgButtonClick(i):
   
   
   print("Button clicked is:",i.text())


