# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'codeeditor.ui'
#
# Created: Fri Jul 25 16:50:47 2008
#      by: PyQt4 UI code generator 4.4.2
#
# WARNING! All changes made in this file will be lost!

from openalea.vpltk.qt import qt

class Ui_CodeEditor(object):
    def setupUi(self, CodeEditor):
        CodeEditor.setObjectName("CodeEditor")
        CodeEditor.resize(506,541)
        self.verticalLayout_2 = qt.QtGui.QVBoxLayout(CodeEditor)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = qt.QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.filenames = qt.QtGui.QTabBar(CodeEditor)
        self.filenames.setObjectName("filenames")
        self.verticalLayout.addWidget(self.filenames)
        self.codeeditor = LpyCodeEditor(CodeEditor)
        self.codeeditor.setEnabled(True)
        font = qt.QtGui.QFont()
        font.setFamily("Courier New")
        self.codeeditor.setFont(font)
        self.codeeditor.setTabStopWidth(20)
        self.codeeditor.setObjectName("codeeditor")
        self.verticalLayout.addWidget(self.codeeditor)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.frameFind = qt.QtGui.QFrame(CodeEditor)
        self.frameFind.setFrameShape(qt.QtGui.QFrame.StyledPanel)
        self.frameFind.setFrameShadow(qt.QtGui.QFrame.Raised)
        self.frameFind.setObjectName("frameFind")
        self.gridLayout = qt.QtGui.QGridLayout(self.frameFind)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(2)
        self.gridLayout.setObjectName("gridLayout")
        self.findNextButton = qt.QtGui.QPushButton(self.frameFind)
        self.findNextButton.setObjectName("findNextButton")
        self.gridLayout.addWidget(self.findNextButton,0,3,1,1)
        self.closeFind = qt.QtGui.QToolButton(self.frameFind)
        palette = qt.QtGui.QPalette()
        brush = qt.QtGui.QBrush(qt.QtGui.QColor(170,0,0))
        brush.setStyle(qt.QtCore.Qt.SolidPattern)
        palette.setBrush(qt.QtGui.QPalette.Active,qt.QtGui.QPalette.ButtonText,brush)
        brush = qt.QtGui.QBrush(qt.QtGui.QColor(0,0,0))
        brush.setStyle(qt.QtCore.Qt.SolidPattern)
        palette.setBrush(qt.QtGui.QPalette.Inactive,qt.QtGui.QPalette.ButtonText,brush)
        brush = qt.QtGui.QBrush(qt.QtGui.QColor(118,116,108))
        brush.setStyle(qt.QtCore.Qt.SolidPattern)
        palette.setBrush(qt.QtGui.QPalette.Disabled,qt.QtGui.QPalette.ButtonText,brush)
        self.closeFind.setPalette(palette)
        self.closeFind.setObjectName("closeFind")
        self.gridLayout.addWidget(self.closeFind,0,0,1,1)
        self.label_8 = qt.QtGui.QLabel(self.frameFind)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8,0,1,1,1)
        self.wholeWordButton = qt.QtGui.QRadioButton(self.frameFind)
        self.wholeWordButton.setAutoExclusive(False)
        self.wholeWordButton.setObjectName("wholeWordButton")
        self.gridLayout.addWidget(self.wholeWordButton,1,4,1,1)
        self.matchCaseButton = qt.QtGui.QRadioButton(self.frameFind)
        self.matchCaseButton.setAutoExclusive(False)
        self.matchCaseButton.setObjectName("matchCaseButton")
        self.gridLayout.addWidget(self.matchCaseButton,1,3,1,1)
        spacerItem = qt.QtGui.QSpacerItem(61,20,qt.QtGui.QSizePolicy.Expanding,qt.QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem,0,5,1,1)
        self.replaceEdit = qt.QtGui.QLineEdit(self.frameFind)
        self.replaceEdit.setObjectName("replaceEdit")
        self.gridLayout.addWidget(self.replaceEdit,0,2,1,1)
        spacerItem1 = qt.QtGui.QSpacerItem(177,17,qt.QtGui.QSizePolicy.Expanding,qt.QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1,1,0,1,3)
        self.findPreviousButton = qt.QtGui.QPushButton(self.frameFind)
        sizePolicy = qt.QtGui.QSizePolicy(qt.QtGui.QSizePolicy.Minimum,qt.QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.findPreviousButton.sizePolicy().hasHeightForWidth())
        self.findPreviousButton.setSizePolicy(sizePolicy)
        self.findPreviousButton.setObjectName("findPreviousButton")
        self.gridLayout.addWidget(self.findPreviousButton,0,4,1,1)
        spacerItem2 = qt.QtGui.QSpacerItem(61,17,qt.QtGui.QSizePolicy.Expanding,qt.QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2,1,5,1,1)
        self.verticalLayout_2.addWidget(self.frameFind)
        self.frameReplace = qt.QtGui.QFrame(CodeEditor)
        self.frameReplace.setFrameShape(qt.QtGui.QFrame.StyledPanel)
        self.frameReplace.setFrameShadow(qt.QtGui.QFrame.Raised)
        self.frameReplace.setObjectName("frameReplace")
        self.horizontalLayout = qt.QtGui.QHBoxLayout(self.frameReplace)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_9 = qt.QtGui.QLabel(self.frameReplace)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout.addWidget(self.label_9)
        self.findEdit = qt.QtGui.QLineEdit(self.frameReplace)
        self.findEdit.setObjectName("findEdit")
        self.horizontalLayout.addWidget(self.findEdit)
        self.replaceButton = qt.QtGui.QPushButton(self.frameReplace)
        self.replaceButton.setObjectName("replaceButton")
        self.horizontalLayout.addWidget(self.replaceButton)
        self.replaceAllButton = qt.QtGui.QPushButton(self.frameReplace)
        self.replaceAllButton.setObjectName("replaceAllButton")
        self.horizontalLayout.addWidget(self.replaceAllButton)
        spacerItem3 = qt.QtGui.QSpacerItem(142,20,qt.QtGui.QSizePolicy.Expanding,qt.QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout_2.addWidget(self.frameReplace)

        self.retranslateUi(CodeEditor)
        qt.QtCore.QObject.connect(self.closeFind,qt.QtCore.SIGNAL("pressed()"),self.frameFind.hide)
        qt.QtCore.QObject.connect(self.closeFind,qt.QtCore.SIGNAL("pressed()"),self.frameReplace.hide)
        qt.QtCore.QMetaObject.connectSlotsByName(CodeEditor)

    def retranslateUi(self, CodeEditor):
        CodeEditor.setWindowTitle(qt.QtGui.QApplication.translate("CodeEditor", "Form", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.findNextButton.setText(qt.QtGui.QApplication.translate("CodeEditor", "Next", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.closeFind.setText(qt.QtGui.QApplication.translate("CodeEditor", "X", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(qt.QtGui.QApplication.translate("CodeEditor", "Find", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.wholeWordButton.setText(qt.QtGui.QApplication.translate("CodeEditor", "Whole word", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.matchCaseButton.setText(qt.QtGui.QApplication.translate("CodeEditor", "Match Case", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.findPreviousButton.setText(qt.QtGui.QApplication.translate("CodeEditor", "Previous", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(qt.QtGui.QApplication.translate("CodeEditor", "Replace", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.replaceButton.setText(qt.QtGui.QApplication.translate("CodeEditor", "Replace", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.replaceAllButton.setText(qt.QtGui.QApplication.translate("CodeEditor", "Rep. All", None, qt.QtGui.QApplication.UnicodeUTF8))

from lpycodeeditor import LpyCodeEditor