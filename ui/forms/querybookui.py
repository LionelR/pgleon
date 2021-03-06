#-*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore
from ui.widgets.editor import QueryEditor

__author__ = 'lionel'


class QueryPageUI(QtGui.QWidget):
    """Represent a page in the central tabwidget widget. Each page is a particular query"""
    def __init__(self, *args, **kwargs):
        super(QueryPageUI, self).__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        # self.uiToolBar = self.addToolBar('Main Toolbar')
        self.uiToolBar = QtGui.QToolBar('Main toolbar', parent=self)
        self.uiToolBar.setObjectName('Main Toolbar')
        self.uiToolBar.setIconSize(QtCore.QSize(32, 32))
        self.uiToolBar.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)

        self.uiQueryEditor = QueryEditor(self)
        self.uiQueryResult = QtGui.QTableView(self)
        self.uiExplainResult = QtGui.QTreeView(self)
        self.uiQueryMsg = QtGui.QTextEdit(self)
        self.uiStatusLabel = QtGui.QLabel(self)
        self.uiTimerLabel = QtGui.QLabel(self)

        self.uiStackedResult = QtGui.QStackedWidget()
        self.uiStackedResult.addWidget(self.uiQueryResult)
        self.uiStackedResult.addWidget(self.uiExplainResult)
        self.uiStackedResult.setCurrentWidget(self.uiQueryResult)

        self.uiTab = QtGui.QTabWidget(self)
        self.uiTab.addTab(self.uiStackedResult, "Results")
        self.uiTab.addTab(self.uiQueryMsg, "Messages")

        self.uiVSplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        self.uiVSplitter.addWidget(self.uiQueryEditor)
        self.uiVSplitter.addWidget(self.uiTab)
        self.uiVSplitter.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        uiVBox = QtGui.QVBoxLayout(self)
        uiVBox.addWidget(self.uiToolBar)
        uiVBox.addWidget(self.uiVSplitter)

        uiHBox = QtGui.QHBoxLayout()
        uiHBox.addWidget(self.uiStatusLabel)
        uiHBox.addStretch()
        uiHBox.addWidget(self.uiTimerLabel)
        uiVBox.addLayout(uiHBox)

        self.setLayout(uiVBox)

    def setStatus(self, status):
        self.uiStatusLabel.setText(status)


class QueryBookUI(QtGui.QMainWindow):

    def __init__(self):
        super(QueryBookUI, self).__init__()
        self.initUI()

    def initUI(self):
        self.uiMenuBar = self.menuBar()

        self.uiQueryBook = QtGui.QTabWidget()
        self.setCentralWidget(self.uiQueryBook)

        self.setGeometry(300, 300, 600, 400)

        self.uiStatusBar = self.statusBar()

        self.show()




