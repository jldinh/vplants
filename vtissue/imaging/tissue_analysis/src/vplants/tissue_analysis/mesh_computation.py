#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#       Vplants.tissue_analysis
#
#       Copyright 2011 INRIA - CIRAD - ENS 
#
#       File author(s): Jonathan Legrand <jlegra02@ens-lyon.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################

__license__ = "CeCILL v2"
__revision__ = " $Id$ "

from openalea.image.serial.basics import imread
import numpy as np
from enthought.mayavi import mlab
import scipy.ndimage as nd
import vtk
from enthought.tvtk.tools import ivtk
from vplants.tissue_analysis.growth_analysis import cells_walls_detection


def calcule_vertex(mat,walls_coord,display=False,display_edges=False,remove_borders=False):
	"""
	Calculates cell's vertices positions according to the rule: a vertex is the point where you can find 4 differents cells.
	For the surface, the outer 'cell' #1 is considered as a cell.
	
	:INPUTS:
		.x,y,z: coordinates of the voxels at the surface of the meristem (also called the first layer or L1)
		.mat: Spatial Image containing cells (segmented image). Can be a full spatial image or an extracted surface.
		.display: boolean defining if the function should open an mlab window to represent the cells and the vertex (red cubes)
		.remove_borders: boolean defining if the function sould try to remove cells at the border of the stack before representation.
	
	:OUTPUT:
		.Bary_vrtx: 
			*keys = the 4 cells ids associated with the vertex position(values);
			*values = 3D coordinates of the vertex in the Spatial Image;
	"""
	## We first regroup all the voxels coordiantes in three vectors 'x','y' and 'z'.
	x,y,z=[],[],[]
	for c in walls_coord.keys():
		x.extend(walls_coord[c][0,:]),y.extend(walls_coord[c][1,:]),z.extend(walls_coord[c][2,:])

	## Compute vertices positions by findind the voxel belonging to each vertex.
	print 'Compute vertices positions by findind the voxels belonging to each vertex.'
	Vvox_c={}
	Evox_c={}
	dim=len(x)
	for n in xrange(dim):
		if n%20000==0:
			print n,'/',dim
		i,j,k=x[n],y[n],z[n]
		sub=mat[(i-1):(i+2),(j-1):(j+2),(k-1):(k+2)] # we generate a sub-matrix...
		sub=tuple(np.unique(sub)) # ...in which we search for 4 different cells
		if (len(sub)==4): # detect voxels defining cells' vertices.
			if Vvox_c.has_key(sub):
				Vvox_c[sub]=np.vstack((Vvox_c[sub],np.array((i,j,k)).T)) # we group voxels defining the same vertex by the IDs of the 4 cells.
			else:
				Vvox_c[sub]=np.ndarray((0,3))
		if display_edges:
			if (len(sub)==3): # detect voxels defining cells' edges.
				if Evox_c.has_key(sub):
					Evox_c[sub]=np.vstack((Evox_c[sub],np.array((i,j,k)).T))
				else:
					Evox_c[sub]=np.ndarray((0,3))
	
	## Compute the barycenter of the voxels associated to each vertex (correspondig to the 3 cells detected previously).
	print 'Compute the barycenter of the voxels associated to each vertex (correspondig to the 3 cells detected previously).\n'
	Bary_vrtx={}
	for i in Vvox_c.keys():
		Bary_vrtx[i]=np.mean(Vvox_c[i],0)

	if display:
		Vvox_x,Vvox_y,Vvox_z=[],[],[]
		Bary_vrtx_x,Bary_vrtx_y,Bary_vrtx_z=[],[],[]
		for i in Vvox_c.keys():
			if len(Vvox_c[i]) != 0:
				Vvox_x+=list(Vvox_c[i][:,0])
				Vvox_y+=list(Vvox_c[i][:,1])
				Vvox_z+=list(Vvox_c[i][:,2])
				Bary_vrtx_x.append(np.mean(Vvox_c[i][:,0]))
				Bary_vrtx_y.append(np.mean(Vvox_c[i][:,1]))
				Bary_vrtx_z.append(np.mean(Vvox_c[i][:,2]))
		print 'Generating mlab representation of the surface. Red cube indicate the location of the vertices.'
		around=np.vectorize(np.around)
		intv=np.vectorize(int)
		s=mat[intv(around(Bary_vrtx_x)),intv(around(Bary_vrtx_y)),intv(around(Bary_vrtx_z))]
		mlab.figure(size=(800, 800))
		mlab.points3d(Bary_vrtx_x,Bary_vrtx_y,Bary_vrtx_z,s,mode="cube",scale_mode='none',scale_factor=2,color=(1,0,0),opacity=0.6)
		if display_edges:
			mlab.points3d(Evox_c[0],Evox_c[1],Evox_c[2],s,mode="cube",scale_mode='none',scale_factor=1,color=(0,0,0),opacity=0.3)
		x,y,z=cells_walls_detection(mat)		
		mlab.points3d(x,y,z,mat[x,y,z],mode="point",scale_mode='none',scale_factor=0.3,colormap='prism')
		mlab.show()

	return Bary_vrtx

	
