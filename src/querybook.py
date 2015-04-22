# -*- coding:utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import sys
from src import db
from PyQt4 import QtGui, QtCore
from ui.forms.querybookui import QueryBookUI, QueryPageUI
from ui.forms.bookmarksui import SaveAsBookmarDialog
from ui.widgets.qtable import QTableModel
from src.objects_explorer import ObjectsExplorer
from src.bookmarks_explorer import BookMarksExplorer
from src.conf import DBConfig, Bookmark
import sqlparse
import time
import resources_rc


class GenericThread(QtCore.QThread):
    def __init__(self, function, query):
        QtCore.QThread.__init__(self)
        self.function = function
        self.query = query
        self.started.connect(self.onStart)
        self.finished.connect(self.onFinish)
        self.terminated.connect(self.onTerminate)

    def __del__(self):
        self.wait()

    def run(self):
        self.function(self.query)
        return

    def onStart(self):
        print('GenericThread started')

    def onFinish(self):
        print('GenericThread finished')

    def onTerminate(self):
        print('GenericThread terminated')


class PeriodicThread(QtCore.QThread):
    def __init__(self, function, query, mswait, count):
        QtCore.QThread.__init__(self)
        self.function = function
        self.query = query
        self.mswait = mswait
        self.count = count

    def __del__(self):
        self.wait()

    def run(self):
        for i in range(self.count):
            self.function(self.query)
            time.sleep(self.mswait)
        return


