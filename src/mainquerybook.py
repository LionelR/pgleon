#-*- coding:utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore
import sys

__author__ = 'lionel'

from src import db
from src.mainbookmarks import ShowBookMarks, EditBookMarks, SaveBookMarks
from ui.forms.querybookui import QueryBookUI, QueryPageUI
from ui.widgets.qtable import QTableModel


class GenericThread(QtCore.QThread):
    def __init__(self, function, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def __del__(self):
        self.wait()

    def run(self):
        self.function(*self.args, **self.kwargs)
        return


class QueryPage(QueryPageUI):

    resultSignal = QtCore.pyqtSignal([object, object, object])

    def __init__(self, *args, **kwargs):
        self.connection = kwargs.pop("connection")
        self.parent = kwargs.pop("parent")
        self.name = ""
        self.queryThread = None
        super(QueryPage, self).__init__(*args, **kwargs)
        fontSize = self.uiQueryResult.verticalHeader().font().pointSize()
        self.uiQueryResult.verticalHeader().setDefaultSectionSize(fontSize+2*3)

    def currentConnection(self):
        return self.connection

    def currentName(self):
        return self.name

    def setCurrentName(self, name):
        self.name = name
        index = self.parent.indexOf(self)
        self.parent.setPageTitle(index, name)

    def execute(self, prefix=""):
        query = unicode(self.uiQueryEditor.text())
        if query.strip() == "":
            return
        query = prefix + unicode(query)

        # Run the query in a thread
        self.queryThread = GenericThread(self._execute, query)
        # self.resultSignal.disconnect(self._setResult)
        self.resultSignal.connect(self._setResult)
        self.queryThread.start()

    def _execute(self, query):
        """Internal function to be called by the execute function in a thread.
        The results will be passed to the _setResult function"""
        self._preProcessing() #The thread is started
        headers, res, status = db.execute(self.connection, query)
        self.resultSignal.emit(headers, res, status)


    def _preProcessing(self):
        """Preprocessing operations before running query"""
        #Change the states of the buttons, based on the onChangePage function
        index = self.parent.indexOf(self)
        self.parent.onChangePage(index)

    def _postProcessing(self):
        """Apply operations after running query"""
        index = self.parent.indexOf(self)
        self.parent.onChangePage(index)

    def _setResult(self, headers, res, status):
        if isinstance(res, db.DBError):
            self.uiQueryMsg.setPlainText(QtCore.QString.fromUtf8(res.get_msg()))
            self.uiTab.setCurrentWidget(self.uiQueryMsg)
        else:
            tm = QTableModel(res, headers, self)
            self.uiQueryResult.setModel(tm)
            # self.uiQueryResult.resizeColumnsToContents()
            # self.uiQueryResult.resizeRowsToContents() #Very slow
            self.uiTab.setCurrentWidget(self.uiQueryResult)
            self.setStatus(status)
        self._postProcessing()

    def runQuery(self):
        self.execute()

    def explainQuery(self):
        self.execute(prefix=u"EXPLAIN ")

    def analyseQuery(self):
        self.execute(prefix=u"EXPLAIN ANALYSE ")

    def cancelQuery(self):
        print("Canceling query")
        self.connection.cancel()
        print("Query canceled")


class MainQueryBook(QueryBookUI):
    def __init__(self, database):
        super(MainQueryBook, self).__init__()
        self.database = database
        self.setWindowTitle(self.database.name)
        self.setToolBar()

        self.uiQueryBook.setTabsClosable(True)
        self.uiQueryBook.setMovable(True)
        self.uiQueryBook.setTabShape(QtGui.QTabWidget.Rounded)
        self.uiQueryBook.setElideMode(1)
        self.pageCount = 0
        self.newQueryPage()

        #Signals
        self.uiQueryBook.tabCloseRequested.connect(self.onClosePage)
        self.uiQueryBook.currentChanged.connect(self.onChangePage)

    def runQuery(self):
        page = self.uiQueryBook.currentWidget()
        page.runQuery()

    def explainQuery(self):
        page = self.uiQueryBook.currentWidget()
        page.explainQuery()

    def analyseQuery(self):
        page = self.uiQueryBook.currentWidget()
        page.analyseQuery()

    def onStopQuery(self):
        page = self.uiQueryBook.currentWidget()
        page.cancelQuery()

    def newQueryPage(self):
        """Add a new query page to the book"""
        name = "Query_%i" % self._pageCount()
        page = QueryPage(connection=self.database.newConnection(), parent=self)
        self.uiQueryBook.addTab(page, name)
        self.uiQueryBook.setCurrentWidget(page)
        return page

    def setPageTitle(self, index, title):
        self.uiQueryBook.setTabText(index, title)

    def indexOf(self, page):
        return self.uiQueryBook.indexOf(page)

    def _pageCount(self):
        """A page counter"""
        self.pageCount += 1
        return self.pageCount

    def onClosePage(self, index):
        page = self.uiQueryBook.currentWidget()
        page.currentConnection().close()
        self.uiQueryBook.removeTab(index)
        del page

    def onChangePage(self, index):
        page = self.uiQueryBook.widget(index)
        if page.queryThread is not None:
            running = page.queryThread.isRunning()
            self.uiRunAction.setEnabled(not running)
            self.uiExplainAction.setEnabled(not running)
            self.uiAnalyseAction.setEnabled(not running)
        else:
            self.uiRunAction.setEnabled(True)
            self.uiExplainAction.setEnabled(True)
            self.uiAnalyseAction.setEnabled(True)

    def onSaveBookMarks(self):
        page = self.uiQueryBook.currentWidget()
        query = page.uiQueryEditor.text()
        dlg = SaveBookMarks(database=self.database, query=query)
        result = dlg.exec_()
        if result == QtGui.QDialog.Accepted:
            self.updateShowBookMarksButton()
            name = dlg.getName()
            index = self.uiQueryBook.currentIndex()
            self.setPageTitle(index, name)

    def setToolBar(self):
        self.uiNewAction = QtGui.QAction(QtGui.QIcon('icons/plus.png'), '&New', self)
        self.uiNewAction.setShortcut('Ctrl+N')
        self.uiNewAction.setStatusTip('New query')
        self.uiNewAction.triggered.connect(self.newQueryPage)
        self.uiToolBar.addAction(self.uiNewAction)

        self.uiToolBar.addSeparator()

        self.uiRunAction = QtGui.QAction(QtGui.QIcon('icons/run.png'), '&Run', self)
        self.uiRunAction.setShortcut('Ctrl+R')
        self.uiRunAction.setStatusTip('Run query')
        self.uiRunAction.triggered.connect(self.runQuery)
        self.uiToolBar.addAction(self.uiRunAction)

        self.uiStopAction = QtGui.QAction(QtGui.QIcon('icons/stop.png'), '&Stop', self)
        self.uiStopAction.setShortcut('Ctrl+Q')
        self.uiStopAction.setStatusTip('Stop the current query')
        self.uiStopAction.triggered.connect(self.onStopQuery)
        self.uiToolBar.addAction(self.uiStopAction)

        self.uiExplainAction = QtGui.QAction(QtGui.QIcon('icons/explain.png'), '&Explain', self)
        self.uiExplainAction.setShortcut('Ctrl+E')
        self.uiExplainAction.setStatusTip('Explain query')
        self.uiExplainAction.triggered.connect(self.explainQuery)
        self.uiToolBar.addAction(self.uiExplainAction)

        self.uiAnalyseAction = QtGui.QAction(QtGui.QIcon('icons/analyse.png'), '&Analyse', self)
        # uiAnalyseAction.setShortcut('Ctrl+A')
        self.uiAnalyseAction.setStatusTip('Analyse query')
        self.uiAnalyseAction.triggered.connect(self.analyseQuery)
        self.uiToolBar.addAction(self.uiAnalyseAction)

        self.uiToolBar.addSeparator()

        uiSaveBookMarksAction = QtGui.QAction(QtGui.QIcon('icons/star.png'), '&Save', self)
        uiSaveBookMarksAction.setShortcut('Ctrl+D')
        uiSaveBookMarksAction.setStatusTip('Save as bookmark')
        uiSaveBookMarksAction.triggered.connect(self.onSaveBookMarks)
        self.uiToolBar.addAction(uiSaveBookMarksAction)

        uiShowBookMarksButton = QtGui.QToolButton()
        uiShowBookMarksButton.setIcon(QtGui.QIcon('icons/bookmarks.png'))
        uiShowBookMarksButton.setStatusTip('Show all bookmarks')
        uiShowBookMarksButton.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.uiToolBar.addWidget(uiShowBookMarksButton)
        self.uiShowBookMarksButton = uiShowBookMarksButton
        self.updateShowBookMarksButton()

    def updateShowBookMarksButton(self):
        self.uiShowBookMarksButton.setMenu(ShowBookMarks(database=self.database, parent=self))


def main():
    app = QtGui.QApplication(sys.argv)
    ex = MainQueryBook()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()