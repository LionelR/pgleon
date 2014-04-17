#-*- coding:utf-8 -*-

__author__ = 'lionel'

import sys
from PyQt4 import QtGui, QtCore

from ui.widgets.qscint import QScint


class MainUI(QtGui.QWidget):

    def __init__(self):
        super(MainUI, self).__init__()

        self.initUI()

    def initUI(self):

        vbox = QtGui.QVBoxLayout(self)

        self.run_btn = QtGui.QPushButton("&Run")
        self.query_editor = QScint(self)
        self.query_result = QtGui.QTableView(self)
        self.query_msg = QtGui.QTextEdit(self)

        tab = QtGui.QTabWidget()

        vlayout1 = QtGui.QVBoxLayout(self.query_result)
        vlayout2 = QtGui.QVBoxLayout(self.query_msg)

        tab.addTab(self.query_result, "Results")
        tab.addTab(self.query_msg, "Messages")

        vsplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        vsplitter.addWidget(self.query_editor)
        vsplitter.addWidget(tab)

        vbox.addWidget(self.run_btn)
        vbox.addWidget(vsplitter)


        self.setLayout(vbox)
        # QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('QtGui.QSplitter')
        self.show()
