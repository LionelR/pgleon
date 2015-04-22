# -*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore
from src.conf import Bookmark
from ui.forms.explorerui import ExplorerUI
import explorer_model as em
from functools import partial


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

        self.rootNode = em.Node("", parent=None, icon=self.icons['DATABASE'])

        self.model = em.ExplorerModel(self.rootNode, self.parent, "Bookmark")
        self.view = self.uiExplorerTree
        self.view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.view.setUniformRowHeights(True)
        self.view.setAnimated(True)
        self.view.setModel(self.model)

        self.setupExplorer()
        self.setupToolBar()

        # Signals
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
            for bmk in globalBookmarks:
                em.BookMarkNode(bmk.name, oid=bmk.id, query=bmk.query, isglobal=True,
                                parent=parentItem, icon=self.icons['GLOBAL'])

        specificBookmarks = Bookmark.select().where(Bookmark.isglobal == False)
        if specificBookmarks.count() > 0:
            parentItem = em.GenericNode("Specific queries", parent=self.rootNode, icon=self.icons["SPECIFIC"])
            for bmk in specificBookmarks:
                em.BookMarkNode(bmk.name, oid=bmk.id, query=bmk.query, isglobal=False,
                                parent=parentItem, icon=self.icons['SPECIFIC'])

    def onDoubleClick(self, index):
        parentNode = self.model.getNode(index)
        if parentNode.typeInfo() == 'BOOKMARK':
            page = self.nativeParentWidget().newQueryPage()
            page.uiQueryEditor.setText(parentNode.query())
            page.onRewriteQuery()
            page.setCurrentName(parentNode.name())
            page.onRunQuery()

    def onContextMenu(self, point):
        index = self.view.indexAt(point)
        parentNode = self.model.getNode(index)
        globalPos = self.view.mapToGlobal(point)
        if isinstance(parentNode, em.BookMarkNode):
            uiMenu = QtGui.QMenu()

            uiQueryLimitAction = QtGui.QAction('Remove', self)
            uiQueryLimitAction.setStatusTip('Remove this bookmark')
            uiQueryLimitAction.triggered.connect(partial(self.onDeleteBookmark, parentNode))
            uiMenu.addAction(uiQueryLimitAction)

            uiMenu.exec_(globalPos)

    def onDeleteBookmark(self, parentNode):
        q = Bookmark.delete().where(Bookmark.id==parentNode._oid)
        q.execute()
        self.onRefresh()

    def addPage(self, query, name):
        page = self.parent.newQueryPage()
        page.uiQueryEditor.setText(query)
        page.setCurrentName(name)