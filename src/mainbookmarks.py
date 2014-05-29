#-*- coding:utf-8 -*-
from PyQt4 import QtGui

__author__ = 'lionel'

from PyQt4 import QtCore
# from ui.forms.bookmarksui import BookMarksUI
from functools import partial
from src.conf import Query, GlobalQuery, Section


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
        for section in Section.select().where(Section.connection==self.database.id):
            sectionMenu = self.addMenu(section.name)
            for query in Query.select().where(Query.section==section.id):
                action = QtGui.QAction(QtCore.QString.fromUtf8(query.name), self)
                action.setStatusTip(query.description)
                action.triggered.connect(partial(self.addPage, query.query))
                sectionMenu.addAction(action)


    def addPage(self, query):
        page = self.parent.newQueryPage()
        page.uiQueryEditor.setText(query)