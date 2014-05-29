#-*- coding:utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore
import sys

__author__ = 'lionel'

from src import db
from src.mainbookmarks import ShowBookMarks
from ui.forms.querybookui import QueryBookUI, QueryPageUI
from ui.widgets.qtable import QTableModel


class QueryPage(QueryPageUI):
    def __init__(self, *args, **kwargs):
        self.connection = kwargs.pop("connection")
        super(QueryPage, self).__init__(*args, **kwargs)

    def currentConnection(self):
        return self.connection


class MainQueryBook(QueryBookUI):
    def __init__(self, database):
        super(MainQueryBook, self).__init__()
        self.database = database
        self.uiSetTitle(self.database.name)
        self.setToolBar()

        self.uiQueryBook.setTabsClosable(True)
        self.uiQueryBook.setMovable(True)
        self.uiQueryBook.setTabShape(QtGui.QTabWidget.Rounded)
        self.pageCount = 0
        self.newQueryPage()

        #Signals
        self.uiQueryBook.tabCloseRequested.connect(self.onClosePage)

    def execute(self, prefix=""):
        page = self.uiQueryBook.currentWidget()
        connection = page.currentConnection()
        query = unicode(page.uiQueryEditor.text())
        if query.strip() == "":
            return
        query = prefix + unicode(query)

        headers, res, status = db.execute(connection, query)
        if isinstance(res, db.DBError):
            page.uiQueryMsg.setPlainText(QtCore.QString.fromUtf8(res.get_msg()))
            page.uiTab.setCurrentWidget(page.uiQueryMsg)
        else:
            tm = QTableModel(res, headers, self)
            page.uiQueryResult.setModel(tm)
            page.uiQueryResult.resizeColumnsToContents()
            page.uiQueryResult.resizeRowsToContents()
            page.uiTab.setCurrentWidget(page.uiQueryResult)
            page.setStatus(status)

    def runQuery(self):
        self.execute()

    def explainQuery(self):
        self.execute(prefix=u"EXPLAIN ")

    def analyseQuery(self):
        self.execute(prefix=u"EXPLAIN ANALYSE ")

    def newQueryPage(self):
        """Add a new query page to the book"""
        name = "Query_%i"%self._pageCount()
        page = QueryPage(connection=self.database.newConnection())
        self.uiQueryBook.addTab(page, name)
        self.uiQueryBook.setCurrentWidget(page)
        return page

    def _pageCount(self):
        """A page counter"""
        self.pageCount += 1
        return self.pageCount

    def onClosePage(self, index):
        page = self.uiQueryBook.currentWidget()
        page.currentConnection().close()
        self.uiQueryBook.removeTab(index)
        del page

    def setToolBar(self):
        uiNewAction = QtGui.QAction(QtGui.QIcon('icons/plus.png'), '&New', self)
        uiNewAction.setShortcut('Ctrl+N')
        uiNewAction.setStatusTip('New query')
        uiNewAction.triggered.connect(self.newQueryPage)
        self.uiToolBar.addAction(uiNewAction)

        uiRunAction = QtGui.QAction(QtGui.QIcon('icons/run.png'), '&Run', self)
        uiRunAction.setShortcut('Ctrl+R')
        uiRunAction.setStatusTip('Run query')
        uiRunAction.triggered.connect(self.runQuery)
        self.uiToolBar.addAction(uiRunAction)

        uiExplainAction = QtGui.QAction(QtGui.QIcon('icons/explain.png'), '&Explain', self)
        uiExplainAction.setShortcut('Ctrl+E')
        uiExplainAction.setStatusTip('Explain query')
        uiExplainAction.triggered.connect(self.explainQuery)
        self.uiToolBar.addAction(uiExplainAction)

        uiAnalyseAction = QtGui.QAction(QtGui.QIcon('icons/analyse.png'), '&Analyse', self)
        # uiAnalyseAction.setShortcut('Ctrl+A')
        uiAnalyseAction.setStatusTip('Analyse query')
        uiAnalyseAction.triggered.connect(self.analyseQuery)
        self.uiToolBar.addAction(uiAnalyseAction)

        uiShowBookMarksAction = QtGui.QAction(QtGui.QIcon('icons/bookmarks.png'), '&Bookmarks', self)
        uiShowBookMarksAction.setShortcut('Ctrl+B')
        uiShowBookMarksAction.setStatusTip('Show all bookmarks')
        uiShowBookMarksAction.setMenu(ShowBookMarks(database=self.database, parent=self))
        self.uiToolBar.addAction(uiShowBookMarksAction)


def main():
    app = QtGui.QApplication(sys.argv)
    ex = MainQueryBook()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()