# -*- coding:utf-8 -*-

__author__ = 'lionel'

from PyQt4 import QtGui, QtCore, Qsci
# from qutepart import Qutepart
from PyQt4.Qsci import QsciScintilla, QsciLexerSQL  # , QsciLexerPython


class QueryEditor(QsciScintilla):
    def __init__(self, *args, **kwargs):
        super(QueryEditor, self).__init__(*args, **kwargs)

        # Set the default font
        # font = QtGui.QFont()
        # font.setFamily('Courier')
        # font.setFixedPitch(True)
        # font.setPointSize(10)
        # # Margin 0 is used for line numbers
        # fontmetrics = QtGui.QFontMetrics(font)

        # Lexer
        lexer = QsciLexerSQL(self)
        self.setLexer(lexer)

        #AutoCompletion
        api = Qsci.QsciAPIs(lexer)
        for cmd in sql_commands:
            api.add(cmd)
        api.prepare()
        self.setAutoCompletionThreshold(2)
        self.setAutoCompletionSource(QsciScintilla.AcsAPIs)

        #General
        self.setUtf8(True)
        self.setFolding(QsciScintilla.BoxedTreeFoldStyle)
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        self.setFolding(QsciScintilla.BoxedTreeFoldStyle)
        # self.setFont(font)

        #LineHighlight
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QtGui.QColor("gainsboro"))

        #AutoIndentation
        self.setAutoIndent(True)
        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(True)
        self.setIndentationWidth(4)

        #Margins
        self.setMarginsBackgroundColor(QtGui.QColor("gainsboro"))
        # self.setMarginsFont(font)
        self.setMarginsFont(QtGui.QFont("Consolas", 9, 87))
        self.setMarginLineNumbers(0, True)
        self.setMarginType(1, self.SymbolMargin)
        self.setMarginWidth(0, QtCore.QString("-------"))
        # self.setMarginWidth(1, QtCore.QString().setNum(10))

        #Indentation
        self.setIndentationsUseTabs(True)
        self.setIndentationGuides(True)
        self.setIndentationWidth(4)

    def getText(self):
        return self.text()


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

sql_commands = ['ACCESS', 'ADD', 'ALL', 'ALTER TABLE', 'AND', 'ANY', 'AS',
            'ASC', 'AUDIT', 'BETWEEN', 'BY', 'CASE', 'CHAR', 'CHECK',
            'CLUSTER', 'COLUMN', 'COMMENT', 'COMPRESS', 'CONNECT', 'COPY',
            'CREATE', 'CURRENT', 'DATABASE', 'DATE', 'DECIMAL', 'DEFAULT',
            'DELETE FROM', 'DELIMITER', 'DESC', 'DESCRIBE', 'DISTINCT', 'DROP',
            'ELSE', 'ENCODING', 'ESCAPE', 'EXCLUSIVE', 'EXISTS', 'EXTENSION',
            'FILE', 'FLOAT', 'FOR', 'FORMAT', 'FORCE_QUOTE', 'FORCE_NOT_NULL',
            'FREEZE', 'FROM', 'FULL', 'FUNCTION', 'GRANT', 'GROUP BY',
            'HAVING', 'HEADER', 'IDENTIFIED', 'IMMEDIATE', 'IN', 'INCREMENT',
            'INDEX', 'INITIAL', 'INSERT INTO', 'INTEGER', 'INTERSECT', 'INTO',
            'IS', 'JOIN', 'LEFT', 'LEVEL', 'LIKE', 'LIMIT', 'LOCK', 'LONG',
            'MAXEXTENTS', 'MINUS', 'MLSLABEL', 'MODE', 'MODIFY', 'NOAUDIT',
            'NOCOMPRESS', 'NOT', 'NOWAIT', 'NULL', 'NUMBER', 'OIDS', 'OF',
            'OFFLINE', 'ON', 'ONLINE', 'OPTION', 'OR', 'ORDER BY', 'OUTER',
            'OWNER', 'PCTFREE', 'PRIMARY', 'PRIOR', 'PRIVILEGES', 'QUOTE',
            'RAW', 'RENAME', 'RESOURCE', 'REVOKE', 'RIGHT', 'ROW', 'ROWID',
            'ROWNUM', 'ROWS', 'SELECT', 'SESSION', 'SET', 'SHARE', 'SIZE',
            'SMALLINT', 'START', 'SUCCESSFUL', 'SYNONYM', 'SYSDATE', 'TABLE',
            'TEMPLATE', 'THEN', 'TO', 'TRIGGER', 'TRUNCATE', 'UID', 'UNION',
            'UNIQUE', 'UPDATE', 'USE', 'USER', 'USING', 'VALIDATE', 'VALUES',
            'VARCHAR', 'VARCHAR2', 'VIEW', 'WHEN', 'WHENEVER', 'WHERE', 'WITH']

if __name__ == "__main__":
    from PyQt4 import QtGui
    import sys

    app = QtGui.QApplication(sys.argv)
    editor = QueryEditor()
    editor.show()
    editor.setText(open(sys.argv[0]).read())
    app.exec_()