# -*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore
from src.conf import Bookmark
from ui.forms.explorerui import ExplorerUI
import explorer_model as em


class BookMarksExplorer(ExplorerUI):
    def __init__(self, *args, **kwargs):
        self.database = kwargs.pop('database')
        self.parent = kwargs.pop('parent')
        super(BookMarksExplorer, self).__init__(*args, **kwargs)
        self.setName('Bookmarks')

        self.icons = {
            'GLOBAL': QtGui.QIcon(QtGui.QPixmap(':/global_bookmark.png')),
            'SPECIFIC': QtGui.QIcon(QtGui.QPixmap(':/specific_bookmark.png')),
            'DATABASE': QtGui.QIcon(QtGui.QPixmap(':/database.png')),
        }

        self.rootNode = em.Node(self.database, parent=None, icon=self.icons['DATABASE'])

        self.model = em.ExplorerModel(self.rootNode, self.parent)
        self.view = self.uiExplorerTree
        self.view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.view.setUniformRowHeights(True)
        self.view.setAnimated(True)
        self.view.setModel(self.model)

        self.setupExplorer()
        self.setupToolBar()

        #Signals
        self.view.doubleClicked.connect(self.onDoubleClick)
        self.view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.onContextMenu)


    def setupToolBar(self):
        self.uiRefreshAction.triggered.connect(self.onRefresh)
        self.uiCollapseAction.triggered.connect(self.onCollapse)
        self.uiExpandAction.triggered.connect(self.onExpand)

    def onRefresh(self):
        self.setupExplorer()

    def onCollapse(self):
        self.uiExplorerTree.collapseAll()

    def onExpand(self):
        self.uiExplorerTree.expandAll()

    def setupExplorer(self):
        self.view.reset()
        self.model.removeRows(0, self.model.rowCount(QtCore.QModelIndex()))

        globalBookmarks = Bookmark.select().where(Bookmark.isglobal == True)
        if globalBookmarks.count() > 0:
            parentItem = em.GenericNode("Globals queries", parent=self.rootNode, icon=self.icons["GLOBAL"])
            keywordItemDict = {}
            for bmk in globalBookmarks:
                if bmk.keyword not in keywordItemDict.keys():
                    keywordItemDict[bmk.keyword] = em.KeyWordNode(bmk.keyword, parent=parentItem, icon=None)
                em.BookMarkNode(bmk.name, oid=bmk.id, query=bmk.query, isglobal=True,
                               parent=keywordItemDict[bmk.keyword], icon=self.icons['GLOBAL'])

        specificBookmarks = Bookmark.select().where(Bookmark.isglobal == False)
        if specificBookmarks.count() > 0:
            parentItem = em.GenericNode("Specific queries", parent=self.rootNode, icon=self.icons["SPECIFIC"])
            keywordItemDict = {}
            for bmk in specificBookmarks:
                if bmk.keyword not in keywordItemDict.keys():
                    keywordItemDict[bmk.keyword] = em.KeyWordNode(bmk.keyword, parent=parentItem, icon=None)
                em.BookMarkNode(bmk.name, oid=bmk.id, query=bmk.query, isglobal=False,
                               parent=keywordItemDict[bmk.keyword], icon=self.icons['SPECIFIC'])


    def onDoubleClick(self, index):
        parentNode = self.model.getNode(index)
        if parentNode.typeInfo() == 'BOOKMARK':
            page = self.nativeParentWidget().newQueryPage()
            page.uiQueryEditor.setText(parentNode.query())
            page.onRewriteQuery()
            page.setCurrentName(parentNode.name())
            page.onRunQuery()

    def onContextMenu(self):
        pass

    def addPage(self, query, name):
        page = self.parent.newQueryPage()
        page.uiQueryEditor.setText(query)
        page.setCurrentName(name)