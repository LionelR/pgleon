#-*- coding:utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore
import sys

__author__ = 'lionel'

from src import db
from ui.forms.mainui import MainUI
from ui.widgets.qtable import QTableModel


class Main(MainUI):
    def __init__(self):
        super(Main, self).__init__()

        self.run_btn.clicked.connect(self.run_query)


    def run_query(self):
        query = unicode(self.query_editor.text())
        conn = db.Database()
        headers, res = conn.execute(query)
        if isinstance(res, db.DBError):
            self.query_msg.setPlainText(QtCore.QString(res.get_msg()))
        else:
            tm = QTableModel(res, headers, self)
            self.query_result.setModel(tm)


def main():

    app = QtGui.QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()