def calcule_vertex2(mat,x,y,z,display=False,display_edges=False,remove_borders=False):
	"""
	Calculates cell's vertices positions according to the rule: a vertex is the point where you can find 4 differents cells.
	For the surface, the outer 'cell' #1 is considered as a cell.
	
	:INPUTS:
		.x,y,z: coordinates of the voxels at the surface of the meristem (also called the first layer or L1)
		.mat: Spatial Image containing cells (segmented image). Can be a full spatial image or an extracted surface.
		.display: boolean defining if the function should open an mlab window to represent the cells and the vertex (red cubes)
		.remove_borders: boolean defining if the function sould try to remove cells at the border of the stack before representation.
	
	:OUTPUT:
		.Bary_vrtx: 
			*keys = the 4 cells ids associated with the vertex position(values);
			*values = 3D coordinates of the vertex in the Spatial Image;
	"""
	## Compute vertices positions by findind the voxel belonging to each vertex.
	print 'Compute vertices positions by findind the voxels belonging to each vertex.'
	Vvox_c={}
	Evox_c={}
	dim=len(x)
	for n in xrange(dim):
		if n%20000==0:
			print n,'/',dim
		i,j,k=x[n],y[n],z[n]
		sub=mat[(i-1):(i+2),(j-1):(j+2),(k-1):(k+2)] # we generate a sub-matrix...
		sub=tuple(np.unique(sub)) # ...in which we search for 4 different cells
		if (len(sub)==4): # detect voxels defining cells' vertices.
			if Vvox_c.has_key(sub):
				Vvox_c[sub]=np.vstack((Vvox_c[sub],np.array((i,j,k)).T)) # we group voxels defining the same vertex by the IDs of the 4 cells.
			else:
				Vvox_c[sub]=np.ndarray((0,3))
		if display_edges:
			if (len(sub)==3): # detect voxels defining cells' edges.
				if Evox_c.has_key(sub):
					Evox_c[sub]=np.vstack((Evox_c[sub],np.array((i,j,k)).T))
				else:
					Evox_c[sub]=np.ndarray((0,3))
	
	## Compute the barycenter of the voxels associated to each vertex (correspondig to the 3 cells detected previously).
	print 'Compute the barycenter of the voxels associated to each vertex (correspondig to the 3 cells detected previously).\n'
	Bary_vrtx={}
	for i in Vvox_c.keys():
		Bary_vrtx[i]=np.mean(Vvox_c[i],0)

	if display:
		Vvox_x,Vvox_y,Vvox_z=[],[],[]
		Bary_vrtx_x,Bary_vrtx_y,Bary_vrtx_z=[],[],[]
		for i in Vvox_c.keys():
			if len(Vvox_c[i]) != 0:
				Vvox_x+=list(Vvox_c[i][:,0])
				Vvox_y+=list(Vvox_c[i][:,1])
				Vvox_z+=list(Vvox_c[i][:,2])
				Bary_vrtx_x.append(np.mean(Vvox_c[i][:,0]))
				Bary_vrtx_y.append(np.mean(Vvox_c[i][:,1]))
				Bary_vrtx_z.append(np.mean(Vvox_c[i][:,2]))
		print 'Generating mlab representation of the surface. Red cube indicate the location of the vertices.'
		around=np.vectorize(np.around)
		intv=np.vectorize(int)
		s=mat[intv(around(Bary_vrtx_x)),intv(around(Bary_vrtx_y)),intv(around(Bary_vrtx_z))]
		mlab.figure(size=(800, 800))
		mlab.points3d(Bary_vrtx_x,Bary_vrtx_y,Bary_vrtx_z,s,mode="cube",scale_mode='none',scale_factor=2,color=(1,0,0),opacity=0.6)
		if display_edges:
			mlab.points3d(Evox_c[0],Evox_c[1],Evox_c[2],s,mode="cube",scale_mode='none',scale_factor=1,color=(0,0,0),opacity=0.3)
		x,y,z=cells_walls_detection(mat)		
		mlab.points3d(x,y,z,mat[x,y,z],mode="point",scale_mode='none',scale_factor=0.3,colormap='prism')
		mlab.show()

	return Bary_vrtx


def dictionnaries(Bary_vrtx):
	"""
	Creates vrtx2cell, cell2vrtx & vrtx2bary dictionnaries.
	
	:INPUT:
		.Bary_vrtx: dict *keys=the 4 cells ids at the vertex position ; *values=3D coordinates of the vertex in the Spatial Image.
	
	:OUPTUTS:
		.vrtx2cell: dict *keys=vertex id ; *values=ids of the 4 associated cells
		.cell2vrtx: dict *keys=cell id ; *values=ids of the vertex defining the cell
		.vrtx2bary: dict *keys=vertex id ; *values=3D coordinates of the vertex in the Spatial Image
	"""
	print 'Creates vrtx2cell(vertex and its cells) , cell2vrtx(cell and its vertices) dictionnaries'
	vrtx2cell={} #associated cells to each vertex;
	cell2vrtx={} #associated vertex to each cells;
	vrtx2bary={}
	for n,i in enumerate(Bary_vrtx.keys()):
		if i in vrtx2cell.values():
			print 'Vertex ',n,' already assigned to ',i
		vrtx2cell[n]=i
		vrtx2bary[n]=list(Bary_vrtx[i])
		for j in i:
			#check if cell j is already in the dict
			if cell2vrtx.has_key(j): 
				cell2vrtx[j]=cell2vrtx[j]+[n] #if true, keep the previous entry (vertex)and give the value of the associated vertex
			else:
				cell2vrtx[j]=[n] #if false, create a new one and give the value of the associated vertex
	#~ del(cell2vrtx[1]) #cell n°1 doesn't really exist...
	
	return vrtx2cell, cell2vrtx, vrtx2bary


