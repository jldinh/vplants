# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c:\openalea\vplants\lpy\src\openalea\lpy\gui\lpyprefwidget.ui'
#
# Created: Thu Nov 29 08:57:15 2012
#      by: PyQt4 UI code generator 4.8.6
#
# WARNING! All changes made in this file will be lost!

from openalea.vpltk.qt import qt

try:
    _fromUtf8 = qt.QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_PreferenceDialog(object):
    def setupUi(self, PreferenceDialog):
        PreferenceDialog.setObjectName(_fromUtf8("PreferenceDialog"))
        PreferenceDialog.resize(315, 306)
        PreferenceDialog.setWindowTitle(qt.QtGui.QApplication.translate("PreferenceDialog", "Preferences", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout_4 = qt.QtGui.QVBoxLayout(PreferenceDialog)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.prefTab = qt.QtGui.QTabWidget(PreferenceDialog)
        self.prefTab.setObjectName(_fromUtf8("prefTab"))
        self.tabAppearance = qt.QtGui.QWidget()
        self.tabAppearance.setObjectName(_fromUtf8("tabAppearance"))
        self.verticalLayout_2 = qt.QtGui.QVBoxLayout(self.tabAppearance)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox = qt.QtGui.QGroupBox(self.tabAppearance)
        self.groupBox.setTitle(qt.QtGui.QApplication.translate("PreferenceDialog", "ToolBar", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout = qt.QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = qt.QtGui.QLabel(self.groupBox)
        self.label.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "Show", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        spacerItem = qt.QtGui.QSpacerItem(95, 20, qt.QtGui.QSizePolicy.Expanding, qt.QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.toolbarAppEdit = qt.QtGui.QComboBox(self.groupBox)
        self.toolbarAppEdit.setObjectName(_fromUtf8("toolbarAppEdit"))
        self.toolbarAppEdit.addItem(_fromUtf8(""))
        self.toolbarAppEdit.setItemText(0, qt.QtGui.QApplication.translate("PreferenceDialog", "Icons", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.toolbarAppEdit.addItem(_fromUtf8(""))
        self.toolbarAppEdit.setItemText(1, qt.QtGui.QApplication.translate("PreferenceDialog", "Texts", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.toolbarAppEdit.addItem(_fromUtf8(""))
        self.toolbarAppEdit.setItemText(2, qt.QtGui.QApplication.translate("PreferenceDialog", "Icons and texts", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.toolbarAppEdit.addItem(_fromUtf8(""))
        self.toolbarAppEdit.setItemText(3, qt.QtGui.QApplication.translate("PreferenceDialog", "Texts below icons", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.horizontalLayout.addWidget(self.toolbarAppEdit)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.groupBox_2 = qt.QtGui.QGroupBox(self.tabAppearance)
        self.groupBox_2.setTitle(qt.QtGui.QApplication.translate("PreferenceDialog", "Text Editor", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout = qt.QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = qt.QtGui.QLabel(self.groupBox_2)
        self.label_2.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "Font Family", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        spacerItem1 = qt.QtGui.QSpacerItem(52, 20, qt.QtGui.QSizePolicy.Expanding, qt.QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 1, 1, 1)
        self.fontFamilyEdit = qt.QtGui.QFontComboBox(self.groupBox_2)
        font = qt.QtGui.QFont()
        font.setFamily(_fromUtf8("MS Sans Serif"))
        self.fontFamilyEdit.setCurrentFont(font)
        self.fontFamilyEdit.setObjectName(_fromUtf8("fontFamilyEdit"))
        self.gridLayout.addWidget(self.fontFamilyEdit, 0, 2, 1, 1)
        self.label_3 = qt.QtGui.QLabel(self.groupBox_2)
        self.label_3.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "Font Size", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        spacerItem2 = qt.QtGui.QSpacerItem(52, 20, qt.QtGui.QSizePolicy.Expanding, qt.QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 1, 1, 1, 1)
        self.fontSizeEdit = qt.QtGui.QSpinBox(self.groupBox_2)
        self.fontSizeEdit.setMinimum(6)
        self.fontSizeEdit.setMaximum(20)
        self.fontSizeEdit.setProperty("value", 8)
        self.fontSizeEdit.setObjectName(_fromUtf8("fontSizeEdit"))
        self.gridLayout.addWidget(self.fontSizeEdit, 1, 2, 1, 1)
        self.verticalLayout_2.addWidget(self.groupBox_2)
        spacerItem3 = qt.QtGui.QSpacerItem(20, 22, qt.QtGui.QSizePolicy.Minimum, qt.QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem3)
        self.prefTab.addTab(self.tabAppearance, _fromUtf8(""))
        self.tabEditing = qt.QtGui.QWidget()
        self.tabEditing.setObjectName(_fromUtf8("tabEditing"))
        self.verticalLayout_5 = qt.QtGui.QVBoxLayout(self.tabEditing)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.groupBox_4 = qt.QtGui.QGroupBox(self.tabEditing)
        self.groupBox_4.setTitle(qt.QtGui.QApplication.translate("PreferenceDialog", "Tabulation", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.gridLayout_2 = qt.QtGui.QGridLayout(self.groupBox_4)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.spaceForTabEdit = qt.QtGui.QCheckBox(self.groupBox_4)
        self.spaceForTabEdit.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "Replace by spaces", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.spaceForTabEdit.setObjectName(_fromUtf8("spaceForTabEdit"))
        self.gridLayout_2.addWidget(self.spaceForTabEdit, 0, 0, 1, 2)
        self.label_4 = qt.QtGui.QLabel(self.groupBox_4)
        self.label_4.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "Tab size", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 1, 0, 1, 1)
        spacerItem4 = qt.QtGui.QSpacerItem(143, 20, qt.QtGui.QSizePolicy.Expanding, qt.QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem4, 1, 1, 1, 1)
        self.tabSizeEdit = qt.QtGui.QSpinBox(self.groupBox_4)
        self.tabSizeEdit.setMinimum(1)
        self.tabSizeEdit.setProperty("value", 2)
        self.tabSizeEdit.setObjectName(_fromUtf8("tabSizeEdit"))
        self.gridLayout_2.addWidget(self.tabSizeEdit, 1, 2, 1, 1)
        self.verticalLayout_5.addWidget(self.groupBox_4)
        spacerItem5 = qt.QtGui.QSpacerItem(20, 90, qt.QtGui.QSizePolicy.Minimum, qt.QtGui.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem5)
        self.prefTab.addTab(self.tabEditing, _fromUtf8(""))
        self.tabFile = qt.QtGui.QWidget()
        self.tabFile.setObjectName(_fromUtf8("tabFile"))
        self.gridLayout_3 = qt.QtGui.QGridLayout(self.tabFile)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label_5 = qt.QtGui.QLabel(self.tabFile)
        self.label_5.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "History max size", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_3.addWidget(self.label_5, 0, 0, 1, 1)
        spacerItem6 = qt.QtGui.QSpacerItem(123, 20, qt.QtGui.QSizePolicy.Expanding, qt.QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem6, 0, 1, 1, 1)
        self.historySizeEdit = qt.QtGui.QSpinBox(self.tabFile)
        self.historySizeEdit.setMinimum(1)
        self.historySizeEdit.setProperty("value", 50)
        self.historySizeEdit.setObjectName(_fromUtf8("historySizeEdit"))
        self.gridLayout_3.addWidget(self.historySizeEdit, 0, 2, 1, 1)
        self.startupReloadEdit = qt.QtGui.QCheckBox(self.tabFile)
        self.startupReloadEdit.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "Reload file at startup", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.startupReloadEdit.setChecked(True)
        self.startupReloadEdit.setObjectName(_fromUtf8("startupReloadEdit"))
        self.gridLayout_3.addWidget(self.startupReloadEdit, 1, 0, 1, 2)
        self.fileMonitoringEdit = qt.QtGui.QCheckBox(self.tabFile)
        self.fileMonitoringEdit.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "Check file change on disk.", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.fileMonitoringEdit.setChecked(True)
        self.fileMonitoringEdit.setObjectName(_fromUtf8("fileMonitoringEdit"))
        self.gridLayout_3.addWidget(self.fileMonitoringEdit, 2, 0, 1, 2)
        self.groupBox_7 = qt.QtGui.QGroupBox(self.tabFile)
        self.groupBox_7.setTitle(qt.QtGui.QApplication.translate("PreferenceDialog", "Backup", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.groupBox_7.setObjectName(_fromUtf8("groupBox_7"))
        self.verticalLayout = qt.QtGui.QVBoxLayout(self.groupBox_7)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_6 = qt.QtGui.QLabel(self.groupBox_7)
        self.label_6.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "Create backup file", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout.addWidget(self.label_6)
        self.fileBackupEdit = qt.QtGui.QRadioButton(self.groupBox_7)
        self.fileBackupEdit.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "Of previous file before saving", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.fileBackupEdit.setAutoExclusive(False)
        self.fileBackupEdit.setObjectName(_fromUtf8("fileBackupEdit"))
        self.verticalLayout.addWidget(self.fileBackupEdit)
        self.codeBackupEdit = qt.QtGui.QRadioButton(self.groupBox_7)
        self.codeBackupEdit.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "Of code before execution", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.codeBackupEdit.setAutoExclusive(False)
        self.codeBackupEdit.setObjectName(_fromUtf8("codeBackupEdit"))
        self.verticalLayout.addWidget(self.codeBackupEdit)
        self.gridLayout_3.addWidget(self.groupBox_7, 3, 0, 1, 3)
        spacerItem7 = qt.QtGui.QSpacerItem(20, 3, qt.QtGui.QSizePolicy.Minimum, qt.QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem7, 4, 1, 1, 1)
        self.prefTab.addTab(self.tabFile, _fromUtf8(""))
        self.tab = qt.QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.verticalLayout_6 = qt.QtGui.QVBoxLayout(self.tab)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.groupBox_6 = qt.QtGui.QGroupBox(self.tab)
        self.groupBox_6.setTitle(qt.QtGui.QApplication.translate("PreferenceDialog", "Parsing", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.groupBox_6.setObjectName(_fromUtf8("groupBox_6"))
        self.horizontalLayout_4 = qt.QtGui.QHBoxLayout(self.groupBox_6)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.pycodeDebugEdit = qt.QtGui.QCheckBox(self.groupBox_6)
        self.pycodeDebugEdit.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "Show python code for debug.", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.pycodeDebugEdit.setObjectName(_fromUtf8("pycodeDebugEdit"))
        self.horizontalLayout_4.addWidget(self.pycodeDebugEdit)
        self.verticalLayout_6.addWidget(self.groupBox_6)
        self.groupBox_8 = qt.QtGui.QGroupBox(self.tab)
        self.groupBox_8.setTitle(qt.QtGui.QApplication.translate("PreferenceDialog", "Cython", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.groupBox_8.setObjectName(_fromUtf8("groupBox_8"))
        self.horizontalLayout_5 = qt.QtGui.QHBoxLayout(self.groupBox_8)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.label_7 = qt.QtGui.QLabel(self.groupBox_8)
        self.label_7.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "GCC Path", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.horizontalLayout_5.addWidget(self.label_7)
        self.gccPathEdit = qt.QtGui.QLineEdit(self.groupBox_8)
        sizePolicy = qt.QtGui.QSizePolicy(qt.QtGui.QSizePolicy.Maximum, qt.QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gccPathEdit.sizePolicy().hasHeightForWidth())
        self.gccPathEdit.setSizePolicy(sizePolicy)
        self.gccPathEdit.setObjectName(_fromUtf8("gccPathEdit"))
        self.horizontalLayout_5.addWidget(self.gccPathEdit)
        self.gccPathButton = qt.QtGui.QPushButton(self.groupBox_8)
        sizePolicy = qt.QtGui.QSizePolicy(qt.QtGui.QSizePolicy.Fixed, qt.QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.gccPathButton.sizePolicy().hasHeightForWidth())
        self.gccPathButton.setSizePolicy(sizePolicy)
        self.gccPathButton.setMaximumSize(qt.QtCore.QSize(30, 16777215))
        self.gccPathButton.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "...", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.gccPathButton.setObjectName(_fromUtf8("gccPathButton"))
        self.horizontalLayout_5.addWidget(self.gccPathButton)
        self.verticalLayout_6.addWidget(self.groupBox_8)
        spacerItem8 = qt.QtGui.QSpacerItem(18, 54, qt.QtGui.QSizePolicy.Minimum, qt.QtGui.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem8)
        self.prefTab.addTab(self.tab, _fromUtf8(""))
        self.tabExecution = qt.QtGui.QWidget()
        self.tabExecution.setObjectName(_fromUtf8("tabExecution"))
        self.verticalLayout_3 = qt.QtGui.QVBoxLayout(self.tabExecution)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.groupBox_3 = qt.QtGui.QGroupBox(self.tabExecution)
        self.groupBox_3.setTitle(qt.QtGui.QApplication.translate("PreferenceDialog", "Threading", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.horizontalLayout_2 = qt.QtGui.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.useThreadEdit = qt.QtGui.QCheckBox(self.groupBox_3)
        self.useThreadEdit.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "Use thread (Experimental).", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.useThreadEdit.setObjectName(_fromUtf8("useThreadEdit"))
        self.horizontalLayout_2.addWidget(self.useThreadEdit)
        self.verticalLayout_3.addWidget(self.groupBox_3)
        self.visuCheckBoxLayout = qt.QtGui.QGroupBox(self.tabExecution)
        self.visuCheckBoxLayout.setTitle(qt.QtGui.QApplication.translate("PreferenceDialog", "Visualization", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.visuCheckBoxLayout.setObjectName(_fromUtf8("visuCheckBoxLayout"))
        self.verticalLayout_9 = qt.QtGui.QVBoxLayout(self.visuCheckBoxLayout)
        self.verticalLayout_9.setObjectName(_fromUtf8("verticalLayout_9"))
        self.fitViewEdit = qt.QtGui.QCheckBox(self.visuCheckBoxLayout)
        self.fitViewEdit.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "Fit last view before animation.", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.fitViewEdit.setChecked(True)
        self.fitViewEdit.setObjectName(_fromUtf8("fitViewEdit"))
        self.verticalLayout_9.addWidget(self.fitViewEdit)
        self.integratedViewEdit = qt.QtGui.QCheckBox(self.visuCheckBoxLayout)
        self.integratedViewEdit.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "Integrated viewer", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.integratedViewEdit.setObjectName(_fromUtf8("integratedViewEdit"))
        self.verticalLayout_9.addWidget(self.integratedViewEdit)
        self.visuInfoEdit = qt.QtGui.QCheckBox(self.visuCheckBoxLayout)
        self.visuInfoEdit.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "Display info at run", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.visuInfoEdit.setObjectName(_fromUtf8("visuInfoEdit"))
        self.verticalLayout_9.addWidget(self.visuInfoEdit)
        self.verticalLayout_3.addWidget(self.visuCheckBoxLayout)
        self.textOutputBox = qt.QtGui.QGroupBox(self.tabExecution)
        self.textOutputBox.setTitle(qt.QtGui.QApplication.translate("PreferenceDialog", "Text Output", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.textOutputBox.setObjectName(_fromUtf8("textOutputBox"))
        self.verticalLayout_10 = qt.QtGui.QVBoxLayout(self.textOutputBox)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setContentsMargins(-1, 4, -1, 4)
        self.verticalLayout_10.setObjectName(_fromUtf8("verticalLayout_10"))
        self.LPyConsoleButton = qt.QtGui.QRadioButton(self.textOutputBox)
        self.LPyConsoleButton.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "LPy Console", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.LPyConsoleButton.setChecked(True)
        self.LPyConsoleButton.setAutoExclusive(False)
        self.LPyConsoleButton.setObjectName(_fromUtf8("LPyConsoleButton"))
        self.verticalLayout_10.addWidget(self.LPyConsoleButton)
        self.systemConsoleButton = qt.QtGui.QRadioButton(self.textOutputBox)
        self.systemConsoleButton.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "System Console", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.systemConsoleButton.setChecked(False)
        self.systemConsoleButton.setAutoExclusive(False)
        self.systemConsoleButton.setObjectName(_fromUtf8("systemConsoleButton"))
        self.verticalLayout_10.addWidget(self.systemConsoleButton)
        self.verticalLayout_3.addWidget(self.textOutputBox)
        spacerItem9 = qt.QtGui.QSpacerItem(20, 3, qt.QtGui.QSizePolicy.Minimum, qt.QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem9)
        self.prefTab.addTab(self.tabExecution, _fromUtf8(""))
        self.profilingTab = qt.QtGui.QWidget()
        self.profilingTab.setObjectName(_fromUtf8("profilingTab"))
        self.verticalLayout_8 = qt.QtGui.QVBoxLayout(self.profilingTab)
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.groupBox_9 = qt.QtGui.QGroupBox(self.profilingTab)
        self.groupBox_9.setTitle(qt.QtGui.QApplication.translate("PreferenceDialog", "Visualisation", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.groupBox_9.setObjectName(_fromUtf8("groupBox_9"))
        self.verticalLayout_7 = qt.QtGui.QVBoxLayout(self.groupBox_9)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.profilingAnimatedButton = qt.QtGui.QRadioButton(self.groupBox_9)
        self.profilingAnimatedButton.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "Animated Mode", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.profilingAnimatedButton.setObjectName(_fromUtf8("profilingAnimatedButton"))
        self.verticalLayout_7.addWidget(self.profilingAnimatedButton)
        self.profilingFinalPlotButton = qt.QtGui.QRadioButton(self.groupBox_9)
        self.profilingFinalPlotButton.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "Final plot", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.profilingFinalPlotButton.setChecked(True)
        self.profilingFinalPlotButton.setObjectName(_fromUtf8("profilingFinalPlotButton"))
        self.verticalLayout_7.addWidget(self.profilingFinalPlotButton)
        self.profilingNoPlotButton = qt.QtGui.QRadioButton(self.groupBox_9)
        self.profilingNoPlotButton.setText(qt.QtGui.QApplication.translate("PreferenceDialog", "No plot", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.profilingNoPlotButton.setObjectName(_fromUtf8("profilingNoPlotButton"))
        self.verticalLayout_7.addWidget(self.profilingNoPlotButton)
        self.verticalLayout_8.addWidget(self.groupBox_9)
        spacerItem10 = qt.QtGui.QSpacerItem(20, 71, qt.QtGui.QSizePolicy.Minimum, qt.QtGui.QSizePolicy.Expanding)
        self.verticalLayout_8.addItem(spacerItem10)
        self.prefTab.addTab(self.profilingTab, _fromUtf8(""))
        self.verticalLayout_4.addWidget(self.prefTab)
        self.buttonBox = qt.QtGui.QDialogButtonBox(PreferenceDialog)
        self.buttonBox.setOrientation(qt.QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(qt.QtGui.QDialogButtonBox.Cancel|qt.QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_4.addWidget(self.buttonBox)

        self.retranslateUi(PreferenceDialog)
        self.prefTab.setCurrentIndex(0)
        qt.QtCore.QObject.connect(self.buttonBox, qt.QtCore.SIGNAL(_fromUtf8("accepted()")), PreferenceDialog.accept)
        qt.QtCore.QObject.connect(self.buttonBox, qt.QtCore.SIGNAL(_fromUtf8("rejected()")), PreferenceDialog.reject)
        qt.QtCore.QMetaObject.connectSlotsByName(PreferenceDialog)

    def retranslateUi(self, PreferenceDialog):
        self.prefTab.setTabText(self.prefTab.indexOf(self.tabAppearance), qt.QtGui.QApplication.translate("PreferenceDialog", "Appearance", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.prefTab.setTabText(self.prefTab.indexOf(self.tabEditing), qt.QtGui.QApplication.translate("PreferenceDialog", "Editing", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.prefTab.setTabText(self.prefTab.indexOf(self.tabFile), qt.QtGui.QApplication.translate("PreferenceDialog", "File", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.prefTab.setTabText(self.prefTab.indexOf(self.tab), qt.QtGui.QApplication.translate("PreferenceDialog", "Compilation", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.prefTab.setTabText(self.prefTab.indexOf(self.tabExecution), qt.QtGui.QApplication.translate("PreferenceDialog", "Execution", None, qt.QtGui.QApplication.UnicodeUTF8))
        self.prefTab.setTabText(self.prefTab.indexOf(self.profilingTab), qt.QtGui.QApplication.translate("PreferenceDialog", "Profiling", None, qt.QtGui.QApplication.UnicodeUTF8))

