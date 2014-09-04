from PyQt4 import QtCore, QtGui
import sys
import resources_rc

# Source : PyQt4 Model View Tutorial by Yasin Uludag on Youtube

class Node(object):
    def __init__(self, name, parent=None):
        self._name = name
        self._children = []
        self._parent = parent
        if parent is not None:
            parent.addChild(self)

    def typeInfo(self):
        return "NODE"

    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):
        if position < 0 or position > len(self._children):
            return False
        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):
        if position < 0 or position > len(self._children):
            return False
        child = self._children.pop(position)
        child._parent = None
        return True

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def child(self, row):
        return self._children[row]

    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def log(self, tabLevel=-1):
        output = ""
        tabLevel += 1
        for i in range(tabLevel):
            output += "\t"
        output += "|------" + self._name + "\n"
        for child in self._children:
            output += child.log(tabLevel)
        tabLevel -= 1
        output += "\n"
        return output

    def __repr__(self):
        return self.log()


class SchemaNode(Node):
    def __init__(self, name, parent=None):
        super(SchemaNode, self).__init__(name, parent)

    def typeInfo(self):
        return "SCHEMA"


class TableNode(Node):
    def __init__(self, name, parent=None):
        super(TableNode, self).__init__(name, parent)

    def typeInfo(self):
        return "TABLE"


class ViewNode(Node):
    def __init__(self, name, parent=None):
        super(ViewNode, self).__init__(name, parent)

    def typeInfo(self):
        return "VIEW"


class ColumnNode(Node):
    def __init__(self, name, parent=None):
        super(ColumnNode, self).__init__(name, parent)

    def typeInfo(self):
        return "COLUMN"


class IndexNode(Node):
    def __init__(self, name, parent=None):
        super(IndexNode, self).__init__(name, parent)

    def typeInfo(self):
        return "INDEX"


class SequenceNode(Node):
    def __init__(self, name, parent=None):
        super(SequenceNode, self).__init__(name, parent)

    def typeInfo(self):
        return "SEQUENCE"


class MaterializedView(Node):
    def __init__(self, name, parent=None):
        super(MaterializedView, self).__init__(name, parent)

    def typeInfo(self):
        return "MATERIALIZEDVIEW"


class ForeignTable(Node):
    def __init__(self, name, parent=None):
        super(ForeignTable, self).__init__(name, parent)

    def typeInfo(self):
        return "FOREIGNTABLE"


class Special(Node):
    def __init__(self, name, parent=None):
        super(Special, self).__init__(name, parent)

    def typeInfo(self):
        return "SPECIAL"


class ExplorerModel(QtCore.QAbstractItemModel):
    def __init__(self, root, parent=None):
        """INPUTS: Node, QObject"""

        super(ExplorerModel, self).__init__(parent)
        self._rootNode = root

    def rowCount(self, parent):
        """
        :param parent: QModelIndex
        :return:int
        """
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()
        return parentNode.childCount()

    def columnCount(self, parent):
        """
        INPUTS: QModelIndex
        OUTPUT: int
        """
        return 1

    def data(self, index, role):
        """
        INPUTS: QModelIndex, int
        OUTPUT: QVariant, strings are cast to QString which is a QVariant
        """
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return node.name()
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                typeInfo = node.typeInfo()
                if typeInfo == "LIGHT":
                    return QtGui.QIcon(QtGui.QPixmap(":/Light.png"))
                if typeInfo == "TRANSFORM":
                    return QtGui.QIcon(QtGui.QPixmap(":/Transform.png"))
                if typeInfo == "CAMERA":
                    return QtGui.QIcon(QtGui.QPixmap(":/Camera.png"))

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        """INPUTS: QModelIndex, QVariant, int (flag)"""
        if index.isValid():
            if role == QtCore.Qt.EditRole:
                node = index.internalPointer()
                node.setName(value)
                return True
        return False

    def headerData(self, section, orientation, role):
        """
        INPUTS: int, Qt::Orientation, int
        OUTPUT: QVariant, strings are cast to QString which is a QVariant
        """
        if role == QtCore.Qt.DisplayRole:
            if section == 0:
                return "Scenegraph"
            else:
                return "Typeinfo"

    def flags(self, index):
        """
        INPUTS: QModelIndex
        OUTPUT: int (flag)
        """
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def parent(self, index):
        """
        INPUTS: QModelIndex
        OUTPUT: QModelIndex
        Should return the parent of the node with the given QModelIndex
        """
        node = self.getNode(index)
        parentNode = node.parent()
        if parentNode == self._rootNode:
            return QtCore.QModelIndex()
        return self.createIndex(parentNode.row(), 0, parentNode)


    def index(self, row, column, parent):
        """
        :param row: int
        :param column: int
        :param parent: QModelIndex
        :return: QModelIndex
       Should return a QModelIndex that corresponds to the given row, column and parent node
       """
        parentNode = self.getNode(parent)
        childItem = parentNode.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def getNode(self, index):
        """
        INPUTS: QModelIndex
        """
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self._rootNode

    def onInsertColumn(self, position, columns, parent=QtCore.QModelIndex()):
        parentNode = self.getNode(parent)
        if parentNode.typeInfo in ("TABLE", "VIEW", "MATERIALIZEDVIEW") and len(columns)>0:
            self.beginInsertRows(parent, position, position + columns - 1)
            for column in columns:
                # childCount = parentNode.childCount()
                childNode = ColumnNode(column)
                success = parentNode.insertChild(position, childNode)
            self.endInsertRows()
            return success

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        """
        INPUTS: int, int, QModelIndex
        """
        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        for row in range(rows):
            success = parentNode.removeChild(position)
        self.endRemoveRows()
        return success


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    # app.setStyle("plastique")

    rootNode = Node("Hips")
    childNode0 = TransformNode("RightPirateLeg", rootNode)
    childNode1 = Node("RightPirateLeg_END", childNode0)
    childNode2 = CameraNode("LeftFemur", rootNode)
    childNode3 = Node("LeftTibia", childNode2)
    childNode4 = Node("LeftFoot", childNode3)
    childNode5 = LightNode("LeftFoot_END", childNode4)

    print rootNode

    model = ExplorerModel(rootNode)

    treeView = QtGui.QTreeView()
    treeView.show()

    treeView.setModel(model)

    rightPirateLeg = model.index(0, 0, QtCore.QModelIndex())

    model.insertRows(1, 5, rightPirateLeg)
    model.insertLights(1, 5, rightPirateLeg)

    sys.exit(app.exec_())