class QueryPage(QueryPageUI):
    resultSignal = QtCore.pyqtSignal([object, object, object])

    def __init__(self, *args, **kwargs):
        self.database = kwargs.pop("database")
        self.parent = kwargs.pop("parent")
        self.connection = self.database.newConnection()
        self.name = ""
        self.queryThread = None
        self.model = None
        super(QueryPage, self).__init__(*args, **kwargs)

        # Query result tableView
        fontSize = self.uiQueryResult.verticalHeader().font().pointSize()
        self.uiQueryResult.verticalHeader().setDefaultSectionSize(fontSize + 6)
        self.uiQueryResult.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.uiQueryResult.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        # allow to copy results
        copyAction = QtGui.QAction("Copy data", self)
        copyAction.setShortcuts(QtGui.QKeySequence.Copy)
        copyAction.triggered.connect(self.onCopySelectedResults)
        self.addAction(copyAction)

        # Timer
        self.time = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.onTimeOut)

        # Toolbar
        self.setupToolBar()

    def currentConnection(self):
        return self.connection

    def currentName(self):
        return self.name

    def setCurrentName(self, name):
        self.name = name
        index = self.parent.indexOf(self)
        self.parent.setPageTitle(index, name)

    def execute(self, prefix=""):
        """Execute a query.
        Parameters:
        prefix: text to prepend to the text contained in the uiQueryEditor before
        executing it as a query. Normally a word like EXPLAIN or ANALYSE
        """
        query = self.currentQuery()
        if query.strip() == "":
            return
        query = prefix + unicode(query)
        # Run the query in a thread
        self.queryThread = GenericThread(self._execute, query)
        self.resultSignal.connect(self._setResult)
        self.queryThread.started.connect(self._preProcessing)
        self.queryThread.finished.connect(self._postProcessing)
        self.queryThread.start()

    def executeToCSV(self, filename):
        """Execute the query and set the result in a CSV file
        Parameters:
        filename: complete path of the resulting CSV file
        """
        query = self.currentQuery()
        if query.strip() == "":
            return
        # Run the query in a thread
        self.filename = filename
        self.queryThread = GenericThread(self._execute, query)
        self.resultSignal.connect(self._setResultToCSV)
        self.queryThread.finished.connect(self._postProcessing)
        self.queryThread.start()

    def executePeriodically(self, mswait=1000, count=5):
        """Periodically execute a query
        Parameters:
        mswait: waiting time by cycle, in millisecond
        count: cycle number
        """
        query = self.currentQuery()
        if query.strip() == "":
            return
        # Run the query in a thread
        self.queryThread = PeriodicThread(self._execute, query, mswait, count)
        self.resultSignal.connect(self._appendResult)
        self.queryThread.finished.connect(self._postProcessing)
        self.queryThread.start()

    def _execute(self, query):
        """Internal function to be called in a thread.
        The results will be emitted via the resultSignal signal"""
        headers, res, status = db.execute(self.connection, query)
        self.resultSignal.emit(headers, res, status)

    def _checkRunning(self):
        """Change the states of the buttons based on the queryThread"""
        if self.queryThread is not None:
            running = self.queryThread.isRunning()
            self.uiRunAction.setEnabled(not running)
            self.uiExplainAction.setEnabled(not running)
            self.uiAnalyseAction.setEnabled(not running)
        else:
            self.uiRunAction.setEnabled(True)
            self.uiExplainAction.setEnabled(True)
            self.uiAnalyseAction.setEnabled(True)

    def _preProcessing(self):
        """Preprocessing operations before running query"""
        self._checkRunning()
        self.uiQueryMsg.clear()
        self.time = 0
        self.timer.start(1)
        self.model = None

    def _postProcessing(self):
        """Apply operations after running query"""
        self._checkRunning()
        self.timer.stop()
        self.time = 0
        self.model = None
        # self.queryThread.quit()

    def _setResult(self, headers, res, status):
        """Set the result in the uiQueryResult table, or in uiQueryMsg if error
        Parameters:
        headers: list of strings to use as table's columns headers
        res: list of list of results values, (rows, columns) shape
        status: Result message from the db. Usually the row count number
        """
        if isinstance(res, db.DBError):
            self.uiQueryMsg.setPlainText(QtCore.QString.fromUtf8(str(res.get_msg())))
            self.uiTab.setCurrentWidget(self.uiQueryMsg)
            self.setStatus('')
        else:
            self.model = QTableModel(res, headers, self)
            self.uiQueryResult.setModel(self.model)
            self.uiQueryResult.resizeColumnsToContents()
            # self.uiQueryResult.resizeRowsToContents() #Very slow
            self.uiTab.setCurrentWidget(self.uiQueryResult)
            self.setStatus(status)
            self.uiQueryMsg.clear()
            # self._postProcessing()

    def _setResultToCSV(self, headers, res, status):
        """Export the result in a CSV file, or write to uiQueryMsg if error
        Parameters:
        headers: list of strings to use as table's columns headers
        res: list of list of results values, (rows, columns) shape
        status: Result message from the db. Usually the row count number (not used
        here but keeped here for convenience with the _setResult method
        """
        if isinstance(res, db.DBError):
            self.uiQueryMsg.setPlainText(QtCore.QString.fromUtf8(res.get_msg()))
            self.uiTab.setCurrentWidget(self.uiQueryMsg)
            self.setStatus('')
        else:
            import csv

            with open(self.filename, 'w') as f:
                writer = csv.writer(f, delimiter=',')
                writer.writerow(headers)
                for row in res:
                    writer.writerow(row)
            self.setStatus('Export to %s OK' % self.filename)
            # self._postProcessing()

    def _appendResult(self, headers, res, status):
        """Append the result in the uiQueryResult table, or in uiQueryMsg if error
        Parameters:
        headers: list of strings to use as table's columns headers
        res: list of list of results values, (rows, columns) shape
        status: Result message from the db. Usually the row count number
        """
        if isinstance(res, db.DBError):
            self.uiQueryMsg.setPlainText(QtCore.QString.fromUtf8(res.get_msg()))
            self.uiTab.setCurrentWidget(self.uiQueryMsg)
            self.setStatus('')
        else:
            print(res)
            if self.model is None:  # First iteration, we create the model at set it to the view
                self.model = QTableModel(res, headers, self)
                self.uiQueryResult.setModel(self.model)
            else:  # ...else we just have to append rows
                self.model.addRow(res[0])
            self.uiQueryResult.resizeColumnsToContents()
            # self.uiQueryResult.resizeRowsToContents() #Very slow
            self.uiTab.setCurrentWidget(self.uiQueryResult)
            self.setStatus(status)
            self.uiQueryMsg.clear()

    def onRunQuery(self):
        self.execute()

    def onExplainQuery(self):
        self.execute(prefix=u"EXPLAIN ")

    def onAnalyseQuery(self):
        self.execute(prefix=u"EXPLAIN ANALYSE ")

    def onCancelQuery(self):
        self.connection.cancel()
        self.queryThread.quit()

    def onRewriteQuery(self):
        query = self.currentQuery()
        formattedQuery = sqlparse.format(query, keyword_case="upper", reindent=True, indent_width=4, indent_tabs=False)
        self.uiQueryEditor.setText(formattedQuery)

    def onSetVertical(self):
        self.uiVSplitter.setOrientation(QtCore.Qt.Vertical)

    def onSetHorizontal(self):
        self.uiVSplitter.setOrientation(QtCore.Qt.Horizontal)

    def onTimeOut(self):
        self.time += 1
        self.uiTimerLabel.setText("Time: {0}ms".format(self.time))

    def onCopySelectedResults(self):
        """Copy the selected datas (entire rows selections) from the queryResult table
        to the clipboard"""
        # Get the selected indexes from the view
        indexes = self.uiQueryResult.selectedIndexes()
        # If nothing selected, return
        if len(indexes) <= 0:
            return
        # By default the selected indexes are sorted first by row, after by column, but we need the opposed
        # Sorting by indexes id do the trick
        indexes.sort()
        model = self.uiQueryResult.model()
        # Know where we are in the indexes implies to have 2 indexes.
        # Pop the first index from the list and set it's value in a result list
        previousIdx = indexes.pop(0)
        text = model.data(previousIdx, QtCore.Qt.DisplayRole).toString()
        selectedText = [unicode(text)]
        for currentIdx in indexes:
            if currentIdx.row() != previousIdx.row():  # We are on another row in the table : implies new line in the clipboard
                selectedText.append('\n')
            else:  # else we are on the same line, new index = new column in the table = tab separator
                selectedText.append('\t')
            text = model.data(currentIdx, QtCore.Qt.DisplayRole).toString()
            selectedText.append(unicode(text))
            previousIdx = currentIdx
        selectedText = "".join(selectedText)
        QtGui.QApplication.clipboard().setText(selectedText)

    def currentQuery(self):
        query = unicode(self.uiQueryEditor.getText())
        return query

    def onExportToCSV(self):
        query = self.currentQuery()
        if query.strip() == "":
            return
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Export data to CSV file :', selectedFilter='*.csv')
        if filename:
            self.executeToCSV(filename)

    def onMonitor(self):
        query = self.currentQuery()
        if query.strip() == "":
            return
        self.executePeriodically(mswait=1, count=3)

    def onSaveAsBookmark(self):
        name, isGlobal, ok = SaveAsBookmarDialog.getParams()
        if name=="":
            return

        if isGlobal:
            if Bookmark.select().where(Bookmark.name == name, Bookmark.isglobal == isGlobal).exists():
                overwrite = QtGui.QMessageBox.question(self, 'Overwrite',
                                                      "A global bookmark with the same name already exists. Overwrite it?",
                                                      QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                      QtGui.QMessageBox.No)
                if overwrite == QtGui.QMessageBox.Yes:
                    logger.info('Overwriting global bookmark')
                    q = Bookmark.update(query=self.currentQuery()).where(Bookmark.name == name,
                                                                     Bookmark.isglobal == isGlobal)
                    q.execute()
            else:
                newBookmark = Bookmark(name=name, isglobal=isGlobal, query=self.currentQuery(), dbconfig=None)
                newBookmark.save()
        else:
            dbconfig = DBConfig.get(DBConfig.id == self.database.id)
            if Bookmark.select().where(Bookmark.name == name, Bookmark.isglobal == isGlobal,
                                       Bookmark.dbconfig == dbconfig).exists():
                overwrite = QtGui.QMessageBox.question(self, 'Overwrite',
                                                      "A bookmark for this specific database connection with the same name already exists. Overwrite it?",
                                                      QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                                      QtGui.QMessageBox.No)
                if overwrite == QtGui.QMessageBox.Yes:
                    logger.info('Overwriting specific bookmark')
                    q = Bookmark.update(query=self.currentQuery()).where(Bookmark.name == name,
                                                                     Bookmark.isglobal == isGlobal,
                                                                     Bookmark.dbconfig == dbconfig)
                    q.execute()
            else:
                newBookmark = Bookmark(name=name, isglobal=isGlobal, query=self.currentQuery(), dbconfig=dbconfig)
                newBookmark.save()



    def setupToolBar(self):
        self.uiRunAction = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap(':/run.png')), '&Run', self)
        self.uiRunAction.setShortcut('Ctrl+R')
        self.uiRunAction.setStatusTip('Run query')
        self.uiRunAction.triggered.connect(self.onRunQuery)

        self.uiCSVExportAction = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap(':/csv.png')), 'Export as CSV', self)
        self.uiCSVExportAction.setShortcut('Ctrl+Shift+R')
        self.uiCSVExportAction.setStatusTip('Export query results to CSV file')
        self.uiCSVExportAction.setIconVisibleInMenu(True)
        self.uiCSVExportAction.triggered.connect(self.onExportToCSV)

        self.uiStopAction = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap(':/stop.png')), '&Stop', self)
        self.uiStopAction.setShortcut('Ctrl+Q')
        self.uiStopAction.setStatusTip('Stop the current query')
        self.uiStopAction.triggered.connect(self.onCancelQuery)

        self.uiExplainAction = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap(':/explain.png')), '&Explain', self)
        self.uiExplainAction.setShortcut('Ctrl+E')
        self.uiExplainAction.setStatusTip('Explain query')
        self.uiExplainAction.setIconVisibleInMenu(True)
        self.uiExplainAction.triggered.connect(self.onExplainQuery)

        self.uiAnalyseAction = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap(':/analyse.png')), '&Analyse', self)
        self.uiAnalyseAction.setShortcut('Ctrl+Shift+E')
        self.uiAnalyseAction.setStatusTip('Analyse query')
        self.uiAnalyseAction.setIconVisibleInMenu(True)
        self.uiAnalyseAction.triggered.connect(self.onAnalyseQuery)

        self.uiRewriteAction = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap(':/rewrite.png')), 'Rewrite', self)
        self.uiRewriteAction.setShortcut('Ctrl+B')
        self.uiRewriteAction.setStatusTip('Rewrite query in a beautiful manner')
        self.uiRewriteAction.triggered.connect(self.onRewriteQuery)

        self.uiSetVerticalAction = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap(':/vertical.png')), 'Vertical', self)
        self.uiSetVerticalAction.setShortcut('Ctrl+Shift+V')
        self.uiSetVerticalAction.setStatusTip('Set the query page vertically')
        self.uiSetVerticalAction.triggered.connect(self.onSetVertical)

        self.uiSetHorizontalAction = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap(':/horizontal.png')), 'Horizontal', self)
        self.uiSetHorizontalAction.setShortcut('Ctrl+Shift+H')
        self.uiSetHorizontalAction.setStatusTip('Set the query page horizontally')
        self.uiSetHorizontalAction.triggered.connect(self.onSetHorizontal)

        # self.uiMonitorAction = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap(':/run.png')), 'Monitor', self)
        # self.uiMonitorAction.setShortcut('Ctrl+M')
        # self.uiMonitorAction.setStatusTip('Monitor the query result and plot it')
        # self.uiMonitorAction.triggered.connect(self.onMonitor)

        self.uiSaveAsBookmarkAction = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap(':/star.png')), '&Bookmark this query',
                                                    self)
        self.uiSaveAsBookmarkAction.setShortcut('Ctrl+B')
        self.uiSaveAsBookmarkAction.setStatusTip('Bookmark the current query for later access')
        self.uiSaveAsBookmarkAction.triggered.connect(self.onSaveAsBookmark)

        # Toolbar
        uiRunMenu = QtGui.QMenu()
        uiRunMenu.addAction(self.uiExplainAction)
        uiRunMenu.addAction(self.uiAnalyseAction)
        uiRunMenu.addAction(self.uiCSVExportAction)
        self.uiRunAction.setMenu(uiRunMenu)
        self.uiToolBar.addAction(self.uiRunAction)
        self.uiToolBar.addAction(self.uiStopAction)
        self.uiToolBar.addSeparator()
        self.uiToolBar.addAction(self.uiRewriteAction)
        self.uiToolBar.addSeparator()
        self.uiToolBar.addAction(self.uiSetHorizontalAction)
        self.uiToolBar.addAction(self.uiSetVerticalAction)
        self.uiToolBar.addSeparator()
        self.uiToolBar.addAction(self.uiSaveAsBookmarkAction)

        # self.uiToolBar.addAction(self.uiMonitorAction)


