# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'root.ui'
#
# Created: Wed Oct 17 15:05:27 2007
#      by: PyQt4 UI code generator 4.3-snapshot-20071006
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):



        self.menuRoot = QtGui.QMenu(MainWindow)
        self.menuRoot.setObjectName("menuRoot")


        self.actionDisplayAuxin = QtGui.QAction(MainWindow)
        self.actionDisplayAuxin.setCheckable(True)
        self.actionDisplayAuxin.setChecked(True)
        self.actionDisplayAuxin.setIcon(QtGui.QIcon(":/images/icons/azureusicon2.png"))
        self.actionDisplayAuxin.setObjectName("actionDisplayAuxin")

        self.actionDisplayWalls = QtGui.QAction(MainWindow)
        self.actionDisplayWalls.setCheckable(True)
        self.actionDisplayWalls.setChecked(True)
        self.actionDisplayWalls.setIcon(QtGui.QIcon(":/images/icons/cube2.png"))
        self.actionDisplayWalls.setObjectName("actionDisplayWalls")

        self.actionDisplayPumps = QtGui.QAction(MainWindow)
        self.actionDisplayPumps.setCheckable(True)
        self.actionDisplayPumps.setIcon(QtGui.QIcon(":/images/icons/fishy01.png"))
        self.actionDisplayPumps.setObjectName("actionDisplayPumps")
        self.menuRoot.addAction(self.actionDisplayAuxin)
        self.menuRoot.addAction(self.actionDisplayWalls)
        self.menuRoot.addAction(self.actionDisplayPumps)
        self.menuRoot.addSeparator()
        self.menuRoot.addSeparator()

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        self.menuRoot.setTitle(QtGui.QApplication.translate("MainWindow", "Root", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDisplayAuxin.setText(QtGui.QApplication.translate("MainWindow", "display auxin", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDisplayWalls.setText(QtGui.QApplication.translate("MainWindow", "display walls", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDisplayPumps.setText(QtGui.QApplication.translate("MainWindow", "display pumps", None, QtGui.QApplication.UnicodeUTF8))

import root_rc
