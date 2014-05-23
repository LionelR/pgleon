#-*- coding:utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore
import sys

__author__ = 'lionel'

from src import db
from ui.forms.queryui import MainUI, QueryPage
from ui.widgets.qtable import QTableModel

name = "PGLeon"
version = "0.1"


class MainQueryBook(MainUI):
    def __init__(self, connParams):
        super(MainQueryBook, self).__init__()
        self.connParams = connParams
        name = self.connParams.pop('name')
        self.uiSetTitle(name)
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
        query = unicode(page.uiQueryEditor.text())
        if query.strip() == "":
            return
        query = prefix + unicode(query)
        conn = db.Database(**self.connParams)
        headers, res = conn.execute(query)
        if isinstance(res, db.DBError):
            page.uiQueryMsg.setPlainText(QtCore.QString(res.get_msg()))
            page.uiTab.setCurrentWidget(self.uiQueryMsg)
        else:
            tm = QTableModel(res, headers, self)
            page.uiQueryResult.setModel(tm)
            page.uiQueryResult.resizeColumnsToContents()
            page.uiQueryResult.resizeRowsToContents()
            page.uiTab.setCurrentWidget(self.uiQueryResult)
            self.setStatus(conn.cur.statusmessage)

    def runQuery(self):
        self.execute()

    def explainQuery(self):
        self.execute(prefix=u"EXPLAIN ")

    def analyseQuery(self):
        self.execute(prefix=u"EXPLAIN ANALYSE ")

    def newQueryPage(self):
        """Add a new query page to the book"""
        name = "Query_%i"%self._pageCount()
        page = QueryPage()
        self.uiQueryBook.addTab(page, name)
        self.uiQueryBook.setCurrentWidget(page)

    def _pageCount(self):
        """A page counter"""
        self.pageCount += 1
        return self.pageCount

    def onClosePage(self, index):
        self.uiQueryBook.removeTab(index)

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
        uiAnalyseAction.setShortcut('Ctrl+A')
        uiAnalyseAction.setStatusTip('Analyse query')
        uiAnalyseAction.triggered.connect(self.analyseQuery)
        self.uiToolBar.addAction(uiAnalyseAction)


def main():
    app = QtGui.QApplication(sys.argv)
    ex = MainQueryBook()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()