# -*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore
from ui.forms.explorerui import ExplorerUI
import explorer_model as em
import string
from functools import partial


class ObjectsExplorer(ExplorerUI):
    def __init__(self, *args, **kwargs):

        self.database = kwargs.pop("database")
        self.parent = kwargs["parent"]
        super(ObjectsExplorer, self).__init__(*args, **kwargs)
        self.setName('Database Objects')

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
            'FUNCTION': QtGui.QIcon(QtGui.QPixmap(':/function.png')),
            'DATABASE': QtGui.QIcon(QtGui.QPixmap(':/database.png')),
        }

        self.nodes = {
            'COLUMN': em.ColumnNode,
            'TABLE': em.TableNode,
            'VIEW': em.ViewNode,
            'INDEX': em.IndexNode,
            'SEQUENCE': em.SequenceNode,
            'MATERIALIZED VIEW': em.MaterializedViewNode,
            'FOREIGN TABLE': em.ForeignTableNode,
            'SPECIAL': em.SpecialNode,
            'SCHEMA': em.SchemaNode,
            'FUNCTION': em.FunctionNode,
        }

        self.rootNode = em.Node(self.database, parent=None, icon=self.icons['DATABASE'])

        self.model = em.ExplorerModel(self.rootNode, self.parent, "Database")
        self.view = self.uiExplorerTree
        self.view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.view.setUniformRowHeights(True)
        self.view.setAnimated(True)
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
        headers, res, status = self.database.execute(query)

        # populate data
        parentSchema = None
        parentType = None
        for schema, type_, name, oid in res:
            if schema != parentSchema:  # On changing/first schema in the list
                schemaItem = em.SchemaNode(schema, parent=self.rootNode, icon=self.icons['SCHEMA'])
                parentSchema = schema  # Set the schema name as the parent
                parentType = None  # Reset the type
            if type_ != parentType:  # On changing/first type in the list
                typeItem = em.GenericNode(type_, parent=schemaItem, icon=self.icons[type_])
                parentType = type_  # Set the type as the parent type
            if type_ in self.nodes.keys():
                nodeItem = self.nodes[type_](name, oid=oid, parent=typeItem, icon=self.icons[type_])
                # # Too slow
                # if type_ in ['TABLE', 'VIEW', 'MATERIALIZED VIEW']:
                #     columns = self.getColumnsNames(parentSchema, name)
                #     for col in columns:
                #         self.nodes['COLUMN'](col, oid=None, parent=nodeItem, icon=self.icons['COLUMN'])


    def getColumnsNamesAndDesc(self, schema, table):
        """Returns columns names list with extra information (primary key * and type)"""
        query = """SELECT
        concat(f.attname, CASE WHEN p.contype = 'p' THEN '*' ELSE '' END, ' ('::varchar, pg_catalog.format_type(f.atttypid, f.atttypmod), ')'::varchar) AS name
        FROM pg_attribute f
        JOIN pg_class c ON c.oid = f.attrelid
        LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
        LEFT JOIN pg_constraint p ON p.conrelid = c.oid
        AND f.attnum = ANY (p.conkey)
        WHERE c.relkind IN ('r', 'v', 'm')
            AND n.nspname = '{0:s}'
            AND c.relname = '{1:s}'
            AND f.attnum > 0
            AND f.attisdropped IS FALSE
        ORDER BY f.attnum DESC""".format(schema, table)
        _, res, _ = self.database.execute(query)
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
            AND f.attisdropped IS FALSE
        ORDER BY f.attnum ASC""".format(schema, table)
        _, res, _ = self.database.execute(query)
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
            modifiers = QtGui.QApplication.queryKeyboardModifiers()
            # Ctrl modifier == Set standard DML to the editor
            if modifiers == QtCore.Qt.ControlModifier:
                self.showSelectQuery(index)
            # Ctrl+Shift modifiers == Set standard DML to the editor and run the query, with a limited amount of rows
            elif modifiers == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
                self.showAndRunSelectQuery(index, limit=1000)
            # Ctrl+Shift+Alt modifiers == Set standard DML to the editor and run the query, without rows limit
            elif modifiers == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier | QtCore.Qt.AltModifier):
                self.showAndRunSelectQuery(index, limit=None)
            # No modifier == show columns info
            elif modifiers == QtCore.Qt.NoModifier:
                self.showColumns(index)
            else:
                pass

    def showColumns(self, index):
        """
        Show/Append columns informations to the Node
        :param index: Node's index in the tree
        :return:
        """
        type_ = 'COLUMN'
        parentNode = self.model.getNode(index)
        if parentNode.typeInfo() in ("TABLE", "VIEW", "MATERIALIZED VIEW"):
            childCount = parentNode.childCount()
            if childCount > 0:
                self.model.removeRows(0, childCount, index)
            schemaName, tableName = self.getNames(index)
            columns = self.getColumnsNamesAndDesc(schemaName, tableName)
            if len(columns) > 0:
                self.model.beginInsertRows(index, 0, len(columns) - 1)
                for column in columns[::-1]:
                    print(column)
                    childNode = self.nodes[type_](column, oid=None, parent=parentNode, icon=self.icons[type_])
                self.model.endInsertRows()

    def showSelectQuery(self, index):
        """
        Set the standard DML SELECT * FROM TABLE in the editor
        :param index: Node's index in the tree
        :return:
        """
        schemaName, tableName = self.getNames(index)
        columns = self.getColumnsNames(schemaName, tableName)
        query = """SELECT {0:s}
        FROM "{1:s}"."{2:s}"
        """.format(','.join(columns), schemaName, tableName)
        page = self.nativeParentWidget().newQueryPage()
        page.uiQueryEditor.setText(query)
        page.onRewriteQuery()
        page.setCurrentName(tableName)

    def showAndRunSelectQuery(self, index, limit=None):
        """
        Set the standard DML SELECT * FROM TABLE in the editor and run it
        :param index: Node's index in the tree
        :param limit: amount of rows to return. None = no limit
        :return:
        """
        schemaName, tableName = self.getNames(index)
        columns = self.getColumnsNames(schemaName, tableName)
        if limit is not None:
            limit = " LIMIT %i"%limit
        else:
            limit = ''
        query = """SELECT {0:s}
        FROM "{1:s}"."{2:s}"
        {3:s}""".format(','.join(columns), schemaName, tableName, limit)
        page = self.nativeParentWidget().newQueryPage()
        page.uiQueryEditor.setText(query)
        page.onRewriteQuery()
        page.setCurrentName(tableName)
        page.onRunQuery()


    def onContextMenu(self, point):
        index = self.view.indexAt(point)
        parentNode = self.model.getNode(index)
        globalPos = self.view.mapToGlobal(point)
        if parentNode.typeInfo() in ("TABLE", "VIEW", "MATERIALIZED VIEW"):
            schemaName, tableName = self.getNames(index)

            uiMenu = QtGui.QMenu()

            uiQueryLimitAction = QtGui.QAction('Partial', self)
            uiQueryLimitAction.setStatusTip('Select first 500 rows')
            uiQueryLimitAction.triggered.connect(partial(self.onQueryLimit, schemaName, tableName))
            uiMenu.addAction(uiQueryLimitAction)

            uiQueryAllAction = QtGui.QAction('All', self)
            uiQueryAllAction.setStatusTip('Select all rows (may be slow...)')
            uiQueryAllAction.triggered.connect(partial(self.onQueryAll, schemaName, tableName))
            uiMenu.addAction(uiQueryAllAction)

            uiEditAction = QtGui.QAction('Show definition', self)
            uiEditAction.setStatusTip('Show the definition of the object')
            uiEditAction.triggered.connect(partial(self.onEditTable, schemaName, tableName, parentNode.typeInfo()))
            uiMenu.addAction(uiEditAction)

            uiMenu.exec_(globalPos)


    def onQueryLimit(self, schemaName, tableName):
        columns = self.getColumnsNames(schemaName, tableName)
        query = """SELECT {0:s}
        FROM "{1:s}"."{2:s}"
        LIMIT 1000""".format(','.join(columns), schemaName, tableName)
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

    def onEditTable(self, schemaName, tableName, typeInfo):
        if typeInfo == "TABLE":
            query = ""

        if typeInfo == "VIEW":
            query = """SELECT 'CREATE OR REPLACE VIEW ' || quote_ident(schemaname) || '.'
            || quote_ident(viewname) || ' AS \n' || definition
            FROM pg_views
            WHERE viewname = '{0}' AND schemaname='{1}'
            """.format(tableName, schemaName)
        _, res, _ = self.database.execute(query)
        # print(res)
        page = self.nativeParentWidget().newQueryPage()
        page.uiQueryEditor.setText(res[0][0])
        page.onRewriteQuery()
        page.setCurrentName(tableName)

    def onDefineFunction(self, schemaName, functionName, oid):
        query = """SELECT pg_get_functiondef({0})""".format(oid)
        _, res, _ = self.getQueryResult(query)

