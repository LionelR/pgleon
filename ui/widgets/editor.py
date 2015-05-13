# -*- coding:utf-8 -*-

__author__ = 'lionel'

from PyQt4 import QtGui, QtCore, Qsci
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


class SqlCompleter(QtGui.QCompleter):
    def __init__(self, parent):
        # # get the wordlist
        # dictionary = None
        # if db:
        # dictionary = db.connector.getSqlDictionary()
        # if not dictionary:
        # # use the generic sql dictionary
        # from .sql_dictionary import getSqlDictionary

        dictionary = getSqlDictionary()

        wordlist = QtCore.QStringList()
        for name, value in dictionary.iteritems():
            wordlist << value

        # setup the completer
        QtGui.QCompleter.__init__(self, sorted(wordlist), parent)
        self.setModelSorting(QtGui.QCompleter.CaseInsensitivelySortedModel)
        self.setWrapAround(False)
        self.setWidget(parent)
        self.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)


class QueryEditor(QtGui.QTextEdit):
    def __init__(self, *args, **kwargs):
        QtGui.QTextEdit.__init__(self, *args, **kwargs)
        self.completer = SqlCompleter(self)
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
        tc = self.textCursor()
        tc.select(QtGui.QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self)
        QtGui.QTextEdit.focusInEvent(self, event)

    def keyPressEvent(self, event):
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Escape, QtCore.Qt.Key_Tab,
                               QtCore.Qt.Key_Backtab):
                event.ignore()
                return

        # has ctrl-E or ctrl-space been pressed??
        isShortcut = event.modifiers() == QtCore.Qt.ControlModifier and event.key() in (
            QtCore.Qt.Key_E, QtCore.Qt.Key_Space)
        if not self.completer or not isShortcut:
            QtGui.QTextEdit.keyPressEvent(self, event)

        # ctrl or shift key on it's own??
        ctrlOrShift = event.modifiers() in (QtCore.Qt.ControlModifier, QtCore.Qt.ShiftModifier)
        if ctrlOrShift and event.text().isEmpty():
            # ctrl or shift key on it's own
            return

        eow = QtCore.QString("~!@#$%^&*()+{}|:\"<>?,./;'[]\\-=")  # end of word

        hasModifier = event.modifiers() != QtCore.Qt.NoModifier and not ctrlOrShift

        completionPrefix = self.textUnderCursor()

        if not isShortcut and (hasModifier or event.text().isEmpty() or
                                       completionPrefix.length() < 3 or eow.contains(event.text().right(1))):
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