#!/usr/bin/env python
"""Test of plot environment

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
__revision__="$Id: 07-09-27-pxyllotaxis,gui,test.py 7875 2010-02-08 18:24:36Z cokelaer $"

import openalea.plotools.plotable as ptb
#import openalea.plotools as pt
import openalea.mersim.gui.phyllotaxis as px
import copy
from math import sin, pi
import visual

prim_nbr = [1, 2, 3, 4, 5, 6, 7]
prim_t = copy.copy( prim_nbr )
prim_pos = [visual.vector(1,0,0).rotate(i*140./360*2*pi) for i in range(7)]
#prim_ang = [ 0 ] + [prim_ang[i+1]-prim_ang[i] for i in range(0, len( prim_ang ) - 1 ) ]

d1={}
d2={}
d3={}
for i in range( len( prim_nbr ) ):
    d1[ i ] = prim_t[ i ]
    d2[ i ] = prim_t[ i ] + sin( i )*0.5
    d3[ i ] = prim_pos[ i ]
#p1 = px.generate_plotable_prim_id2abs_time( d1, legend="Absolute time of Set1" )
#p2 = px.generate_plotable_prim_id2rel_time( d2, color="g", legend="Time diffrence of Set2" )
#ptb.plot_plotable( plotable_list=[p1, p2], title="Primordium to its creation time", xlabel="Primordium", ylabel="Time" )
p3 = px.generate_VisualSequence2D_prim_id2div_angle( d3 )
ptb.display_visual_sequence2D( vis_seq2D_list=[p3], title="Primordium to its divergence angle", xlabel="Primordium", ylabel="Divergance Angle" )
