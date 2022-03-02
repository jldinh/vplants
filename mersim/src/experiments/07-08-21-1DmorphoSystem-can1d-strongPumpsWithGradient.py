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
__revision__="$Id: 07-08-21-1DmorphoSystem-can1d-strongPumpsWithGradient.py 7875 2010-02-08 18:24:36Z cokelaer $"

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
        self.phys=Phys1Dcanalisation5( tissue_system=self )
        self.frame=0
        self.tissue.time=0
        self.concentration_range=(5,20)
        self.pin_range = (1.,1.3)
        self.field_list =["h",
        "c_kappa", 
        "c_sigma_p", 
        "c_theta_p",  
        "c_sigma_a", 
        "c_sigma_a_prim", 
        "c_theta_a",
        "c_omega", 
        "c_gamma", 
        "c_pin_max"] 



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
            for i in range(500):
                self.phys.step(1, 0)
            self.update_visualisation()
        
       
    def update_visualisation( self, cell=None ):
        self.frame+=1
        self.update_conc_range()
        self.update_pin_range()
        visualisation_mpl_1D_linear_tissue_aux_pin( self.tissue, pin_range=(0.09,0.41), phys=self.phys )
        frame = "%.4d" % self.frame
        pylab.savefig(generate_name(s.phys, init_string="can,1d,RL,2ndEq", terminal_string=frame+".png", field_list=self.field_list ), format="png")
        pylab.clf()

wtpr = WalledTissuePickleReader( "/home/stymek/mdata/1DlinearTissue", mode="r")
wtpr.read_tissue()
wt3=IOTissue2WalledTissue( wtpr.tissue, wtpr.wv_properties[ "_positions" ], const=WalledTissueCanalisationExp1() )
s=TissueSystem( wt3, const=WalledTissueCanalisationExp1() )
s.tissue.const=WalledTissueCanalisationExp1() 

for i in s.tissue.wvs():
    s.tissue.wv_pos( i, s.tissue.wv_pos( i )*10 ) 

for i in range(50,100):
    s.tissue.remove_cell( i )
s.tissue.cell_property( 49, "CZ", 1)
s.tissue.cell_property( 0, "CZ", 1)
s.tissue.cell_property( 25, "PrZ", 1)

p = {"c_sigma_p and c_theta_p": [(0.005,0.05),(0.0005,0.005)], 
        "c_kappa": [0.00001],
        "c_sigma_a_prim and c_theta_a": [(500,0.05),(5,0.0005),(5,0.0),(50,0),(50,0.05),(0.5,0.0005),(0.5,0.0),(5,0)], #, (0.1,0.00001), (0.1,0.0001)
        "c_sigma_a": [0,5,50], 
        "c_gamma": [1.,0.5],
        "c_pin_max": [0.2,0.4,1. ]}

for a1 in p[ "c_kappa"]:
    for a2 in p[ "c_sigma_p and c_theta_p" ]:
        for  a3 in p[ "c_sigma_a_prim and c_theta_a" ]:
            for a4 in p[ "c_sigma_a" ]: 
                for a5 in p[ "c_gamma" ]:
                    for a6 in p[ "c_pin_max" ]:
                        s.phys.h = 0.1
                        s.phys.c_kappa = a1
                        s.phys.c_sigma_p = a2[ 0 ]
                        s.phys.c_theta_p = a2[ 1 ]
                        s.phys.c_sigma_a_prim = a3[ 0 ]
                        s.phys.c_theta_a = a3[ 1 ]
                        s.phys.c_sigma_a = a4
                        s.phys.c_gamma = a5
                        s.phys.c_pin_max = a6
                        s.phys.init_aux()
                        s.phys.init_pin()
                        s.phys.hist={}
                        s.phys.t=0
                        s.frame=0
                        for i in range(50):
                            try:
                                s.step()
                            except Exception:
                                continue