def outlines(vertex2bary, vertex2cells, cells2vertex, as_vtk_mesh=True):
	"""
	VTK 3D representation of the vertices and the edges of cells .
	
	:INPUT:
		- vertex2bary : vertices (keys) found on the segmented tissue and their xyz co-ordinates (values);
		- vertex2cells : vertices (keys) found on the segmented tissue and their (4) surrounding cells (values);
		- cells2vertex : cells (keys) found on the segmented tissue and their (4) surrounding cells (vertices);
	
	:OUTPUT: 
		- p : VTK polyData containing *Points:'points', *Lines:'lines' and *Scalars:'vrtx_labels'.
		- vrtx2points : Dict with labels of the cell (keys) and it's vtkPoint value.
	"""

	p=vtk.vtkPolyData()
	points=vtk.vtkPoints() # Contain vertices.
	lines=vtk.vtkCellArray() # Contain edges between vertices.
	vrtx_labels=vtk.vtkLongArray() # Contain vertices labels.
	vlv=[] # Contain edges between two vertices.
	vrtx2points={} # Dict with labels of the cell (keys) and it's vtkPoint value.
	
	print 'Creating "Point" object in VTK to represent the cells'' vertices.'
	nb_v=len(vertex2bary.keys())
	for k in vertex2bary.keys(): # For all the vertices we save their xyz position.
		if k%100==0:
			print k,'/',nb_v
		p1=points.InsertNextPoint(vertex2bary[k])# Add co-ordinates (xyz) of edge-related vertices.
		vrtx2points[k]=p1
		# Add labels of the vertices.
		vrtx_labels.InsertValue(p1, k)

	print 'Creating ''Lines'' object in VTK to represent the edges connecting the vertices.'
	for k in vertex2bary.keys(): # For all the vertices we will look for their related neighbours vertices to create edges between them (and so delimit cells).
		if k%100==0:
			print k,'/',nb_v
		l=[cells2vertex[i] for i in vertex2cells[k] if i!=1] ## vertices of the surrounding cells associated with the vertex k. (!!!include the vertex k!!!)
		l2=np.unique([l[t][tt] for t in range(len(l)) for tt in range(len(l[t]))]) ## We create a unique array of the previous list.
		for j in l2: ## Loop on only those potentially edge-related vertices;
			test1=set(vertex2cells[k])
			test2=set(vertex2cells[j])
			## We make sure that:
			# - ( j!=k ): we are considering two DIFFERENT vertices;
			# - ( sorted([j,k]) ) not in vlv ): there is no edge already defined between the two vertices j & k;
			# - ( len(test1&test2)==3 ): the 2 vertices (j & k) have 3 cells in common (definition of an edge);
			if ( j!=k ) and ( sorted([j,k]) not in vlv ) and ( len(test1&test2)==3 ):
				vlv.append(sorted([j,k])) # Add an edge between the two vertices j & k.
				# Create the edge.
				lines.InsertNextCell(2)
				lines.InsertCellPoint(vrtx2points[k])
				lines.InsertCellPoint(vrtx2points[j])
				
	# Give the *Points:'points', *Lines:'lines' and *Scalars:'vrtx_labels' to the PolyData.
	p.SetPoints(points)
	p.SetLines(lines)
	p.GetPointData().SetScalars(vrtx_labels)
	
	if as_vtk_mesh:
		return p,vrtx2points
	else:
		return vlv


def pairedEdge_color(vrtx2points, p, mapped):
	"""
	Color vertices according to their status in the 'mapped' dict (associated to its corresponding in the other time point).
	
	:INPUTS:
		.vrtx2points: Dict with labels of the cell (keys) and it's vtkPoint value.
		.p: VTK polyData containing *Points:'points', *Lines:'lines' and *Scalars:'vrtx_labels'.
		.mapped: list of vertex that have been associate over time.
	
	:OUTPUT:
		.lut: vtkLookupTable = Green if the vertex have been mapped.
	"""
	lut = vtk.vtkLookupTable()
	nb_v=max(mapped)
	lut.SetNumberOfColors(max(vrtx2points.keys())+1)
	# Color vertices according to their status in the 'mapped' dict.
	for k in vrtx2points.keys(): # For all the vertices we will look for their related neighbours vertices to create edges between them (and so delimit cells).
		if k in mapped:
			lut.SetTableValue(vrtx2points[k],0.,1.,0.,1.) # Green if the vertex have been mapped (associated to its corresponding in the other time point)
		else:
			lut.SetTableValue(vrtx2points[k],1.,1.,1.,1.) # White if the vertex have not been mapped.
	
	return lut


def vertices_edge(p, lut=vtk.vtkLookupTable()):
	"""
	"""
	# Explain that the *Scalars are labels
	ldm = vtk.vtkLabeledDataMapper()
	ldm.SetInput(p)
	ldm.SetLabelModeToLabelScalars()
	# Define the *Actor(2D) and *Mapper for the labels.
	a2=vtk.vtkActor2D()
	a2.SetMapper(ldm)

	# Define the *Actor and *Mapper for the vertices and edges.
	a=vtk.vtkActor()
	m=vtk.vtkPolyDataMapper()
	a.SetMapper(m)
	m.SetInput(p)
	
	m.SetScalarRange(0,p.GetPointData().GetArray(0).GetRange()[1])
	m.ScalarVisibilityOn()
	m.SetLookupTable(lut)
	a.GetProperty().SetLineWidth(5)
	a.GetProperty().SetColor(1.,1.,1.)
	m.Update()
	ldm.Update()

	return a, a2


