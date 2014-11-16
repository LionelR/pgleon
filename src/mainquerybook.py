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
import resources_rc


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
    resultSignal = QtCore.pyqtSignal([object, object, object, object])

    def __init__(self, *args, **kwargs):
        self.connection = kwargs.pop("connection")
        self.parent = kwargs.pop("parent")
        self.name = ""
        self.queryThread = None
        super(QueryPage, self).__init__(*args, **kwargs)

        # Query result tableView
        fontSize = self.uiQueryResult.verticalHeader().font().pointSize()
        self.uiQueryResult.verticalHeader().setDefaultSectionSize(fontSize + 2 * 3)
        self.uiQueryResult.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.uiQueryResult.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        # allow to copy results
        copyAction = QtGui.QAction("Copy data", self)
        copyAction.setShortcuts(QtGui.QKeySequence.Copy)
        copyAction.triggered.connect(self.onCopySelectedResults)
        self.addAction(copyAction)

        #Timer
        self.time = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.onTimeOut)

        #Toolbar
        self.setupToolBar()

    def currentConnection(self):
        return self.connection

    def currentName(self):
        return self.name

    def setCurrentName(self, name):
        self.name = name
        index = self.parent.indexOf(self)
        self.parent.setPageTitle(index, name)

    def execute(self, prefix="", to_csv=False):
        query = unicode(self.uiQueryEditor.text())
        if query.strip() == "":
            return
        query = prefix + unicode(query)

        # Run the query in a thread
        self.queryThread = GenericThread(self._execute, query, to_csv)
        self.resultSignal.connect(self._setResult)
        self.queryThread.start()

    def _execute(self, query, to_csv=False):
        """Internal function to be called by the execute function in a thread.
        The results will be passed to the _setResult function"""
        self._preProcessing()  #The thread is started
        headers, res, status = db.execute(self.connection, query)
        self.resultSignal.emit(headers, res, status, to_csv)

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
        self.timer.start(1)

    def _postProcessing(self):
        """Apply operations after running query"""
        self._checkRunning()
        self.timer.stop()

    def _setResult(self, headers, res, status, to_csv):

        def CSVExport(headers, res):
            import csv
            with open('/tmp/somefile.csv', 'w') as f:
                writer = csv.writer(f, delimiter=',')
                writer.writerow(headers)
                for row in res:
                    writer.writerow(row)

        if isinstance(res, db.DBError):
            self.uiQueryMsg.setPlainText(QtCore.QString.fromUtf8(res.get_msg()))
            self.uiTab.setCurrentWidget(self.uiQueryMsg)
            self.setStatus('')
        else:
            if to_csv is False:
                self.model = QTableModel(res, headers, self)
                self.uiQueryResult.setModel(self.model)
                self.uiQueryResult.resizeColumnsToContents()
                # self.uiQueryResult.resizeRowsToContents() #Very slow
                self.uiTab.setCurrentWidget(self.uiQueryResult)
                self.setStatus(status)
                self.uiQueryMsg.clear()
            else:
                CSVExport(headers, res)
        self._postProcessing()


    def onRunQuery(self):
        self.execute()

    def onExplainQuery(self):
        self.execute(prefix=u"EXPLAIN ")

    def onAnalyseQuery(self):
        self.execute(prefix=u"EXPLAIN ANALYSE ")

    def onCancelQuery(self):
        print("Canceling query")
        self.connection.cancel()
        print("Query canceled")

    def onRewriteQuery(self):
        query = unicode(self.uiQueryEditor.text())
        formattedQuery = sqlparse.format(query, keyword_case="upper", reindent=True, indent_width=4, indent_tabs=False)
        self.uiQueryEditor.setText(formattedQuery)

    def onSetVertical(self):
        self.uiVSplitter.setOrientation(QtCore.Qt.Vertical)

    def onSetHorizontal(self):
        self.uiVSplitter.setOrientation(QtCore.Qt.Horizontal)

    def onTimeOut(self):
        self.time += 1
        self.uiTimerLabel.setText(str(self.time))

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
            if currentIdx.row() != previousIdx.row(): # We are on another row in the table : implies new line in the clipboard
                selectedText.append('\n')
            else: # else we are on the same line, new index = new column in the table = tab separator
                selectedText.append('\t')
            text = model.data(currentIdx, QtCore.Qt.DisplayRole).toString()
            selectedText.append(unicode(text))
            previousIdx = currentIdx
        selectedText = "".join(selectedText)
        QtGui.QApplication.clipboard().setText(selectedText)

    def onCSVExport(self):
        query = unicode(self.uiQueryEditor.text())
        if query.strip() == "":
            return
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Export data to CSV file :', selectedFilter='*.csv')
        if filename:
            self.execute(to_csv=filename)

    def setupToolBar(self):
        self.uiRunAction = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap(':/run.png')), '&Run', self)
        self.uiRunAction.setShortcut('Ctrl+R')
        self.uiRunAction.setStatusTip('Run query')
        self.uiRunAction.triggered.connect(self.onRunQuery)

        self.uiCSVExportAction = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap(':/run.png')), 'Export as CSV', self)
        self.uiCSVExportAction.setShortcut('Ctrl+Shift+R')
        self.uiCSVExportAction.setStatusTip('Export query results to CSV file')
        self.uiCSVExportAction.setIconVisibleInMenu(True)
        self.uiCSVExportAction.triggered.connect(self.onCSVExport)

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

        #Toolbar
        uiRunMenu = QtGui.QMenu()
        # uiRunMenu.addAction(self.uiRunAction)
        uiRunMenu.addAction(self.uiExplainAction)
        uiRunMenu.addAction(self.uiAnalyseAction)
        uiRunMenu.addAction(self.uiCSVExportAction)
        self.uiRunAction.setMenu(uiRunMenu)
        self.uiToolBar.addAction(self.uiRunAction)
        # self.uiToolBar.addAction(self.uiExplainAction)
        # self.uiToolBar.addAction(self.uiAnalyseAction)
        # self.uiToolBar.addAction(self.uiCSVExportAction)
        self.uiToolBar.addAction(self.uiStopAction)
        self.uiToolBar.addSeparator()
        self.uiToolBar.addAction(self.uiRewriteAction)
        self.uiToolBar.addSeparator()
        self.uiToolBar.addAction(self.uiSetHorizontalAction)
        self.uiToolBar.addAction(self.uiSetVerticalAction)


