#-*- coding:utf-8 -*-

__author__ = 'lionel'

from PyQt4 import QtGui



class MainUI(QtGui.QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()

        self.initUI()

    def initUI(self):
        #Menu bar
        self.menu_bar = self.menuBar()

        #Left side
        self.uiConnList = QtGui.QListView()
        self.uiAppendButton = QtGui.QPushButton("+")
        self.uiDeleteButton = QtGui.QPushButton("-")
        self.uiEditButton = QtGui.QPushButton("Edit")
        hBox1 = QtGui.QHBoxLayout()
        hBox1.addStretch(1)
        hBox1.addWidget(self.uiEditButton)
        hBox1.addWidget(self.uiAppendButton)
        hBox1.addWidget(self.uiDeleteButton)
        vBox1 = QtGui.QVBoxLayout()
        vBox1.addWidget(self.uiConnList)
        vBox1.addLayout(hBox1)
        groupBox1 =QtGui.QGroupBox("Connections")
        groupBox1.setLayout(vBox1)

        #Right side
        self.uiNameEdit = QtGui.QLineEdit()
        self.uiHostEdit = QtGui.QLineEdit()
        self.uiPortEdit = QtGui.QLineEdit()
        self.uiDatabaseEdit = QtGui.QLineEdit()
        self.uiUserEdit = QtGui.QLineEdit()
        self.uiPasswordEdit = QtGui.QLineEdit()
        self.uiPasswordEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.uiTestButton = QtGui.QPushButton('Test')
        form = QtGui.QFormLayout()
        form.addRow("Name", self.uiNameEdit)
        form.addRow("Host", self.uiHostEdit)
        form.addRow("Port", self.uiPortEdit)
        form.addRow("Database", self.uiDatabaseEdit)
        form.addRow("User", self.uiUserEdit)
        form.addRow("Password", self.uiPasswordEdit)
        form.addRow("", self.uiTestButton)
        self.uiSaveButton = QtGui.QPushButton('Save')
        self.uiCancelButton = QtGui.QPushButton('Cancel')
        self.uiOpenButton = QtGui.QPushButton('Open')
        hBox2 = QtGui.QHBoxLayout()
        hBox2.addStretch(1)
        hBox2.addWidget(self.uiSaveButton)
        hBox2.addWidget(self.uiCancelButton)
        hBox2.addWidget(self.uiOpenButton)
        vBox2 = QtGui.QVBoxLayout()
        vBox2.addLayout(form)
        vBox2.addLayout(hBox2)
        groupBox2 = QtGui.QGroupBox("Parameters")
        groupBox2.setLayout(vBox2)

        hBox3 = QtGui.QHBoxLayout()
        # hBox3.addLayout(vBox1)
        # hBox3.addLayout(vBox2)
        hBox3.addWidget(groupBox1)
        hBox3.addWidget(groupBox2)

        centralWidget = QtGui.QWidget()
        centralWidget.setLayout(hBox3)
        self.setCentralWidget(centralWidget)
        # QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.setGeometry(300, 300, 600, 400)

