#!/usr/bin/env python
"""Node definitions for Canalization 1D model.

<Long description of the module functionality.>

:todo:
    Nothing.

:bug:
    None known.
    
:organization:
    INRIA

"""
# Module documentation variables:
__authors__="""Szymon Stoma    
"""
__contact__=""
__license__="Cecill-C"
__date__="<Timestamp>"
__version__="0.1"
__docformat__= "restructuredtext en"
__revision__="$Id: can_model_wraper.py 8407 2010-03-08 07:53:28Z pradal $"

from openalea.core.core import Node
from openalea.core.interface import IBool, IFloat, IInt, IStr, IDict
from openalea.visualea.node_widget import NodeWidget
import can1d_static_model
import model_widget
from PyQt4 import QtCore, QtGui 

class NodeCanalization1DModel(Node):
    def __init__( self ):
        Node.__init__( self )        
        self.add_output( name= "result_dict", interface=None )

        self.model = can1d_static_model.LinearTransportModel()#None
        self.model.set_prims( [0, len(self.model.cells)-1] )

    def __call__( self, inputs ):
        #self.model.read_gui_conf( self )
        #self.notify_listeners( )
        self.model.run( )
        self.model.plot()
        return ({}, )


class NodeCanalization1DModelWidget(model_widget.Ui_Form, QtGui.QWidget, NodeWidget ) :
    def __init__( self, node, parent ):
        model_widget.Ui_Form.__init__( self )
        QtGui.QWidget.__init__( self, parent )
        NodeWidget.__init__( self, node )
        self.setupUi( self )
        self.add_events_updating_widget( model_params=self.node.model )
        self.add_start_values( model_params=self.node.model )
    
    #def notify(self, sender, event):   
    #    """ Function called by observed objects """
    #    # examplary notify
    #    if event[0] == "input_modified":
    #        self.lineEdit.setText( self.node.get_input( "nbr_cells" ) )
    #    # update widget

    def add_start_values( self, model_params=None ):
        mp=model_params
        self.gamma_d.setValue(self.mp.c_gamma_act)
        self.gamma_a.setValue(self.mp.c_gamma_diff)
        self.sigma_a.setValue(self.mp.c_sigma_a)
        #self.sigma_a_prim.setValue(self.mp.c_sigma_a_prim)
        self.theta_a.setValue(self.mp.c_theta_a)
        self.sigma_p.setValue(self.mp.c_sigma_p)
        self.theta_p.setValue(self.mp.c_theta_p)

        self.cell_nbr.setValue(self.mp.c_cell_nbr)
        self.step.setValue(self.mp.h)
        self.break_step.setValue(self.mp.c_break_step_nbr)
        self.step_nbr.setValue(self.mp.c_step_nbr)
        self.stable_tol.setValue(self.mp.c_stable_tolerance)
        self.rtol.setValue(self.mp.c_rtol)
        self.atol.setValue(self.mp.c_atol)
        self.initial_iaa.setValue(self.mp.c_iaa_init_val)
        self.initial_iaa_sink.setValue(self.mp.c_prim_iaa_conc)
        self.initial_pin.setValue(self.mp.c_pin_init)

        self.phi_edit.setPlainText(self.mp.c_phi_str)

        self.iaa_diff_enabled.setChecked(True)
        self.iaa_act_enabled.setChecked(True)
        self.iaa_act_enabled.setChecked(True)
        self.new_simulation.setChecked(self.mp.c_new_simulation)
        
        self.PIN_capping_enabled.setChecked( self.mp.c_PIN_capping_enabled )
        self.max_PIN.setValue( self.mp.c_max_PIN)

        self.sink_fixed_concentration.setChecked( self.mp.c_sink_fixed_concentration )
        self.sink_destruction_rate.setValue( self.mp.c_sink_destruction_rate)


    def add_events_updating_widget( self, model_params=None ):
        """Adds event modification from widget to  model params.
        
        <Long description of the function functionality.>
        
        :parameters:
            model_params : `object containing param fields used below ;] `
                The model params are fixed on this object
        """
        self.mp = model_params
        QtCore.QObject.connect(self.gamma_d,QtCore.SIGNAL("valueChanged(double)"),self.f_gamma_d)
        QtCore.QObject.connect(self.gamma_a,QtCore.SIGNAL("valueChanged(double)"),self.f_gamma_a)
        QtCore.QObject.connect(self.sigma_a,QtCore.SIGNAL("valueChanged(double)"),self.f_sigma_a)
        QtCore.QObject.connect(self.sigma_a_prim,QtCore.SIGNAL("valueChanged(double)"),self.f_sigma_a_prim)
        QtCore.QObject.connect(self.theta_a,QtCore.SIGNAL("valueChanged(double)"),self.f_theta_a)
        QtCore.QObject.connect(self.sigma_p,QtCore.SIGNAL("valueChanged(double)"),self.f_sigma_p)
        QtCore.QObject.connect(self.theta_p,QtCore.SIGNAL("valueChanged(double)"),self.f_theta_p)

        QtCore.QObject.connect(self.cell_nbr,QtCore.SIGNAL("valueChanged(int)"),self.f_cell_nbr)
        QtCore.QObject.connect(self.step,QtCore.SIGNAL("valueChanged(double)"),self.f_step)
        QtCore.QObject.connect(self.break_step,QtCore.SIGNAL("valueChanged(int)"),self.f_break_step)
        QtCore.QObject.connect(self.step_nbr,QtCore.SIGNAL("valueChanged(int)"),self.f_step_nbr)
        QtCore.QObject.connect(self.stable_tol,QtCore.SIGNAL("valueChanged(double)"),self.f_stable_tol)
        QtCore.QObject.connect(self.rtol,QtCore.SIGNAL("valueChanged(double)"),self.f_rtol)
        QtCore.QObject.connect(self.atol,QtCore.SIGNAL("valueChanged(double)"),self.f_atol)
        QtCore.QObject.connect(self.initial_iaa,QtCore.SIGNAL("valueChanged(double)"),self.f_initial_iaa)
        QtCore.QObject.connect(self.initial_iaa_sink,QtCore.SIGNAL("valueChanged(double)"),self.f_initial_iaa_sink)
        QtCore.QObject.connect(self.initial_pin,QtCore.SIGNAL("valueChanged(double)"),self.f_initial_pin)

        QtCore.QObject.connect(self.PIN_capping_enabled,QtCore.SIGNAL("toggled(bool)"),self.f_PIN_capping_enabled)
        QtCore.QObject.connect(self.max_PIN,QtCore.SIGNAL("valueChanged(double)"),self.f_max_PIN)

        QtCore.QObject.connect(self.sink_destruction_rate,QtCore.SIGNAL("valueChanged(double)"),self.f_sink_destruction_rate)
        QtCore.QObject.connect(self.sink_fixed_concentration,QtCore.SIGNAL("toggled(bool)"),self.f_sink_fixed_concentration)
        
        QtCore.QObject.connect(self.phi_edit,QtCore.SIGNAL("textChanged()"),self.f_phi_edit)
        QtCore.QObject.connect(self.phi_default,QtCore.SIGNAL("toggled(bool)"),self.f_phi_default_toggle)
        QtCore.QObject.connect(self.phi_default,QtCore.SIGNAL("toggled(bool)"),self.f_phi_default_toggle)

        QtCore.QObject.connect(self.iaa_diff_enabled,QtCore.SIGNAL("toggled(bool)"),self.f_iaa_diff_enabled)
        QtCore.QObject.connect(self.iaa_act_enabled,QtCore.SIGNAL("toggled(bool)"),self.f_iaa_act_enabled)

        QtCore.QObject.connect(self.new_simulation,QtCore.SIGNAL("toggled(bool)"),self.f_new_simulation)

    def f_gamma_d( self, v ):
        self.mp.c_gamma_diff = v
    def f_gamma_a( self, v ):
        self.mp.c_gamma_act = v
    def f_sigma_a( self, v ):
        self.mp.c_sigma_a = v
    def f_sigma_a_prim( self, v ):
        self.mp.c_sigma_a_prim = v
    def f_sigma_p( self, v ):
        self.mp.c_sigma_p = v
    def f_theta_a( self, v ):
        self.mp.c_theta_a = v
    def f_theta_p( self, v ):
        self.mp.c_theta_p = v
    def f_cell_nbr( self, v ):
        pass #self.node.model = LinearTransportModel( v )
    def f_step( self, v ):
        self.mp.h = v
    def f_break_step( self, v ):
        self.mp.c_break_step_nbr = v
    def f_step_nbr( self, v ):
        self.mp.c_step_nbr = v
    def f_stable_tol( self, v ):
        self.mp.c_stable_tolerance = v
    def f_atol( self, v ):
        self.mp.c_atol = v
    def f_rtol( self, v ):
        self.mp.c_rtol = v
    def f_initial_iaa( self, v ):
        self.mp.c_iaa_init_val = v
    def f_initial_iaa_sink( self, v ):
        self.mp.c_prim_iaa_conc = v
    def f_initial_pin( self, v ):
        self.mp.c_pin_init = v
    def f_phi_edit( self ):
        try:
            fs = self.phi_edit.toPlainText()
            f = can1d_static_model.pyfunction( fs )
            self.mp.c_phi_str=fs
            self.mp.f_phi = f
            print " #: new phi was set"
        except Exception:
            pass
    def f_phi_default_toggle( self, state):
        self.phi_edit.setEnabled( state )
        if state:
            self.mp.c_phi_str = """def Phi( x ):
  if x < 0:
    return 0
  return x*x"""
            self.mp.f_phi = can1d_static_model.pyfunction( self.mp.c_phi_str )
            self.phi_edit.setPlainText( self.mp.c_phi_str )
    def f_iaa_diff_enabled( self, v ):
        self.mp.c_iaa_diff_enabled = v
    def f_iaa_act_enabled( self, v ):
        self.mp.c_iaa_act_enabled = v
    def f_new_simulation( self, v ):
        self.mp.c_new_simulation = v
    def f_max_PIN( self, v):
        self.mp.c_max_PIN=v
    def f_PIN_capping_enabled( self, v):
        self.mp.c_PIN_capping_enabled=v
    def f_sink_fixed_concentration( self, v):
        self.mp.c_sink_fixed_concentration=v
    def f_sink_destruction_rate( self, v):
        self.mp.c_sink_destruction_rate=v