class MainQueryBook(QueryBookUI):
    def __init__(self, database, icon):
        super(MainQueryBook, self).__init__()
        self.database = database
        self.setWindowTitle(self.database.name)
        self.setWindowIcon(icon)

        self.uiQueryBook.setTabsClosable(True)
        self.uiQueryBook.setMovable(True)
        self.uiQueryBook.setTabShape(QtGui.QTabWidget.Rounded)
        self.uiQueryBook.setElideMode(1)
        self.pageCount = 0
        self.newQueryPage()

        #ExplorerTree
        self.setupExplorerTree()

        #Menubar
        self.setupMenuBar()

        #Signals
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

    def onSaveBookMarks(self):
        page = self.uiQueryBook.currentWidget()
        query = page.uiQueryEditor.text()
        dlg = SaveBookMarks(database=self.database, query=query)
        result = dlg.exec_()
        if result == QtGui.QDialog.Accepted:
            self.uiShowBookMarksMenu.clear()
            self.uiShowBookMarksMenu.initMenu()
            name = dlg.getName()
            index = self.uiQueryBook.currentIndex()
            self.setPageTitle(index, name)

    def setupExplorerTree(self):
        self.Explorer = MainExplorer(database=self.database, parent=self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.Explorer)

    def setupMenuBar(self):
        #Menubar
        self.uiFileMenu = self.uiMenuBar.addMenu('&File')
        self.uiExitAction = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap(':/exit.png')), '&Exit', self)
        self.uiExitAction.setShortcut('Ctrl+Q')
        self.uiExitAction.setStatusTip('Exit application')
        self.uiExitAction.triggered.connect(self.close)
        self.uiFileMenu.addAction(self.uiExitAction)

        self.uiQueryMenu = self.uiMenuBar.addMenu('&Query')
        self.uiNewAction = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap(':/plus.png')), '&New', self)
        self.uiNewAction.setShortcut('Ctrl+N')
        self.uiNewAction.setStatusTip('New query')
        self.uiNewAction.triggered.connect(self.newQueryPage)
        self.uiQueryMenu.addAction(self.uiNewAction)
        self.uiSaveBookMarksAction = QtGui.QAction(QtGui.QIcon(QtGui.QPixmap(':/star.png')), '&Save', self)
        self.uiSaveBookMarksAction.setShortcut('Ctrl+D')
        self.uiSaveBookMarksAction.setStatusTip('Save as bookmark')
        self.uiSaveBookMarksAction.triggered.connect(self.onSaveBookMarks)
        self.uiQueryMenu.addAction(self.uiSaveBookMarksAction)
        # self.uiShowBookMarksButton = QtGui.QToolButton()
        # self.uiShowBookMarksButton.setIcon(QtGui.QIcon('icons/bookmarks.png'))
        # self.uiShowBookMarksButton.setStatusTip('Show all bookmarks')
        # self.uiShowBookMarksButton.setPopupMode(QtGui.QToolButton.InstantPopup)
        # self.uiShowBookMarksButton.setMenu(self.uiShowBookMarksMenu)
        self.uiShowBookMarksMenu = ShowBookMarks('Bookmarks', database=self.database, parent=self)
        self.uiQueryMenu.addMenu(self.uiShowBookMarksMenu)

        self.uiWindowMenu = self.uiMenuBar.addMenu('&Window')
        self.uiToggleDockExplorerTreeAction = self.Explorer.toggleViewAction()
        self.uiWindowMenu.addAction(self.uiToggleDockExplorerTreeAction)

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