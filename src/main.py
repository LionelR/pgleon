#-*- coding:utf-8 -*-

__author__ = 'lionel'

import sys
from PyQt4 import QtGui
from mainconf import MainConf


name = "PGLeon"
version = "0.1"

title = "{0:s} - {1:s}".format(name, version)


def main():
    app = QtGui.QApplication(sys.argv)
    # app.setOrganizationName(name)
    app.setApplicationName(name)
    from src import conf # Generate the configuration database
    ex = MainConf(title=name)
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()