# -*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore
from ui.forms.explorerui import ExplorerUI
from src import db
import explorermodel as em
import string
from functools import partial

__author__ = 'lionel'


class MainExplorer(ExplorerUI):
    def __init__(self, *args, **kwargs):
        self.icons = {
            'COLUMN': QtGui.QIcon(QtGui.QPixmap(':/column.png')),
            'TABLE': QtGui.QIcon(QtGui.QPixmap(':/table.png')),
            'VIEW': QtGui.QIcon(QtGui.QPixmap(':/view.png')),
            'INDEX': QtGui.QIcon(QtGui.QPixmap(':/index.png')),
            'SEQUENCE': QtGui.QIcon(QtGui.QPixmap(':/sequence.png')),
            'MATERIALIZED VIEW': QtGui.QIcon(QtGui.QPixmap(':/materialized_view.png')),
            'FOREIGN TABLE': QtGui.QIcon(QtGui.QPixmap(':/foreign_table.png')),
            'SPECIAL': QtGui.QIcon(QtGui.QPixmap(':/view.png')),
            'SCHEMA': QtGui.QIcon(QtGui.QPixmap(':/schema.png')),
            'DATABASE': QtGui.QIcon(QtGui.QPixmap(':/database.png')),
            'FUNCTION': QtGui.QIcon(QtGui.QPixmap(':/function.png')),
        }

        self.database = kwargs.pop("database")
        self.parent = kwargs.pop("parent")
        super(MainExplorer, self).__init__(*args, **kwargs)
        self.rootNode = em.Node(self.database, parent=None, icon=self.icons['DATABASE'])

        self.model = em.ExplorerModel(self.rootNode, self.parent)
        self.view = self.uiExplorerTree
        self.view.setModel(self.model)

        self.setupExplorer()
        self.setupToolBar()

        #Signals
        self.view.doubleClicked.connect(self.onDoubleClick)
        self.view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.onContextMenu)


    def setupExplorer(self):
        self.view.reset()
        self.model.removeRows(0, self.model.rowCount(QtCore.QModelIndex()))

        query = """SELECT * FROM ((
            SELECT
                n.nspname as "schema",
                CASE c.relkind
                    WHEN 'r' THEN 'TABLE'
                    WHEN 'v' THEN 'VIEW'
                    WHEN 'm' THEN 'MATERIALIZED VIEW'
                    WHEN 'i' THEN 'INDEX'
                    WHEN 'S' THEN 'SEQUENCE'
                    WHEN 's' THEN 'SPECIAL'
                    WHEN 'f' THEN 'FOREIGN TABLE'
                END as "type",
                c.relname as "name",
                c.oid
            FROM pg_catalog.pg_class c
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind IN ('r','v','m','S','f','')
                --AND n.nspname <> 'pg_catalog'
                --AND n.nspname <> 'information_schema'
                --AND n.nspname !~ '^pg_toast'
        )
        UNION (
            SELECT
                n.nspname as schema,
                'FUNCTION'::varchar as "type",
                p.proname AS "name",
                p.oid
                --p.proargnames as arg_names,
                --t.typname as return_type,
                --d.description
                --pg_get_functiondef(p.oid) as definition
            FROM pg_catalog.pg_proc p
            --INNER JOIN pg_catalog.pg_type t ON (p.prorettype=t.oid)
            --INNER JOIN pg_catalog.pg_description d ON (p.oid=d.objoid)
            INNER JOIN pg_catalog.pg_namespace n ON (n.oid=p.pronamespace)
            --WHERE n.nspname='public'
        )) as t
        ORDER BY 1,2,3"""
        headers, res, status = self.getQueryResult(query)

        self.view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.view.setUniformRowHeights(True)
        self.view.setAnimated(True)

        # populate data
        parentSchema = None
        parentType = None
        for schema, type_, name, oid in res:
            if schema != parentSchema:  # On changing/first schema in the list
                schemaItem = em.SchemaNode(schema, parent=self.rootNode, icon=self.icons['SCHEMA'])
                parentSchema = schema  # Set the schema name as the parent
                parentType = None  # Reset the type
            if type_ != parentType:  # On changing/first type in the list
                parentType = type_  # Set the type as the parent type
                typeItem = em.GenericNode(type_, parent=schemaItem, icon=self.icons[type_])
            if type_ == "TABLE":
                nameItem = em.TableNode(name, typeItem, icon=self.icons["TABLE"])
            if type_ == "SEQUENCE":
                nameItem = em.SequenceNode(name, typeItem, icon=self.icons["SEQUENCE"])
            if type_ == "VIEW":
                nameItem = em.ViewNode(name, typeItem, icon=self.icons["VIEW"])
            if type_ == "FUNCTION":
                nameItem = em.ViewNode(name, typeItem, icon=self.icons["FUNCTION"])
            if type_ == "MATERIALIZED VIEW":
                nameItem = em.MaterializedViewNode(name, typeItem, icon=self.icons["MATERIALIZED VIEW"])
            if type_ == "INDEX":
                nameItem = em.IndexNode(name, typeItem, icon=self.icons["INDEX"])
            if type_ == "FOREIGN TABLE":
                nameItem = em.ForeignTable(name, typeItem, icon=self.icons["FOREIGN TABLE"])
            if type_ == "SPECIAL":
                nameItem = em.Special(name, typeItem, icon=self.icons["SPECIAL"])

                # if type_ in ('tables', 'views', 'materialized views'):
                #     for colName in self.getColumnsNamesAndDesc(schema, name):
                #         colNameItem = QtGui.QStandardItem(self.icons['columns'], colName[0])
                #         nameItem.appendRow(colNameItem)

    def getColumnsNamesAndDesc(self, schema, table):
        """Returns columns names list with extra information (primary key * and type)"""
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
        ORDER BY f.attnum DESC""".format(schema, table)
        _, res, _ = self.getQueryResult(query)
        res = [r[0] for r in res]
        return res

    def getColumnsNames(self, schema, table):
        """Returns columns names list"""
        def convert(t):
            def hasUpper(t):
                for i in t:
                    if i in string.uppercase:
                        return True
                return False
            if hasUpper(t):
                return '"%s"'%t
            else:
                return t

        query = """SELECT
        f.attname AS name
        FROM pg_attribute f
        JOIN pg_class c ON c.oid = f.attrelid
        LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
        LEFT JOIN pg_constraint p ON p.conrelid = c.oid
        AND f.attnum = ANY (p.conkey)
        WHERE c.relkind IN ('r', 'v', 'm')
            AND n.nspname = '{0:s}'
            AND c.relname = '{1:s}'
            AND f.attnum > 0
        ORDER BY f.attnum ASC""".format(schema, table)
        _, res, _ = self.getQueryResult(query)
        res = [convert(r[0]) for r in res]
        return res

    def getNames(self, index):
        """Gets names of schema and object (table, view, ...) of the node at index"""
        parentNode = self.model.getNode(index)
        schemaIndex = self.model.parent(self.model.parent(index))  # Needed to jump the generic node
        schemaNode = self.model.getNode(schemaIndex)
        return schemaNode.name(), parentNode.name()

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
        parentNode = self.model.getNode(index)
        if parentNode.typeInfo() in ("TABLE", "VIEW", "MATERIALIZED VIEW"):
            childCount = parentNode.childCount()
            if childCount > 0:
                self.model.removeRows(0, childCount, index)
            schemaName, tableName = self.getNames(index)
            columns = self.getColumnsNamesAndDesc(schemaName, tableName)
            self.model.insertColumnNames(0, columns, index)

    def onContextMenu(self, point):
        index = self.view.indexAt(point)
        parentNode = self.model.getNode(index)
        globalPos = self.view.mapToGlobal(point)
        if parentNode.typeInfo() in ("TABLE", "VIEW", "MATERIALIZED VIEW"):
            schemaName, tableName = self.getNames(index)

            uiMenu = QtGui.QMenu()

            uiQueryLimitAction = QtGui.QAction('SHOW PARTIAL', self)
            uiQueryLimitAction.setStatusTip('Select first 500 rows')
            uiQueryLimitAction.triggered.connect(partial(self.onQueryLimit, schemaName, tableName))
            uiMenu.addAction(uiQueryLimitAction)

            uiQueryAllAction = QtGui.QAction('SHOW ALL', self)
            uiQueryAllAction.setStatusTip('Select all (may be slow...)')
            uiQueryAllAction.triggered.connect(partial(self.onQueryAll, schemaName, tableName))
            uiMenu.addAction(uiQueryAllAction)

            uiEditAction = QtGui.QAction('Definition', self)
            uiEditAction.setStatusTip('Show the definition of the object')
            uiEditAction.triggered.connect(partial(self.onEditTable, schemaName, tableName, parentNode.typeInfo()))
            uiMenu.addAction(uiEditAction)

            uiMenu.exec_(globalPos)


    def onQueryLimit(self, schemaName, tableName):
        columns = self.getColumnsNames(schemaName, tableName)
        query = """SELECT {0:s}
        FROM "{1:s}"."{2:s}"
        LIMIT 500""".format(','.join(columns), schemaName, tableName)
        page = self.nativeParentWidget().newQueryPage()
        page.uiQueryEditor.setText(query)
        page.onRewriteQuery()
        page.setCurrentName(tableName)
        page.onRunQuery()

    def onQueryAll(self, schemaName, tableName):
        columns = self.getColumnsNames(schemaName, tableName)
        query = """SELECT {0:s}
        FROM "{1:s}"."{2:s}"
        """.format(','.join(columns), schemaName, tableName)
        page = self.nativeParentWidget().newQueryPage()
        page.uiQueryEditor.setText(query)
        page.onRewriteQuery()
        page.setCurrentName(tableName)
        page.onRunQuery()

    def getQueryResult(self, query):
        conn = self.database.newConnection()
        headers, res, status = db.execute(conn, query)
        conn.close()
        return headers, res, status

    def onEditTable(self, schemaName, tableName, typeInfo):
        if typeInfo == "TABLE":
            query = ""

        if typeInfo == "VIEW":
            query = """SELECT 'CREATE OR REPLACE VIEW ' || quote_ident(schemaname) || '.'
            || quote_ident(viewname) || ' AS \n' || definition
            FROM pg_views
            WHERE viewname = '{0}' AND schemaname='{1}'
            """.format(tableName, schemaName)
        _, res, _ = self.getQueryResult(query)
        page = self.nativeParentWidget().newQueryPage()
        page.uiQueryEditor.setText(res[0][0])
        page.onRewriteQuery()
        page.setCurrentName(tableName)

    def onDefineFunction(self, schemaName, functionName, oid):
        query = """SELECT pg_get_functiondef({0})""".format(oid)
        _, res, _ = self.getQueryResult(query)

