# -*- coding:utf-8 -*-

__author__ = 'lionel'

"""
Largely inspired by
http://doc.qt.digia.com/4.6/tools-customcompleter.html
https://john.nachtimwald.com/2009/08/19/better-qplaintextedit-with-line-numbers/
and the QGiS dbmanager plugin and
"""

import logging
logger = logging.getLogger(__name__)

from PyQt4 import QtGui, QtCore
from pygments import highlight
from pygments.lexers import sql
from pygments.formatter import Formatter
from pygments.lexers._postgres_builtins import KEYWORDS, DATATYPES, PSEUDO_TYPES, PLPGSQL_KEYWORDS
import src.explorer_model as em



def getSqlDictionary():
    return {'KEYWORDS': KEYWORDS,
            'DATATYPES': DATATYPES,
            'PSEUDO_TYPES': PSEUDO_TYPES,
            'PLPGSQL_KEYWORDS': PLPGSQL_KEYWORDS
    }


def hex2QColor(c):
    r = int(c[0:2], 16)
    g = int(c[2:4], 16)
    b = int(c[4:6], 16)
    return QtGui.QColor(r, g, b)


class QFormatter(Formatter):
    def __init__(self):
        Formatter.__init__(self)
        self.data = []

        # Create a dictionary of text styles, indexed
        # by pygments token names, containing QTextCharFormat
        # instances according to pygments' description
        # of each style

        self.styles = {}
        for token, style in self.style:
            qtf = QtGui.QTextCharFormat()

            if style['color']:
                qtf.setForeground(hex2QColor(style['color']))
            if style['bgcolor']:
                qtf.setBackground(hex2QColor(style['bgcolor']))
            if style['bold']:
                qtf.setFontWeight(QtGui.QFont.Bold)
            if style['italic']:
                qtf.setFontItalic(True)
            if style['underline']:
                qtf.setFontUnderline(True)
            self.styles[str(token)] = qtf
        # missing token
        self.styles['Token.Literal.String.Name'] = self.styles['Token.Literal.String']

    def format(self, tokensource, outfile):
        # global styles
        # We ignore outfile, keep output in a buffer
        self.data = []

        # Just store a list of styles, one for each character
        # in the input. Obviously a smarter thing with
        # offsets and lengths is a good idea!

        for ttype, value in tokensource:
            l = len(value)
            t = str(ttype)
            # if t in self.styles.keys():
            self.data.extend([self.styles[t], ] * l)


class SqlHighlighter(QtGui.QSyntaxHighlighter):
    # from ralsina.me/static/highlighter.py
    def __init__(self, parent):
        QtGui.QSyntaxHighlighter.__init__(self, parent)

        # Keep the formatter and lexer, initializing them
        # may be costly.
        self.formatter = QFormatter()
        self.lexer = sql.PostgresLexer()

    def highlightBlock(self, text):
        """Takes a block, applies format to the document.
        according to what's in it.
        """

        # I need to know where in the document we are,
        # because our formatting info is global to
        # the document
        cb = self.currentBlock()
        p = cb.position()

        # The \n is not really needed, but sometimes
        # you are in an empty last block, so your position is
        # **after** the end of the document.
        text = unicode(self.document().toPlainText()) + '\n'

        # Yes, re-highlight the whole document.
        # There **must** be some optimizacion possibilities
        # but it seems fast enough.
        highlight(text, self.lexer, self.formatter)

        # Just apply the formatting to this block.
        # For titles, it may be necessary to backtrack
        # and format a couple of blocks **earlier**.
        for i in range(len(unicode(text))):
            try:
                self.setFormat(i, 1, self.formatter.data[p + i])
            except IndexError:
                pass


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
            'OTHER': QtGui.QIcon(QtGui.QPixmap(':/star.png')),
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
            'OTHER': em.Node,
        }

        super(CompletionModel, self).__init__(None, self.parent, "Database Model")
        self._rootNode = em.Node(self.database, parent=None, icon=self.icons['DATABASE'])
        self.setupDBStructureModel()
        self.setupDictionnaryModel()

    def setupDBStructureModel(self):
        """Add database structure informations to the model
        """
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
        headers, res, status = self.database.execute(query)

        # populate data
        parentSchema = None
        for schema, type_, name, oid in res:
            if schema != parentSchema:  # On changing/first schema in the list
                schemaItem = em.SchemaNode(schema, parent=self._rootNode, icon=self.icons['SCHEMA'])
                parentSchema = schema  # Set the schema name as the parent
            if type_ in self.nodes.keys():
                node = self.nodes[type_](name, oid=oid, parent=schemaItem, icon=self.icons[type_])

    def setupDictionnaryModel(self):
        dictionary = getSqlDictionary()
        type_ = 'OTHER'
        for nameList in dictionary.itervalues():
            for name in nameList:
                self.nodes[type_](name, oid=None, parent=self._rootNode, icon=self.icons[type_])


class SqlCompleter(QtGui.QCompleter):
    def __init__(self, *args):
        # dictionary = getSqlDictionary()
        # wordlist = QtCore.QStringList()
        # for name, value in dictionary.iteritems():
        # wordlist << value

        # setup the completer
        super(SqlCompleter, self).__init__(*args)
        # self.setModelSorting(QtGui.QCompleter.CaseInsensitivelySortedModel)
        self.setModelSorting(QtGui.QCompleter.UnsortedModel)
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


