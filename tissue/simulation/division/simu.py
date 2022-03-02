# -*- python -*-
#
#       simulation.template: example simulation package
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

__doc__="""
This module launch the simulation
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

###################################################
#
print "read tissue and properties"
#
###################################################
from vplants.plantgl.math import Vector2,norm
from openalea.celltissue import topen

pos = {}
mesh = None

def load_tissue () :
	global pos,mesh
	f = topen("tissue.zip",'r')
	t,descr = f.read()
	pos,descr = f.read("position")
	cfg = f.read_config("config")
	f.close()
	
	pos = dict( (pid,Vector2(*tup)) for pid,tup in pos.iteritems() )
	mesh = t.relation(cfg.mesh_id)

load_tissue()
###################################################
#
#	cell division
#
###################################################
from math import sin,cos,radians
from openalea.container import Topomesh
from openalea.tissueshape import edge_length,face_surface_2D,face_main_axes_2D,divide_segment

def divide_cell (cid, point, axis, mesh, pos) :
	"""
	divide a cell according to the given axis
	return the id of the newly created wall
	"""
	#create daughter cells
	daughter = [mesh.add_wisp(2) for i in xrange(2)]
	#compute side of points
	point_side = {}
	for pid in mesh.borders(2,cid,2) :
		val = ( pos[pid] - point ) * axis
		if val > 0 :
			point_side[pid] = 1
		else :
			point_side[pid] = 0
	#compute side of walls
	border_points = {}
	for wid in list(mesh.borders(2,cid)) :
		wall_side = set(point_side[pid] for pid in mesh.borders(1,wid))
		if len(wall_side) == 1 :
			side, = wall_side
			mesh.link(2,daughter[side],wid)
		else : #need to divide wall
			pid0, = (pid for pid in mesh.borders(1,wid) if point_side[pid]==0)
			pid1, = (pid for pid in mesh.borders(1,wid) if point_side[pid]==1)
			#mid point
			mid_pid = mesh.add_wisp(0)
			#pos[mid_pid] = (pos[pid0] + pos[pid1]) / 2.
			pos[mid_pid] = divide_segment(pos[pid0],pos[pid1],axis,point)
			border_points[mid_pid] = (mesh.nb_regions(1,wid) == 1) #property used later to create the new separation wall
																   #and shrink the size of this new wall
			#first half wall
			wid0 = mesh.add_wisp(1)
			mesh.link(1,wid0,pid0)
			mesh.link(1,wid0,mid_pid)
			for rid in mesh.regions(1,wid) :
				mesh.link(2,rid,wid0)
			mesh.link(2,daughter[0],wid0)
			#second half wall
			wid1 = mesh.add_wisp(1)
			mesh.link(1,wid1,pid1)
			mesh.link(1,wid1,mid_pid)
			for rid in mesh.regions(1,wid) :
				mesh.link(2,rid,wid1)
			mesh.link(2,daughter[1],wid1)
			#remove old wall
			mesh.remove_wisp(1,wid)
	#remove old cell
	mesh.remove_wisp(2,cid)
	#create border
	wid = mesh.add_wisp(1)
	for pid in border_points :
		mesh.link(1,wid,pid)
	for cid in daughter :
		mesh.link(2,cid,wid)
	#return
	return border_points,wid,daughter

def clone_cell_division (cid, axis) :
	"""
	create a new mesh with the geometry of the cell
	and divide it perpendicularly to axis
	"""
	#create local mesh
	lmesh = Topomesh(3)
	lmesh.add_wisp(2,cid)
	for offset in xrange(1,3) :
		for wid in mesh.borders(2,cid,offset) :
			lmesh.add_wisp(2-offset,wid)
	for wid in mesh.borders(2,cid) :
		lmesh.link(2,cid,wid)
		for pid in mesh.borders(1,wid) :
			lmesh.link(1,wid,pid)
	#create local pos
	lpos = dict( (pid,pos[pid]) for pid in lmesh.wisps(0) )
	centroid = sum(lpos.itervalues(),Vector2()) / len(lpos)
	#divide cell
	border_points,wid,daughter = divide_cell (cid,centroid,axis,lmesh,lpos)
	#return
	return lmesh,lpos,wid

def test_cell_division (cid, prec, w_main_axis, w_wall_length, w_perp, w_daughters_size) :
	"""
	test the division of the cell according to many axis
	"""
	bary,main_axis = face_main_axes_2D(mesh,pos,cid)
	walls = list(mesh.borders(2,cid))
	wall_length_moy = sum(edge_length(mesh,pos,wid) for wid in walls) / len(walls)
	res = []
	for angle in xrange(0,180,prec) :
		axis = Vector2(cos(radians(angle)),sin(radians(angle)))
		lmesh,lpos,wid = clone_cell_division(cid,axis)
		#distance to main axis
		distance_main_axis = abs(axis * main_axis)
		#length of division wall
		ratio_wall_length = - edge_length(lmesh,lpos,wid) / wall_length_moy
		#perpendicularity
		perp = 0
		for pid in lmesh.borders(1,wid) :
			pid1,pid2 = (nid for nid in lmesh.region_neighbors(0,pid) if nid not in lmesh.borders(1,wid))
			wall_dir = lpos[pid2] - lpos[pid1]
			perp += abs(axis * wall_dir) / norm(wall_dir)
		#daughters size
		S1,S2 = ( face_surface_2D(lmesh,lpos,did) for did in lmesh.wisps(2) )
		ratio_daughters_size = - abs(S2 - S1) / (S1 + S2)
		#results
		res.append( (distance_main_axis * w_main_axis +
					 ratio_wall_length * w_wall_length +
					 perp * w_perp +
					 ratio_daughters_size * w_daughters_size,angle) )
	#sort
	res.sort()
	angle = res[-1][1]
	return bary,Vector2(cos(radians(angle)),sin(radians(angle)))
		
def divide_cell_full (cid, point, axis, shrink_factor) :
	"""
	divide a cell
	"""
	border_points,wid,daughter = divide_cell (cid,point,axis,mesh,pos)
	#shrink border
	pid1,pid2 = border_points
	mid = (pos[pid1] + pos[pid2])/2.
	for pid,is_border in border_points.iteritems() :
		if not is_border :
			pos[pid] = mid + ( pos[pid] - mid ) * shrink_factor

###################################################
#
print "GUI"
#
###################################################
from simu_view import SimuView
from simu_gui import SimuGUI

sc = SimuView(vars())
gui = SimuGUI(sc)

###################################################
#
print "simulation loop"
#
###################################################
from openalea.pglviewer import QApplication,Viewer

qapp = QApplication([])
v = Viewer()
v.set_world(sc)
v.add_gui(gui)
v.show()
v.set_2D()
qapp.exec_()


