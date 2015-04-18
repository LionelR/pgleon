# -*- coding:utf-8 -*-

__author__ = 'lionel'


from PyQt4 import QtGui, QtCore, Qsci
from qutepart import Qutepart
from PyQt4.Qsci import QsciScintilla, QsciLexerSQL #, QsciLexerPython


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

        #Lexer
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
#     def __init__(self, *args, **kwargs):
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

sql_commands = ["ABORT",
"ALTER AGGREGATE",
"ALTER COLLATION",
"ALTER CONVERSION",
"ALTER DATABASE",
"ALTER DEFAULT PRIVILEGES",
"ALTER DOMAIN",
"ALTER EVENT TRIGGER",
"ALTER EXTENSION",
"ALTER FOREIGN DATA WRAPPER",
"ALTER FOREIGN TABLE",
"ALTER FUNCTION",
"ALTER GROUP",
"ALTER INDEX",
"ALTER LANGUAGE",
"ALTER LARGE OBJECT",
"ALTER MATERIALIZED VIEW",
"ALTER OPERATOR",
"ALTER OPERATOR CLASS",
"ALTER OPERATOR FAMILY",
"ALTER ROLE",
"ALTER RULE",
"ALTER SCHEMA",
"ALTER SEQUENCE",
"ALTER SERVER",
"ALTER TABLE",
"ALTER TABLESPACE",
"ALTER TEXT SEARCH CONFIGURATION",
"ALTER TEXT SEARCH DICTIONARY",
"ALTER TEXT SEARCH PARSER",
"ALTER TEXT SEARCH TEMPLATE",
"ALTER TRIGGER",
"ALTER TYPE",
"ALTER USER",
"ALTER USER MAPPING",
"ALTER VIEW",
"ANALYZE",
"BEGIN",
"CHECKPOINT",
"CLOSE",
"CLUSTER",
"COMMENT",
"COMMIT",
"COMMIT PREPARED",
"COPY",
"CREATE AGGREGATE",
"CREATE CAST",
"CREATE COLLATION",
"CREATE CONVERSION",
"CREATE DATABASE",
"CREATE DOMAIN",
"CREATE EVENT TRIGGER",
"CREATE EXTENSION",
"CREATE FOREIGN DATA WRAPPER",
"CREATE FOREIGN TABLE",
"CREATE FUNCTION",
"CREATE GROUP",
"CREATE INDEX",
"CREATE LANGUAGE",
"CREATE MATERIALIZED VIEW",
"CREATE OPERATOR",
"CREATE OPERATOR CLASS",
"CREATE OPERATOR FAMILY",
"CREATE ROLE",
"CREATE RULE",
"CREATE SCHEMA",
"CREATE SEQUENCE",
"CREATE SERVER",
"CREATE TABLE",
"CREATE TABLE AS",
"CREATE TABLESPACE",
"CREATE TEXT SEARCH CONFIGURATION",
"CREATE TEXT SEARCH DICTIONARY",
"CREATE TEXT SEARCH PARSER",
"CREATE TEXT SEARCH TEMPLATE",
"CREATE TRIGGER",
"CREATE TYPE",
"CREATE USER",
"CREATE USER MAPPING",
"CREATE VIEW",
"DEALLOCATE",
"DECLARE",
"DELETE",
"DISCARD",
"DO",
"DROP AGGREGATE",
"DROP CAST",
"DROP COLLATION",
"DROP CONVERSION",
"DROP DATABASE",
"DROP DOMAIN",
"DROP EXTENSION",
"DROP EVENT TRIGGER",
"DROP FOREIGN DATA WRAPPER",
"DROP FOREIGN TABLE",
"DROP FUNCTION",
"DROP GROUP",
"DROP INDEX",
"DROP LANGUAGE",
"DROP MATERIALIZED VIEW",
"DROP OPERATOR",
"DROP OPERATOR CLASS",
"DROP OPERATOR FAMILY",
"DROP OWNED",
"DROP ROLE",
"DROP RULE",
"DROP SCHEMA",
"DROP SEQUENCE",
"DROP SERVER",
"DROP TABLE",
"DROP TABLESPACE",
"DROP TEXT SEARCH CONFIGURATION",
"DROP TEXT SEARCH DICTIONARY",
"DROP TEXT SEARCH PARSER",
"DROP TEXT SEARCH TEMPLATE",
"DROP TRIGGER",
"DROP TYPE",
"DROP USER",
"DROP USER MAPPING",
"DROP VIEW",
"END",
"EXECUTE",
"EXPLAIN",
"FETCH",
"FROM",
"GRANT",
"INSERT",
"LISTEN",
"LOAD",
"LOCK",
"MOVE",
"NOTIFY",
"PREPARE",
"PREPARE TRANSACTION",
"REASSIGN OWNED",
"REFRESH MATERIALIZED VIEW",
"REINDEX",
"RELEASE SAVEPOINT",
"RESET",
"REVOKE",
"ROLLBACK",
"ROLLBACK PREPARED",
"ROLLBACK TO SAVEPOINT",
"SAVEPOINT",
"SECURITY LABEL",
"SELECT",
"SELECT INTO",
"SET",
"SET CONSTRAINTS",
"SET ROLE",
"SET SESSION AUTHORIZATION",
"SET TRANSACTION",
"SHOW",
"START TRANSACTION",
"TRUNCATE",
"UNLISTEN",
"UPDATE",
"VACUUM",
"VALUES",
]

if __name__ == "__main__":
    from PyQt4 import QtGui
    import sys
    app = QtGui.QApplication(sys.argv)
    editor = QueryEditor()
    editor.show()
    editor.setText(open(sys.argv[0]).read())
    app.exec_()