def SaveVTK(p,filename="outlines"):
	"""
	"""
	w=vtk.vtkPolyDataWriter()
	w.SetFileName(filename+".vtk")
	w.SetInput(p)
	w.Update()


def cells_labels(vertex2bary,cells2vertex,donotdisplay=np.array((0,1))):
	"""
	###### MAPPING VTK DES LABELS DES CELLULES ######
	"""
	p_c=vtk.vtkPolyData()
	points_c=vtk.vtkPoints()
	label_c=vtk.vtkLongArray()
	cs=vtk.vtkCubeSource()
	cs.SetXLength(0.5); cs.SetYLength(0.5); cs.SetZLength(0.5)
	
	for c in cells2vertex.keys():
		if c not in donotdisplay:
			xyz=np.array([vertex2bary[vrtx] for vrtx in cells2vertex[c]])
			centroid=np.array((np.mean(xyz[:,0]),np.mean(xyz[:,1]),np.mean(xyz[:,2])))
			p_centroid=points_c.InsertNextPoint(centroid)
			label_c.InsertValue(p_centroid, c)

	p_c.SetPoints(points_c)
	p_c.GetPointData().SetScalars(label_c)
	ldm_c = vtk.vtkLabeledDataMapper()
	ldm_c.SetInput(p_c)
	ldm_c.SetLabelModeToLabelFieldData()
	ldm_c.GetLabelTextProperty().SetColor(1.,0.,0.)
	a_c2=vtk.vtkActor2D()
	a_c2.SetMapper(ldm_c)
	a_c2.GetProperty().SetColor(1.,0.,0.)

	a_c=vtk.vtkActor()
	m_c=vtk.vtkPolyDataMapper()
	a_c.SetMapper(m_c)
	m_c.SetInput(p_c)
	a_c.GetProperty().SetLineWidth(4)
	m_c.Update()

	# The glyph filter.
	g = vtk.vtkGlyph3D()
	g.SetScaleModeToDataScalingOff()
	g.SetVectorModeToUseVector()
	g.SetInput(p_c)
	g.SetSource(cs.GetOutput())
	# Define the *Actor and *Mapper for the vertices and edges.
	m = vtk.vtkPolyDataMapper()
	m.SetInputConnection(g.GetOutputPort())
	a = vtk.vtkActor()
	a.SetMapper(m)
  
	m.ScalarVisibilityOn()
	a.GetProperty().SetColor(0.,1.,0.)
	m.Update()

	return a_c, a_c2, a


def lineaged_cells(vertex2bary,cells2vertex,mapped_cell):
	"""
	"""
	p=vtk.vtkPolyData()
	points=vtk.vtkPoints()
	label=vtk.vtkLongArray()
	cs=vtk.vtkCubeSource()
	cs.SetXLength(2.); cs.SetYLength(2.); cs.SetZLength(2.)
	
	for c in cells2vertex.keys():
		if c in mapped_cell and c!=1:
			xyz=np.array([vertex2bary[vrtx] for vrtx in cells2vertex[c]])
			centroid=np.array((np.mean(xyz[:,0]),np.mean(xyz[:,1]),np.mean(xyz[:,2])))
			p_centroid=points.InsertNextPoint(centroid)
			label.InsertValue(p_centroid, c)

	p.SetPoints(points)
	p.GetPointData().SetScalars(label)
	ldm = vtk.vtkLabeledDataMapper()
	ldm.SetInput(p)
	ldm.SetLabelModeToLabelFieldData()
	ldm.GetLabelTextProperty().SetColor(1.,1.,0.)
	a2=vtk.vtkActor2D()
	a2.SetMapper(ldm)
	a2.GetProperty().SetColor(0,1,0)

	# The glyph filter.
	g = vtk.vtkGlyph3D()
	g.SetScaleModeToDataScalingOff()
	g.SetVectorModeToUseVector()
	g.SetInput(p)
	g.SetSource(cs.GetOutput())
	# Define the *Actor and *Mapper for the vertices and edges.
	m = vtk.vtkPolyDataMapper()
	m.SetInputConnection(g.GetOutputPort())
	a = vtk.vtkActor()
	a.SetMapper(m)
  
	m.ScalarVisibilityOn()
	a.GetProperty().SetColor(0,0,1)
	m.Update()

	return a, a2


def divEdge_color(vrtx2points, p, vrtx_div):
	"""
	"""
	lut = vtk.vtkLookupTable()
	nb_v=max(vrtx_div)
	lut.SetNumberOfColors(max(vrtx2points.keys())+1)
	# Color vertices according to their status in the 'mapped' dict.
	for k in vrtx2points.keys(): # For all the vertices we will look for their related neighbours vertices to create edges between them (and so delimit cells).
		if k in vrtx_div:
			lut.SetTableValue(vrtx2points[k],1.,0.,0.,1.)

	return lut


