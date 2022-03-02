# -*- python -*-
#
#       tissueview: function used to display tissues
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
This module defines functions to convert topomesh elements
into geometrical pgl objects
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from vplants.plantgl.math import Vector2,Vector3,norm
from vplants.plantgl.scenegraph import Polyline,TriangleSet
from openalea.tissueshape import centroid
from openalea.container import triangulate_face

def edge_geom (mesh, pos, eid) :
	"""PGL geometry of an edge (polyline)
	
	mesh : a container.topomesh instance
	pos : a dict of (pid,Vector)
	eid : id of the edge
	return : pgl.Polyline
	"""
	return Polyline([Vector3(pos[pid]) for pid in mesh.borders(1,eid)])

edge_geom2D = edge_geom
edge_geom3D = edge_geom

def face_geom2D (mesh, pos, fid, up_reversed = False, method = "topo") :
	"""PGL geometry of a face (polygon)
	
	Construct a TriangleSet to represent
	the polygonal geometry of the face.
	
	.. warning:: the face must be almost
	  convex (please)
	
	:Parameters:
	 - `mesh` (:class:`Topomesh`)
	 - `pos` (dict of (pid,Vector2) ) - position of point in space
	 - `fid` (fid) - id of the face
	 - `up_reversed` (bool) - if True, normals point downside instead
	   of upside.
	 - `method` (str) - method used to triangulate the face:
	       - 'topo', use topological triangulation good for convexe faces
	       - 'star', use star triangulation
	
	:Returns Type: :class:`TriangleSet`
	"""
	pids = tuple(mesh.borders(2,fid,2) )
	
	if len(pids) < 3 : #error
		raise UserWarning("face %d not geometrically defined" % fid)
	else :
		#point list
		pts = tuple(Vector3(pos[pid]) for pid in pids)
		trans = dict( (pid,i) for i,pid in enumerate(pids) )
		
		#triangle list
		triangles = []
		if method == 'topo' :
			for pids in triangulate_face(mesh,fid,pos) :
				i1,i2,i3 = (trans[pid] for pid in pids)
				N = (pts[i2] - pts[i1]) ^ (pts[i3] - pts[i1])
				if N.z < 0 :
					i2,i3 = i3,i2
				
				if up_reversed :
					i2,i3 = i3,i2
				
				triangles.append( (i1,i2,i3) )
		elif method == 'star' :
			pts += (sum(pts,Vector3() ) / len(pts),)
			i1 = len(trans)
			
			triangles = []
			for eid in mesh.borders(2,fid) :
				i2,i3 = (trans[pid] for pid in mesh.borders(1,eid) )
				N = (pts[i2] - pts[i1]) ^ (pts[i3] - pts[i1])
				if N.z < 0 :
					i2,i3 = i3,i2
				
				if up_reversed :
					i2,i3 = i3,i2
				
				triangles.append( (i1,i2,i3) )
		else :
			raise UserWarning("triangulation method '%s' unrecognized" % method)
		
		return TriangleSet(pts,triangles)

def face_geom3D (mesh, pos, fid, up_vector, method = "topo") :
	"""PGL geometry of a face (polygon)
	
	Construct a TriangleSet to represent
	the polygonal geometry of the face.
	
	.. warning::
	 - the face must be almost convex (please)
	 - the face must be almost planar
	
	:Parameters:
	 - `mesh` (:class:`Topomesh`)
	 - `pos` (dict of (pid,Vector2) ) - position of point in space
	 - `fid` (fid) - id of the face
	 - `up_vector` (Vector) - give the orientation of the normal
	 - `method` (str) - method used to triangulate the face:
	       - 'topo', use topological triangulation good for convexe faces
	       - 'star', use star triangulation
	
	:Returns Type: :class:`TriangleSet`
	"""
	pids = tuple(mesh.borders(2,fid,2) )
	if len(pids) < 3 : #error
		raise UserWarning("face %d not geometrically defined" % fid)
	else :
		#point list
		pts = tuple(pos[pid] for pid in pids)
		trans = dict( (pid,i) for i,pid in enumerate(pids) )
		
		#triangle list
		triangles = []
		if method == 'topo' :
			for pids in triangulate_face(mesh,fid,pos) :
				i1,i2,i3 = (trans[pid] for pid in pids)
				if ( (pts[i2] - pts[i1]) ^ (pts[i3] - pts[i1]) ) \
				   * up_vector < 0 :
					i2,i3 = i3,i2
				
				triangles.append( (i1,i2,i3) )
		elif method == 'star' :
			pts += (sum(pts,Vector3() ) / len(pts),)
			i1 = len(trans)
			
			for eid in mesh.borders(2,fid) :
				i2,i3 = (trans[pid] for pid in mesh.borders(1,eid) )
				N = (pts[i2] - pts[i1]) ^ (pts[i3] - pts[i1])
				if N * up_vector < 0 :
					i2,i3 = i3,i2
				
				triangles.append( (i1,i2,i3) )
		else :
			raise UserWarning("triangulation method '%s' unrecognized" % method)
		
		return TriangleSet(pts,triangles)

def cell_geom (mesh, pos, cid, normal_inside = False, method = "topo") :
	"""PGL geometry of a face (polyhedron)
	
	Construct a TriangleSet to represent
	the geometry of the cell as a polyhedron.
	
	.. warning::
	 - the cell must be almost convex (please)
	 - the faces of the cell must be almost planar
	
	:Parameters:
	 - `mesh` (:class:`Topomesh`)
	 - `pos` (dict of (pid,Vector3) ) - position of point in space
	 - `cid` (cid) - id of the cell
	 - `normal_inside` (bool) - if True faces normals point inside instead
	    of outside.
	 - `method` (str) - method used to triangulate the face:
	       - 'topo', use topological triangulation good for convexe faces
	       - 'star', use star triangulation
	
	:Returns Type: :class:`TriangleSet`
	"""
	pids = tuple(mesh.borders(3,cid,3) )
	if len(pids) < 4 : #error
		raise UserWarning("cell %d not geometrically defined" % cid)
	else :
		#point list
		pts = tuple(pos[pid] for pid in pids)
		trans = dict( (pid,i) for i,pid in enumerate(pids) )
		cell_cent = reduce(lambda x,y : x + y,pts) / len(pts)
		
		#triangle list
		triangles = []
		if method == 'topo' :
			for fid in mesh.borders(3,cid) :
				up_vector = centroid(mesh,pos,2,fid) - cell_cent
				for pids in triangulate_face(mesh,fid,pos) :
					i1,i2,i3 = (trans[pid] for pid in pids)
					N = (pts[i2] - pts[i1]) ^ (pts[i3] - pts[i1])
					if N * up_vector < 0 :
						i2,i3 = i3,i2
					
					if normal_inside :
						i2,i3 = i3,i2
					
					triangles.append( (i1,i2,i3) )
		elif method == 'star' :
			for fid in mesh.borders(3,cid) :
				i1 = len(pts)
				face_cent = centroid(mesh,pos,2,fid)
				pts += (face_cent,)
				up_vector = face_cent - cell_cent
				
				for eid in mesh.borders(2,fid) :
					i2,i3 = (trans[pid] for pid in mesh.borders(1,eid) )
					N = (pts[i2] - pts[i1]) ^ (pts[i3] - pts[i1])
					if N * up_vector < 0 :
						i2,i3 = i3,i2
					
					if normal_inside :
						i2,i3 = i3,i2
					
					triangles.append( (i1,i2,i3) )
		else :
			raise UserWarning("triangulation method '%s' unrecognized" % method)
		
		return TriangleSet(pts,triangles)


