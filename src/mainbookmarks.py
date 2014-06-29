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
        self.database = kwargs.pop('database')
        self.query = kwargs.pop('query')
        super(SaveBookMarks, self).__init__(*args, **kwargs)
        self.setWindowTitle("Save Bookmark")
        self.name = ""

        #Models
        self.setupSectionModel()
        self.setupQueryModel()

        #Signals
        self.uiNameOldCombo.currentIndexChanged[int].connect(self.onItemNameChanged)
        self.uiSectionOldCombo.currentIndexChanged[int].connect(self.onItemSectionChanged)
        self.uiSectionOldRadionBtn.toggled.connect(self.onSectionToggle)
        self.uiSectionNewRadionBtn.toggled.connect(self.onSectionToggle)
        self.uiNameOldRadioBtn.toggled.connect(self.onNameToggle)
        self.uiNameNewRadioBtn.toggled.connect(self.onNameToggle)
        self.uiSaveBtn.clicked.connect(self.onSave)
        self.uiCancelBtn.clicked.connect(self.reject)

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
        for row, section in enumerate(Section.select().where(Section.connection == self.database.id)):
            id = QtGui.QStandardItem(str(section.id))
            connection_id = QtGui.QStandardItem(section.connection.id)
            name = QtGui.QStandardItem(section.name)
            rowValuesList = [id, connection_id, name]
            for column in range(len(rowValuesList)):
                model.setItem(row + 1, column, rowValuesList[column])
        self.sectionModel = model
        self.uiSectionOldCombo.setModel(self.sectionModel)
        self.uiSectionOldCombo.setModelColumn(2)

    def setupQueryModel(self):
        model = QtGui.QStandardItemModel(0, 5, self)
        row = self.uiSectionOldCombo.currentIndex()
        section_id = self.sectionModel.item(row, 0).text()
        print(section_id)
        ngrows = 0
        #Globals queries
        if section_id == GLOBALID:
            for row, gquery in enumerate(GlobalQuery.select()):
                id = QtGui.QStandardItem(str(gquery.id))
                section = QtGui.QStandardItem(GLOBALID)
                name = QtGui.QStandardItem(gquery.name)
                description = QtGui.QStandardItem(gquery.description)
                query = QtGui.QStandardItem(gquery.query)
                rowValuesList = [id, section, name, description, query]
                for column in range(len(rowValuesList)):
                    model.setItem(row, column, rowValuesList[column])
                ngrows += 1
        #Specific sections queries
        else:
            for row, squery in enumerate(Query.select().where(Query.section == section_id)):
                id = QtGui.QStandardItem(str(squery.id))
                section = QtGui.QStandardItem(squery.section.id)  #the same we set previously? yes!
                name = QtGui.QStandardItem(squery.name)
                description = QtGui.QStandardItem(squery.description)
                query = QtGui.QStandardItem(squery.query)
                rowValuesList = [id, section, name, description, query]
                for column in range(len(rowValuesList)):
                    model.setItem(row + ngrows, column, rowValuesList[column])
        self.queryModel = model
        self.uiNameOldCombo.setModel(self.queryModel)
        self.uiNameOldCombo.setModelColumn(2)
        self.queryMapper = self.setupQueryMapper(self.queryModel)
        self.onNameToggle()

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
        if isOld:
            index = self.uiNameOldCombo.currentIndex()
            self.onItemNameChanged(index)
        else:
            self.uiNameNewText.clear()
            self.uiDescriptionText.clear()

    def onItemSectionChanged(self, index):
        """When the user select/change a item in the Section combo"""
        #Update of the query model based on the selected Section
        self.setupQueryModel()

    def onItemNameChanged(self, index):
        """When the user select/change a item in the Name combo"""
        self.queryMapper.setCurrentIndex(index)

    def onSave(self):
        #Some tests
        if self.uiSectionNewRadionBtn.isChecked() and self.uiSectionNewText.text().isEmpty():
            self.uiWarningLabel.setText("<font color='red'>Enter a section title</font>")
            return
        if self.uiNameNewRadioBtn.isChecked() and self.uiNameNewText.text().isEmpty():
            self.uiWarningLabel.setText("<font color='red'>Enter a query name</font>")
            return

        #First looking at the section part
        if self.uiSectionOldRadionBtn.isChecked():
            #We use a existing section
            row = self.uiSectionOldCombo.currentIndex()
            section_id = self.sectionModel.item(row, 0).text()
        else:
            #We need to create a new section first
            section_name = self.uiSectionNewText.text()
            section = Section(connection=self.database.id, name=section_name)
            section.save()
            section_id = section.id

        #Secondly, processing the query part
        if self.uiNameOldRadioBtn.isChecked():
            #We're going to update a existing query
            row = self.uiNameOldCombo.currentIndex()
            query_id = self.queryModel.item(row, 0).text()
            description = self.uiDescriptionText.text()
            name = self.uiNameOldCombo.currentText()
            if section_id == GLOBALID:
                #Update a global query
                query = GlobalQuery.update(name=name,
                                           description=description,
                                           query=self.query).where(GlobalQuery.id == query_id)
                query.execute()
                print("UPDATE GLOBAL")
            else:
                #Update a section specific query
                query = Query.update(name=name,
                                     section=section_id,
                                     description=description,
                                     query=self.query).where(GlobalQuery.id == query_id)
                query.execute()
                print("UPDATE LOCALE")
            self.name = name
        else:
            #We create a new query
            description = self.uiDescriptionText.text()
            name = self.uiNameNewText.text()
            if section_id == GLOBALID:
                #Create a global query
                query = GlobalQuery(name=name,
                                    description=description,
                                    query=self.query)
                query.save()
                print("CREATE GLOBALE")
            else:
                #Create a section specific query
                query = Query(name=name,
                              section=section_id,
                              description=description,
                              query=self.query)
                query.save()
                print("CREATE LOCALE")
            self.name = name
        self.accept()

    def getName(self):
        return self.name


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
            action.triggered.connect(partial(self.addPage, globalQuery.query, globalQuery.name))
            globalMenu.addAction(action)
        self.addSeparator()

        #Sections based specialized connection queries
        for section in Section.select().where(Section.connection == self.database.id):
            sectionMenu = self.addMenu(section.name)
            for query in Query.select().where(Query.section == section.id):
                action = QtGui.QAction(QtCore.QString.fromUtf8(query.name), self)
                action.setStatusTip(query.description)
                action.triggered.connect(partial(self.addPage, query.query, query.name))
                sectionMenu.addAction(action)


    def addPage(self, query, name):
        page = self.parent.newQueryPage()
        page.uiQueryEditor.setText(query)
        page.setCurrentName(name)