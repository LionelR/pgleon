#-*- coding:utf-8 -*-
from PyQt4 import QtGui
from PyQt4 import QtCore
import sys

__author__ = 'lionel'

from src import db
from ui.forms.confui import MainUI

name = "PGLeon"
version = "0.1"

class Main(MainUI):
    def __init__(self):
        super(Main, self).__init__()
        self.set_title("{0:s} - {1:s}".format(name, version))

    def append(self):
        pass

    def delete(self):
        pass

    def launch(self):
        pass

    def set_tool_bar(self):
        append_action = QtGui.QAction(QtGui.QIcon('icons/run.png'), '&Run', self)
        append_action.setShortcut('Ctrl+R')
        append_action.setStatusTip('Run query')
        append_action.triggered.connect(self.append)
        self.tool_bar.addAction(append_action)

        delete_action = QtGui.QAction(QtGui.QIcon('icons/explain.png'), '&Explain', self)
        delete_action.setShortcut('Ctrl+E')
        delete_action.setStatusTip('Explain query')
        delete_action.triggered.connect(self.delete)
        self.tool_bar.addAction(delete_action)

        launch_action = QtGui.QAction(QtGui.QIcon('icons/analyse.png'), '&Analyse', self)
        launch_action.setShortcut('Ctrl+A')
        launch_action.setStatusTip('Analyse query')
        launch_action.triggered.connect(self.launch)
        self.tool_bar.addAction(launch_action)

def main():

    app = QtGui.QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()