#!/usr/bin/python
# -*- coding: utf-8 -*-

import strain_toolbox
reload(strain_toolbox)
from strain_toolbox import *

from vplants.mars_alt import imread as imread
print 'Loading Images...'
t1=imread("p114-t1_imgSeg.inr.gz")
t2=imread("p114-t2_imgSeg.inr.gz")

## Extract infos form t1:
x_1,y_1,z_1,L1_1=extraction_surf_L1(t1)
border_1=border_cells(t1)
vertex_1=calcule_vertex(x_1,y_1,z_1,t1,True)
v2c_1, c2v_1, v2b_1 = dictionnaries(vertex_1)

## Read lineage file:
l12=LienTissuTXT.LienTissuTXT("suiviExpert_01.txt")

## Extract infos form t2:
x_2,y_2,z_2,L1_2=extraction_surf_L1(t2)
border_2=border_cells(t2)
vertex_2=calcule_vertex(x_2,y_2,z_2,t2,True)
v2c_2, c2v_2, v2b_2 = dictionnaries(vertex_2)

v2v_21=V2V(l12,v2c_1,v2c_2)
v2v_21[64]=196
v2map=V2MAP(l12,v2c_1)
print 'Percentage of associated Vertex :',float(len(v2v_21))/len(v2map)*100.,'%'

import strain_toolbox
reload(strain_toolbox)
from strain_toolbox import *

import GrowthParamDisplay_vtk2
reload(GrowthParamDisplay_vtk2)
from GrowthParamDisplay_vtk2 import *

p_1,v2p_1=outlines(v2b_1,v2c_1,c2v_1)
#~ SaveVTK(p_1)
pairedEdge_1=pairedEdge_color(v2p_1, p_1, mapped=v2v_21.values())
actors1_1=vertices_edge(p_1, pairedEdge_1)
actors2_1=cells_labels(v2b_1,c2v_1,border_1)
actors3_1=lineaged_cells(v2b_1,c2v_1,l12.cellT1_cellT2.keys())
Global_Display(actors1_1+actors2_1+actors3_1)

p_2,v2p_2=outlines(v2b_2,v2c_2,c2v_2)
pairedEdge_2=pairedEdge_color(v2p_2, p_2, mapped=v2v_21.keys())
actors1_2=vertices_edge(p_2, pairedEdge_2)
actors2_2=cells_labels(v2b_2,c2v_2,border_2)
actors3_2=lineaged_cells(v2b_2,c2v_2,l12.cellT2_cellT1.keys())
Global_Display(actors1_2+actors2_2+actors3_2)

# Coloring division edges:
cells2vrtx_div,list_div=Div_vrtx(l12,c2v_2)
divEdge=divEdge_color(v2p_2, p_2, list_div)
actors4_2=vertices_edge(p_2, divEdge)
Global_Display(actors1_2+actors2_2+actors3_2+actors4_2)


## 2D Strain Crosses in 3D Graphical Display
#############################################

p_1,v2p_1=outlines(v2b_1,v2c_1,c2v_1)
pairedEdge_1=pairedEdge_color(v2p_1, p_1, mapped=v2v_21.values())
actors1_1=vertices_edge(p_1, pairedEdge_1)
actors2_1=cells_labels(v2b_1,c2v_1,border_1)
actors3_1=lineaged_cells(v2b_1,c2v_1,l12.cellT1_cellT2.keys())

v2v_12 = dict((v,k) for k, v in v2v_21.items())
sr,asr,anisotropy,s_t1,s_t2=GOODAL_2D(v2v_21,l12,c2v_1,v2b_1,v2b_2,t1.resolution,deltaT=24)
actors5_1=tensor_display(s_t1, v2b_1,c2v_1,v2v_12,l12)
Global_Display(list(actors1_1)+list(actors2_1)+list(actors3_1)+[actors5_1])



##########################################################################################
## Test Strain Cube
##########################################################################################

cd ~/Meristems/virtuel

## Extract infos form t1:
x_1,y_1,z_1,L1_1=extraction_surf_L1(m)
border_1=border_cells(m)
vertex_1=calcule_vertex(x_1,y_1,z_1,m)
v2c_1, c2v_1, v2b_1 = dictionnaries(vertex_1)

## Recover lineage file:
l12=LienTissuTXT.LienTissuTXT("suiviCarre.txt")

## Extract infos form t2:
x_2,y_2,z_2,mat_2,L1_2=extraction_surf_L1(m2)
border_2=border_cells(m2)
vertex_2=calcule_vertex(x_2,y_2,z_2,m2)
v2c_2, c2v_2, v2b_2 = dictionnaries(vertex_2)

