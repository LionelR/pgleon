#-*- coding:utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore
import sys

__author__ = 'lionel'

from src import db
from src.mainbookmarks import ShowBookMarks, SaveBookMarks
from ui.forms.querybookui import QueryBookUI, QueryPageUI
from ui.widgets.qtable import QTableModel
from src.mainexplorer import MainExplorer
import sqlparse


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
        self.uiQueryResult.verticalHeader().setDefaultSectionSize(fontSize + 2 * 3)

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
        self._preProcessing()  #The thread is started
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
            self.setStatus('')
        else:
            self.tm = QTableModel(res, headers, self)
            self.uiQueryResult.setModel(self.tm)
            # self.uiQueryResult.resizeColumnsToContents()
            # self.uiQueryResult.resizeRowsToContents() #Very slow
            self.uiTab.setCurrentWidget(self.uiQueryResult)
            self.setStatus(status)
            self.uiQueryMsg.clear()
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

        self.uiQueryBook.setTabsClosable(True)
        self.uiQueryBook.setMovable(True)
        self.uiQueryBook.setTabShape(QtGui.QTabWidget.Rounded)
        self.uiQueryBook.setElideMode(1)
        self.pageCount = 0
        self.newQueryPage()

        #ExplorerTree
        self.setupExplorerTree()

        #Toolbar and menubar
        self.setupToolBar()

        #Signals
        self.uiQueryBook.tabCloseRequested.connect(self.onClosePage)
        self.uiQueryBook.currentChanged.connect(self.onChangePage)

        #Window position and size
        self.settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope,
                                         'pgleon', 'pgleon', parent=self)
        self.settings.setFallbacksEnabled(False)  # File only, no fallback to registry or or.
        self.restoreGeometry(self.settings.value("geometry").toByteArray())
        self.restoreState(self.settings.value("windowState").toByteArray())


    def onRunQuery(self):
        page = self.uiQueryBook.currentWidget()
        page.runQuery()

    def onExplainQuery(self):
        page = self.uiQueryBook.currentWidget()
        page.explainQuery()

    def onAnalyseQuery(self):
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
            self.updateShowBookMarksMenu()
            name = dlg.getName()
            index = self.uiQueryBook.currentIndex()
            self.setPageTitle(index, name)

    def onRewriteQuery(self):
        page = self.uiQueryBook.currentWidget()
        query = unicode(page.uiQueryEditor.text())
        formattedQuery = sqlparse.format(query, keyword_case="upper", reindent=True, indent_width=4, indent_tabs=False)
        page.uiQueryEditor.setText(formattedQuery)

    def setupExplorerTree(self):
        self.Explorer = MainExplorer(database=self.database, parent=self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.Explorer)

    def setupToolBar(self):
        self.uiExitAction = QtGui.QAction(QtGui.QIcon('icons/exit.png'), '&Exit', self)
        self.uiExitAction.setShortcut('Ctrl+Q')
        self.uiExitAction.setStatusTip('Exit application')
        self.uiExitAction.triggered.connect(self.close)

        self.uiNewAction = QtGui.QAction(QtGui.QIcon('icons/plus.png'), '&New', self)
        self.uiNewAction.setShortcut('Ctrl+N')
        self.uiNewAction.setStatusTip('New query')
        self.uiNewAction.triggered.connect(self.newQueryPage)

        self.uiRunAction = QtGui.QAction(QtGui.QIcon('icons/run.png'), '&Run', self)
        self.uiRunAction.setShortcut('Ctrl+R')
        self.uiRunAction.setStatusTip('Run query')
        self.uiRunAction.triggered.connect(self.onRunQuery)

        self.uiStopAction = QtGui.QAction(QtGui.QIcon('icons/stop.png'), '&Stop', self)
        self.uiStopAction.setShortcut('Ctrl+Q')
        self.uiStopAction.setStatusTip('Stop the current query')
        self.uiStopAction.triggered.connect(self.onStopQuery)

        self.uiExplainAction = QtGui.QAction(QtGui.QIcon('icons/explain.png'), '&Explain', self)
        self.uiExplainAction.setShortcut('Ctrl+E')
        self.uiExplainAction.setStatusTip('Explain query')
        self.uiExplainAction.triggered.connect(self.onExplainQuery)

        self.uiAnalyseAction = QtGui.QAction(QtGui.QIcon('icons/analyse.png'), '&Analyse', self)
        # uiAnalyseAction.setShortcut('Ctrl+A')
        self.uiAnalyseAction.setStatusTip('Analyse query')
        self.uiAnalyseAction.triggered.connect(self.onAnalyseQuery)

        self.uiSaveBookMarksAction = QtGui.QAction(QtGui.QIcon('icons/star.png'), '&Save', self)
        self.uiSaveBookMarksAction.setShortcut('Ctrl+D')
        self.uiSaveBookMarksAction.setStatusTip('Save as bookmark')
        self.uiSaveBookMarksAction.triggered.connect(self.onSaveBookMarks)

        self.uiShowBookMarksButton = QtGui.QToolButton()
        self.uiShowBookMarksButton.setIcon(QtGui.QIcon('icons/bookmarks.png'))
        self.uiShowBookMarksButton.setStatusTip('Show all bookmarks')
        self.uiShowBookMarksButton.setPopupMode(QtGui.QToolButton.InstantPopup)
        self.updateShowBookMarksMenu() #First initialization
        self.uiShowBookMarksButton.setMenu(self.uiShowBookMarksMenu)

        self.uiRewriteAction = QtGui.QAction(QtGui.QIcon('icons/rewrite.png'), 'Rewrite', self)
        self.uiRewriteAction.setShortcut('Ctrl+B')
        self.uiRewriteAction.setStatusTip('Rewrite query in a beautiful manner')
        self.uiRewriteAction.triggered.connect(self.onRewriteQuery)

        #Toolbar
        self.uiToolBar.addAction(self.uiNewAction)
        self.uiToolBar.addSeparator()
        self.uiToolBar.addAction(self.uiRunAction)
        self.uiToolBar.addAction(self.uiStopAction)
        self.uiToolBar.addAction(self.uiExplainAction)
        self.uiToolBar.addAction(self.uiAnalyseAction)
        self.uiToolBar.addSeparator()
        self.uiToolBar.addAction(self.uiSaveBookMarksAction)
        self.uiToolBar.addWidget(self.uiShowBookMarksButton)
        self.uiToolBar.addSeparator()
        self.uiToolBar.addAction(self.uiRewriteAction)

        #Menubar
        self.uiFileMenu = self.uiMenuBar.addMenu('&File')
        self.uiFileMenu.addAction(self.uiExitAction)

        self.uiQueryMenu = self.uiMenuBar.addMenu('&Query')
        self.uiQueryMenu.addAction(self.uiNewAction)
        self.uiQueryMenu.addAction(self.uiRunAction)
        self.uiQueryMenu.addAction(self.uiStopAction)
        self.uiQueryMenu.addAction(self.uiExplainAction)
        self.uiQueryMenu.addAction(self.uiAnalyseAction)

        self.uiBookMarksMenu = self.uiMenuBar.addMenu('&Bookmarks')
        self.uiBookMarksMenu.addAction(self.uiSaveBookMarksAction)
        self.uiBookMarksMenu.addMenu(self.uiShowBookMarksMenu)

        self.uiWindowMenu = self.uiMenuBar.addMenu('&Window')
        self.uiToggleDockExplorerTreeAction = self.Explorer.toggleViewAction()
        self.uiWindowMenu.addAction(self.uiToggleDockExplorerTreeAction)
        self.uiToggleToolbarAction = self.uiToolBar.toggleViewAction()
        self.uiWindowMenu.addAction(self.uiToggleToolbarAction)


    def updateShowBookMarksMenu(self):
        self.uiShowBookMarksMenu = ShowBookMarks('Bookmarks', database=self.database, parent=self)


    def closeEvent(self, event):
        print('close')
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        event.accept()


def main():
    app = QtGui.QApplication(sys.argv)
    ex = MainQueryBook()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()