#-*- coding:utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore
import sys

__author__ = 'lionel'

from src import db
from ui.forms.queryui import MainUI
from ui.widgets.qtable import QTableModel

name = "PGLeon"
version = "0.1"

class Main(MainUI):
    def __init__(self):
        super(Main, self).__init__()
        self.set_title("{0:s} - {1:s}".format(name, version))
        self.set_tool_bar()

    def __execute__(self, prefix=""):
        query = unicode(self.query_editor.text())
        if query.strip()=="":
            return
        query = prefix + unicode(query)
        conn = db.Database()
        headers, res = conn.execute(query)
        if isinstance(res, db.DBError):
            self.query_msg.setPlainText(QtCore.QString(res.get_msg()))
            self.query_msg.setFocus()
        else:
            tm = QTableModel(res, headers, self)
            self.query_result.setModel(tm)
            self.query_result.resizeColumnsToContents()
            self.query_result.resizeRowsToContents()
            # self.query_msg.setPlainText(conn.cur.statusmessage)
            self.set_status(conn.cur.statusmessage)

    def run_query(self):
        self.__execute__()

    def explain_query(self):
        self.__execute__(prefix=u"EXPLAIN ")

    def analyse_query(self):
        self.__execute__(prefix=u"EXPLAIN ANALYSE ")

    def set_tool_bar(self):
        run_action = QtGui.QAction(QtGui.QIcon('icons/run.png'), '&Run', self)
        run_action.setShortcut('Ctrl+R')
        run_action.setStatusTip('Run query')
        run_action.triggered.connect(self.run_query)
        self.tool_bar.addAction(run_action)

        explain_action = QtGui.QAction(QtGui.QIcon('icons/explain.png'), '&Explain', self)
        explain_action.setShortcut('Ctrl+E')
        explain_action.setStatusTip('Explain query')
        explain_action.triggered.connect(self.explain_query)
        self.tool_bar.addAction(explain_action)

        analyse_action = QtGui.QAction(QtGui.QIcon('icons/analyse.png'), '&Analyse', self)
        analyse_action.setShortcut('Ctrl+A')
        analyse_action.setStatusTip('Analyse query')
        analyse_action.triggered.connect(self.analyse_query)
        self.tool_bar.addAction(analyse_action)

def main():

    app = QtGui.QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()