v2v_21=V2V(l12,v2c_1,v2c_2)

## 2D Strain Crosses in 3D:
sr,asr,anisotropy,s_t1,s_t2=GOODAL_2D(v2v_21,l12,c2v_1,v2b_1,v2b_2,m.resolution,deltaT=24)

p_1,v2p_1=outlines(v2b_1,v2c_1,c2v_1)
pairedEdge_1=pairedEdge_color(v2p_1, p_1, mapped=v2v_21.values())
actors1_1=vertices_edge(p_1, pairedEdge_1)
actors2_1=cells_labels(v2b_1,c2v_1,border_1)
actors3_1=lineaged_cells(v2b_1,c2v_1,l12.cellT1_cellT2.keys())
actors5_1=tensor_display(s_t1, v2b_1,c2v_1,v2v_12,l12)
Global_Display(list(actors1_1)+list(actors2_1)+list(actors3_1)+[actors5_1])



##########################################################################################
## FULL 3D GOODALL
##########################################################################################

from numpy.linalg import *
v2v_12 = dict((v,k) for k, v in v2v.items())
c_xyz1,c_xyz2={},{}
c1,c2={},{}
leastsq={}
SVD={}
######### WARNING: NEED TO CHECK IF THE BARYCENTER OF THE VERTICES ARE GIVEN IN THE SAME ORDER IN xyz1 & xyz2
for c in l12.cellT1_cellT2.keys():
	if sum([(c2v_1[c][k] in v2v_12.keys()) for k in range(len(c2v_1[c]))])==len(c2v_1[c]):
		xyz1=np.array([v2b_1[c2v_1[c][k]] for k in range(len(c2v_1[c]))])
		xyz2=np.array([v2b_2[v2v_12[c2v_1[c][k]]] for k in range(len(c2v_1[c]))])
		c1[c]=np.array((np.mean(xyz1[:,0]),np.mean(xyz1[:,1]),np.mean(xyz1[:,2])))
		c2[c]=np.array((np.mean(xyz2[:,0]),np.mean(xyz2[:,1]),np.mean(xyz2[:,2])))
		c_xyz1[c]=np.array(xyz1-c1[c])
		c_xyz2[c]=np.array(xyz2-c2[c])
		leastsq[c]=np.linalg.lstsq(c_xyz1[c],c_xyz2[c])
		SVD[c]=svd(leastsq[c][0])
	else:
		print 't1-cell ',c,'has some vertex association missing!!!' 



########################################
### Volume L1
########################################
import vertex_detection3
reload(vertex_detection3)
from vertex_detection3 import *

print 'Loading Images...'
t1=imread("p114-t1_imgSeg_L1.inr.gz")
t2=imread("p114-t2_imgSeg_L1.inr.gz")

## Extract infos form t1:
x_1,y_1,z_1,L1_1=extraction_vol_L1(t1)
border_1=border_cells(t1)
vertex_1=calcule_vertex(x_1,y_1,z_1,t1)
v2c_1, c2v_1, v2b_1 = dictionnaries(vertex_1)

## Recover lineage file:
l12=LienTissuTXT.LienTissuTXT("suiviExpert_01.txt")

## Extract infos form t2:
x_2,y_2,z_2,L1_2=extraction_vol_L1(t2)
border_2=border_cells(t2)
vertex_2=calcule_vertex(x_2,y_2,z_2,t2)
v2c_2, c2v_2, v2b_2 = dictionnaries(vertex_2)

v2v=V2V(l12,v2c_1,v2c_2)
v2map=V2MAP(l12,v2c_1)
print 'Percentage of associated Vertex :',float(len(v2v))/len(v2map)*100.,'%'

p_1,v2p_1=outlines(v2b_1,v2c_1,c2v_1)
pairedEdge_1=pairedEdge_color(v2p_1, p_1, mapped=v2v.values())
actors1_1=vertices_edge(p_1, pairedEdge_1)
actors2_1=cells_labels(v2b_1,c2v_1,border_1)
actors3_1=lineaged_cells(v2b_1,c2v_1,l12.cellT1_cellT2.keys())
Global_Display(actors1_1+actors2_1+actors3_1)

p_2,v2p_2=outlines(v2b_2,v2c_2,c2v_2)
pairedEdge_2=pairedEdge_color(v2p_2, p_2, mapped=v2v.keys())
actors1_2=vertices_edge(p_2, pairedEdge_2)
actors2_2=cells_labels(v2b_2,c2v_2,border_2)
actors3_2=lineaged_cells(v2b_2,c2v_2,l12.cellT2_cellT1.keys())
Global_Display(actors1_2+actors2_2+actors3_2)
