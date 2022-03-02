# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created: Thu Nov 16 18:43:29 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui
import visual

class Ui_MainWindow(object):
    def setupUi(self, MainWindow, m):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(QtCore.QSize(QtCore.QRect(0,0,800,600).size()).expandedTo(MainWindow.minimumSizeHint()))

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(20,30,171,481))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName("frame")

        self.pushButton_2 = QtGui.QPushButton(self.frame)
        self.pushButton_2.setGeometry(QtCore.QRect(30,110,94,30))
        self.pushButton_2.setObjectName("pushButton_2")

        self.pushButton = QtGui.QPushButton(self.frame)
        self.pushButton.setGeometry(QtCore.QRect(30,50,94,30))
        self.pushButton.setObjectName("pushButton")

        self.lineEdit = QtGui.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(250,90,113,28))
        self.lineEdit.setObjectName("lineEdit")
        MainWindow.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0,0,800,32))
        self.menubar.setObjectName("menubar")

        self.menuOptions = QtGui.QMenu(self.menubar)
        self.menuOptions.setObjectName("menuOptions")

        self.menuTes = QtGui.QMenu(self.menubar)
        self.menuTes.setObjectName("menuTes")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.actionDoSth1 = QtGui.QAction(MainWindow)
        self.actionDoSth1.setObjectName("actionDoSth1")

        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName("actionQuit")

        self.actionOpt1 = QtGui.QAction(MainWindow)
        self.actionOpt1.setObjectName("actionOpt1")

        self.actionDoSth1_2 = QtGui.QAction(MainWindow)
        self.actionDoSth1_2.setObjectName("actionDoSth1_2")
        self.menuOptions.addAction(self.actionOpt1)
        self.menuTes.addAction(self.actionDoSth1_2)
        self.menuTes.addSeparator()
        self.menuTes.addAction(self.actionQuit)
        self.menubar.addAction(self.menuTes.menuAction())
        self.menubar.addAction(self.menuOptions.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.actionQuit,QtCore.SIGNAL("triggered()"),dupa)
        QtCore.QObject.connect(self.lineEdit,QtCore.SIGNAL("textChanged(QString)"), m.set_C)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_2.setText(QtGui.QApplication.translate("MainWindow", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("MainWindow", "PushButton", None, QtGui.QApplication.UnicodeUTF8))
        self.menuOptions.setTitle(QtGui.QApplication.translate("MainWindow", "Options", None, QtGui.QApplication.UnicodeUTF8))
        self.menuTes.setTitle(QtGui.QApplication.translate("MainWindow", "Test", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDoSth1.setText(QtGui.QApplication.translate("MainWindow", "Test", None, QtGui.QApplication.UnicodeUTF8))
        self.actionQuit.setText(QtGui.QApplication.translate("MainWindow", "Quit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionOpt1.setText(QtGui.QApplication.translate("MainWindow", "Opt1", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDoSth1_2.setText(QtGui.QApplication.translate("MainWindow", "DoSth1", None, QtGui.QApplication.UnicodeUTF8))

 
def dupa():
    print "dupa"


class MW( QtCore.QThread):
    def run( self ):
        import math
        self.display=visual.display()
        s=visual.sphere(pos=visual.vector(1,0,0))
        i=0
        self.C=1
        while True:
            s.pos.x = self.C*math.sin(i)
            s.pos.y = math.cos(i)
            i+=0.00001
            self.process()
            
    def process(self):
        if self.display.mouse.clicked : 
            click = self.display.mouse.getclick()
            # ------------------------------------------------------------------------------------------ fixed
            if click.pick.__class__ == visual.sphere:
                o = click.pick
                print "click"
    
    def set_C( self, s):
        self.C = s.toFloat()[ 0 ]
        
if __name__ == "__main__":        
        app = QtGui.QApplication(sys.argv)
        m = MW()
        m.start()
        MainWindow = QtGui.QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(MainWindow, m)
        MainWindow.show()

        sys.exit(app.exec_())