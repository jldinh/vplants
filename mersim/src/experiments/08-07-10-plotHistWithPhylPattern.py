#!/usr/bin/env python
"""<Short description of the module functionality.>

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
__revision__="$Id: 08-07-10-plotHistWithPhylPattern.py 7875 2010-02-08 18:24:36Z cokelaer $"

import pylab
import pickle
import openalea.snowAndSnow.phyllotaxis as opx
import openalea.plotools.plotable as pt

px_dict_file="/home/stymek/mtmp/08-07-08-can2d,dynamic,spiralPhyllotaxis2-errorTest-5/primHist.dict"
d = pickle.load(file(px_dict_file,"r"))


prim2data={}
for i in range( max( d["step2PrC"].keys() ) ):
    for j in d["step2PrC"][ i ]:
        (id_cell, time, pos, id_pr) = j
        if not prim2data.has_key(id_pr):
            prim2data[ id_pr ] = (pos, time)

prim2data_pos={}
prim2data_time={}
for i in prim2data.keys():
    prim2data_pos[ i ] = prim2data[ i ][ 0 ]
    prim2data_time[ i ] = prim2data[ i ][ 1 ]
    
vs1 = opx.generate_VisualSequence_prim_id2div_angle( prim2data_pos, standarize_angle=False )
vs2 = opx.generate_VisualSequence_prim_id2rel_time( prim2data_time )
vs1.x = vs1.x[1:59]
vs1.y = vs1.y[1:59]
z=0.
for i in vs1.y:
    z+= abs(i)
z=z/len(vs1.y)
yy = []
for i in vs1.y:
    if i > 0: yy.append(i)
    else: yy.append(i+360)
    
#pylab.subplot(121)
pylab.figure(1)
#pylab.title("Spriral pattern")
#pylab.plot( vs1.x, [180+i for i in vs1.y], "r:", marker="o", markerfacecolor="k"  )
pylab.plot( vs1.x, yy, "r:", marker="o", markerfacecolor="k"  )
#pylab.legend(tuple("Model"), loc='best', shadow=True)
#pylab.plot( vs1.x, [180+137.5 for i in vs1.x ], "g--", marker=""  )
#pylab.plot( vs1.x, [180+137.5 for i in vs1.x ], "g--", marker=""  )
pylab.plot( vs1.x, [137.5 for i in vs1.x ], "g--", marker=""  )
#pylab.legend(tuple("Golden angle"), loc='best', shadow=True)
#pylab.plot( vs1.x, [z for i in vs1.x ], "b--", marker=""  )
#pylab.legend(tuple("Model avg."), loc='best', shadow=True)
pylab.xlabel( "Primordium nbr." )
pylab.ylabel( "Divergence angle" )
#pylab.subplot(122)
pylab.savefig("spiralPhyllotaxis-p.png", format="png")
pylab.figure(2)
#pylab.hist( vs1.y, bins=20 )
pylab.hist( yy, bins=20 )
pylab.xlabel( "Divergence angle" )
pylab.ylabel( "Number of primordia" )
#pylab.show()
pylab.savefig("spiralPhyllotaxis-h.png", format="png")
#pt.display_VisualSequence_as_Hist(vs1)
#pt.display_VisualSequence_as_PointLine(vs1)
assert False



pylab.figure(2)
px_dict_file="/home/stymek/mtmp/phyl/alt/primHist.dict"
d = pickle.load(file(px_dict_file,"r"))


prim2data={}
for i in range( max( d["step2PrC"].keys() ) ):
    for j in d["step2PrC"][ i ]:
        (id_cell, time, pos, id_pr) = j
        if not prim2data.has_key(id_pr):
            prim2data[ id_pr ] = (pos, time)

prim2data_pos={}
prim2data_time={}
for i in prim2data.keys():
    prim2data_pos[ i ] = prim2data[ i ][ 0 ]
    prim2data_time[ i ] = prim2data[ i ][ 1 ]
    
vs1 = opx.generate_VisualSequence_prim_id2div_angle( prim2data_pos, standarize_angle=False )
vs2 = opx.generate_VisualSequence_prim_id2rel_time( prim2data_time )
vs1.x = vs1.x[1:]
vs1.y = vs1.y[1:]
z=0.
for i in vs1.y:
    if i >0:
        z+= i
    else: z+=abs(i)
z=z/len(vs1.y)
pylab.subplot(121)
pylab.title("Alternate pattern")
yy = []
for i in vs1.y:
    if i > 0: yy.append(i)
    else: yy.append(i+360)
pylab.plot( vs1.x, yy, "r:", marker="o", markerfacecolor="k"  )
#pylab.legend(tuple("Model"), loc='best', shadow=True)
pylab.plot( vs1.x, [180 for i in vs1.x ], "g--", marker=""  )
#pylab.legend(tuple("Golden angle"), loc='best', shadow=True)
#pylab.plot( vs1.x, [z for i in vs1.x ], "b--", marker=""  )
#pylab.legend(tuple("Model avg."), loc='best', shadow=True)
pylab.xlabel( "Primordium nbr." )
pylab.ylabel( "Divergence angle" )
pylab.subplot(122)
pylab.hist( yy, bins=10 )
pylab.xlabel( "Divergence angle" )
pylab.xlabel( "# probes" )
pylab.show()