def Div_vrtx(l12,cell2vrtx):
	"""
	We search for the vertex belonging to the division edges.
	
	:INPUTS:
		.l12: LienTissuTXT cells lineage;
		.cell2vrtx: cells to vertex at time t_n+1 (time where division have occured);
	
	:OUTPUTS:
		.cell_div: *keys= mother cell number ; *values= t_n+1 vertex dividing the mother cell
		.list_div: list des vertices appartenant aux plans de divisions.
	"""
	## We create a dict: keys = mother cells numbers; values = vertex belonging to the daughters.
	mc2dv={}
	for m in l12.cellT1_cellT2.keys():
		for i in l12.cellT1_cellT2[m]:
			if mc2dv.has_key(m):
				mc2dv[m]=mc2dv[m]+[cell2vrtx[i]]
			else:
				mc2dv[m]=[cell2vrtx[i]]

	## We serch for vertex appearing two times for the same mother cell in the previous dict: they belong to the division plan(s).
	cell_div={} # keys mother cell number; values= vertex belonging to the division plane(s)
	for c in mc2dv.keys():
		nb_d=len(mc2dv[c])
		div=[]
		if nb_d>1:
			s=[mc2dv[c][n] for n in range(nb_d)]
			for i in range(nb_d):
				for j in range(i+1,nb_d):
					div.extend(set(mc2dv[c][i])&set(mc2dv[c][j]))
			cell_div[c]=div
	
	list_div=[cell_div[n][nn] for n in cell_div.keys() for nn in range(len(cell_div[n]))]
		
	return cell_div, list_div


def tensor_display(strain, v2b,c2v,v2v,l12):
	"""
	Display strain crosses in 3D space.
	
	:INPUTS:
		.strain: 2D strain at time t_n represented in a 3D space (tensor: 3x3 matrix)
		.v2b: vertices (keys) found on the segmented tissue and their xyz co-ordinates (values);
		.c2v: cells to vertex at time t_n+1
		.v2v: associated vertex over time (t_n : t_n+1)
		.l12: LienTissuTXT cells lineage;
	
	:OUTPUT:
		.a: vtkActor
	"""
	pts = vtk.vtkPoints()
	tensors=vtk.vtkFloatArray()
	tensors.SetNumberOfComponents(9)
	p=vtk.vtkPolyData()
	sg = vtk.vtkSphereSource()
	sg = vtk.vtkAxes()

	#~ for c in l12.cellT1_cellT2.keys():
	for c in c2v.keys():
		if sum([(c2v[c][k] in v2v.keys()) for k in range(len(c2v[c]))])==len(c2v[c]):
			if (len(c2v[c])>2):
				N = len(c2v[c])
				xyz=np.array([v2b[c2v[c][k]] for k in range(N)]) # t1 coordinates
				#~ xyz=np.array([v2b_2[v2v_12[c2v_1[c][k]]] for k in range(N)]) # t2 coordinates
				x,y,z=np.array((np.mean(xyz[:,0]),np.mean(xyz[:,1]),np.mean(xyz[:,2])))
				pts.InsertNextPoint(x,y,z)
				tensors.InsertNextTuple9(strain[c][0,0],strain[c][0,1],strain[c][0,2],strain[c][1,0],strain[c][1,1],strain[c][1,2],strain[c][2,0],strain[c][2,1],strain[c][2,2])

	p.SetPoints(pts)
	p.GetPointData().SetTensors(tensors)
	g = vtk.vtkTensorGlyph()
	g.SetInput(p)
	g.SetSource(sg.GetOutput())
	#~ g.SymmetricOn()
	#~ g.ScalingOff()
	#~ g.ExtractEigenvaluesOn()
	#~ g.SetScaling(4)
	# Define the *Actor and *Mapper for the vertices and edges.
	m = vtk.vtkPolyDataMapper()
	m.SetInput(g.GetOutput())
	a = vtk.vtkActor()
	a.SetMapper(m)
	m.ScalarVisibilityOn()
	m.Update()

	return a


