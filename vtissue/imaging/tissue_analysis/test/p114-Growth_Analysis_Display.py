#!/usr/bin/python
# -*- coding: utf-8 -*-

from openalea.image.serial import imread
print 'Loading Images...'
t1=imread("p114-t1_imgSeg.inr.gz")
t2=imread("p114-t2_imgSeg.inr.gz")
t3=imread("p114-t3_imgSeg.inr.gz")


import strain_toolbox
reload(strain_toolbox)
from strain_toolbox import *
# Extracting the first Layer (and removing the cells at the border of the stack !!):
t1_L1=extraction_vol_L1(t1,"p114-t1_imgSeg_L1-b")
#~ x,y,z=cells_walls_detection(t1_L1)
#~ mlab.points3d(x,y,z,t1_L1[x,y,z],mode="point",scale_mode='none',scale_factor=0.3,colormap='prism')
t2_L1=extraction_vol_L1(t2,"p114-t2_imgSeg_L1-b")
#~ x,y,z=cells_walls_detection(t2_L1)
#~ mlab.points3d(x,y,z,t2_L1[x,y,z],mode="point",scale_mode='none',scale_factor=0.3,colormap='prism')
t3_L1=extraction_vol_L1(t3,"p114-t3_imgSeg_L1-b")
#~ x,y,z=cells_walls_detection(t3_L1)
#~ mlab.points3d(x,y,z,t3_L1[x,y,z],mode="point",scale_mode='none',scale_factor=0.3,colormap='prism')


from openalea.image.serial import imread
# Loading (previously) saved imaged :
t1_L1=imread("p114-t1_imgSeg_L1-b.inr.gz")
t2_L1=imread("p114-t2_imgSeg_L1-b.inr.gz")
t3_L1=imread("p114-t3_imgSeg_L1-b.inr.gz")


import LienTissuTXT
print 'Loading lineages...'
l12=LienTissuTXT.LienTissuTXT("suiviExpert_01.txt")
l23=LienTissuTXT.LienTissuTXT("suiviExpert_12.b.txt")
## Pour générer "suiviExpert_02.txt", utiliser le script ~/Meristems/Scripts_PYTHON/lineage_extension.py (non automatisé)
l13=LienTissuTXT.LienTissuTXT("suiviExpert_02.txt")


import CalculsTissusLiens
reload(CalculsTissusLiens)
from CalculsTissusLiens import nbD_TXT, volumetric_growth, Cells_Volumes

import pickle
# Volumetric Growth:
try:
	f=open('volumetric_growth_12.pic',"r")
	VG_12=pickle.load(f)
	f.close()
except IOError:
	print 'Computing Volumetric Growth...'
	VG_12=volumetric_growth(t1_L1,t2_L1,l12)
	f=open('volumetric_growth_12.pic',"w")
	pickle.dump(VG_12,f)
	f.close()

try:
	f=open('volumetric_growth_23.pic',"r")
	VG_23=pickle.load(f)
	f.close()
except IOError:
	print 'Computing Volumetric Growth...'
	VG_23=volumetric_growth(t2_L1,t3_L1,l23)
	f=open('volumetric_growth_23.pic',"w")
	pickle.dump(VG_23,f)
	f.close()

try:
	f=open('volumetric_growth_13.pic',"r")
	VG_13=pickle.load(f)
	f.close()
except IOError:
	print 'Computing Volumetric Growth...'
	VG_13=volumetric_growth(t1_L1,t3_L1,l13)
	f=open('volumetric_growth_13.pic',"w")
	pickle.dump(VG_13,f)
	f.close()

#Inverting volumetric_growth dict:
VG_21={}
for k in VG_12.keys():
	for v in l12.cellT1_cellT2[k]:
		VG_21[v]=VG_12[k]

VG_32={}
for k in VG_23.keys():
	for v in l23.cellT1_cellT2[k]:
		VG_32[v]=VG_23[k]

VG_31={}
for k in VG_13.keys():
	for v in l13.cellT1_cellT2[k]:
		VG_31[v]=VG_13[k]


# Number of Daughters:
print 'Computing Numbers of Daughters...'
nD_12=nbD_TXT(l12.cellT1_cellT2)
nD_23=nbD_TXT(l23.cellT1_cellT2)
nD_13=nbD_TXT(l13.cellT1_cellT2)


