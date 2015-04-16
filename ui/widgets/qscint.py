#-*- coding:utf-8 -*-

__author__ = 'lionel'

"""
from http://eli.thegreenplace.net/2011/04/01/sample-using-qscintilla-with-pyqt/
"""

import sys
from PyQt4 import QtGui, Qsci
from PyQt4.Qsci import QsciScintilla, QsciLexerSQL


class QScint(QsciScintilla):
    ARROW_MARKER_NUM = 8

    def __init__(self, parent=None):
        super(QScint, self).__init__(parent)

        # Set the default font
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setMarginsFont(font)

        # Margin 0 is used for line numbers
        fontmetrics = QtGui.QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("0000"))
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QtGui.QColor("#cccccc"))


        # Brace matching: enable for a brace immediately before or after
        # the current position
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Current line visible with special background color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QtGui.QColor("#ffe4e4"))

        # Set lexer
        lexer = QsciLexerSQL()
        lexer.setDefaultFont(font)

        # Create an API for us to populate with our autocomplete terms
        api = Qsci.QsciAPIs(lexer)
        # Add autocompletion strings
        api.add("aLongString")
        api.add("aLongerString")
        api.add("aDifferentString")
        api.add("sOmethingElse")
        # Compile the api for use in the lexer
        api.prepare()

        self.setLexer(lexer)
        # self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, 'Courier')

        # Don't want to see the horizontal scrollbar at all
        # self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

        # Set the length of the string before the editor tries to autocomplete
        self.setAutoCompletionThreshold(1)
        # Tell the editor we are using a QsciAPI for the autocompletion
        self.setAutoCompletionSource(QsciScintilla.AcsAPIs)

        # not too small
        self.setMinimumSize(50, 50)

class EditorWidget(QtGui.QWidget):

    def __init__(self, main):
        QtGui.QWidget.__init__(self)

        self.main = main

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setContentsMargins(0,0,0,0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

        # Set the default font
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setMarginsFont(font)

        # Margin 0 is used for line numbers
        fontmetrics = QtGui.QFontMetrics(font)

        self.editor = QsciScintilla(self)
        self.editor.setUtf8(True)
        self.editor.setFolding(QsciScintilla.BoxedTreeFoldStyle)
        self.editor.setAutoIndent(True)
        self.editor.setMarginsFont(font)
        self.editor.setMarginWidth(0, fontmetrics.width("0000"))
        self.editor.setMarginLineNumbers(0, True)
        self.editor.setMarginsBackgroundColor(QtGui.QColor("#cccccc"))
        self.editor.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        self.editor.setCaretLineVisible(True)
        self.editor.setCaretLineBackgroundColor(QtGui.QColor("#ffe4e4"))
        #self.setCentralWidget(self.editor)
        mainLayout.addWidget(self.editor)

        # Set lexer
        self.lexer = QsciLexerSQL()
        self.lexer.setDefaultFont(font)

        # Create an API for us to populate with our autocomplete terms
        self.api = Qsci.QsciAPIs(self.lexer)
        # Add autocompletion strings
        self.api.add("aLongString")
        self.api.add("aLongerString")
        self.api.add("aDifferentString")
        self.api.add("sOmethingElse")
        # Compile the api for use in the lexer
        self.api.prepare()
        self.editor.setLexer(self.lexer)

        # keywords_file = self.main.settings.def_path().append("/autocomplete.txt")
        # api.load(keywords_file)
        self.api.prepare()
        self.lexer.setAPIs(self.api)

        self.editor.setAutoCompletionThreshold(1)
        self.editor.setAutoCompletionSource(QsciScintilla.AcsAPIs)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    editor = QScint()
    editor.show()
    editor.setText(open(sys.argv[0]).read())
    app.exec_()