class QueryBook(QueryBookUI):
    """Main Window after a successful database connection
    """

    def __init__(self, database, icon):
        super(QueryBook, self).__init__()
        self.database = database
        self.setWindowTitle(self.database.name)
        self.setWindowIcon(icon)

        self.uiQueryBook.setTabsClosable(True)
        self.uiQueryBook.setMovable(True)
        self.uiQueryBook.setTabShape(QtGui.QTabWidget.Rounded)
        self.uiQueryBook.setElideMode(1)
        self.pageCount = 0
        self.newQueryPage()

        # Explorers
        self.setupObjectsExplorer()
        self.setupBookMarksExplorer()

        # Menubar
        self.setupMenuBar()

        # Signals
        self.uiQueryBook.tabCloseRequested.connect(self.onClosePage)

        #Window position and size
        self.settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope,
                                         'pgleon', 'pgleon', parent=self)
        self.settings.setFallbacksEnabled(False)  # File only, no fallback to registry or or.
        self.restoreGeometry(self.settings.value("geometry").toByteArray())
        self.restoreState(self.settings.value("windowState").toByteArray())

    def newQueryPage(self):
        """Add a new query page to the book"""
        name = "Query_%i" % self._pageCount()
        page = QueryPage(database=self.database, parent=self)
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

    # def onSaveBookMarks(self):
    # page = self.uiQueryBook.currentWidget()
    # query = page.uiQueryEditor.text()
    # dlg = SaveBookMarks(database=self.database, query=query)
    #     result = dlg.exec_()
    #     if result == QtGui.QDialog.Accepted:
    #         self.uiShowBookMarksMenu.clear()
    #         self.uiShowBookMarksMenu.initMenu()
    #         name = dlg.getName()
    #         index = self.uiQueryBook.currentIndex()
    #         self.setPageTitle(index, name)

    def setupObjectsExplorer(self):
        self.objectsExplorer = ObjectsExplorer(database=self.database, parent=self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.objectsExplorer)

    def setupBookMarksExplorer(self):
        self.bookmarksExplorer = BookMarksExplorer(database=self.database, parent=self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.bookmarksExplorer)

    def setupMenuBar(self):
        #Menubar
        self.uiFileMenu = self.uiMenuBar.addMenu('&File')
        self.uiExitAction = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap(':/exit.png')), '&Exit', self)
        self.uiExitAction.setShortcut('Ctrl+Q')
        self.uiExitAction.setStatusTip('Exit application')
        self.uiExitAction.triggered.connect(self.close)
        self.uiFileMenu.addAction(self.uiExitAction)

        self.uiNewAction = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap(':/plus.png')), '&New', self)
        self.uiNewAction.setShortcut('Ctrl+N')
        self.uiNewAction.setStatusTip('New query')
        self.uiNewAction.triggered.connect(self.newQueryPage)
        self.uiFileMenu.addAction(self.uiNewAction)

        self.uiWindowMenu = self.uiMenuBar.addMenu('&Window')
        self.uiToggleDockObjectExplorerAction = self.objectsExplorer.toggleViewAction()
        self.uiWindowMenu.addAction(self.uiToggleDockObjectExplorerAction)
        self.uiToggleDockBookmarkExplorerAction = self.bookmarksExplorer.toggleViewAction()
        self.uiWindowMenu.addAction(self.uiToggleDockBookmarkExplorerAction)

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        event.accept()


def main():
    app = QtGui.QApplication(sys.argv)
    ex = QueryBook()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()