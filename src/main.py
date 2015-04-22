# -*- coding:utf-8 -*-

import logging
import logging.config
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# handler = logging.StreamHandler()
# handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,  # this fixes the problem

    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default': {
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        }
    }
})

import sys
from PyQt4 import QtGui
from ui.forms.confui import MainUI
from src.conf import DBConfig, title, appIcon
from src.db import Database
from src.querybook import QueryBook

TEMPID = "-999"

class Main(MainUI):
    def __init__(self, title, appIcon):
        super(Main, self).__init__()
        self.setWindowTitle(title)
        self.icon = QtGui.QIcon(QtGui.QPixmap(appIcon))
        self.setWindowIcon(self.icon)
        self.queryBookList = list()
        self.initMenu()

        # All others stuffs
        self.model = self.setupModel()
        self.mapper = self.setupMapper(self.model)
        self.uiConnList.setModel(self.model)
        self.uiConnList.setModelColumn(1)  #Show the name of the connection, stored in the second column of the model
        self.selection = self.uiConnList.selectionModel()

        #Signals
        self.selection.currentChanged.connect(self.onItemChanged)
        self.uiEditButton.clicked.connect(self.onEdit)
        self.uiAppendButton.clicked.connect(self.onAdd)
        self.uiDeleteButton.clicked.connect(self.onDelete)
        self.uiSaveButton.clicked.connect(self.onSave)
        self.uiCancelButton.clicked.connect(self.onCancel)
        self.uiTestButton.clicked.connect(self.onTest)
        self.uiOpenButton.clicked.connect(self.onOpen)
        self.uiConnList.doubleClicked.connect(self.onOpen)

        self.editMode(False)
        self.show()

    def setupModel(self):
        model = QtGui.QStandardItemModel(0, 7, self)
        for row, conn in enumerate(DBConfig.select()):
            id = QtGui.QStandardItem(str(conn.id))
            name = QtGui.QStandardItem(conn.name)
            host = QtGui.QStandardItem(conn.host)
            port = QtGui.QStandardItem(conn.port)
            database = QtGui.QStandardItem(conn.database)
            user = QtGui.QStandardItem(conn.user)
            password = QtGui.QStandardItem(conn.password)
            rowValuesList = [id, name, host, port, database, user, password]
            for column in range(len(rowValuesList)):
                model.setItem(row, column, rowValuesList[column])
        return model

    def setupMapper(self, model):
        mapper = QtGui.QDataWidgetMapper(self)
        mapper.setModel(model)
        # 0 == connection.id
        mapper.addMapping(self.uiNameEdit, 1)
        mapper.addMapping(self.uiHostEdit, 2)
        mapper.addMapping(self.uiPortEdit, 3)
        mapper.addMapping(self.uiDatabaseEdit, 4)
        mapper.addMapping(self.uiUserEdit, 5)
        mapper.addMapping(self.uiPasswordEdit, 6)
        return mapper

    def initMenu(self):
        exit_action = QtGui.QAction(QtGui.QIcon('icons/exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QtGui.qApp.quit)
        file_menu = self.menu_bar.addMenu('&File')
        file_menu.addAction(exit_action)

    def onItemChanged(self, index):
        """When the user select/change a item in the left list of connections"""
        self.mapper.setCurrentIndex(index.row())

    def onAdd(self):
        """Add a new connection by presenting the left list with a temp item and
            the rights fields with default values"""
        self.editMode(True)
        row = self.model.rowCount()  # Take the last row in the model
        id = QtGui.QStandardItem(TEMPID)
        name = QtGui.QStandardItem("MyConnection")
        host = QtGui.QStandardItem("localhost")
        port = QtGui.QStandardItem("5432")
        database = QtGui.QStandardItem("postgres")
        user = QtGui.QStandardItem("postgres")
        password = QtGui.QStandardItem("")
        rowValuesList = [id, name, host, port, database, user, password]
        for column in range(len(rowValuesList)):
            self.model.setItem(row, column, rowValuesList[column])
        index = self.model.indexFromItem(name)
        self.selection.clear()
        self.selection.select(index, QtGui.QItemSelectionModel.Select)
        self.uiConnList.setCurrentIndex(index)
        self.onItemChanged(index)

    def onDelete(self):
        """Delete a connection"""
        index = self.uiConnList.currentIndex()
        idItem = self.model.item(index.row(), 0)
        id = int(idItem.text())
        query = DBConfig.delete().where(DBConfig.id == id)
        query.execute()
        row = index.row()
        self.removeRow(row)
        self.enabledEditButton()

    def onCancel(self):
        index = self.uiConnList.currentIndex()
        idItem = self.model.item(index.row(), 0)
        row = index.row()
        if idItem.text() == TEMPID:
            self.removeRow(row)
        else:
            [self.model.setItem(row, col, self.editedRowItems[col]) for col in range(len(self.editedRowItems))]
            self.selection.select(index, QtGui.QItemSelectionModel.Select)
            self.uiConnList.setCurrentIndex(index)
        self.editMode(False)

    def onEdit(self):
        """Edit a previously created connection"""
        index = self.uiConnList.currentIndex()
        self.editedRowItems = [self.model.item(index.row(), col).clone() for col in range(self.model.columnCount())]
        self.editMode(True)

    def onSave(self):
        index = self.uiConnList.currentIndex()
        row = index.row()
        id, name, host, port, database, user, password = self.rowData(row)
        if id == TEMPID:  # we are in append mode, then we create a new connection
            query = DBConfig.create(name=name, host=host, port=port,
                                    database=database, user=user,
                                    password=password)
            query.save()
            self.model.item(index.row(), 0).setText(str(query.id))
        else:  # we are in edit mode
            query = DBConfig.update(name=name, host=host, port=port,
                                    database=database, user=user,
                                    password=password).where(DBConfig.id == id)
            query.execute()
        self.editMode(False)

    def onTest(self):
        database = self.openDatabase()
        try:
            connection = database.newConnection()
            connection.close()
            QtGui.QMessageBox.information(self, "Success", "Successful connection", QtGui.QMessageBox.Ok)
        except Exception, error:
            QtGui.QMessageBox.critical(self, "Error", str(error), QtGui.QMessageBox.Ok)

    def onOpen(self):
        database = self.openDatabase()
        try:
            connection = database.newConnection()
            connection.close()
            queryBook = QueryBook(database=database, icon=self.icon)
            self.queryBookList.append(queryBook)
            queryBook.show()
        except Exception, error:
            QtGui.QMessageBox.critical(self, "Error", str(error), QtGui.QMessageBox.Ok)

    def openDatabase(self):
        """Create an instance of the current selected database"""
        index = self.uiConnList.currentIndex()
        row = index.row()
        id, name, host, port, database, user, password = self.rowData(row)
        database = Database(id=id,
                            name=name,
                            host=host,
                            port=port,
                            database=database,
                            user=user,
                            password=password)
        return database

    def removeRow(self, row):
        self.model.removeRows(row, 1)
        if self.model.rowCount() == 0:
            self.uiNameEdit.clear()
            self.uiHostEdit.clear()
            self.uiPortEdit.clear()
            self.uiDatabaseEdit.clear()
            self.uiUserEdit.clear()
            self.uiPasswordEdit.clear()

    def rowData(self, row):
        """Returns datas contained in the model at a specified row"""
        #We use the mapper to retrieve datas entered in the widgets
        id = unicode(self.model.item(row, 0).text())
        name = unicode(self.model.item(row, 1).text())
        host = unicode(self.model.item(row, 2).text())
        port = unicode(self.model.item(row, 3).text())
        database = unicode(self.model.item(row, 4).text())
        user = unicode(self.model.item(row, 5).text())
        password = unicode(self.model.item(row, 6).text())
        return [id, name, host, port, database, user, password]

    def editMode(self, mode=True):
        """Switch buttons when in edit mode or not"""
        self.uiConnList.setEnabled(not mode)
        self.uiEditButton.setEnabled(not mode)
        self.uiAppendButton.setEnabled(not mode)
        self.uiDeleteButton.setEnabled(not mode)
        self.uiSaveButton.setEnabled(mode)
        self.uiCancelButton.setEnabled(mode)
        self.uiTestButton.setEnabled(mode)
        self.uiOpenButton.setEnabled(not mode)
        self.uiNameEdit.setEnabled(mode)
        self.uiHostEdit.setEnabled(mode)
        self.uiPortEdit.setEnabled(mode)
        self.uiDatabaseEdit.setEnabled(mode)
        self.uiUserEdit.setEnabled(mode)
        self.uiPasswordEdit.setEnabled(mode)
        self.enabledEditButton()

    def enabledEditButton(self):
        """Test if the edit button can be enabled"""
        if self.model.rowCount() == 0:
            self.uiEditButton.setEnabled(False)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = Main(title=title, appIcon=appIcon)
    ex.show()
    logger.info("%s started"%title)
    sys.exit(app.exec_())
