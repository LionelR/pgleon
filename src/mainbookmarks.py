#-*- coding:utf-8 -*-
from PyQt4 import QtGui

__author__ = 'lionel'

from PyQt4 import QtCore
from functools import partial
from src.conf import Query, GlobalQuery, Section
from ui.forms.bookmarksui import EditBookMarksUI, SaveBookMarksUI


GLOBALID = "-999"


class SaveBookMarks(SaveBookMarksUI):
    def __init__(self, *args, **kwargs):
        self.connection = kwargs.pop('connection')
        self.query = kwargs.pop('query')
        super(SaveBookMarks, self).__init__(*args, **kwargs)
        self.setWindowTitle("Save Bookmark")

        #Models
        self.sectionModel = self.setupSectionModel()
        self.uiSectionOldCombo.setModel(self.sectionModel)
        self.uiSectionOldCombo.setModelColumn(2)
        self.queryModel = self.setupQueryModel()
        self.uiNameOldCombo.setModel(self.queryModel)
        self.uiNameOldCombo.setModelColumn(2)
        self.queryMapper = self.setupQueryMapper(self.queryModel)

        #Signals
        self.uiNameOldCombo.currentIndexChanged[int].connect(self.onItemNameChanged)
        self.uiSectionOldRadionBtn.toggled.connect(self.onSectionToggle)
        self.uiSectionNewRadionBtn.toggled.connect(self.onSectionToggle)
        self.uiNameOldRadioBtn.toggled.connect(self.onNameToggle)
        self.uiNameNewRadioBtn.toggled.connect(self.onNameToggle)

        #Defaults states
        self.uiSectionOldRadionBtn.setChecked(True)
        self.uiNameNewRadioBtn.setChecked(True)

    def setupSectionModel(self):
        model = QtGui.QStandardItemModel(0, 4, self)
        #we add the "global" section first, related to the GlobalQuery
        id = QtGui.QStandardItem(GLOBALID)
        connection_id = QtGui.QStandardItem(GLOBALID)
        name = QtGui.QStandardItem("Global")
        rowValuesList = [id, connection_id, name]
        for column in range(len(rowValuesList)):
            model.setItem(0, column, rowValuesList[column])

        #then we add the specific sections for this connection
        for row, section in enumerate(Section.select()):
            id = QtGui.QStandardItem(str(section.id))
            connection_id = QtGui.QStandardItem(section.connection)
            name = QtGui.QStandardItem(section.name)
            rowValuesList = [id, connection_id, name]
            for column in range(len(rowValuesList)):
                model.setItem(row + 1, column, rowValuesList[column])
        return model

    def setupQueryModel(self):
        model = QtGui.QStandardItemModel(0, 5, self)
        ngrows = 0
        #Globals queries
        for row, gquery in enumerate(GlobalQuery.select()):
            id = QtGui.QStandardItem(str(gquery.id))
            section_id = QtGui.QStandardItem(GLOBALID)
            name = QtGui.QStandardItem(gquery.name)
            description = QtGui.QStandardItem(gquery.description)
            query = QtGui.QStandardItem(gquery.query)
            rowValuesList = [id, section_id, name, description, query]
            for column in range(len(rowValuesList)):
                model.setItem(row, column, rowValuesList[column])
            ngrows += 1
        #Specific sections queries
        for row, squery in enumerate(Query.select()):
            id = QtGui.QStandardItem(str(squery.id))
            section_id = QtGui.QStandardItem(squery.section)
            name = QtGui.QStandardItem(squery.name)
            description = QtGui.QStandardItem(squery.description)
            query = QtGui.QStandardItem(squery.query)
            rowValuesList = [id, section_id, name, description, query]
            for column in range(len(rowValuesList)):
                model.setItem(row+ngrows, column, rowValuesList[column])
        return model

    def setupQueryMapper(self, model):
        mapper = QtGui.QDataWidgetMapper(self)
        mapper.setModel(model)
        # 0 == query.id ...
        mapper.addMapping(self.uiDescriptionText, 3)
        return mapper

    def onSectionToggle(self):
        isOld = self.uiSectionOldRadionBtn.isChecked()
        self.uiSectionOldCombo.setEnabled(isOld)
        self.uiSectionNewText.setEnabled(not isOld)

    def onNameToggle(self):
        isOld = self.uiNameOldRadioBtn.isChecked()
        self.uiNameOldCombo.setEnabled(isOld)
        self.uiNameNewText.setEnabled(not isOld)

    def onItemNameChanged(self, index):
        """When the user select/change a item in the left list of connections"""
        self.queryMapper.setCurrentIndex(index)


class EditBookMarks(EditBookMarksUI):
    def __init__(self, *args, **kwargs):
        super(EditBookMarks, self).__init__(*args, **kwargs)


class ShowBookMarks(QtGui.QMenu):
    def __init__(self, *args, **kwargs):
        self.database = kwargs.pop('database')
        self.parent = kwargs.pop('parent')
        super(ShowBookMarks, self).__init__(*args, **kwargs)
        self.initMenu()

    def initMenu(self):
        #Global queries
        globalMenu = self.addMenu("Global")
        for globalQuery in GlobalQuery.select():
            action = QtGui.QAction(QtCore.QString.fromUtf8(globalQuery.name), self)
            action.setStatusTip(globalQuery.description)
            action.triggered.connect(partial(self.addPage, globalQuery.query))
            globalMenu.addAction(action)
        self.addSeparator()

        #Sections based specialized connection queries
        for section in Section.select().where(Section.connection == self.database.id):
            sectionMenu = self.addMenu(section.name)
            for query in Query.select().where(Query.section == section.id):
                action = QtGui.QAction(QtCore.QString.fromUtf8(query.name), self)
                action.setStatusTip(query.description)
                action.triggered.connect(partial(self.addPage, query.query))
                sectionMenu.addAction(action)


    def addPage(self, query):
        page = self.parent.newQueryPage()
        page.uiQueryEditor.setText(query)