import GrowthParamDisplay_vtk2
reload(GrowthParamDisplay_vtk2)
from GrowthParamDisplay_vtk2 import *

act1=vtk_volume(t1_L1,l12.cellT1_cellT2,VG_12,"Volumetric Growth (%)")
act2=labels_nbDaughters(t1_L1,l12.cellT1_cellT2,nD_12)
actors=[list(act1),[act2]]
Global_Display(actors)

act1=vtk_volume(t2_L1,l23.cellT1_cellT2,VG_23,"Volumetric Growth (%)")
act2=labels_nbDaughters(t2_L1,l23.cellT1_cellT2,nD_23)
actors=[list(act1),[act2]]
Global_Display(actors)

act1=vtk_volume(t1,l13.cellT1_cellT2,VG_13,"Volumetric Growth (%)")
act2=labels_nbDaughters(t1,l13.cellT1_cellT2,nD_13)
actors=[list(act1),[act2]]
Global_Display(actors)

#Inverting volumetric_growth dict:
VG_21={}
for k in VG_12.keys():
	for v in l12.cellT1_cellT2[k]:
		VG_21[v]=VG_12[k]

VG_32={}
for k in VG_23.keys():
	for v in l23.cellT1_cellT2[k]:
		VG_32[v]=VG_23[k]

VG_31={}
for k in VG_13.keys():
	for v in l13.cellT1_cellT2[k]:
		VG_31[v]=VG_13[k]

act1=vtk_volume(t2_L1,l12.cellT2_cellT1,VG_21,"Volumetric Growth (%)")
act2=labels_nbDaughters(t2_L1,l12.cellT1_cellT2,nD_12,daugthers=True)
actors=[list(act1),[act2]]
Global_Display(actors)

act1=vtk_volume(t3_L1,l23.cellT2_cellT1,VG_32,"Volumetric Growth (%)")
act2=labels_nbDaughters(t3_L1,l23.cellT1_cellT2,nD_23,daugthers=True)
actors=[list(act1),[act2]]
Global_Display(actors)

act1=vtk_volume(t3_L1,l13.cellT2_cellT1,VG_31,"Volumetric Growth (%)")
act2=labels_nbDaughters(t3_L1,l13.cellT1_cellT2,nD_13,daugthers=True)
actors=[list(act1),[act2]]
Global_Display(actors)

try:
	f=open('vg-nbd_13.pic',"r")
	actors=pickle.load(f)
	f.close()
	Global_Display(actors)
except IOError:
	print 'Generating Display:'
	act1=vtk_volume(t3_L1,l13.cellT2_cellT1,VG_31,"Volumetric Growth (%)")
	act2=labels_nbDaughters(t3_L1,l13.cellT1_cellT2,nD_13,daugthers=True)
	actors=[list(act1),[act2]]
	f=open('vg-nbd_13.pic',"w")
	pickle.dump(actors,f)
	f.close()
	Global_Display(actors)


## Strain Graphical display.
#############################################
print 'Loading Images...'
t1=imread("p114-t1_imgSeg.inr.gz")
t2=imread("p114-t2_imgSeg.inr.gz")

## Extract infos form t1:
x_1,y_1,z_1,L1_1=extraction_surf_L1(t1)
border_1=border_cells(t1)
vertex_1=calcule_vertex(x_1,y_1,z_1,t1)
v2c_1, c2v_1, v2b_1 = dictionnaries(vertex_1)

## Extract infos form t2:
x_2,y_2,z_2,L1_2=extraction_surf_L1(t2)
border_2=border_cells(t2)
vertex_2=calcule_vertex(x_2,y_2,z_2,t2)
v2c_2, c2v_2, v2b_2 = dictionnaries(vertex_2)

v2v_21=V2V(l12,v2c_1,v2c_2)
v2map=V2MAP(l12,v2c_1)
print 'Percentage of associated Vertex :',float(len(v2v_21))/len(v2map)*100.,'%'

sr,asr,anisotropy,s_t1,s_t2=GOODAL_2D(v2v_21,l12,c2v_1,v2b_1,v2b_2,t1.resolution,deltaT=24)

act1=vtk_volume(t1,l12.cellT1_cellT2,asr,"Areal Strain Rate (µm².µm-².day-¹)")
Global_Display(act1)

act1=vtk_volume(t1,l12.cellT1_cellT2,anisotropy,"Growth Anisotropy")
Global_Display(act1)
