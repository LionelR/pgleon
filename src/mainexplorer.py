#-*- coding:utf-8 -*-

from PyQt4 import QtGui
from ui.forms.explorerui import ExplorerUI
from src import db
__author__ = 'lionel'



class MainExplorer(ExplorerUI):

    def __init__(self, *args, **kwargs):
        self.icons = {
            'tables': QtGui.QIcon('icons/table.png'),
            'views': QtGui.QIcon('icons/view.png'),
            'indexes': QtGui.QIcon('icons/index.png'),
            'sequences': QtGui.QIcon('icons/sequence.png'),
            'materialized views': QtGui.QIcon('icons/materialized_view.png'),
            'foreign tables': QtGui.QIcon('icons/foreign_table.png'),
            'specials': QtGui.QIcon('icons/view.png'),
            'schema': QtGui.QIcon('icons/schema.png'),
            }
        self.database = kwargs.pop("database")
        super(MainExplorer, self).__init__(*args, **kwargs)
        self.setupExplorer()
        self.setupToolBar()

    def setupExplorer(self):
        query = """SELECT
            n.nspname as "schema",
            CASE c.relkind
                WHEN 'r' THEN 'tables'
                WHEN 'v' THEN 'views'
                WHEN 'm' THEN 'materialized views'
                WHEN 'i' THEN 'indexes'
                WHEN 'S' THEN 'sequences'
                WHEN 's' THEN 'specials'
                WHEN 'f' THEN 'foreign tables'
            END as "type",
            c.relname as "name",
            pg_catalog.pg_get_userbyid(c.relowner) as "owner",
            c.oid
        FROM pg_catalog.pg_class c
        LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind IN ('r','v','m','S','f','')
            AND n.nspname <> 'pg_catalog'
            AND n.nspname <> 'information_schema'
            AND n.nspname !~ '^pg_toast'
        ORDER BY 1,2,3"""

        conn = self.database.newConnection()
        headers, res, status = db.execute(conn, query)
        conn.close()
        view = self.uiExplorerTree
        view.reset()
        view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['Database'])
        view.setModel(model)
        view.setUniformRowHeights(True)
        view.setAnimated(True)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # populate data
        parentSchema = None
        parentType = None
        for schema, type_, name, owner, oid in res:
            if schema != parentSchema: # On changing/first schema in the list
                schemaItem = QtGui.QStandardItem(self.icons['schema'], schema)
                parentSchema = schema #Set the schema name as the parent
                parentType = None #Reset the type
                model.appendRow(schemaItem)
            if type_ != parentType: #On changing/first type in the list
                parentType = type_ #Set the type as the parent type
                typeItem = QtGui.QStandardItem(self.icons[type_], type_)
                schemaItem.appendRow(typeItem)
            nameItem = QtGui.QStandardItem(self.icons[type_], name)
            ownerItem = QtGui.QStandardItem(owner)
            oidItem = QtGui.QStandardItem(oid)
            typeItem.appendRow([nameItem, ownerItem, oidItem])

    def setupToolBar(self):
        self.uiRefreshAction.triggered.connect(self.onRefresh)
        self.uiCollapseAction.triggered.connect(self.onCollapse)
        self.uiExpandAction.triggered.connect(self.onExpand)

    def onRefresh(self):
        self.setupExplorer()

    def onCollapse(self):
        self.uiExplorerTree.collapseAll()

    def onExpand(self):
        self.uiExplorerTree.expandAll()