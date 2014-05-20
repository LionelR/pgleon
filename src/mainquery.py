#-*- coding:utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore
import sys

__author__ = 'lionel'

from src import db
from ui.forms.queryui import MainUI, QueryTab
from ui.widgets.qtable import QTableModel

name = "PGLeon"
version = "0.1"

class Main(MainUI):
    def __init__(self):
        super(Main, self).__init__()
        self.uiSetTitle("{0:s} - {1:s}".format(name, version))
        self.setToolBar()
        self.firstPage = QueryTab(self)
        self.uiCentralWidget.addTab(self.firstPage, "Query1")

    def execute(self, prefix=""):
        query = unicode(self.firstPage.uiQueryEditor.text())
        if query.strip()=="":
            return
        query = prefix + unicode(query)
        conn = db.Database()
        headers, res = conn.execute(query)
        if isinstance(res, db.DBError):
            self.firstPage.uiQueryMsg.setPlainText(QtCore.QString(res.get_msg()))
            self.firstPage.uiTab.setCurrentWidget(self.uiQueryMsg)
        else:
            tm = QTableModel(res, headers, self)
            self.firstPage.uiQueryResult.setModel(tm)
            self.firstPage.uiQueryResult.resizeColumnsToContents()
            self.firstPage.uiQueryResult.resizeRowsToContents()
            self.firstPage.uiTab.setCurrentWidget(self.uiQueryResult)
            self.setStatus(conn.cur.statusmessage)

    def runQuery(self):
        self.execute()

    def explainQuery(self):
        self.execute(prefix=u"EXPLAIN ")

    def analyseQuery(self):
        self.execute(prefix=u"EXPLAIN ANALYSE ")

    def setToolBar(self):
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
    ex = Main()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()