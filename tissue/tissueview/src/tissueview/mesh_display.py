# -*- python -*-
#
#       tissueview: function used to display tissue geometry
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
This module defines functions to display a topomesh
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from vplants.plantgl.math import Vector2,Vector3
from vplants.plantgl.scenegraph import Scene,Shape,Material,\
              Sphere,Box,\
              Translated,Scaled
from openalea.tissueshape import centroid
from mesh_pgl import edge_geom2D,edge_geom3D, \
                     face_geom2D,face_geom3D, \
                     cell_geom

def draw_mesh (mesh, pos, deg, material, shrink,
               normal_inversed = False, method = 'topo', ref_point = None) :
	"""Draw elements of a mesh
	
	:Parameters:
	 - `mesh` (:class:`Topomesh`)
	 - `pos` (dict of (pid,Vector) ) - position of points in space
	 - `deg` (int) -  degree of elements to display
	 - `material` :
	    - (func) - a colormap for each element
	    - (:class:`Material`) - unique color for each element
	 - `shrink` :
	    - (int) - percentage of shrinking between 0 and 100
	    - (float) in the case of deg == 0, radius of the sphere used
	 - `normal_inversed` (bool) - if True, normals point 
	      in the opposite direction:
	      - downside for faces
	      - inside for cells
	 - `method` (str) - method used to triangulate the face:
	       - 'topo', use topological triangulation good for convexe faces
	       - 'star', use star triangulation
	
	:Returns Type: :class:`Scene`
	"""
	#material
	if isinstance(material,Material) :
		def cmap (*args) :
			return material
	else :
		cmap = material
	
	#dimension
	dim = len(pos.itervalues().next() )
	if dim == 2 :
		pos = dict( (pid,Vector2(*(float(v) for v in vec) ) ) \
		             for pid,vec in pos.iteritems() )
	else :
		pos = dict( (pid,Vector3(*(float(v) for v in vec) ) ) \
		             for pid,vec in pos.iteritems() )
	
	#ref point
	if ref_point is None :
		if dim == 2 :
			ref_point = Vector2.ORIGIN
		else :
			ref_point = Vector3.ORIGIN
	else :
		if dim == 2 :
			ref_point = Vector2(*ref_point)
		else :
			ref_point = Vector3(*ref_point)
	
	#geometry
	sc = Scene()
	if deg == 0 :
		pt_repr = Sphere(shrink)
	
	for wid in mesh.wisps(deg) :
		try :
			#material
			mat = cmap(wid)
			if mat is not None :
				#geometry
				if deg == 0 :
					if dim == 2 :
						geom = Translated(Vector3(pos[wid]),pt_repr)
					else :
						geom = Translated(pos[wid],pt_repr)
				elif deg == 1 :
					if dim == 2 :
						geom = edge_geom2D(mesh,pos,wid)
					else :
						geom = edge_geom3D(mesh,pos,wid)
				elif deg == 2 :
					if dim == 2 :
						geom = face_geom2D(mesh,pos,wid,normal_inversed,method)
					else :
						up = centroid(mesh,pos,deg,wid) - ref_point
						geom = face_geom3D(mesh,pos,wid,up,method)
				elif deg == 3 :
					geom = cell_geom(mesh,pos,wid,normal_inversed,method)
				else :
					raise NotImplementedError("unable to display elements of degree %d with this function" % deg)
				
				if deg > 0 and shrink > 0 :
					bary = centroid(mesh,pos,deg,wid)
					if dim == 2 :
						bary = Vector3(*(float(v) for v in bary) )
					scale = 1. - shrink / 100.
					geom = Translated(bary,
					         Scaled( (scale,scale,scale),
					           Translated(- bary,
					             geom
					           )
					         )
					       )
				
				#shape
				shp = Shape(geom,mat)
				shp.id = wid
				sc.add(shp)
		except KeyError :
			pass
	
	return sc

def draw_mesh2D (mesh, pos, deg, material, shrink, offset, method = 'topo') :
	"""Draw elements of a mesh.
	
	:Parameters:
	 - `mesh` (:class:`Topomesh`)
	 - `pos` (dict of (pid,Vector) ) - position of points in space
	 - `deg` (int) -  degree of elements to display
	 - `material` :
	    - (func) - a colormap for each element
	    - (:class:`Material`) - unique color for each element
	 - `shrink` :
	    - (int) - percentage of shrinking between 0 and 100
	    - (float) in the case of deg == 0, radius of the sphere used
	 - `offset` (int) - a depth offset
	 - `method` (str) - method used to triangulate the face:
	       - 'topo', use topological triangulation good for convexe faces
	       - 'star', use star triangulation
	
	return: a PGL scene
	"""
	pos = dict( (pid,Vector2(*(float(v) for v in vec) ) ) \
	             for pid,vec in pos.iteritems() )
	
	#material
	if isinstance(material,Material) :
		def cmap (*args) :
			return material
	else :
		cmap = material
	
	#offset
	offset_vec = Vector3(0,0,offset)
	
	#geometry
	sc = Scene()
	if deg == 0 :
		pt_repr = Sphere(shrink)
	
	for wid in mesh.wisps(deg) :
		try :
			#material
			mat = cmap(wid)
			if mat is not None :
				#geometry
				if deg == 0 :
					geom = Translated(Vector3(pos[wid]),pt_repr)
				elif deg == 1 :
					geom = edge_geom2D(mesh,pos,wid)
				elif deg == 2 :
					geom = face_geom2D(mesh,pos,wid,method = method)
				else :
					raise NotImplementedError("unable to display elements of degree %d with this function" % deg)
				
				if deg > 0 and shrink > 0 :
					bary = centroid(mesh,pos,deg,wid)
					bary = Vector3(*(float(v) for v in bary) )
					scale = 1. - shrink / 100.
					geom = Translated(bary,
					         Scaled( (scale,scale,scale),
					           Translated(- bary,
					             geom
				               )
						     )
					       )
				
				#offset
				if offset != 0 :
					geom = Translated(offset_vec,geom)
				
				#shape
				shp = Shape(geom,mat)
				shp.id = wid
				sc.add(shp)
		except KeyError :
			pass
	
	#return
	return sc

def draw_mesh1D (mesh, pos, width, material, shrink) :
	"""Draw elements of a mesh.
	
	mesh: an instance of topomesh
	pos: a dict of (pid,float)
	width: thickness of the line
	material: either a single material or a colormap
	shrink: int (0-100) percentage of shrinking
	
	return: a PGL scene
	"""
	#material
	if isinstance(material,Material) :
		def cmap (*args) :
			return material
	else :
		cmap = material
	
	#geometry
	sc = Scene()
	cell_geom = Box( (0.5,width / 2.,width / 2.) )
	for wid in mesh.wisps(1) :
		try :
			#material
			mat = cmap(wid)
			if mat is not None :
				#geometry
				pid1,pid2 = mesh.borders(1,wid)
				length = abs(pos[pid2] - pos[pid1])
				center = (pos[pid1] + pos[pid2]) / 2.
				geom = Scaled( (length,1,1),cell_geom )
				
				if shrink > 0 :
					scale = 1. - shrink / 100.
					geom = Scaled( (scale,scale,scale),geom)
				
				geom = Translated( (center,0,0),geom)
				
				#shape
				shp = Shape(geom,mat)
				shp.id = wid
				sc.add(shp)
		except KeyError :
			pass
	
	#return
	return sc


