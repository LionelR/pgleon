#!/usr/bin/env python
# -*- coding: utf-8 -*-

# based on
# https://qt.gitorious.org/pyside/pyside-examples/source/060dca8e4b82f301dfb33a7182767eaf8ad3d024:examples/itemviews/simpletreemodel/simpletreemodel.py

from PyQt4 import QtCore, QtGui
import re


class TreeItem(object):
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            return self.itemData[column]
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0


class ExplainModel(QtCore.QAbstractItemModel):
    def __init__(self, data, parent=None):
        super(ExplainModel, self).__init__(parent)
        self.maxInclusive = None
        self.rootItem = TreeItem(("Query plan", "Inclusive", "Estimated cost", "Estimated end", "Estimated rows", "Estimated width", "Actual time", "Actual end", "Actual rows", "Actual loops"))
        self.setupModelData(data, self.rootItem)

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        # if role == QtCore.Qt.EditRole:
        #     return self.rootItem.data(0)

        item = index.internalPointer()

        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())

        if role == QtCore.Qt.BackgroundRole :
        # if role == QtCore.Qt.DecorationRole:
            if index.column() != 1: # not the inclusive computed column
                return
            else:
                if item.data(index.column()) is None:
                    return
                value = float(item.data(index.column()))
                ratio = value/self.maxInclusive
                if ratio > 0.9:
                    return QtGui.QColor(136, 0, 0) # red
                elif ratio > 0.5:
                    return QtGui.QColor(238, 136, 0) # orange
                elif ratio > 0.1:
                    return QtGui.QColor(255, 238, 136) # yellow
                else:
                    return

        if role == QtCore.Qt.ForegroundRole :
            if index.column() != 1: # not the inclusive computed column
                return
            else:
                value = float(item.data(index.column()))
                ratio = value/self.maxInclusive
                if ratio > 0.5:
                    return QtGui.QColor(255, 255, 255) # orange or red background
                else:
                    return

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.rootItem.data(section)
        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def setupModelData(self, lines, parent):
        parents = [parent]
        indentations = [0]

        lineNumber = 0

        while lineNumber < len(lines):
            line = lines[lineNumber][0]
            position = 0
            while position < len(line):
                if line[position] != ' ':
                    break
                position += 1
            lineData = line[position:].strip()

            if lineData:
                pre = re.compile("\(cost=(?P<coststart>\d+\.\d+)\.\.(?P<costend>\d+\.\d+)\s+rows=(?P<costrows>\d+)\s+width=(?P<costwidth>\d+)\)\s*(\(actual\stime=(?P<actualtime>\d+\.\d+)\.\.(?P<actualend>\d+\.\d+)\s+rows=(?P<actualrows>\d+)\s+loops=(?P<actualloops>\d+)\))?")
                m = pre.search(lineData)
                if m:
                    if m.group("actualend") is not None and m.group("actualloops") is not None:
                        inclusive = float(m.group("actualend")) * float(m.group("actualloops"))
                        if lineNumber == 0:
                            self.maxInclusive = inclusive
                    else:
                        inclusive = None
                    rowData = [lineData,
                               inclusive,
                               m.group("coststart"),
                               m.group("costend"),
                               m.group("costrows"),
                               m.group("costwidth"),
                               m.group("actualtime"),
                               m.group("actualend"),
                               m.group("actualrows"),
                               m.group("actualloops")]
                else:
                    rowData = [lineData, None, None, None, None, None, None, None, None, None]

                if position > indentations[-1]:
                    # The last child of the current parent is now the new
                    # parent unless the current parent has no children.

                    if parents[-1].childCount() > 0:
                        parents.append(parents[-1].child(parents[-1].childCount() - 1))
                        indentations.append(position)

                else:
                    while position < indentations[-1] and len(parents) > 0:
                        parents.pop()
                        indentations.pop()

                # Append a new item to the current parent's list of children.
                newtreeitem = TreeItem(rowData, parents[-1])
                parents[-1].appendChild(newtreeitem)

            lineNumber += 1