class SqlEdit(QtGui.QPlainTextEdit):

    def __init__(self, *args, **kwargs):
        super(SqlEdit, self).__init__(*args, **kwargs)
        # QtGui.QTextEdit.__init__(self, *args, **kwargs)
        self.completer = SqlCompleter()
        self.completer.setWidget(self)
        self.highlighter = SqlHighlighter(self.document())

        self.setFrameStyle(QtGui.QFrame.NoFrame)
        self.highlight()
        #self.setLineWrapMode(QPlainTextEdit.NoWrap)
        # self.setStyleSheet("background-color: grey")

        self.font =QtGui.QFont("Monospace", 10)
        self.font.setStyleHint(QtGui.QFont.Courier)
        self.document().setDefaultFont(self.font)
        fontMetrics = QtGui.QFontMetrics(self.font)
        self.setTabStopWidth(fontMetrics.width(' ') * 4)

        self.cursorPositionChanged.connect(self.highlight)
        self.connect(self.completer, QtCore.SIGNAL("activated(const QString&)"), self.insertCompletion)

    def insertCompletion(self, completion):
        # tc = self.textCursor()
        # extra = completion.length() - self.completer.completionPrefix().length()
        # tc.movePosition(QtGui.QTextCursor.Left)
        # tc.movePosition(QtGui.QTextCursor.EndOfWord)
        # tc.insertText(completion.right(extra))
        # self.setTextCursor(tc)
        tc = self.textCursor()
        tc.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor, self.completer.completionPrefix().length())
        tc.insertText(completion)
        self.setTextCursor(tc)

    def textUnderCursor(self):
        # Hack for searching the word under the cursor because WordUnderCursor doesn't take
        # care of dots, but we need them
        tc = self.textCursor()
        isStartOfWord = False
        if tc.atStart() or (tc.positionInBlock() == 0):
            isStartOfWord = True
        while not isStartOfWord:
            tc.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)
            if tc.atStart() or (tc.positionInBlock() == 0):
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

    def setText(self, t):
        self.text(t)

    def highlight(self):
        hi_selection = QtGui.QTextEdit.ExtraSelection()
        hi_selection.format.setBackground(self.palette().alternateBase())
        hi_selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, QtCore.QVariant(True))
        hi_selection.cursor = self.textCursor()
        hi_selection.cursor.clearSelection()
        self.setExtraSelections([hi_selection])

    def numberbarPaint(self, number_bar, event):
        font_metrics = self.fontMetrics()
        current_line = self.document().findBlock(self.textCursor().position()).blockNumber() + 1

        block = self.firstVisibleBlock()
        line_count = block.blockNumber()
        painter = QtGui.QPainter(number_bar)
        painter.fillRect(event.rect(), self.palette().base())

        # Iterate over all visible text blocks in the document.
        while block.isValid():
            line_count += 1
            block_top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()

            # Check if the position of the block is out side of the visible area.
            if not block.isVisible() or block_top >= event.rect().bottom():
                break

            # We want the line number for the selected line to be bold.
            if line_count == current_line:
                font = painter.font()
                font.setBold(True)
                painter.setFont(font)
            else:
                font = painter.font()
                font.setBold(False)
                painter.setFont(font)

            # Draw the line number right justified at the position of the line.
            paint_rect = QtCore.QRect(0, block_top, number_bar.width(), font_metrics.height())
            painter.drawText(paint_rect, QtCore.Qt.AlignRight, unicode(line_count))

            block = block.next()

        painter.end()


class NumberBar(QtGui.QWidget):
    def __init__(self, edit):
        QtGui.QWidget.__init__(self, edit)
        self.edit = edit
        self.adjustWidth(1)

    def paintEvent(self, event):
        self.edit.numberbarPaint(self, event)
        QtGui.QWidget.paintEvent(self, event)

    def adjustWidth(self, count):
        width = self.fontMetrics().width(unicode(count))
        if self.width() != width:
            self.setFixedWidth(width)

    def updateContents(self, rect, scroll):
        if scroll:
            self.scroll(0, scroll)
        else:
            # It would be nice to do
            # self.update(0, rect.y(), self.width(), rect.height())
            # But we can't because it will not remove the bold on the
            # current line if word wrap is enabled and a new block is
            # selected.
            self.update()


class QueryEditor(QtGui.QFrame):
    def __init__(self, *args):
        QtGui.QFrame.__init__(self, *args)
        self.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken)
        self.edit = SqlEdit()
        self.number_bar = NumberBar(self.edit)

        hbox = QtGui.QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setMargin(0)
        hbox.addWidget(self.number_bar)
        hbox.addWidget(self.edit)

        self.edit.blockCountChanged.connect(self.number_bar.adjustWidth)
        self.edit.updateRequest.connect(self.number_bar.updateContents)

    def getText(self):
        return self.edit.getText()

    def setText(self, text):
        self.edit.setText(text)

    def setCompletionModel(self, database):
        self.edit.setCompletionModel(database)

    def isModified(self):
        return self.edit.document().isModified()

    def setModified(self, modified):
        self.edit.document().setModified(modified)

    def setLineWrapMode(self, mode):
        self.edit.setLineWrapMode(mode)

if __name__ == "__main__":
    from PyQt4 import QtGui
    import sys

    app = QtGui.QApplication(sys.argv)
    editor = QueryEditor()
    editor.show()
    editor.setText(open(sys.argv[0]).read())
    app.exec_()