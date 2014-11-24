#-*- coding:utf-8 -*-

__author__ = 'lionel'

"""
from: http://www.saltycrane.com/blog/2007/12/pyqt-43-qtableview-qabstracttablemodel/
"""

import operator
from PyQt4.QtCore import *


class QTableModel(QAbstractTableModel):
    def __init__(self, res, headers, parent=None, *args):
        """ res: a list of lists
            headers: a list of strings
        """
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = res
        self.headers = headers

    def rowCount(self, parent):
        return len(self.arraydata)

    def columnCount(self, parent):
        # if not self.arraydata:
        #     return 0
        # return len(self.arraydata[0])
        return len(self.headers)

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.arraydata[index.row()][index.column()])

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.headers[col])
        return QVariant()

    def sort(self, Ncol, order):
        """Sort table by given column number.
        """
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(Ncol))
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()
        self.emit(SIGNAL("layoutChanged()"))

    def addRow(self, row):
        # we insert new row at the end of the model
        nRow = self.rowCount(None)
        self.beginInsertRows(QModelIndex(), nRow, nRow)
        self.arraydata.append(row)
        self.endInsertRows()
        return True


