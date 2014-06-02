#-*- coding:utf-8 -*-

__author__ = 'lionel'

from PyQt4 import QtGui
from ui.widgets.qscint import QScint


class SaveBookMarksUI(QtGui.QDialog):
    """The bookmarks query dialog UI"""

    def __init__(self, *args, **kwargs):
        super(SaveBookMarksUI, self).__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        #Section part
        self.uiSectionOldRadionBtn = QtGui.QRadioButton("Existing")
        self.uiSectionOldCombo = QtGui.QComboBox()
        self.uiSectionNewRadionBtn = QtGui.QRadioButton("New")
        self.uiSectionNewText = QtGui.QLineEdit()
        gridBox1 = QtGui.QGridLayout()
        gridBox1.addWidget(self.uiSectionOldRadionBtn, 0, 0)
        gridBox1.addWidget(self.uiSectionOldCombo, 0, 1)
        gridBox1.addWidget(self.uiSectionNewRadionBtn, 1, 0)
        gridBox1.addWidget(self.uiSectionNewText, 1, 1)
        groupBox1 = QtGui.QGroupBox("Section")
        groupBox1.setLayout(gridBox1)

        #Name part
        self.uiNameOldRadioBtn = QtGui.QRadioButton("Existing")
        self.uiNameOldCombo = QtGui.QComboBox()
        self.uiNameNewRadioBtn = QtGui.QRadioButton("New")
        self.uiNameNewText = QtGui.QLineEdit()
        gridBox2 = QtGui.QGridLayout()
        gridBox2.addWidget(self.uiNameOldRadioBtn, 0, 0)
        gridBox2.addWidget(self.uiNameOldCombo, 0, 1)
        gridBox2.addWidget(self.uiNameNewRadioBtn, 1, 0)
        gridBox2.addWidget(self.uiNameNewText, 1, 1)
        groupBox2 = QtGui.QGroupBox("Name")
        groupBox2.setLayout(gridBox2)

        #Description
        self.uiDescriptionText = QtGui.QTextEdit()
        hBox1 = QtGui.QHBoxLayout()
        hBox1.addWidget(self.uiDescriptionText)
        groupBox3 = QtGui.QGroupBox("Description")
        groupBox3.setLayout(hBox1)

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)

        #Final step
        vBox1 = QtGui.QVBoxLayout()
        vBox1.addWidget(groupBox1)
        vBox1.addWidget(groupBox2)
        vBox1.addWidget(groupBox3)
        vBox1.addStretch(1)
        vBox1.addWidget(buttonBox)

        self.setLayout(vBox1)


class EditBookMarksUI(QtGui.QDialog):
    """The bookmarks query dialog UI"""

    def __init__(self, *args, **kwargs):
        super(EditBookMarksUI, self).__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        #The section part
        self.uiSectionList = QtGui.QListView()
        self.uiSectionAppendButton = QtGui.QPushButton("+")
        self.uiSectionDeleteButton = QtGui.QPushButton("-")
        hBox1 = QtGui.QHBoxLayout()
        hBox1.addStretch(1)
        hBox1.addWidget(self.uiSectionAppendButton)
        hBox1.addWidget(self.uiSectionDeleteButton)
        vBox1 = QtGui.QVBoxLayout()
        vBox1.addWidget(self.uiSectionList)
        vBox1.addLayout(hBox1)
        groupBox1 = QtGui.QGroupBox("Sections")
        groupBox1.setLayout(vBox1)

        #The name part
        self.uiNameList = QtGui.QListView()
        self.uiNameAppendButton = QtGui.QPushButton("+")
        self.uiNameDeleteButton = QtGui.QPushButton("-")
        hBox2 = QtGui.QHBoxLayout()
        hBox2.addStretch(1)
        hBox2.addWidget(self.uiNameAppendButton)
        hBox2.addWidget(self.uiNameDeleteButton)
        vBox2 = QtGui.QVBoxLayout()
        vBox2.addWidget(self.uiNameList)
        vBox2.addLayout(hBox2)
        groupBox2 = QtGui.QGroupBox("Names")
        groupBox2.setLayout(vBox2)

        #The query part
        self.uiDescriptionText = QtGui.QLineEdit()
        self.uiQueryEditor = QScint()
        vBox3 = QtGui.QVBoxLayout()
        vBox3.addWidget(self.uiDescriptionText)
        vBox3.addWidget(self.uiQueryEditor)
        groupBox3 = QtGui.QGroupBox("Query")
        groupBox3.setLayout(vBox3)

        #This is the end...
        hBox3 = QtGui.QHBoxLayout()
        hBox3.addWidget(groupBox1)
        hBox3.addWidget(groupBox2)
        hBox3.addWidget(groupBox3)
        self.setLayout(hBox3)