class MyCompleter(QtGui.QCompleter):
    def splitPath(self, path):
        return path.split('.')

    def pathFromIndex(self, index):
        result = []
        while index.isValid():
            result = [self.model().data(index, QtCore.Qt.DisplayRole)] + result
            index = index.parent()
        r = '.'.join(result)
        return r

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)

    data = '''
CTE Scan on emi_par_numcom emi  (cost=24571.63..24796.24 rows=9983 width=724) (actual time=1395.614..1573.980 rows=16079 loops=1)
  CTE fe
    ->  Subquery Scan on fe  (cost=11701.46..11730.14 rows=6 width=774) (actual time=1130.675..1131.811 rows=23 loops=1)
          ->  CTE Scan on tout_fe  (cost=11701.46..11730.08 rows=6 width=775) (actual time=1130.673..1131.798 rows=23 loops=1)
                Filter: ((snap)::text = '060104'::text)
                CTE annee_ref
                  ->  HashAggregate  (cost=1.10..1.18 rows=8 width=20) (actual time=0.055..0.058 rows=6 loops=1)
                        ->  Seq Scan on regions_a_calculer  (cost=0.00..1.08 rows=8 width=20) (actual time=0.038..0.045 rows=14 loops=1)
                CTE tout_annee
                  ->  HashAggregate  (cost=97.82..110.53 rows=1271 width=74) (actual time=2.223..2.574 rows=1011 loops=1)
                        ->  Append  (cost=0.00..69.22 rows=1271 width=74) (actual time=0.090..1.263 rows=1011 loops=1)
                              ->  Nested Loop  (cost=0.00..35.00 rows=1040 width=77) (actual time=0.089..0.846 rows=780 loops=1)
                                    ->  CTE Scan on annee_ref  (cost=0.00..0.16 rows=8 width=20) (actual time=0.057..0.063 rows=6 loops=1)
                                    ->  Materialize  (cost=0.00..22.16 rows=130 width=57) (actual time=0.005..0.076 rows=130 loops=6)
                                          ->  Seq Scan on fe_autres_que_0202 fe  (cost=0.00..21.51 rows=130 width=57) (actual time=0.027..0.255 rows=130 loops=1)
                                                Filter: ((annee_ref)::text = 'tt'::text)
                              ->  Seq Scan on fe_autres_que_0202 fe  (cost=0.00..21.51 rows=231 width=61) (actual time=0.014..0.136 rows=231 loops=1)
                                    Filter: ((annee_ref)::text <> 'tt'::text)
                CTE tout_fe
                  ->  HashAggregate  (cost=11577.03..11589.75 rows=1272 width=783) (actual time=1130.630..1130.986 rows=1011 loops=1)
                        ->  Append  (cost=7868.59..11548.41 rows=1272 width=783) (actual time=952.975..1129.498 rows=1011 loops=1)
                              ->  Merge Right Join  (cost=7868.59..11510.27 rows=636 width=775) (actual time=952.973..1128.832 rows=216 loops=1)
                                    Merge Cond: (((tot.polluant)::text = (fe.polluant)::text) AND ((tot.napfue)::text = (fe.napfue)::text) AND ((tot.annee_ref)::text = (fe.annee_ref)::text))
                                    ->  Merge Left Join  (cost=7813.55..10424.76 rows=58518 width=472) (actual time=944.499..1117.873 rows=10884 loops=1)
                                          Merge Cond: (((tot.polluant)::text = (fe_spe.polluant)::text) AND ((tot.napfue)::text = (fe_spe.napfue)::text) AND ((tot.annee_ref)::text = (fe_spe.annee_ref)::text))
                                          Filter: (COALESCE(((2000::double precision * (teneur_souffre.teneur_souffre_pourcentage / 100::double precision)) * (1::double precision / (pci.pci / 42000::double precision))), fe_spe.fe, fe_tt.fe) IS NOT NULL)
                                          CTE annee
                                            ->  HashAggregate  (cost=15.07..15.33 rows=26 width=5) (actual time=0.548..0.575 rows=26 loops=1)
                                                  ->  Seq Scan on region region_copy  (cost=0.00..13.26 rows=726 width=5) (actual time=0.034..0.269 rows=732 loops=1)
                                          CTE polluant
                                            ->  HashAggregate  (cost=22.90..23.19 rows=29 width=4) (actual time=0.606..0.613 rows=29 loops=1)
                                                  ->  Seq Scan on fe_defaut  (cost=0.00..21.12 rows=712 width=4) (actual time=0.013..0.342 rows=712 loops=1)
                                          CTE tot
                                            ->  Nested Loop  (cost=0.00..753.01 rows=58812 width=142) (actual time=1.190..32.578 rows=60320 loops=1)
                                                  ->  Nested Loop  (cost=0.00..15.89 rows=754 width=138) (actual time=1.164..1.759 rows=754 loops=1)
                                                        ->  CTE Scan on annee  (cost=0.00..0.52 rows=26 width=20) (actual time=0.550..0.597 rows=26 loops=1)
                                                        ->  CTE Scan on polluant  (cost=0.00..0.58 rows=29 width=118) (actual time=0.024..0.033 rows=29 loops=26)
                                                  ->  Materialize  (cost=0.00..2.17 rows=78 width=4) (actual time=0.000..0.014 rows=80 loops=754)
                                                        ->  Seq Scan on napfue  (cost=0.00..1.78 rows=78 width=4) (actual time=0.014..0.031 rows=80 loops=1)
                                          CTE fe_spe
                                            ->  Seq Scan on fe_defaut  (cost=0.00..22.90 rows=303 width=105) (actual time=0.052..0.193 rows=303 loops=1)
                                                  Filter: ((annee_ref)::text <> 'tt'::text)
                                          CTE fe_tt
                                            ->  Nested Loop  (cost=0.00..157.37 rows=10634 width=42) (actual time=0.038..6.413 rows=10634 loops=1)
                                                  ->  CTE Scan on annee  (cost=0.00..0.52 rows=26 width=20) (actual time=0.002..0.024 rows=26 loops=1)
                                                  ->  Materialize  (cost=0.00..24.95 rows=409 width=22) (actual time=0.001..0.089 rows=409 loops=26)
                                                        ->  Seq Scan on fe_defaut  (cost=0.00..22.90 rows=409 width=22) (actual time=0.029..0.294 rows=409 loops=1)
                                                              Filter: ((annee_ref)::text = 'tt'::text)
                                          ->  Merge Left Join  (cost=6823.20..7966.18 rows=58812 width=346) (actual time=941.443..1078.478 rows=59305 loops=1)
                                                Merge Cond: (((tot.polluant)::text = (fe_tt.polluant)::text) AND ((tot.napfue)::text = (fe_tt.napfue)::text) AND ((tot.annee_ref)::text = (fe_tt.annee_ref)::text))
                                                ->  Merge Left Join  (cost=5899.30..6494.07 rows=58812 width=220) (actual time=815.456..850.389 rows=59305 loops=1)
                                                      Merge Cond: (((tot.polluant)::text = (teneur_souffre.polluant)::text) AND ((tot.napfue)::text = (teneur_souffre.napfue)::text) AND ((tot.annee_ref)::text = (teneur_souffre.annee_ref)::text))
                                                      ->  Sort  (cost=5835.27..5982.30 rows=58812 width=172) (actual time=815.418..827.812 rows=59305 loops=1)
                                                            Sort Key: tot.polluant, tot.napfue, tot.annee_ref
                                                            Sort Method: quicksort  Memory: 4445kB
                                                            ->  CTE Scan on tot  (cost=0.00..1176.24 rows=58812 width=172) (actual time=1.192..70.272 rows=60320 loops=1)
                                                      ->  Sort  (cost=64.02..65.67 rows=660 width=62) (actual time=0.031..0.031 rows=0 loops=1)
                                                            Sort Key: teneur_souffre.polluant, teneur_souffre.napfue, teneur_souffre.annee_ref
                                                            Sort Method: quicksort  Memory: 25kB
                                                            ->  Hash Join  (cost=7.44..33.11 rows=660 width=62) (actual time=0.004..0.004 rows=0 loops=1)
                                                                  Hash Cond: ((teneur_souffre.napfue)::text = (pci.napfue)::text)
                                                                  ->  Seq Scan on teneur_souffre  (cost=0.00..16.60 rows=660 width=22) (actual time=0.002..0.002 rows=0 loops=1)
                                                                  ->  Hash  (cost=6.51..6.51 rows=74 width=32) (never executed)
                                                                        ->  Hash Join  (cost=2.75..6.51 rows=74 width=32) (never executed)
                                                                              Hash Cond: ((pci.napfue)::text = (general.napfue.napfue)::text)
                                                                              ->  Seq Scan on pci  (cost=0.00..2.74 rows=74 width=28) (never executed)
                                                                              ->  Hash  (cost=1.78..1.78 rows=78 width=4) (never executed)
                                                                                    ->  Seq Scan on napfue  (cost=0.00..1.78 rows=78 width=4) (never executed)
                                                ->  Sort  (cost=923.90..950.49 rows=10634 width=302) (actual time=125.975..128.580 rows=10581 loops=1)
                                                      Sort Key: fe_tt.polluant, fe_tt.napfue, fe_tt.annee_ref
                                                      Sort Method: quicksort  Memory: 1215kB
                                                      ->  CTE Scan on fe_tt  (cost=0.00..212.68 rows=10634 width=302) (actual time=0.042..14.125 rows=10634 loops=1)
                                          ->  Sort  (cost=18.55..19.31 rows=303 width=302) (actual time=2.963..3.054 rows=303 loops=1)
                                                Sort Key: fe_spe.polluant, fe_spe.napfue, fe_spe.annee_ref
                                                Sort Method: quicksort  Memory: 48kB
                                                ->  CTE Scan on fe_spe  (cost=0.00..6.06 rows=303 width=302) (actual time=0.059..0.461 rows=303 loops=1)
                                    ->  Sort  (cost=55.03..56.62 rows=636 width=735) (actual time=4.738..4.790 rows=216 loops=1)
                                          Sort Key: fe.polluant, fe.napfue, fe.annee_ref
                                          Sort Method: quicksort  Memory: 49kB
                                          ->  CTE Scan on tout_annee fe  (cost=0.00..25.42 rows=636 width=735) (actual time=2.249..3.382 rows=216 loops=1)
                                                Filter: (fe_defaut IS TRUE)
                              ->  CTE Scan on tout_annee fe  (cost=0.00..25.42 rows=636 width=791) (actual time=0.004..0.350 rows=795 loops=1)
                                    Filter: (fe_defaut IS FALSE)
  CTE pop_totale
    ->  HashAggregate  (cost=5985.45..5985.52 rows=7 width=9) (actual time=262.607..262.611 rows=7 loops=1)
          ->  Seq Scan on population  (cost=0.00..4704.30 rows=256230 width=9) (actual time=0.003..85.100 rows=256230 loops=1)
  CTE conso_peinture_par_habitant
    ->  Hash Join  (cost=0.23..1.50 rows=7 width=36) (actual time=262.715..262.725 rows=7 loops=1)
          Hash Cond: ((v.annee_ref)::text = (p.annee_ref)::text)
          ->  Seq Scan on vente_peinture v  (cost=0.00..1.12 rows=12 width=28) (actual time=0.016..0.019 rows=14 loops=1)
          ->  Hash  (cost=0.14..0.14 rows=7 width=28) (actual time=262.632..262.632 rows=7 loops=1)
                Buckets: 1024  Batches: 1  Memory Usage: 1kB
                ->  CTE Scan on pop_totale p  (cost=0.00..0.14 rows=7 width=28) (actual time=262.615..262.624 rows=7 loops=1)
  CTE emi_par_numcom
    ->  Hash Join  (cost=3.82..6854.47 rows=9983 width=659) (actual time=1395.593..1555.333 rows=16079 loops=1)
          Hash Cond: (((p.annee_ref)::text = (c.annee_ref)::text) AND ((p.numreg)::text = (general.regions_a_calculer.numreg)::text))
          ->  Seq Scan on population p  (cost=0.00..4704.30 rows=256230 width=18) (actual time=0.013..51.264 rows=256230 loops=1)
          ->  Hash  (cost=3.73..3.73 rows=6 width=698) (actual time=1394.815..1394.815 rows=12 loops=1)
                Buckets: 1024  Batches: 1  Memory Usage: 2kB
                ->  Hash Join  (cost=1.60..3.73 rows=6 width=698) (actual time=1394.770..1394.803 rows=12 loops=1)
                      Hash Cond: ((fe.annee_ref)::text = (c.annee_ref)::text)
                      ->  Hash Join  (cost=1.38..3.42 rows=6 width=670) (actual time=1132.014..1132.042 rows=14 loops=1)
                            Hash Cond: ((fe.annee_ref)::text = (general.regions_a_calculer.annee_ref)::text)
                            ->  Hash Join  (cost=0.20..2.16 rows=6 width=638) (actual time=1131.955..1131.971 rows=23 loops=1)
                                  Hash Cond: ((pol.polluant)::text = (fe.polluant)::text)
                                  ->  Seq Scan on polluant pol  (cost=0.00..1.66 rows=66 width=12) (actual time=0.016..0.029 rows=66 loops=1)
                                  ->  Hash  (cost=0.12..0.12 rows=6 width=630) (actual time=1131.875..1131.875 rows=23 loops=1)
                                        Buckets: 1024  Batches: 1  Memory Usage: 2kB
                                        ->  CTE Scan on fe  (cost=0.00..0.12 rows=6 width=630) (actual time=1130.678..1131.851 rows=23 loops=1)
                            ->  Hash  (cost=1.08..1.08 rows=8 width=32) (actual time=0.026..0.026 rows=14 loops=1)
                                  Buckets: 1024  Batches: 1  Memory Usage: 1kB
                                  ->  Seq Scan on regions_a_calculer  (cost=0.00..1.08 rows=8 width=32) (actual time=0.016..0.018 rows=14 loops=1)
                      ->  Hash  (cost=0.14..0.14 rows=7 width=28) (actual time=262.736..262.736 rows=7 loops=1)
                            Buckets: 1024  Batches: 1  Memory Usage: 1kB
                            ->  CTE Scan on conso_peinture_par_habitant c  (cost=0.00..0.14 rows=7 width=28) (actual time=262.717..262.732 rows=7 loops=1)
Total runtime: 1581.124 ms
'''
    model = ExplainModel(data.split('\n'))
    mainwindow = QtGui.QMainWindow()
    mainwindow.setWindowTitle("Tree Model with Completion")
    mainwindow.show()

    view = QtGui.QTreeView()
    view.setModel(model)
    mainwindow.setCentralWidget(view)

    edit     = QtGui.QLineEdit()
    completer     = MyCompleter(edit)
    completer.setModel(model)
    completer.setCompletionColumn(0)
    completer.setCompletionRole(QtCore.Qt.DisplayRole)
    completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

    edit.setWindowTitle("PySide QLineEdit Auto Complete")
    edit.setCompleter(completer)
    docker = QtGui.QDockWidget()
    docker.setWidget(edit)
    mainwindow.addDockWidget(QtCore.Qt.BottomDockWidgetArea, docker)

    sys.exit(app.exec_())
