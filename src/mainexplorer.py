#-*- coding:utf-8 -*-

from PyQt4 import QtGui
from ui.forms.explorerui import ExplorerUI
from src import db
__author__ = 'lionel'



class MainExplorer(ExplorerUI):

    def __init__(self, *args, **kwargs):
        self.icons = {
            'columns': QtGui.QIcon('icons/column.png'),
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
        self.view = self.uiExplorerTree
        self.model = QtGui.QStandardItemModel()
        self.setupExplorer()
        self.setupToolBar()

        #Signals
        self.uiExplorerTree.doubleClicked.connect(self.onDoubleClick)

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
        self.view.reset()
        self.view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Database'])
        self.view.setModel(self.model)
        self.view.setUniformRowHeights(True)
        self.view.setAnimated(True)
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # populate data
        parentSchema = None
        parentType = None
        for schema, type_, name, owner, oid in res:
            if schema != parentSchema: # On changing/first schema in the list
                schemaItem = QtGui.QStandardItem(self.icons['schema'], schema)
                parentSchema = schema #Set the schema name as the parent
                parentType = None #Reset the type
                self.model.appendRow(schemaItem)
            if type_ != parentType: #On changing/first type in the list
                parentType = type_ #Set the type as the parent type
                typeItem = QtGui.QStandardItem(self.icons[type_], type_)
                schemaItem.appendRow(typeItem)
            nameItem = QtGui.QStandardItem(self.icons[type_], name)
            # ownerItem = QtGui.QStandardItem(owner)
            # oidItem = QtGui.QStandardItem(oid)
            # typeItem.appendRow([nameItem, ownerItem, oidItem])
            typeItem.appendRow(nameItem)
            if type_ in ('tables', 'views', 'materialized views'):
                for colName in self.getColumnsName(schema, name):
                    colNameItem = QtGui.QStandardItem(self.icons['columns'], colName[0])
                    nameItem.appendRow(colNameItem)

    def getColumnsName(self, schema, table):
        query = """SELECT
        concat(f.attname, CASE WHEN p.contype = 'p' THEN '*' ELSE '' END, ' ('::varchar, pg_catalog.format_type(f.atttypid,f.atttypmod), ')'::varchar) AS name
        FROM pg_attribute f
        JOIN pg_class c ON c.oid = f.attrelid
        LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
        LEFT JOIN pg_constraint p ON p.conrelid = c.oid
        AND f.attnum = ANY (p.conkey)
        WHERE c.relkind IN ('r', 'v', 'm')
            AND n.nspname = '{0:s}'
            AND c.relname = '{1:s}'
            AND f.attnum > 0
        ORDER BY f.attnum""".format(schema, table)
        conn = self.database.newConnection()
        _, res, _ = db.execute(conn, query)
        conn.close()
        return res

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

    def onDoubleClick(self, index):
        print(index.sibling(index.row(), 0).data().toString())
        print(index.sibling(index.row(), 2).data())
        # row = index.row()
        # t = unicode(self.model.item(row, 0).text())
        # print(t)