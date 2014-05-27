#-*- coding:utf-8 -*-

__author__ = 'lionel'

from PyQt4 import QtGui
from ui.widgets.qscint import QScint


class BookMarksUI(QtGui.QDialog):
    """The bookmarks query dialog UI"""
    def __init__(self, *args, **kwargs):
        super(BookMarksUI, self).__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        #The section part
        self.uiSectionList = QtGui.QListView()
        self.uiSectionAppendButton = QtGui.QPushButton("+")
        self.uiSectionDeleteButton = QtGui.QPushButton("-")
        hBox1 = QtGui.QHBoxLayout()
        hBox1.addStretch(1)
        hBox1.addWidget(self.uiSectionEditButton)
        hBox1.addWidget(self.uiSectionAppendButton)
        hBox1.addWidget(self.uiSectionDeleteButton)
        vBox1 = QtGui.QVBoxLayout()
        vBox1.addWidget(self.uiSectionList)
        vBox1.addLayout(hBox1)
        groupBox1 =QtGui.QGroupBox("Sections")
        groupBox1.setLayout(vBox1)

        #The name part
        self.uiNameList = QtGui.QListView()
        self.uiNameAppendButton = QtGui.QPushButton("+")
        self.uiNameDeleteButton = QtGui.QPushButton("-")
        hBox2 = QtGui.QHBoxLayout()
        hBox2.addStretch(1)
        hBox2.addWidget(self.uiNameEditButton)
        hBox2.addWidget(self.uiNameAppendButton)
        hBox2.addWidget(self.uiNameDeleteButton)
        vBox2 = QtGui.QVBoxLayout()
        vBox2.addWidget(self.uiNameList)
        vBox2.addLayout(hBox2)
        groupBox2 =QtGui.QGroupBox("Names")
        groupBox2.setLayout(vBox2)

        #The query part
        self.uiQueryEditor = QScint()
        vBox3 = QtGui.QVBoxLayout()
        vBox3.addWidget(self.uiQueryEditor)
        groupBox3 =QtGui.QGroupBox("Query")
        groupBox3.setLayout(vBox3)

        #This is the end...
        hBox3 =QtGui.QHBoxLayout()
        hBox3.addWidget(groupBox1)
        hBox3.addWidget(groupBox2)
        hBox3.addWidget(groupBox3)
        self.setLayout(hBox3)
