# -*- coding:utf-8 -*-

__author__ = 'lionel'

import logging
logger = logging.getLogger(__name__)
from PyQt4 import QtGui, QtCore, Qsci
import explorer_model as em
from src import db
# from qutepart import Qutepart
# from PyQt4.Qsci import QsciScintilla, QsciLexerSQL  # , QsciLexerPython

# keywords
keywords = [
    "ACTION", "ADD", "AFTER", "ALL", "ALTER", "ANALYZE", "AND", "AS", "ASC",
    "BEFORE", "BEGIN", "BETWEEN", "BY", "CASCADE", "CASE", "CAST", "CHECK",
    "COLLATE", "COLUMN", "COMMIT", "CONSTRAINT", "CREATE", "CROSS", "CURRENT_DATE",
    "CURRENT_TIME", "CURRENT_TIMESTAMP", "DEFAULT", "DEFERRABLE", "DEFERRED",
    "DELETE", "DESC", "DISTINCT", "DROP", "EACH", "ELSE", "END", "ESCAPE",
    "EXCEPT", "EXISTS", "FOR", "FOREIGN", "FROM", "FULL", "GROUP", "HAVING",
    "IGNORE", "IMMEDIATE", "IN", "INITIALLY", "INNER", "INSERT", "INTERSECT",
    "INTO", "IS", "ISNULL", "JOIN", "KEY", "LEFT", "LIKE", "LIMIT", "MATCH",
    "NATURAL", "NO", "NOT", "NOTNULL", "NULL", "OF", "OFFSET", "ON", "OR", "ORDER BY",
    "OUTER", "PRIMARY", "REFERENCES", "RELEASE", "RESTRICT", "RIGHT", "ROLLBACK",
    "ROW", "SAVEPOINT", "SELECT", "SET", "TABLE", "TEMPORARY", "THEN", "TO",
    "TRANSACTION", "TRIGGER", "UNION", "UNIQUE", "UPDATE", "USING", "VALUES",
    "VIEW", "WHEN", "WHERE"
]

# functions
functions = [
    "abs", "changes", "coalesce", "glob", "ifnull", "hex", "last_insert_rowid",
    "length", "like", "lower", "ltrim", "max", "min", "nullif", "quote", "random",
    "randomblob", "replace", "round", "rtrim", "soundex", "total_change", "trim",
    "typeof", "upper", "zeroblob", "date", "datetime", "julianday", "strftime",
    "avg", "count", "group_concat", "sum", "total"
]

# constants
constants = ["null", "false", "true"]


def getSqlDictionary():
    return {'keyword': list(keywords), 'constant': list(constants), 'function': list(functions)}


class HighlightingRule:
    def __init__(self, typ, regex):
        self._type = typ
        self._regex = regex

    def type(self):
        return self._type

    def regex(self):
        return QtCore.QRegExp(self._regex)


