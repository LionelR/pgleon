#-*- coding:utf-8 -*-

__author__ = 'lionel'

import sys
from PyQt4 import QtGui

from pgleon.src.mainconf import MainConf
from src.conf import title, icon_path


def main():
    app = QtGui.QApplication(sys.argv)
    ex = MainConf(title=title, icon_path=icon_path)
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()