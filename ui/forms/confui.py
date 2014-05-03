#-*- coding:utf-8 -*-

__author__ = 'lionel'

from PyQt4 import QtGui, QtCore

class MainUI(QtGui.QMainWindow):

    def __init__(self):
        super(MainUI, self).__init__()

        self.initUI()

    def initUI(self):
        self.menu_bar = self.menuBar()
        self.init_menu()

        self.tool_bar = self.addToolBar('Execute')

        self.list_conf = QtGui.QListView()

        self.host = QtGui.QLineEdit()
        self.user= QtGui.QLineEdit()
        self.password=QtGui.QLineEdit()
        self.db=QtGui.QLineEdit()
        grid_layout = QtGui.QGridLayout()
        grid_layout.addWidget(QtGui.QLabel("Host"), 0, 0)
        grid_layout.addWidget(self.host, 0, 1)
        grid_layout.addWidget(QtGui.QLabel("Database"), 1, 0)
        grid_layout.addWidget(self.db, 1, 1)
        grid_layout.addWidget(QtGui.QLabel("User"), 2, 0)
        grid_layout.addWidget(self.user, 2, 1)
        grid_layout.addWidget(QtGui.QLabel("Password"), 3, 0)
        grid_layout.addWidget(self.password, 3, 1)

        right_widget = QtGui.QWidget()
        right_widget.setLayout(grid_layout)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.list_conf)
        hbox.addWidget(right_widget)

        central_widget = QtGui.QWidget()
        central_widget.setLayout(hbox)
        self.setCentralWidget(central_widget)
        # QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.setGeometry(300, 300, 600, 400)

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

