#-*- coding:utf-8 -*-
from PyQt4 import QtGui

__author__ = 'lionel'

from ui.forms.bookmarksui import BookMarksUI
from src.conf import Query


class MainBookmarks(BookMarksUI):
    def __init__(self, *args, **kwargs):
        super(MainBookmarks, self).__init__(*args, **kwargs)
        self.setTitle("Bookmarks configuration")

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

        self.editMode(False)
        self.show()

    def setupModel(self):
        model = QtGui.QStandardItemModel(0, 6, self)
        for row, query in enumerate(Query.select()):
            id = QtGui.QStandardItem(str(query.id))
            connectionId = QtGui.QStandardItem(str(query.connection))
            section = QtGui.QStandardItem(query.section)
            name = QtGui.QStandardItem(query.name)
            description = QtGui.QStandardItem(query.description)
            queryText = QtGui.QStandardItem(query.query)
            rowValuesList = [id, connectionId, section, name, description, queryText]
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