def vtk_volume(mat,lineage_12,data2plot,legend_title=""):
	"""
	VTK 3D "points" representation of the cells according to the 'data' dict
	
	:INPUTS:
		.mat: Spatial Image (matrix) of the FM;
		.lineage_12: dict made of *keys= cell id @ t_n, *values= daughter(s) cell(s) id(s) @ t_n+1;
		.data2plot: dict made of *keys= cell id @ t_n, *values= any previouly computed data to represent;
		.legend_title: text that will appear at the top of the scale bar givin the meaning of the data;
	
	:OUTPUT:
		.av: vtkActor containing the "vertex points" (not interresting part of the FM - or no data available);
		.ac: vtkActor containing the colored "cube points" representing the data;
		.scalarBar: vtkActor containing the color legend of the represented data;
	"""
	# Loading SpatialImage and produces x,y,z coordinates of the surface:
	print 'Producing x,y,z coordinates of the volume of L1 (only cell walls):'
	x,y,z=cells_walls_detection(mat)

	#~ import copy
	#~ stack=copy.copy(mat)
	#~ b=nd.laplace(stack)
	#~ b[np.where(stack==1)]=0
	#~ stack[b!=0]=1
	#~ b=nd.laplace(stack)
	#~ b[np.where(stack==1)]=0
	#~ stack[b==0]=0
	#~ x,y,z=np.where(stack!=0)

	pdv=vtk.vtkPolyData()
	pdc=vtk.vtkPolyData()
	pts_v=vtk.vtkPoints() # Will receive 3D coordinates of each points we will represent as vertex.
	pts_c=vtk.vtkPoints() # Will receive 3D coordinates of each points we will represent as a colored cube.
	labels=vtk.vtkFloatArray()
	cs=vtk.vtkCubeSource()
	cs.SetXLength(1.); cs.SetYLength(1.); cs.SetZLength(1.)
	## LUT
	lut = vtk.vtkLookupTable()
	lut.SetNumberOfColors(256)
	lut.SetRampToLinear()
	lut.SetHueRange(0.667, 0.0)	# This creates a blue to red lut.
	# Creating ''Points'' objects in VTK to represent the vertices.
	print 'Creating ''Points'' objects in VTK to represent the vertices.'
	nb_v=len(x)
	for n in range(nb_v): # For all the vertices we seva their xyz position.
		if n%50000==0:
			print n,'/',nb_v
		if data2plot.has_key(mat[x[n],y[n],z[n]]) and lineage_12.has_key(mat[x[n],y[n],z[n]]): # We don't want to display a 'vtkPoints' object where we will display datas.
			p_c=pts_c.InsertNextPoint(np.array((x[n],y[n],z[n])))# Add co-ordinates (xyz) of points.
			labels.InsertNextValue(data2plot[mat[x[n],y[n],z[n]]])
		else:
			p_v=pts_v.InsertNextPoint(np.array((x[n],y[n],z[n])))# Add co-ordinates (xyz) of points.

	# Give the *Points: 'pts_c' & 'pts_v' to the PolyData.
	pdv.SetPoints(pts_v)
	pdc.SetPoints(pts_c)
	pdc.GetPointData().SetScalars(labels)
	##
	# Glyph 3D Filter:
	gc=vtk.vtkGlyph3D()
	gc.SetInput(pdc)
	gc.SetSource(cs.GetOutput())
	gc.SetVectorModeToUseVector()
	gc.SetScaleModeToDataScalingOff()
	gc.SetScaleFactor(1)
	# Define the *Actor and *Mapper for the vertices and edges.
	mc=vtk.vtkPolyDataMapper()
	mc.SetLookupTable(lut)
	mc.SetInputConnection(gc.GetOutputPort())
	#~ mc.SetScalarRange(min(data2plot.values()),max(data2plot.values()))
	mc.SetScalarRange(labels.GetRange())
	##
	# a colorbar 
	scalarBar = vtk.vtkScalarBarActor()
	scalarBar.SetLookupTable(lut)
	scalarBar.SetTitle(legend_title) 
	ac=vtk.vtkActor()
	ac.SetMapper(mc)
	mc.ScalarVisibilityOn()
	mc.Update()
	##
	# Glyph Vertex Filter:
	gv=vtk.vtkVertexGlyphFilter()
	gv.SetInput(pdv)
	# Define the *Mapper
	mv=vtk.vtkPolyDataMapper()
	mv.SetInputConnection(gv.GetOutputPort())
	mv.ScalarVisibilityOn()
	# Define the *Actor
	av=vtk.vtkActor()
	av.SetMapper(mv)
	av.GetProperty().SetColor(1.,1.,1.)
	mv.Update()

	return av,ac,scalarBar

import types 
def is_instance_method(obj):
	"""
	Checks if an object is a bound method on an instance.
	"""
	# Not a method if obj.im_self is None: return False 
	# Method is not bound if issubclass(obj.im_class, type) or obj.im_class is types.ClassType: return False 
	# Method is a classmethod return True
	if not isinstance(obj, types.MethodType):
		return False
	else:
		return True

