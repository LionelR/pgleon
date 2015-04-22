# -*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore


class SaveAsBookmarDialog(QtGui.QDialog):
    """The bookmark "Save As" dialog"""

    def __init__(self, *args, **kwargs):
        super(SaveAsBookmarDialog, self).__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        self.uiNameEdit = QtGui.QLineEdit(self)
        self.uiIsGlobal = QtGui.QPushButton("Set global")
        self.uiIsGlobal.setCheckable(True)
        hBox = QtGui.QHBoxLayout()
        hBox.addStretch(1)
        hBox.addWidget(QtGui.QLabel("Name: "))
        hBox.addWidget(self.uiNameEdit)
        hBox.addWidget(self.uiIsGlobal)

        buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
                                         QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        vBox = QtGui.QVBoxLayout()
        vBox.addLayout(hBox)
        vBox.addWidget(buttons)
        self.setLayout(vBox)

    @staticmethod
    def getParams(parent=None):
        dialog = SaveAsBookmarDialog(parent)
        result = dialog.exec_()
        name = dialog.uiNameEdit.text()
        isGlobal = dialog.uiIsGlobal.isChecked()
        return name, isGlobal, result == QtGui.QDialog.Accepted



