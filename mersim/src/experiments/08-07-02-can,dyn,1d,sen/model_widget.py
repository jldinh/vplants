# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'model_widget.ui'
#
# Created: Wed Jan 16 15:05:20 2008
#      by: PyQt4 UI code generator 4.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(QtCore.QSize(QtCore.QRect(0,0,594,618).size()).expandedTo(Form.minimumSizeHint()))

        self.hboxlayout = QtGui.QHBoxLayout(Form)
        self.hboxlayout.setObjectName("hboxlayout")

        self.tabWidget = QtGui.QTabWidget(Form)
        self.tabWidget.setObjectName("tabWidget")

        self.equatio_tab = QtGui.QWidget()
        self.equatio_tab.setObjectName("equatio_tab")

        self.gridlayout = QtGui.QGridLayout(self.equatio_tab)
        self.gridlayout.setObjectName("gridlayout")

        self.groupBox = QtGui.QGroupBox(self.equatio_tab)
        self.groupBox.setObjectName("groupBox")

        self.gridlayout1 = QtGui.QGridLayout(self.groupBox)
        self.gridlayout1.setObjectName("gridlayout1")

        self.iaa_diff_enabled = QtGui.QCheckBox(self.groupBox)
        self.iaa_diff_enabled.setChecked(True)
        self.iaa_diff_enabled.setObjectName("iaa_diff_enabled")
        self.gridlayout1.addWidget(self.iaa_diff_enabled,0,0,1,2)

        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridlayout1.addWidget(self.label,1,0,1,1)

        self.gamma_d = QtGui.QDoubleSpinBox(self.groupBox)
        self.gamma_d.setDecimals(6)
        self.gamma_d.setProperty("value",QtCore.QVariant(0.0))
        self.gamma_d.setObjectName("gamma_d")
        self.gridlayout1.addWidget(self.gamma_d,1,1,1,1)
        self.gridlayout.addWidget(self.groupBox,0,0,1,1)

        self.groupBox_4 = QtGui.QGroupBox(self.equatio_tab)
        self.groupBox_4.setObjectName("groupBox_4")

        self.gridlayout2 = QtGui.QGridLayout(self.groupBox_4)
        self.gridlayout2.setObjectName("gridlayout2")

        self.label_6 = QtGui.QLabel(self.groupBox_4)
        self.label_6.setObjectName("label_6")
        self.gridlayout2.addWidget(self.label_6,0,0,1,1)

        self.sigma_a = QtGui.QDoubleSpinBox(self.groupBox_4)
        self.sigma_a.setDecimals(6)
        self.sigma_a.setObjectName("sigma_a")
        self.gridlayout2.addWidget(self.sigma_a,0,1,1,1)

        self.label_10 = QtGui.QLabel(self.groupBox_4)
        self.label_10.setObjectName("label_10")
        self.gridlayout2.addWidget(self.label_10,1,0,1,1)

        self.sigma_a_prim = QtGui.QDoubleSpinBox(self.groupBox_4)
        self.sigma_a_prim.setDecimals(6)
        self.sigma_a_prim.setObjectName("sigma_a_prim")
        self.gridlayout2.addWidget(self.sigma_a_prim,1,1,1,1)

        self.label_7 = QtGui.QLabel(self.groupBox_4)
        self.label_7.setObjectName("label_7")
        self.gridlayout2.addWidget(self.label_7,2,0,1,1)

        self.theta_a = QtGui.QDoubleSpinBox(self.groupBox_4)
        self.theta_a.setDecimals(6)
        self.theta_a.setObjectName("theta_a")
        self.gridlayout2.addWidget(self.theta_a,2,1,1,1)

        self.label_8 = QtGui.QLabel(self.groupBox_4)
        self.label_8.setObjectName("label_8")
        self.gridlayout2.addWidget(self.label_8,3,0,1,1)

        self.sigma_p = QtGui.QDoubleSpinBox(self.groupBox_4)
        self.sigma_p.setDecimals(6)
        self.sigma_p.setObjectName("sigma_p")
        self.gridlayout2.addWidget(self.sigma_p,3,1,1,1)

        self.label_9 = QtGui.QLabel(self.groupBox_4)
        self.label_9.setObjectName("label_9")
        self.gridlayout2.addWidget(self.label_9,4,0,1,1)

        self.theta_p = QtGui.QDoubleSpinBox(self.groupBox_4)
        self.theta_p.setDecimals(6)
        self.theta_p.setObjectName("theta_p")
        self.gridlayout2.addWidget(self.theta_p,4,1,1,1)
        self.gridlayout.addWidget(self.groupBox_4,0,1,2,1)

        self.groupBox_3 = QtGui.QGroupBox(self.equatio_tab)
        self.groupBox_3.setObjectName("groupBox_3")

        self.gridlayout3 = QtGui.QGridLayout(self.groupBox_3)
        self.gridlayout3.setObjectName("gridlayout3")

        self.iaa_act_enabled = QtGui.QCheckBox(self.groupBox_3)
        self.iaa_act_enabled.setChecked(True)
        self.iaa_act_enabled.setObjectName("iaa_act_enabled")
        self.gridlayout3.addWidget(self.iaa_act_enabled,0,0,1,2)

        self.label_3 = QtGui.QLabel(self.groupBox_3)
        self.label_3.setObjectName("label_3")
        self.gridlayout3.addWidget(self.label_3,1,0,1,1)

        self.gamma_a = QtGui.QDoubleSpinBox(self.groupBox_3)
        self.gamma_a.setDecimals(6)
        self.gamma_a.setProperty("value",QtCore.QVariant(0.0))
        self.gamma_a.setObjectName("gamma_a")
        self.gridlayout3.addWidget(self.gamma_a,1,1,1,1)
        self.gridlayout.addWidget(self.groupBox_3,1,0,1,1)

        self.groupBox_2 = QtGui.QGroupBox(self.equatio_tab)
        self.groupBox_2.setObjectName("groupBox_2")

        self.hboxlayout1 = QtGui.QHBoxLayout(self.groupBox_2)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.phi_edit = QtGui.QTextEdit(self.groupBox_2)
        self.phi_edit.setObjectName("phi_edit")
        self.hboxlayout1.addWidget(self.phi_edit)

        self.groupBox_5 = QtGui.QGroupBox(self.groupBox_2)
        self.groupBox_5.setObjectName("groupBox_5")

        self.vboxlayout = QtGui.QVBoxLayout(self.groupBox_5)
        self.vboxlayout.setObjectName("vboxlayout")

        self.phi_default = QtGui.QRadioButton(self.groupBox_5)
        self.phi_default.setChecked(False)
        self.phi_default.setObjectName("phi_default")
        self.vboxlayout.addWidget(self.phi_default)

        self.phi_custom = QtGui.QRadioButton(self.groupBox_5)
        self.phi_custom.setChecked(True)
        self.phi_custom.setObjectName("phi_custom")
        self.vboxlayout.addWidget(self.phi_custom)
        self.hboxlayout1.addWidget(self.groupBox_5)
        self.gridlayout.addWidget(self.groupBox_2,2,0,1,2)

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setObjectName("hboxlayout2")

        spacerItem = QtGui.QSpacerItem(71,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem)

        self.label_2 = QtGui.QLabel(self.equatio_tab)
        self.label_2.setPixmap(QtGui.QPixmap("model_equation.png"))
        self.label_2.setObjectName("label_2")
        self.hboxlayout2.addWidget(self.label_2)

        spacerItem1 = QtGui.QSpacerItem(71,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem1)
        self.gridlayout.addLayout(self.hboxlayout2,3,0,1,2)
        self.tabWidget.addTab(self.equatio_tab,"")

        self.simulation_tab = QtGui.QWidget()
        self.simulation_tab.setObjectName("simulation_tab")

        self.hboxlayout3 = QtGui.QHBoxLayout(self.simulation_tab)
        self.hboxlayout3.setObjectName("hboxlayout3")

        self.groupBox_7 = QtGui.QGroupBox(self.simulation_tab)
        self.groupBox_7.setObjectName("groupBox_7")

        self.gridlayout4 = QtGui.QGridLayout(self.groupBox_7)
        self.gridlayout4.setObjectName("gridlayout4")

        self.label_5 = QtGui.QLabel(self.groupBox_7)
        self.label_5.setObjectName("label_5")
        self.gridlayout4.addWidget(self.label_5,1,0,1,1)

        self.step = QtGui.QDoubleSpinBox(self.groupBox_7)
        self.step.setDecimals(6)
        self.step.setProperty("value",QtCore.QVariant(0.0))
        self.step.setObjectName("step")
        self.gridlayout4.addWidget(self.step,1,2,1,2)

        self.label_14 = QtGui.QLabel(self.groupBox_7)
        self.label_14.setObjectName("label_14")
        self.gridlayout4.addWidget(self.label_14,2,0,1,2)

        self.break_step = QtGui.QSpinBox(self.groupBox_7)
        self.break_step.setMaximum(1000)
        self.break_step.setProperty("value",QtCore.QVariant(0))
        self.break_step.setObjectName("break_step")
        self.gridlayout4.addWidget(self.break_step,2,2,1,2)

        self.label_12 = QtGui.QLabel(self.groupBox_7)
        self.label_12.setObjectName("label_12")
        self.gridlayout4.addWidget(self.label_12,3,0,1,1)

        self.label_11 = QtGui.QLabel(self.groupBox_7)
        self.label_11.setObjectName("label_11")
        self.gridlayout4.addWidget(self.label_11,4,0,1,1)

        self.stable_tol = QtGui.QDoubleSpinBox(self.groupBox_7)
        self.stable_tol.setDecimals(6)
        self.stable_tol.setProperty("value",QtCore.QVariant(0.0))
        self.stable_tol.setObjectName("stable_tol")
        self.gridlayout4.addWidget(self.stable_tol,4,2,1,2)

        self.label_13 = QtGui.QLabel(self.groupBox_7)
        self.label_13.setObjectName("label_13")
        self.gridlayout4.addWidget(self.label_13,5,0,1,1)

        self.atol = QtGui.QDoubleSpinBox(self.groupBox_7)
        self.atol.setDecimals(6)
        self.atol.setProperty("value",QtCore.QVariant(0.0))
        self.atol.setObjectName("atol")
        self.gridlayout4.addWidget(self.atol,5,2,1,2)

        self.label_15 = QtGui.QLabel(self.groupBox_7)
        self.label_15.setObjectName("label_15")
        self.gridlayout4.addWidget(self.label_15,6,0,1,1)

        self.rtol = QtGui.QDoubleSpinBox(self.groupBox_7)
        self.rtol.setDecimals(6)
        self.rtol.setProperty("value",QtCore.QVariant(0.0))
        self.rtol.setObjectName("rtol")
        self.gridlayout4.addWidget(self.rtol,6,2,1,2)

        spacerItem2 = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout4.addItem(spacerItem2,7,1,1,2)

        self.step_nbr = QtGui.QSpinBox(self.groupBox_7)
        self.step_nbr.setProperty("value",QtCore.QVariant(0))
        self.step_nbr.setObjectName("step_nbr")
        self.gridlayout4.addWidget(self.step_nbr,3,2,1,2)

        self.label_4 = QtGui.QLabel(self.groupBox_7)
        self.label_4.setObjectName("label_4")
        self.gridlayout4.addWidget(self.label_4,0,0,1,1)

        self.cell_nbr = QtGui.QSpinBox(self.groupBox_7)
        self.cell_nbr.setProperty("value",QtCore.QVariant(0))
        self.cell_nbr.setObjectName("cell_nbr")
        self.gridlayout4.addWidget(self.cell_nbr,0,2,1,2)
        self.hboxlayout3.addWidget(self.groupBox_7)

        self.groupBox_6 = QtGui.QGroupBox(self.simulation_tab)
        self.groupBox_6.setObjectName("groupBox_6")

        self.gridlayout5 = QtGui.QGridLayout(self.groupBox_6)
        self.gridlayout5.setObjectName("gridlayout5")

        self.new_simulation = QtGui.QCheckBox(self.groupBox_6)
        self.new_simulation.setCheckable(True)
        self.new_simulation.setChecked(False)
        self.new_simulation.setObjectName("new_simulation")
        self.gridlayout5.addWidget(self.new_simulation,0,0,1,2)

        self.label_16 = QtGui.QLabel(self.groupBox_6)
        self.label_16.setObjectName("label_16")
        self.gridlayout5.addWidget(self.label_16,1,0,1,1)

        self.initial_iaa = QtGui.QDoubleSpinBox(self.groupBox_6)
        self.initial_iaa.setDecimals(6)
        self.initial_iaa.setObjectName("initial_iaa")
        self.gridlayout5.addWidget(self.initial_iaa,1,1,1,1)

        self.label_18 = QtGui.QLabel(self.groupBox_6)
        self.label_18.setObjectName("label_18")
        self.gridlayout5.addWidget(self.label_18,2,0,1,1)

        self.initial_iaa_sink = QtGui.QDoubleSpinBox(self.groupBox_6)
        self.initial_iaa_sink.setDecimals(6)
        self.initial_iaa_sink.setObjectName("initial_iaa_sink")
        self.gridlayout5.addWidget(self.initial_iaa_sink,2,1,1,1)

        self.label_17 = QtGui.QLabel(self.groupBox_6)
        self.label_17.setObjectName("label_17")
        self.gridlayout5.addWidget(self.label_17,3,0,1,1)

        self.initial_pin = QtGui.QDoubleSpinBox(self.groupBox_6)
        self.initial_pin.setDecimals(6)
        self.initial_pin.setObjectName("initial_pin")
        self.gridlayout5.addWidget(self.initial_pin,3,1,1,1)

        self.groupBox_8 = QtGui.QGroupBox(self.groupBox_6)
        self.groupBox_8.setObjectName("groupBox_8")

        self.gridlayout6 = QtGui.QGridLayout(self.groupBox_8)
        self.gridlayout6.setObjectName("gridlayout6")

        self.PIN_capping_enabled = QtGui.QCheckBox(self.groupBox_8)
        self.PIN_capping_enabled.setObjectName("PIN_capping_enabled")
        self.gridlayout6.addWidget(self.PIN_capping_enabled,0,0,1,1)

        self.label_19 = QtGui.QLabel(self.groupBox_8)
        self.label_19.setObjectName("label_19")
        self.gridlayout6.addWidget(self.label_19,1,0,1,1)

        self.max_PIN = QtGui.QDoubleSpinBox(self.groupBox_8)
        self.max_PIN.setEnabled(False)
        self.max_PIN.setDecimals(6)
        self.max_PIN.setObjectName("max_PIN")
        self.gridlayout6.addWidget(self.max_PIN,1,1,1,1)
        self.gridlayout5.addWidget(self.groupBox_8,4,0,1,2)

        self.groupBox_9 = QtGui.QGroupBox(self.groupBox_6)
        self.groupBox_9.setObjectName("groupBox_9")

        self.gridlayout7 = QtGui.QGridLayout(self.groupBox_9)
        self.gridlayout7.setObjectName("gridlayout7")

        self.sink_fixed_concentration = QtGui.QCheckBox(self.groupBox_9)
        self.sink_fixed_concentration.setChecked(True)
        self.sink_fixed_concentration.setObjectName("sink_fixed_concentration")
        self.gridlayout7.addWidget(self.sink_fixed_concentration,0,0,1,2)

        self.label_20 = QtGui.QLabel(self.groupBox_9)
        self.label_20.setObjectName("label_20")
        self.gridlayout7.addWidget(self.label_20,1,0,1,1)

        self.sink_destruction_rate = QtGui.QDoubleSpinBox(self.groupBox_9)
        self.sink_destruction_rate.setEnabled(False)
        self.sink_destruction_rate.setDecimals(6)
        self.sink_destruction_rate.setObjectName("sink_destruction_rate")
        self.gridlayout7.addWidget(self.sink_destruction_rate,1,1,1,1)

        spacerItem3 = QtGui.QSpacerItem(111,81,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout7.addItem(spacerItem3,2,0,1,2)
        self.gridlayout5.addWidget(self.groupBox_9,5,0,1,2)
        self.hboxlayout3.addWidget(self.groupBox_6)
        self.tabWidget.addTab(self.simulation_tab,"")

        self.visualisation_tab = QtGui.QWidget()
        self.visualisation_tab.setObjectName("visualisation_tab")
        self.tabWidget.addTab(self.visualisation_tab,"")
        self.hboxlayout.addWidget(self.tabWidget)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.iaa_diff_enabled,QtCore.SIGNAL("toggled(bool)"),self.gamma_d.setEnabled)
        QtCore.QObject.connect(self.iaa_act_enabled,QtCore.SIGNAL("toggled(bool)"),self.gamma_a.setEnabled)
        QtCore.QObject.connect(self.groupBox_5,QtCore.SIGNAL("toggled(bool)"),self.phi_edit.setDisabled)
        QtCore.QObject.connect(self.PIN_capping_enabled,QtCore.SIGNAL("toggled(bool)"),self.max_PIN.setEnabled)
        QtCore.QObject.connect(self.sink_fixed_concentration,QtCore.SIGNAL("toggled(bool)"),self.sink_destruction_rate.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Form", "Diffusion of IAA", None, QtGui.QApplication.UnicodeUTF8))
        self.iaa_diff_enabled.setText(QtGui.QApplication.translate("Form", "Enabled", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Gamma d", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_4.setTitle(QtGui.QApplication.translate("Form", "Production/decay of IAA and PIN", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Form", "Sigma a", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("Form", "Sigma a \'", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("Form", "Theta a", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("Form", "Sigma p", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("Form", "Theta p", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("Form", "Active transport of IAA", None, QtGui.QApplication.UnicodeUTF8))
        self.iaa_act_enabled.setText(QtGui.QApplication.translate("Form", "Enabled", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Form", "Gamma a", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Form", "Phi function", None, QtGui.QApplication.UnicodeUTF8))
        self.phi_edit.setHtml(QtGui.QApplication.translate("Form", "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">def fi( x ):</p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">  return x</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_5.setTitle(QtGui.QApplication.translate("Form", "Phi type", None, QtGui.QApplication.UnicodeUTF8))
        self.phi_default.setText(QtGui.QApplication.translate("Form", "Default", None, QtGui.QApplication.UnicodeUTF8))
        self.phi_custom.setText(QtGui.QApplication.translate("Form", "Custom", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.equatio_tab), QtGui.QApplication.translate("Form", "Equation", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_7.setTitle(QtGui.QApplication.translate("Form", "Simulation details", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("Form", "Step", None, QtGui.QApplication.UnicodeUTF8))
        self.label_14.setText(QtGui.QApplication.translate("Form", "Break step", None, QtGui.QApplication.UnicodeUTF8))
        self.label_12.setText(QtGui.QApplication.translate("Form", "Step nbr.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_11.setText(QtGui.QApplication.translate("Form", "Stable tol.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_13.setText(QtGui.QApplication.translate("Form", "Atol", None, QtGui.QApplication.UnicodeUTF8))
        self.label_15.setText(QtGui.QApplication.translate("Form", "Rtol", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Form", "Cell nbr.", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_6.setTitle(QtGui.QApplication.translate("Form", "Initial conditions", None, QtGui.QApplication.UnicodeUTF8))
        self.new_simulation.setText(QtGui.QApplication.translate("Form", "New simulation", None, QtGui.QApplication.UnicodeUTF8))
        self.label_16.setText(QtGui.QApplication.translate("Form", "Initial IAA", None, QtGui.QApplication.UnicodeUTF8))
        self.label_18.setText(QtGui.QApplication.translate("Form", "Initial IAA sink", None, QtGui.QApplication.UnicodeUTF8))
        self.label_17.setText(QtGui.QApplication.translate("Form", "Initial PIN", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_8.setTitle(QtGui.QApplication.translate("Form", "PIN capping", None, QtGui.QApplication.UnicodeUTF8))
        self.PIN_capping_enabled.setText(QtGui.QApplication.translate("Form", "Enabled", None, QtGui.QApplication.UnicodeUTF8))
        self.label_19.setText(QtGui.QApplication.translate("Form", "Max PIN", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_9.setTitle(QtGui.QApplication.translate("Form", "Sink", None, QtGui.QApplication.UnicodeUTF8))
        self.sink_fixed_concentration.setText(QtGui.QApplication.translate("Form", "Fixed concentration", None, QtGui.QApplication.UnicodeUTF8))
        self.label_20.setText(QtGui.QApplication.translate("Form", "Destruction rate", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.simulation_tab), QtGui.QApplication.translate("Form", "Simulation&&Initial Cond.", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.visualisation_tab), QtGui.QApplication.translate("Form", "Visualisation", None, QtGui.QApplication.UnicodeUTF8))