def graph2vtk_data(mat,dict_data,legend_title="",labels=None,L1_only=False):
	"""
	VTK 3D "points" representation of the cells according to the 'data' dict
	
	:INPUTS:
		.mat: Spatial Image (matrix) of the FM;
		.dict_data: dict made of *keys= cell id @ t_n, *values= any previouly computed data to represent;
		.legend_title: text that will appear at the top of the scale bar givin the meaning of the data;
	
	:OUTPUT:
		.av: vtkActor containing the "vertex points" (not interresting part of the FM - or no data available);
		.ac: vtkActor containing the colored "cube points" representing the data;
		.scalarBar: vtkActor containing the color legend of the represented data;
	"""
	# -- We check for instance methods from 'property_graph' and 'temporal_property_graph'.
	from vplants.tissue_analysis.mesh_computation import is_instance_method
	if is_instance_method(dict_data):
		if labels==None:
			import sys
			print 'You have provided an instance_method but no labels to search in it!!'
			sys.exit(1)
		
		tmp={}
		print 'creating dictionnary from instance method:'
		for i in labels:
			if isinstance(dict_data(i),int):
				tmp[i]=dict_data(i)
			else:
				import sys
				print "Your instance method return ",str(type(dict_data(i)))," and I don't know what to do with that!! Interger needed :)..."
				sys.exit(1)
		dict_data=tmp

	if labels==None:
		labels=dict_data.keys()

	if L1_only:
		from vplants.tissue_analysis.growth_analysis import dict_cells_slices,dict_cells_walls_coordinates
		x,y,z=[],[],[]
		xyz,mat=dict_cells_walls_coordinates(mat,dict_cells_slices(mat,labels),True,labels)
		for i in xyz:
			x.extend(list(xyz[i][0,:]))
			y.extend(list(xyz[i][1,:]))
			z.extend(list(xyz[i][2,:]))
	else:
		# Loading SpatialImage and produces x,y,z coordinates of the surface:
		x,y,z=cells_walls_detection(mat)

	pdv=vtk.vtkPolyData()
	pdc=vtk.vtkPolyData()
	pts_v=vtk.vtkPoints() # Will receive 3D coordinates of each points we will represent as vertex.
	pts_c=vtk.vtkPoints() # Will receive 3D coordinates of each points we will represent as a colored cube.
	scalars=vtk.vtkFloatArray()
	cs=vtk.vtkCubeSource()
	cs.SetXLength(1.); cs.SetYLength(1.); cs.SetZLength(1.)
	## LUT
	lut = vtk.vtkLookupTable()
	lut.SetNumberOfColors(256)
	lut.SetRampToLinear()
	lut.SetHueRange(0.667, 0.0)	# This creates a blue to red lut.
	# Creating ''Points'' objects in VTK to represent the vertices.
	print 'Creating ''Points'' objects in VTK to represent the vertices.'
	nb_v=len(x)
	for n in range(nb_v): # For all the vertices we seva their xyz position.
		if n%50000==0:
			print n,'/',nb_v
		if dict_data.has_key(mat[x[n],y[n],z[n]]) and (mat[x[n],y[n],z[n]] in labels): # We don't want to display a 'vtkPoints' object where we will display datas.
			p_c=pts_c.InsertNextPoint(np.array((x[n],y[n],z[n])))# Add co-ordinates (xyz) of points.
			scalars.InsertNextValue(dict_data[mat[x[n],y[n],z[n]]])
		else:
			p_v=pts_v.InsertNextPoint(np.array((x[n],y[n],z[n])))# Add co-ordinates (xyz) of points.

	# Give the *Points: 'pts_c' & 'pts_v' to the PolyData.
	pdv.SetPoints(pts_v)
	pdc.SetPoints(pts_c)
	pdc.GetPointData().SetScalars(scalars)
	##
	# Glyph 3D Filter:
	gc=vtk.vtkGlyph3D()
	gc.SetInput(pdc)
	gc.SetSource(cs.GetOutput())
	gc.SetVectorModeToUseVector()
	gc.SetScaleModeToDataScalingOff()
	gc.SetScaleFactor(1)
	# Define the *Actor and *Mapper for the vertices and edges.
	mc=vtk.vtkPolyDataMapper()
	mc.SetLookupTable(lut)
	mc.SetInputConnection(gc.GetOutputPort())
	mc.SetScalarRange(scalars.GetRange())
	##
	# a colorbar 
	scalarBar = vtk.vtkScalarBarActor()
	scalarBar.SetLookupTable(lut)
	scalarBar.SetTitle(legend_title)
	if isinstance(max(dict_data.values()),int):
		scalarBar.SetMaximumNumberOfColors(max(dict_data.values()))
		if max(dict_data.values())<10:
			scalarBar.SetNumberOfLabels(max(dict_data.values()))
	ac=vtk.vtkActor()
	ac.SetMapper(mc)
	mc.ScalarVisibilityOn()
	mc.Update()
	##
	# Glyph Vertex Filter:
	gv=vtk.vtkVertexGlyphFilter()
	gv.SetInput(pdv)
	# Define the *Mapper
	mv=vtk.vtkPolyDataMapper()
	mv.SetInputConnection(gv.GetOutputPort())
	mv.ScalarVisibilityOn()
	# Define the *Actor
	av=vtk.vtkActor()
	av.SetMapper(mv)
	av.GetProperty().SetColor(1.,1.,1.)
	mv.Update()

	return av,ac,scalarBar


def surface_cells_labels(stack,lineage,datas,daugthers=False):
	"""
	VTK representation of any data as labels above cells (only on surface).
	
	:INPUTS:
		.stack: Spatial Image (matrix) of the FM;
		.lineage: dict made of *keys= cell id @ t_n, *values= daughter(s) cell(s) id(s) @ t_n+1;
		.datas: datas to display as labels;
		.daugthers: use 'True' to represent ladels of nb_D @ t_n+1;
	
	:OUTPUT:
		.al: vtkActor containing labels and their position;
	"""
	from growth_analysis import extraction_surf_L1
	x_surf,y_surf,z_surf,L1_surf,surf=extraction_surf_L1(stack,True)
	
	print 'Creating ''labels'' objects in VTK to represent any numerical data (ex: the number of daugthers as labels) above cells.'
	pdl=vtk.vtkPolyData()
	pts_l=vtk.vtkPoints() # Will receive 3D coordinates of each vertex
	labels=vtk.vtkIntArray()
		
	for n,c in enumerate(lineage.keys()):
		if n%10==0:
			print n,'/',len(lineage.keys())
		if daugthers: # If we want to represent the datas @ t_n+1, we regroups daugthers under the label of their mother.
			dgth=lineage[c]
			if dgth.__class__!=int:
				xv,yv,zv=[],[],[]
				for i in range(len(dgth)):
					x,y,z=np.where(surf==dgth[i])
					xv.extend(x)
					yv.extend(y)
					zv.extend(z)
			else:
				xv,yv,zv=np.where(surf==dgth)
		else:
			xv,yv,zv=np.where(surf==c)
		centroid=np.array((np.mean(xv),np.mean(yv),np.mean(zv)))
		pts_l.InsertNextPoint(centroid)
		labels.InsertNextValue(int(datas[c]))

	pdl.SetPoints(pts_l)
	pdl.GetPointData().SetScalars(labels)
	# Define the *Mapper
	ldm = vtk.vtkLabeledDataMapper()
	ldm.SetInput(pdl)
	ldm.SetLabelModeToLabelFieldData()
	ldm.GetLabelTextProperty().SetColor(1.,1.,1.)
	ldm.GetLabelTextProperty().SetFontSize(22)
	ldm.GetLabelTextProperty().ItalicOff()
	# Define the *Actor
	al=vtk.vtkActor2D()
	al.SetMapper(ldm)
	
	return al


