#-*- coding:utf-8 -*-

__author__ = 'lionel'

import sys
from PyQt4 import QtGui, QtCore

from ui.widgets.qscint import QScint


# class MainUI(QtGui.QWidget):
class MainUI(QtGui.QMainWindow):

    def __init__(self):
        super(MainUI, self).__init__()

        self.initUI()

    def initUI(self):

        self.menu_bar = self.menuBar()
        self.init_menu()

        self.tool_bar = self.addToolBar('Execute')

        self.central_widget = QtGui.QWidget()
        self.query_editor = QScint(self.central_widget)
        self.query_result = QtGui.QTableView(self.central_widget)
        self.query_msg = QtGui.QTextEdit(self.central_widget)

        tab = QtGui.QTabWidget()
        tab.addTab(self.query_result, "Results")
        tab.addTab(self.query_msg, "Messages")

        vsplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        vsplitter.addWidget(self.query_editor)
        vsplitter.addWidget(tab)

        vbox = QtGui.QVBoxLayout(self.central_widget)
        vbox.addWidget(vsplitter)

        self.central_widget.setLayout(vbox)
        self.setCentralWidget(self.central_widget)
        # QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.setGeometry(300, 300, 600, 400)

        self.status_bar = self.statusBar()
        self.permanent_status_label = QtGui.QLabel()
        self.status_bar.addPermanentWidget(self.permanent_status_label)
        self.set_status('Ready')

        self.show()

    def init_menu(self):
        exit_action = QtGui.QAction(QtGui.QIcon('icons/exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QtGui.qApp.quit)

        file_menu = self.menu_bar.addMenu('&File')
        file_menu.addAction(exit_action)

    def set_title(self, title):
        self.setWindowTitle(title)

    def set_status(self, status):
        # self.status_bar.showMessage(status)
        self.permanent_status_label.setText(QtCore.QString(status))

    def closeEvent(self, event):
        settings = QtCore.QSettings("MyCompany", "MyApp")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        # self.closeEvent(event)


