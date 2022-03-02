#!/usr/bin/env python
"""Real meristem flux maps.

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
__revision__="$Id: 07-09-20-can1d,analitic.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.tissue.walled_tissue import WalledTissue
from openalea.mersim.const.const import *
from openalea.mersim.tissue.algo.walled_tissue import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
#from openalea.mersim.tissue.algo.walled_tissue_cfd import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.serial.walled_tissue import *
from openalea.mersim.serial.merrysim_plugin import *
from openalea.mersim.gui.tissue import *
from openalea.mersim.physio.canalisation import *
from openalea.mersim.physio.cell_identities import *
#from openalea.mersim.mass_spring.forces import * 
#from openalea.mersim.mass_spring.system import *
from openalea.mersim.tissue.algo.walled_tissue_division_policies import *
from openalea.mersim.tissue.algo.walled_tissue_dscs import *
from openalea.mersim.tissue.algo.walled_tissue_cfd import ds_surface
from openalea.mersim.simulation.remove_cell_strategy import *
import random

def generate_name( class_i, init_string="", terminal_string="", field_list=[] ):
    """Used to generate a string representing the specified content of class. 
    
    Format:
    field_list=[param1,param2]
    init_string-param1_param1Val-param2_param2Val-terminal_string
    
    :parameters:
        class_i : `object`
            The class instance to be introspected.
        init_string: `string`
            The init string to be glued before the desired params.
        terminal_strin: `string`
            The terminal string to be glued after the desired params.
        field_list: `[sting]` 
    :rtype: `string`
    :return: A string describing the class.
    """
    res = init_string
    for i in field_list:
        s = "%.5f" % (class_i.__getattribute__( i ))
        res += "-"+i+"_"+s
    res += "-"+terminal_string
    return res
        
class TissueSystem(object):
    """Stub tissue system..
    """
    def __init__( self, tissue, const=None ):
        self.tissue = tissue
        self.const=const
        self.phys=Phys1Dcanalisation10( tissue_system=self )
        self.frame=0
        self.tissue.time=0
        self.concentration_range=(5,20)
        self.pin_range = (1.,1.3)
        self.field_list =["h", 
        "c_sigma_p", 
        "c_theta_p",   
        "c_sigma_a_prim", 
        "c_theta_a",
        "c_gamma"]
        self.c_prim_t = 96500



    def update_conc_range( self ):
        l=[]
        for i in self.tissue.cells():
            l.append(self.tissue.cell_property( i , "auxin_level"))#/calculate_cell_surface(self.tissue, i ))
        self.concentration_range = (min(l),max(l))

    def update_pin_range( self ):
        l=[]
        min = float("inf")
        max = float("-inf")
        for i in self.tissue.cells():
            for n in self.tissue.cell_neighbors( i ):
                v = pin_level( s.tissue, cell_edge=(i,n))
                if v < min:
                    min = v
                if v > max:
                    max = v
        self.pin_range = (min,max)
        
    def loop( self, nbr=10 ):
        while self.frame < nbr:
            self.step()
            
    def step( self, nbr=1 ):
        for i in range( nbr ):
            #if nbr>1:
            #    self.phys.c_change=float("inf")
            self.tissue.time+=1
            #self.cell_identities.apply()
            for i in range(50):
                self.phys.step(1, 0)
                self.check_prim()
            self.update_visualisation()
        
    def check_prim( self ):
        for i in self.tissue.cells():
            if self.tissue.cell_property(i, "auxin_level") > self.c_prim_t:
                self.tissue.cell_property(i, "auxin_level", 0)
                self.tissue.cell_property(i, "CZ", 1)
       
    def update_visualisation( self, cell=None ):
        self.frame+=1
        self.update_conc_range()
        self.update_pin_range()
        visualisation_mpl_1D_linear_tissue_aux_pin( self.tissue,  phys=self.phys )
        frame = "%.4d" % self.frame

        pylab.savefig(generate_name(s.phys, init_string="can,1d,RL,2ndEq,sinks_"+str(self.sinks[0])+"_"+str(self.sinks[1]), terminal_string=frame+".png", field_list=self.field_list ), format="png")
        pylab.clf()

    def set_sinks( self, sinks ):
        for c in s.tissue.cells():
            s.tissue.cell_property( c, "CZ", 0 )
        
        for c in sinks:
            s.tissue.cell_property( c, "CZ", 1 )

wtpr = WalledTissuePickleReader( "/home/stymek/mdata/1DlinearTissue", mode="r")
wtpr.read_tissue()
wt3=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ], const=WalledTissueCanalisationExp1() )
s=TissueSystem( wt3, const=WalledTissueCanalisationExp1() )
s.tissue.const=WalledTissueCanalisationExp1() 

for i in s.tissue.wvs():
    s.tissue.wv_pos( i, s.tissue.wv_pos( i )*10 ) 

for i in range(10,100):
    s.tissue.remove_cell( i )
#s.tissue.cell_property( 79, "CZ", 1)
s.tissue.cell_property( 0, "CZ", 1)
#s.tissue.cell_property( 49, "PrZ", 1)

s.set_sinks( [0] )
s.phys.h = 0.1

r=4.
s.phys.c_sigma_p = 0.01*r
s.phys.c_theta_p = 0.2*r

s.phys.c_sigma_a = 0.0
s.phys.c_sigma_a_prim = 0.01
s.phys.c_theta_a = 0.0002

s.phys.c_gamma = 0.001

s.phys.c_initial_aux_value = s.phys.c_sigma_a_prim/s.phys.c_theta_a
s.phys.c_initial_pin_value = s.phys.c_sigma_p / s.phys.c_theta_p

s.phys.c_pin_max = 1000
s.phys.c_aux_max = 1000
s.phys.c_aux_min = 0.

s.phys.init_aux()
s.phys.init_pin()

s.sinks=[0,0]
