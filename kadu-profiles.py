#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys, os
from PyQt4 import QtGui, QtCore
from subprocess import call, Popen

configurationFile = '/home/sadam/.kadu-profiles'

class KaduProfiles(QtGui.QWidget):
    
    def __init__(self):
        super(KaduProfiles, self).__init__()
        self.profilesList = self.parseFile()
        self.initUI()

    def parseFile(self):
        profilesList = list()
        
        if os.path.exists(configurationFile):
            f = open(configurationFile, 'r')
        else:
            f = open(configurationFile, 'w+')

        for line in f:
            line = line.strip('\r\n')
            splited = line.split(':')
            profilesList.append(splited)
        
        
        f.close()
        return profilesList

    def initUI(self):
        self.setWindowTitle('Kadu - select profile')

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        self.setList()
        vbox.addWidget(self.qProfilesList)
        vbox.addLayout(self.setProfilesButtons())
        vbox.addLayout(self.setMainButtons())
        self.setLayout(vbox)

        self.center()

        self.show()

    def center(self):
        self.resize(500,250)
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
 
    def setProfilesButtons(self): 
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)

        buttonRemove = QtGui.QPushButton('Remove profile', self)
        buttonRemove.setToolTip("Remove selected profile")
        buttonRemove.clicked.connect(self.removeProfile)
        hbox.addWidget(buttonRemove)
       
        buttonEdit = QtGui.QPushButton('Edit profile', self)
        buttonEdit.setToolTip("Edit selected profile")
        buttonEdit.clicked.connect(self.editProfile)
        hbox.addWidget(buttonEdit)
       
        buttonAdd = QtGui.QPushButton('Add profile', self)
        buttonAdd.setToolTip("Add new profile")
        buttonAdd.clicked.connect(self.addNewProfile)
        hbox.addWidget(buttonAdd)

        return hbox


    def setList(self):
        self.qProfilesList = QtGui.QListWidget()
 
        for elem in self.profilesList:
            item = QtGui.QListWidgetItem(elem[0], self.qProfilesList)
            item.setToolTip(elem[1])
            self.qProfilesList.addItem(item)

    def setMainButtons(self):
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)

        buttonRun = QtGui.QPushButton('Run kadu', self)
        buttonExit = QtGui.QPushButton('Exit' , self)

        buttonExit.setToolTip('Exit')
        buttonExit.resize(buttonExit.sizeHint())
        buttonExit.clicked.connect(QtCore.QCoreApplication.instance().quit)

        buttonRun.setToolTip('Run kadu with selected profile')
        buttonRun.resize(buttonRun.sizeHint())
        buttonRun.clicked.connect(self.runKadu)
     
        hbox.addWidget(buttonExit)
        hbox.addWidget(buttonRun)
        
        return hbox
    
    def removeProfile(self):
        selectedProfile = self.qProfilesList.currentRow()
        
        if selectedProfile > -1:
            reply = QtGui.QMessageBox.question(self, 'Are you sure?', "Are you sure, that you want to remove selected profile (directory with configuration stays)?", QtGui.QMessageBox.Yes |QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        
            if reply == QtGui.QMessageBox.Yes:
                self.qProfilesList.takeItem(self.qProfilesList.currentRow())
                del self.profilesList[selectedProfile]
                self.printToFile()
                
    def createDialog(self, title="Create new profile"):
        dialog = QtGui.QDialog(self)
        dialog.setWindowTitle(title)
        dialog.resize(400,50)
        
        vbox = QtGui.QVBoxLayout()
               
        hbox1 = QtGui.QHBoxLayout()
        hbox2 = QtGui.QHBoxLayout()
        hbox3 = QtGui.QHBoxLayout()
        hbox3.addStretch(1)

        labelName = QtGui.QLabel("Name:      ", dialog)
        inputName = QtGui.QLineEdit(dialog)
        hbox1.addWidget(labelName)
        hbox1.addWidget(inputName)
        
        labelDir = QtGui.QLabel("Directory: ", dialog)
        inputDir = QtGui.QLineEdit()

        def chooseFile():
            fileDialog = QtGui.QFileDialog(dialog)
            fileDialog.show()
            
            def fSelected(f):
                inputDir.setText(f)

            fileDialog.fileSelected.connect(fSelected)

        chooseButton = QtGui.QPushButton("Choose")
        chooseButton.clicked.connect(chooseFile)

        hbox2.addWidget(labelDir)
        hbox2.addWidget(inputDir)
        hbox2.addWidget(chooseButton)

        okButton = QtGui.QPushButton("OK", dialog)
        okButton.setToolTip("Save")
        
        cancelButton = QtGui.QPushButton("Cancel", dialog)
        cancelButton.setToolTip("Cancel")

        def closeDialog():
            dialog.close()
        
        cancelButton.clicked.connect(closeDialog)
        hbox3.addWidget(cancelButton)
        hbox3.addWidget(okButton)

          
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        dialog.setLayout(vbox)
        dialog.show()

        return (dialog, okButton, inputName, inputDir)
        
    def addNewProfile(self):
        _tuple = self.createDialog()
        dialog = _tuple[0]
        button = _tuple[1]
        inputName = _tuple[2]
        inputDir = _tuple[3]

        def add():
            name = inputName.text()
            directory = inputDir.text()
        
            if self.validate(name, directory):
                self.profilesList.append((name, directory))
                item = QtGui.QListWidgetItem(name, self.qProfilesList)
                item.setToolTip(directory)
                self.qProfilesList.addItem(item)
                self.printToFile()
                dialog.close()
            else:
                msgBox = QtGui.QMessageBox()
                msgBox.setText("Wrong profile name or directory")
                msgBox.exec_()

        button.clicked.connect(add)

    def validate(self, name, directory):
        if str(name).strip(' ') == '' or str(directory).strip(' ') == '':
            return False
        for tmp in self.profilesList:
            if tmp[0] == name or tmp[1] == directory: 
                return False

        return True

    def editProfile(self):
        selectedProfile = self.qProfilesList.currentRow()
        if selectedProfile > -1:
            _tuple = self.createDialog("Edit profile")
            dialog = _tuple[0]
            button = _tuple[1]
            inputName = _tuple[2]
            inputDir = _tuple[3]

            inputName.setText(self.profilesList[selectedProfile][0])
            inputDir.setText(self.profilesList[selectedProfile][1])

            def saveEdit():
                if self.validateForEdit(selectedProfile, inputName.text(), inputDir.text()):
                    self.profilesList[selectedProfile] = (inputName.text(), inputDir.text())
                    item = self.qProfilesList.item(selectedProfile)
                    item.setText(inputName.text())
                    item.setToolTip(inputDir.text())
                    self.printToFile()
                    dialog.close()
                else: 
                    msgBox = QtGui.QMessageBox()
                    msgBox.setText("Wrong profile name or directory")
                    msgBox.exec_()

            button.clicked.connect(saveEdit)

    def validateForEdit(self, selectedProfile, name, directory):
        if str(name).strip(' ') == '' or str(directory).strip(' ') == '': return False
        
        i = 0
        for profile in self.profilesList:
            if i != selectedProfile and (profile[0] == name or profile[1] == directory):
                return False
            i += 1

        return True
   
    def printToFile(self):
        s = ''
        for profile in self.profilesList:
            s += profile[0] + ':' + profile[1] + '\n'

        f = open(configurationFile, 'w+')
        f.write(s)
        f.close()


    def runKadu(self):
        selectedProfile = self.qProfilesList.currentRow()
        tmp = self.profilesList [selectedProfile]
        directory = tmp[1]
        directory = str(directory).strip(' ')
    
        Popen(["kadu", '--config-dir', directory])
        sys.exit()

        

def main():
    app = QtGui.QApplication(sys.argv)

    ex = KaduProfiles()
    sys.exit(app.exec_())


if __name__=='__main__':
    main()
