# -*- python -*-
#
#       genepattern: abstract geometry and functions to use them
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
This module defines algorithms to geometrycally establish correspondances
between zones
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from pickle import dump,load
from vplants.plantgl.scenegraph import TriangleSet,Scene,Material,Shape
from openalea.container import external_border
from openalea.tissueshape import centroid
from inside import inside,Octree

def read_envelop (filename) :
	"""
	read a file
	return an envelop (TriangleSet)
	"""
	pts,faces = load(open(filename,'rb'))
	if pts is None :
		return None
	else :
		return TriangleSet(pts,faces)

def write_envelop (filename, envelop) :
	"""
	write an envelop into a file
	"""
	if envelop is None :
		pts = None
		faces = None
	else :
		pts = [tuple(vec) for vec in envelop.pointList]
		faces = [tuple(face) for face in envelop.indexList]
	dump( (pts,faces),open(filename,'w') )

def compute_envelop (mesh, pos, zone) :
	"""
	compute the envelop of a zone
	the envelop is the geometrical mesh
	that surround all the cells defined in zone
	return list of point, list of triangles
	"""
	if len(zone) == 0 :
		return None
	#topological border
	border = external_border(mesh,3,zone)
	border_pids = set()
	for fid in border :
		border_pids.update(mesh.borders(2,fid,2))
	#compute geometry
	#
	#list of points
	pts = []
	trans = {}
	for pid in border_pids :
		trans[pid] = len(pts)
		pts.append(pos[pid])
	#list of faces
	bary = reduce(lambda x,y: x+y,pts) / len(pts)
	faces = []
	for fid in border :
		cent = centroid(mesh,pos,2,fid)
		centid = len(pts)
		pts.append(cent)
		up_vector = cent -bary
		for eid in mesh.borders(2,fid) :
			pid1,pid2 = mesh.borders(1,eid)
			if ((pos[pid1]-cent)^(pos[pid2]-cent))*up_vector > 0 :
				faces.append( (centid,trans[pid1],trans[pid2]) )
			else :
				faces.append( (centid,trans[pid2],trans[pid1]) )
	#return
	return TriangleSet(pts,faces)

def find_zone (mesh, pos, envelop) :
	"""
	find all cells in side a given envelop
	envelop closed a triangle set
	"""
	if envelop is None :
		zone = []
	else :
		sc = Scene()
		sc.add(Shape(envelop,Material()))
		octree = Octree(sc,4)
		zone = [cid for cid in mesh.wisps(3) if inside(centroid(mesh,pos,3,cid),octree)]
	return zone
	
