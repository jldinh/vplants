#!/usr/bin/env python
"""Phyllotaxis utils.

Here i gather small utils which are usefull while working with phyllotaxis.

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
__version__="0.1"
__docformat__= "restructuredtext en"
__revision__="$Id: phyllotaxis.py 7875 2010-02-08 18:24:36Z cokelaer $"


def get_angle_between_primordias( yi, yj):
    """Return the angle between primordias.
    """
    d = yi.diff_angle(yj)
    if visual.mag( visual.rotate( yi, axis=(0,0,1), angle=d )- yj ) < 0.001:
        return d*360/(2*math.pi)
    else:
        return (2*math.pi-d)*360/(2*math.pi)

def standarize_angle( a ):
    """Angle standarisation.
    """
    if a > 180:
        return 360 - a 
    return a

def get_primordia_data( wt=None, step2PrC={}, step2PrC_stub={}, step=0 ):
    """Extracts primordium information from tissue.
    
    <Long description of the function functionality.>
    
    :parameters:
        wt : `WalledTissue`
            The tissue from which we extract the information.
    :rtype: `T`
    :return: <Description of ``return_object`` meaning>
    :raise Exception: <Description of situation raising `Exception`>
    """
    from openalea.mersim.tissue.algo.walled_tissue import cell_center
    
    lstep2PrC = []
    lstep2PrC_stub = []
    for i in wt.cells():
        if wt.cell_property(i, "PrC"):
            lstep2PrC.append( (i, step, cell_center( wt, i ), wt.cell_property(i, "PrC") ) )  
        if wt.cell_property(i, "PrC_stub"):
            lstep2PrC_stub.append( (i, step, cell_center( wt, i ), wt.cell_property(i, "PrC_stub") ) )
    step2PrC[ step ] = lstep2PrC
    step2PrC_stub[ step ] = lstep2PrC_stub
    #return {"step2PrC": step2PrC, "step2PrC_stub": step2PrC_stub}