def Global_Display(actors):
	"""
	Display all the actor previously calculated.
	"""
	v=ivtk.viewer()
	v.scene.renderer.background=(0,0,0)
	if type(actors).__name__=='tuple':
		for a in actors:
			v.scene.add_actor(a)
	else:
		v.scene.add_actor(actors)
	
	mlab.show()


def vtk_cells_surf(x,y,z,L1_surf,surf):
	"""
	VTK 3D "points" representation of the cells according to the 'data' dict
	
	:INPUTS:
		.mat: Spatial Image (matrix) of the FM;
	
	:OUTPUT:
		.av: vtkActor containing the surface of cells as "vertex points";
	"""

	## Surface Cells points (Vertex Glyph)
	pdv=vtk.vtkPolyData()
	pts_v=vtk.vtkPoints() # Will receive 3D coordinates of each points we will represent as 'Glyph Vertex Filter'.
	labels=vtk.vtkFloatArray()
	
	## randomLUT
	lut = vtk.vtkLookupTable()
	lut.SetNumberOfColors(max(L1_surf)+1)
	lut.SetRampToLinear()
	lut.SetHueRange(0.667, 0.0)	# This creates a blue to red lut.
	#~ for i in L1_surf:
		#~ lut.SetTableValue(i, float(np.random.random_integers(10,99)/100.), float(np.random.random_integers(10,99)/100.), float(np.random.random_integers(10,99)/100.), 1.0)
	lut.Build() # This creates a random blue to red lut.
	
	# Creating ''Points'' objects in VTK to represent the vertices.
	print 'Creating ''Points'' objects in VTK to represent the vertices.'
	nb_v=len(x)
	for n in range(nb_v): # For all the vertices we seva their xyz position.
		if n%50000==0:
			print n,'/',nb_v
		p_v=pts_v.InsertNextPoint(np.array((x[n],y[n],z[n])))# Add co-ordinates (xyz) of points.
		labels.InsertNextValue( surf[x[n],y[n],z[n]] )

	# Give the *Points: 'pts_v' to the PolyData.
	pdv.SetPoints(pts_v)
	pdv.GetPointData().SetScalars(labels)

	# Glyph Vertex Filter:
	gv=vtk.vtkVertexGlyphFilter()
	gv.SetInput(pdv)
	# Define the *Mapper
	mv=vtk.vtkPolyDataMapper()
	mv.SetLookupTable(lut)
	mv.SetInputConnection(gv.GetOutputPort())
	mv.SetScalarRange(min(L1_surf),max(L1_surf))
	mv.ScalarVisibilityOn()
	# Define the *Actor
	av=vtk.vtkActor()
	av.SetMapper(mv)
	av.GetProperty().SetColor(1.,1.,1.)
	mv.Update()

	return av


def vtk_cells_ids(L1_surf,surf):
	"""
	VTK 3D "points" representation of the cells according to the 'data' dict
	
	:INPUTS:
		.L1_surf: 
		.surf: Spatial Image (matrix) of the FM;
	
	:OUTPUT:
		.av: vtkActor containing the cells ids in their centers;
	"""

	## Creating ''cells_ids'' objects in VTK to represent any numerical data (ex: the number of daugthers as cells_ids) above cells.'
	pdl=vtk.vtkPolyData()
	pts_l=vtk.vtkPoints() # Will receive 3D coordinates of each vertex
	cells_ids=vtk.vtkIntArray()
	
	# Creating ''Points'' objects in VTK to represent the vertices.
	print 'Creating ''Points'' objects in VTK to represent the vertices.'
	for n,c in enumerate(L1_surf):
		if n%10==0:
			print n,'/',len(L1_surf)
		xv,yv,zv=np.where(surf==c)
		centroid=np.array((np.mean(xv),np.mean(yv),np.mean(zv)))
		pts_l.InsertNextPoint(centroid)
		cells_ids.InsertNextValue(int(c))

	pdl.SetPoints(pts_l)
	pdl.GetPointData().SetScalars(cells_ids)
	# Define the *Mapper
	ldm = vtk.vtkLabeledDataMapper()
	ldm.SetInput(pdl)
	ldm.SetLabelModeToLabelFieldData()
	ldm.GetLabelTextProperty().SetColor(1.,1.,1.)
	ldm.GetLabelTextProperty().SetFontSize(22)
	ldm.GetLabelTextProperty().ItalicOff()
	# Define the *Actor
	al=vtk.vtkActor2D()
	al.SetMapper(ldm)
	ldm.Update()
	
	return al