class SqlHighlighter(QtGui.QSyntaxHighlighter):
    COLOR_KEYWORD = QtGui.QColor(0x00, 0x00, 0xE6)
    COLOR_FUNCTION = QtGui.QColor(0xCE, 0x7B, 0x00)
    COLOR_COMMENT = QtGui.QColor(0x96, 0x96, 0x96)
    COLOR_CONSTANT = QtCore.Qt.magenta
    COLOR_IDENTIFIER = QtGui.QColor(0x00, 0x99, 0x00)
    COLOR_PARAMETER = QtGui.QColor(0x25, 0x9D, 0x9D)

    def __init__(self, parent):
        QtGui.QSyntaxHighlighter.__init__(self, parent)
        self.rules = []
        self.styles = {}

        # keyword
        format = QtGui.QTextCharFormat()
        format.setForeground(QtGui.QBrush(self.COLOR_KEYWORD, QtCore.Qt.SolidPattern))
        # format.setFontWeight(QtGui.QFont.Bold)
        self.styles['keyword'] = format

        # function and delimiter
        format = QtGui.QTextCharFormat()
        format.setForeground(QtGui.QBrush(self.COLOR_FUNCTION, QtCore.Qt.SolidPattern))
        self.styles['function'] = format
        self.styles['delimiter'] = format

        # identifier
        format = QtGui.QTextCharFormat()
        format.setForeground(QtGui.QBrush(self.COLOR_IDENTIFIER, QtCore.Qt.SolidPattern))
        self.styles['identifier'] = format

        # comment
        format = QtGui.QTextCharFormat()
        format.setForeground(QtGui.QBrush(self.COLOR_COMMENT, QtCore.Qt.SolidPattern))
        self.styles['comment'] = format

        # constant (numbers, strings)
        format = QtGui.QTextCharFormat()
        format.setForeground(QtGui.QBrush(self.COLOR_CONSTANT, QtCore.Qt.SolidPattern))
        self.styles['constant'] = format

        self.rules = []

        rules = getSqlDictionary()

        for name in self.styles.keys():
            if name not in rules:
                continue
            for value in rules[name]:
                regex = QtCore.QRegExp(u"\\b%s\\b" % QtCore.QRegExp.escape(value), QtCore.Qt.CaseInsensitive)
                rule = HighlightingRule(name, regex)
                self.rules.append(rule)

        # delimiter
        regex = QtCore.QRegExp("[\)\(]")
        rule = HighlightingRule('delimiter', regex)
        self.rules.append(rule)

        # identifier
        regex = QtCore.QRegExp(r'"[^"\\]*(\\.[^"\\]*)*"')
        regex.setMinimal(True)
        rule = HighlightingRule('identifier', regex)
        self.rules.append(rule)

        # constant (numbers, strings)
        # string
        regex = QtCore.QRegExp(r"'[^'\\]*(\\.[^'\\]*)*'")
        regex.setMinimal(True)
        rule = HighlightingRule('constant', regex)
        self.rules.append(rule)
        # number
        regex = QtCore.QRegExp(r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b')
        regex.setMinimal(True)
        rule = HighlightingRule('constant', regex)
        self.rules.append(rule)

        # single-line comment
        regex = QtCore.QRegExp("--.*$")
        rule = HighlightingRule('comment', regex)
        self.rules.append(rule)

        # multi-line comment
        self.multiLineCommentStart = QtCore.QRegExp("/\\*")
        self.multiLineCommentEnd = QtCore.QRegExp("\\*/")

    def highlightBlock(self, text):
        index = 0
        rule_sel = None
        rule_index = -1

        while index < text.length():
            # search for the rule that matches starting from the less index
            rule_sel = None
            rule_index = -1
            rule_length = 0
            for rule in self.rules:
                regex = rule.regex()
                pos = regex.indexIn(text, index)
                if pos >= 0:
                    if rule_sel is None or rule_index > pos:
                        rule_sel = rule
                        rule_index = pos
                        rule_length = regex.cap(0).length()

            if rule_sel is None:  # no rule matches
                break

            # apply the rule found before
            self.setFormat(rule_index, rule_length, self.styles[rule_sel.type()])
            index = rule_index + rule_length

        self.setCurrentBlockState(0)

        # handle with multiline comments
        index = 0
        if self.previousBlockState() != 1:
            index = self.multiLineCommentStart.indexIn(text, index)
        while index >= 0:
            # if the last applied rule is a single-line comment,
            # then avoid multiline comments that start after it
            if rule_sel is not None and rule_sel.type() == 'comment' and index >= rule_index:
                break

            pos = self.multiLineCommentEnd.indexIn(text, index)
            comment_length = 0
            if pos < 0:
                self.setCurrentBlockState(1)
                comment_length = text.length() - index;
            else:
                comment_length = pos - index + self.multiLineCommentEnd.cap(0).length()
            self.setFormat(index, comment_length, self.styles['comment'])
            index = self.multiLineCommentStart.indexIn(text, index + comment_length)


class CompletionModel(em.ExplorerModel):
    def __init__(self, parent, database):
        self.database = database
        self.parent = parent

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

        super(CompletionModel, self).__init__(None, self.parent, "Database Model")
        self._rootNode = em.Node(self.database, parent=None, icon=self.icons['DATABASE'])
        self.setupModel()

    def getQueryResult(self, query):
        conn = self.database.newConnection()
        headers, res, status = db.execute(conn, query)
        conn.close()
        return headers, res, status

    def setupModel(self):
        # self.removeRows(0, self.rowCount(QtCore.QModelIndex()))

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
            WHERE c.relkind IN ('r','v','m')
                --AND n.nspname <> 'pg_catalog'
                --AND n.nspname <> 'information_schema'
                --AND n.nspname !~ '^pg_toast'
        )
        ) as t
        ORDER BY 1,2,3"""
        headers, res, status = self.getQueryResult(query)

        # populate data
        parentSchema = None
        for schema, type_, name, oid in res:
            if schema != parentSchema:  # On changing/first schema in the list
                schemaItem = em.SchemaNode(schema, parent=self._rootNode, icon=self.icons['SCHEMA'])
                parentSchema = schema  # Set the schema name as the parent
            if type_ in self.nodes.keys():
                self.nodes[type_](name, oid=oid, parent=schemaItem, icon=self.icons[type_])


class SqlCompleter(QtGui.QCompleter):
    def __init__(self, *args):
        # dictionary = getSqlDictionary()
        # wordlist = QtCore.QStringList()
        # for name, value in dictionary.iteritems():
        #     wordlist << value

        # setup the completer
        super(SqlCompleter, self).__init__(*args)
        self.setModelSorting(QtGui.QCompleter.CaseInsensitivelySortedModel)
        self.setWrapAround(True)
        self.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setCompletionColumn(0)
        self.setCompletionRole(QtCore.Qt.DisplayRole)

    def splitPath(self, path):
        return path.split('.')

    def pathFromIndex(self, index):
        result = []
        while index.isValid():
            result = [self.model().data(index, QtCore.Qt.DisplayRole)] + result
            index = index.parent()
        r = '.'.join(result)
        return r

    def setModel(self, model):
        # Append model from database objects explorer
        super(SqlCompleter, self).setModel(model)


class QueryEditor(QtGui.QPlainTextEdit):
    """from http://doc.qt.digia.com/4.6/tools-customcompleter.html
    and QGiS dbmanager plugin"""
    def __init__(self, *args, **kwargs):
        super(QueryEditor, self).__init__(*args, **kwargs)
        # QtGui.QTextEdit.__init__(self, *args, **kwargs)
        self.completer = SqlCompleter()
        self.completer.setWidget(self)
        self.highlighter = SqlHighlighter(self)

        self.connect(self.completer, QtCore.SIGNAL("activated(const QString&)"), self.insertCompletion)

    def insertCompletion(self, completion):
        tc = self.textCursor()
        extra = completion.length() - self.completer.completionPrefix().length()
        tc.movePosition(QtGui.QTextCursor.Left)
        tc.movePosition(QtGui.QTextCursor.EndOfWord)
        tc.insertText(completion.right(extra))
        self.setTextCursor(tc)

    def textUnderCursor(self):
        # Hack for searching the word under the cursor because WordUnderCursor doesn't take
        # care of dots, but we need them
        tc = self.textCursor()
        isStartOfWord = False
        while not isStartOfWord:
            tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)
            if tc.atStart():
                isStartOfWord = True
            elif QtCore.QChar(tc.selectedText()[0]).isSpace():
                isStartOfWord = True
        return tc.selectedText().trimmed()

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self)
        QtGui.QPlainTextEdit.focusInEvent(self, event)

    def keyPressEvent(self, event):
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Escape, QtCore.Qt.Key_Tab,
                               QtCore.Qt.Key_Backtab):
                event.ignore()
                return

        # has ctrl-space been pressed??
        isShortcut = event.modifiers() == QtCore.Qt.ControlModifier and event.key() == QtCore.Qt.Key_Space
        if not self.completer or not isShortcut:
            QtGui.QPlainTextEdit.keyPressEvent(self, event)

        # ctrl or shift key on it's own??
        ctrlOrShift = event.modifiers() in (QtCore.Qt.ControlModifier, QtCore.Qt.ShiftModifier)
        if ctrlOrShift and event.text().isEmpty():
            # ctrl or shift key on it's own
            return

        eow = QtCore.QString("~!@#$%^&*()+{}|:\"<>?,/;'[]\\-=")  # end of word

        hasModifier = event.modifiers() != QtCore.Qt.NoModifier and not ctrlOrShift

        completionPrefix = self.textUnderCursor()

        if not isShortcut and (hasModifier or event.text().isEmpty() or
                                       completionPrefix.length() < 2 or eow.contains(event.text().right(1))):
            self.completer.popup().hide()
            return

        if completionPrefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completionPrefix)
            popup = self.completer.popup()
            popup.setCurrentIndex(self.completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0)
                    + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)  # popup it up!

    def setCompletionModel(self, database):
        model = CompletionModel(database=database, parent=self)
        self.completer.setModel(model)


    def getText(self):
        return self.toPlainText()

    def text(self, t):
        self.setPlainText(t)


# class QueryEditor(QsciScintilla):
# def __init__(self, *args, **kwargs):
# super(QueryEditor, self).__init__(*args, **kwargs)
#
# # Set the default font
# # font = QtGui.QFont()
#         # font.setFamily('Courier')
#         # font.setFixedPitch(True)
#         # font.setPointSize(10)
#         # # Margin 0 is used for line numbers
#         # fontmetrics = QtGui.QFontMetrics(font)
#
#         # Lexer
#         lexer = QsciLexerSQL(self)
#         self.setLexer(lexer)
#
#         #AutoCompletion
#         api = Qsci.QsciAPIs(lexer)
#         for cmd in sql_commands:
#             api.add(cmd)
#         api.prepare()
#         self.setAutoCompletionThreshold(2)
#         self.setAutoCompletionSource(QsciScintilla.AcsAPIs)
#
#         #General
#         self.setUtf8(True)
#         self.setFolding(QsciScintilla.BoxedTreeFoldStyle)
#         self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
#         self.setFolding(QsciScintilla.BoxedTreeFoldStyle)
#         # self.setFont(font)
#
#         #LineHighlight
#         self.setCaretLineVisible(True)
#         self.setCaretLineBackgroundColor(QtGui.QColor("gainsboro"))
#
#         #AutoIndentation
#         self.setAutoIndent(True)
#         self.setIndentationGuides(True)
#         self.setIndentationsUseTabs(True)
#         self.setIndentationWidth(4)
#
#         #Margins
#         self.setMarginsBackgroundColor(QtGui.QColor("gainsboro"))
#         # self.setMarginsFont(font)
#         self.setMarginsFont(QtGui.QFont("Consolas", 9, 87))
#         self.setMarginLineNumbers(0, True)
#         self.setMarginType(1, self.SymbolMargin)
#         self.setMarginWidth(0, QtCore.QString("-------"))
#         # self.setMarginWidth(1, QtCore.QString().setNum(10))
#
#         #Indentation
#         self.setIndentationsUseTabs(True)
#         self.setIndentationGuides(True)
#         self.setIndentationWidth(4)
#
#     def getText(self):
#         return self.text()


# class QueryEditor(Qutepart):
# def __init__(self, *args, **kwargs):
#         super(QueryEditor, self).__init__(*args, **kwargs)
#         self.completionEnabled = True
#         self.completionThreshold = 2
#         self.indentUseTabs = True
#         self.indentWidth = 4
#         self.detectSyntax(xmlFileName="sql-postgresql.xml")
#
#     def setText(self, text):
#         self.text = text
#
#     def getText(self):
#         return self.text

# sql_commands = ['ACCESS', 'ADD', 'ALL', 'ALTER TABLE', 'AND', 'ANY', 'AS',
#                 'ASC', 'AUDIT', 'BETWEEN', 'BY', 'CASE', 'CHAR', 'CHECK',
#                 'CLUSTER', 'COLUMN', 'COMMENT', 'COMPRESS', 'CONNECT', 'COPY',
#                 'CREATE', 'CURRENT', 'DATABASE', 'DATE', 'DECIMAL', 'DEFAULT',
#                 'DELETE FROM', 'DELIMITER', 'DESC', 'DESCRIBE', 'DISTINCT', 'DROP',
#                 'ELSE', 'ENCODING', 'ESCAPE', 'EXCLUSIVE', 'EXISTS', 'EXTENSION',
#                 'FILE', 'FLOAT', 'FOR', 'FORMAT', 'FORCE_QUOTE', 'FORCE_NOT_NULL',
#                 'FREEZE', 'FROM', 'FULL', 'FUNCTION', 'GRANT', 'GROUP BY',
#                 'HAVING', 'HEADER', 'IDENTIFIED', 'IMMEDIATE', 'IN', 'INCREMENT',
#                 'INDEX', 'INITIAL', 'INSERT INTO', 'INTEGER', 'INTERSECT', 'INTO',
#                 'IS', 'JOIN', 'LEFT', 'LEVEL', 'LIKE', 'LIMIT', 'LOCK', 'LONG',
#                 'MAXEXTENTS', 'MINUS', 'MLSLABEL', 'MODE', 'MODIFY', 'NOAUDIT',
#                 'NOCOMPRESS', 'NOT', 'NOWAIT', 'NULL', 'NUMBER', 'OIDS', 'OF',
#                 'OFFLINE', 'ON', 'ONLINE', 'OPTION', 'OR', 'ORDER BY', 'OUTER',
#                 'OWNER', 'PCTFREE', 'PRIMARY', 'PRIOR', 'PRIVILEGES', 'QUOTE',
#                 'RAW', 'RENAME', 'RESOURCE', 'REVOKE', 'RIGHT', 'ROW', 'ROWID',
#                 'ROWNUM', 'ROWS', 'SELECT', 'SESSION', 'SET', 'SHARE', 'SIZE',
#                 'SMALLINT', 'START', 'SUCCESSFUL', 'SYNONYM', 'SYSDATE', 'TABLE',
#                 'TEMPLATE', 'THEN', 'TO', 'TRIGGER', 'TRUNCATE', 'UID', 'UNION',
#                 'UNIQUE', 'UPDATE', 'USE', 'USER', 'USING', 'VALIDATE', 'VALUES',
#                 'VARCHAR', 'VARCHAR2', 'VIEW', 'WHEN', 'WHENEVER', 'WHERE', 'WITH']

if __name__ == "__main__":
    from PyQt4 import QtGui
    import sys

    app = QtGui.QApplication(sys.argv)
    editor = QueryEditor()
    editor.show()
    editor.setText(open(sys.argv[0]).read())
    app.exec_()