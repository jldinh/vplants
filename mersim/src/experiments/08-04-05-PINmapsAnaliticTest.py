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
__revision__="$Id: 08-04-05-PINmapsAnaliticTest.py 7875 2010-02-08 18:24:36Z cokelaer $"

from openalea.mersim.serial.merrysim_plugin import save_dat_and_lyn_files_as_WT
from openalea.mersim.const.const import TissueConst
from openalea.mersim.serial.walled_tissue import  read_walled_tissue
from openalea.mersim.tissue.algo.walled_tissue import  comparePIN_1, comparePIN_2

const=TissueConst()
const.cell_properties ={
        "PrC": 0,
        "auxin_level": 0,
    }
const.wv_edge_properties={
        "pin_level":[0,0],
}

path="/home/stymek/mdata/07-07-05-PINwithImmunolab/"
wt_filename="/home/stymek/tmp/tis_test/"
#save_dat_and_lyn_files_as_WT( dat_filename=path+"c16-proj-grey.dat", lyn_filename=path+"c16-proj-grey.link", wt_filename=wt_filename, const=const)

const.cell_properties ={
        "auxin_level": 0,
    }
const.tissue_properties={}
t_digit = read_walled_tissue( file_name=wt_filename, const=const )

const.cell_properties ={
        "auxin_level": 0,
        "CZ":False,
    }
t_canal = read_walled_tissue( file_name="/home/stymek/mtmp/realPierres1withCenter-1/61/", const=const)

t_canal_without_center = read_walled_tissue( file_name="/home/stymek/mtmp/realPierres1-1/61/", const=const)

# finding best center
from openalea.plantgl.all import Vector3, norm
from openalea.mersim.tissue.algo.walled_tissue import cell_center
pos=Vector3()
k=0
for i in t_canal.cells():
    if t_canal.cell_property(i, "CZ"):
        k+=1
        pos= cell_center(t_canal, i)
cc_pos=pos/float(k)

dc={}
for i in t_canal.cells():
    if t_canal.cell_property(i, "CZ"):
        dc[ norm( cell_center(t_canal, i) - cc_pos) ]=i


xx = range(1,15)
xx.reverse()
cc = dc[min(dc.keys())]#353
print "cc=", cc
z1=[]
z2=[]

import networkx as nx
d={}
for i in t_digit.cells():
    d[ i ] = nx.dijkstra_path_length( t_digit._cells, cc, i)
print d

for i in xx:
    for j in t_digit.cells():
        if d[j] > i:
            t_digit.remove_cell( j )
            t_canal.remove_cell( j )
            t_canal_without_center.remove_cell( j )
    z1.append(comparePIN_2(t_digit, t_canal, 0.5, 0.1001))
    z2.append(comparePIN_2(t_digit, t_canal_without_center, 0.5, 0.1001))
    print "nbr_cells", len(t_digit.cells())
    print "with_center", comparePIN_2(t_digit, t_canal, 0.5, 0.1001)
    print "without_center", comparePIN_2(t_digit, t_canal_without_center, 0.5, 0.1001)

import pylab
pylab.plot(xx, [i[0] for i in z1], "r", xx, [i[0] for i in z2], "b",xx, [i[1] for i in z1], "r--", xx, [i[1] for i in z2], "b--",xx, [i[2] for i in z1], "r:", xx, [i[2] for i in z2], "b:",)
pylab.title("Red: with center, Blue: without; continous: present; dashed: absent; dotted: total")
pylab.show()
#from openalea.mersim.tissue.algo.walled_tissue import show_cells
#show_cells( t_digit, True)

