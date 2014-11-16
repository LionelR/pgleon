#-*- coding:utf-8 -*-
from PyQt4 import QtGui, QtCore

__author__ = 'lionel'


class ExplorerUI(QtGui.QDockWidget):
    def __init__(self, *args, **kwargs):
        super(ExplorerUI, self).__init__(*args, **kwargs)
        self.initUI()
        self.setObjectName('Explorer Dock')
        self.setWindowTitle('Explorer Dock')

    def initUI(self):
        #toolbar
        self.uiToolBar = QtGui.QToolBar('Explorer toolbar', self)
        self.uiToolBar.setIconSize(QtCore.QSize(8, 8))
        # self.uiToolBar.setMovable(False)
        self.uiToolBar.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)

        self.uiRefreshAction = QtGui.QAction(QtGui.QIcon('icons/refresh.png'), 'Refresh', self.uiToolBar)
        self.uiRefreshAction.setStatusTip('Refresh')
        self.uiToolBar.addAction(self.uiRefreshAction)

        self.uiExpandAction = QtGui.QAction(QtGui.QIcon('icons/expand.png'), 'Expand', self.uiToolBar)
        self.uiExpandAction.setStatusTip('Expand')
        self.uiToolBar.addAction(self.uiExpandAction)

        self.uiCollapseAction = QtGui.QAction(QtGui.QIcon('icons/collapse.png'), 'Collapse', self.uiToolBar)
        self.uiCollapseAction.setStatusTip('Collapse')
        self.uiToolBar.addAction(self.uiCollapseAction)

        self.uiExplorerTree = QtGui.QTreeView(self)
        self.uiExplorerTree.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        vbox = QtGui.QVBoxLayout()
        vbox.setSpacing(0)
        vbox.addWidget(self.uiToolBar)
        vbox.addWidget(self.uiExplorerTree)

        widget = QtGui.QWidget(self)
        widget.setLayout(vbox)
        self.setWidget(widget)