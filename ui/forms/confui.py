#-*- coding:utf-8 -*-

__author__ = 'lionel'

from PyQt4 import QtGui, QtCore
from src.conf import Connection


class MyStandardItem(QtGui.QStandardItem):
    """Inherited QStandardItem to append connection information to it"""
    def __init__(self, *args, **kwargs):
        super(MyStandardItem, self).__init__(*args, **kwargs)
        self.conn = None

    def set_conn(self, conn):
        self.conn = conn

    def get_conn(self):
        return self.conn


class MainUI(QtGui.QMainWindow):
    def __init__(self):
        super(MainUI, self).__init__()

        self.initUI()

    def initUI(self):
        #Menu bar
        self.init_menu()

        #Left side
        self.conn_list = QtGui.QListView()
        self.append_btn = QtGui.QPushButton("+")
        self.delete_btn = QtGui.QPushButton("-")
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addStretch(1)
        hbox1.addWidget(self.append_btn)
        hbox1.addWidget(self.delete_btn)
        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.conn_list)
        vbox1.addLayout(hbox1)

        #Right side
        self.host = QtGui.QLineEdit()
        self.port = QtGui.QLineEdit()
        self.database = QtGui.QLineEdit()
        self.user = QtGui.QLineEdit()
        self.password = QtGui.QLineEdit()
        form = QtGui.QFormLayout()
        form.addRow("Host", self.host)
        form.addRow("Port", self.port)
        form.addRow("Database", self.database)
        form.addRow("User", self.user)
        form.addRow("Password", self.password)
        self.save_btn = QtGui.QPushButton('Save')
        self.test_btn = QtGui.QPushButton('Test')
        self.open_btn = QtGui.QPushButton('Open')
        hbox2 = QtGui.QHBoxLayout()
        hbox2.addStretch(1)
        hbox2.addWidget(self.save_btn)
        hbox2.addWidget(self.test_btn)
        hbox2.addWidget(self.open_btn)
        vbox2 = QtGui.QVBoxLayout()
        vbox2.addLayout(form)
        vbox2.addLayout(hbox2)

        hbox3 = QtGui.QHBoxLayout()
        hbox3.addLayout(vbox1)
        hbox3.addLayout(vbox2)

        central_widget = QtGui.QWidget()
        central_widget.setLayout(hbox3)
        self.setCentralWidget(central_widget)
        # QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))
        self.setGeometry(300, 300, 600, 400)

        # All others stuffs
        self.model_conn_list = QtGui.QStandardItemModel(self.conn_list)
        self.conn_list.setModel(self.model_conn_list)
        self.conn_list.clicked.connect(self.on_item_changed)
        self.append_btn.clicked.connect(self.on_add)
        self.delete_btn.clicked.connect(self.on_delete)
        self.save_btn.clicked.connect(self.on_save)
        self.populate()
        self.show()

    def init_menu(self):
        self.menu_bar = self.menuBar()

        exit_action = QtGui.QAction(QtGui.QIcon('icons/exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(QtGui.qApp.quit)

        file_menu = self.menu_bar.addMenu('&File')
        file_menu.addAction(exit_action)

    def set_title(self, title):
        self.setWindowTitle(title)

    def populate(self):
        """Append connections informations to the left list"""
        self.model_conn_list.clear()
        for conn in Connection.select():
            print(conn.database)
            name = "{0:s} ({1:s}) : {2:s} [{3:s}]".format(conn.host, conn.port, conn.database, conn.user)
            item = MyStandardItem(name)
            item.set_conn(conn)
            self.model_conn_list.appendRow(item)

    def on_item_changed(self, index):
        """When the user select/change a item in the left list of connections"""
        item = self.model_conn_list.itemFromIndex(index)
        conn = item.get_conn()
        if conn is None:
            return
        self.host.setText(conn.host)
        self.port.setText(conn.port)
        self.database.setText(conn.database)
        self.user.setText(conn.user)
        self.password.setText(conn.password)

    def on_add(self):
        """Add a new connection by presenting the left list with an empty item and
            the rights fields blank"""
        item = MyStandardItem("Temporary connection")
        item.set_conn(None)
        self.model_conn_list.appendRow(item)
        index = self.model_conn_list.indexFromItem(item)
        self.conn_list.setCurrentIndex(index)
        self.host.setText("localhost")
        self.port.setText("5432")
        self.database.setText("postgres")
        self.user.clear()
        self.password.clear()
        self.append_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)


    def on_delete(self):
        """Delete a connection"""
        index = self.conn_list.currentIndex()
        item = index.model().itemFromIndex(index)
        conn = item.get_conn()
        if conn in Connection.select():
            conn.delete_instance()
            self.populate()

    def on_save(self):
        host = unicode(self.host.text())
        port = unicode(self.port.text())
        database = unicode(self.database.text())
        user = unicode(self.user.text())
        password = unicode(self.password.text())
        conn = Connection(host=host, port=port, database=database, user=user, password=password)
        conn.save()
        self.populate()