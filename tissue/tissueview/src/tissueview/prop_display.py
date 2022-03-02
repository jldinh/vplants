# -*- python -*-
#
#       tissueview: function used to display tissue properties
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
This module defines functions to display a property on a topomesh
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from numpy.linalg import eig
from vplants.plantgl.math import Vector2,Vector3
from vplants.plantgl.scenegraph import Scene,Shape,Material,\
              Polyline
from vplants.plantgl.ext.color import red,green,blue,black
from openalea.container import Graph,Topomesh
from openalea.tissueshape import centroid,gcentroid
from mesh_display import draw_mesh, \
                         draw_mesh2D

axes_mat = [Material(col.i3tuple() ) for col in (red,green,blue,black)]

def _mat_map_func (prop, cmap, default_mat) :
	def mat_map (wid) :
		try :
			dat = prop[wid]
			if dat is None :
				return None
			
			col = cmap(dat)
			if col is None :
				return None
			else :
				mat =  Material(col.i3tuple() )
				mat.transparency = col.transparency / 255.
#				mat.diffuse = 0.5
#				mat.specular = (0,0,0)#tuple(int(v / 3.) for v in col.i3tuple() )
#				mat.emission = (0,0,0)#tuple(int(v / 3.) for v in col.i3tuple() )
				return mat
		except KeyError :
			return default_mat
	
	return mat_map

def draw_scalar_prop (mesh, pos, deg, prop, shrink, cmap,
                      default_mat = None, method = 'topo') :
	"""Draw elements of the mesh for which the
	property is defined using the specified color
	map
	"""
	mat_map = _mat_map_func(prop,cmap,default_mat)
	
	return draw_mesh(mesh,pos,deg,mat_map,shrink,False,method)

def draw_scalar_prop2D (mesh, pos, deg, prop, shrink, cmap, offset,
                        default_mat = None, method = 'topo') :
	"""Draw elements of the mesh for which the
	property is defined using the specified color
	map
	"""
	mat_map = _mat_map_func(prop,cmap,default_mat)
	
	return draw_mesh2D(mesh,pos,deg,mat_map,shrink,offset,method)

def draw_vectorial_prop (mesh, pos, deg, prop, scaling, material) :
	"""Draw a vectorial property
	
	draw a polyline from the centroid of the element in the direction
	of the property vector
	
	prop: a dict of (wid,vector)
	"""
	#material
	if isinstance(material,Material) :
		def cmap (*args) :
			return material
	else :
		cmap = material
	
	sc = Scene()
	for wid in mesh.wisps(deg) :
		mat = cmap(wid)
		if mat is not None :
			try :
				vec = prop[wid]
				
				cent = Vector3(centroid(mesh,pos,deg,wid) )
				geom = Polyline([cent,cent + Vector3(vec) * scaling])
				shp = Shape(geom,mat)
				shp.id = wid
				sc.add(shp)
			except KeyError :
				pass
	
	return sc

def draw_tensorial_prop (topo, pos, elm_type, prop, scaling) :
	"""Draw a tensorial property represented by it's main directions.
	
	:Parameters:
	 - `topo` (Graph or Mesh)
	 - `pos` (dict of id|array) - position of elements
	 - `elm_type` (int or str) :
	       - for graph either "vertex" or "edge" to iterate on
	       - for mesh, specify the degree of elements to iterate on
	 - `prop` (dict of id|array)
	 - `scaling` (float) - multiplicating factor
	
	:Returns Type: pgl.Scene
	"""
	sc = Scene()
	
	if isinstance(topo,Graph) :
		cfunc = gcentroid
		if elm_type == "vertex" :
			elms = topo.vertices()
		elif elm_type == "edge" :
			elms = topo.edges()
		else :
			msg = "undefined type %s, must be either 'vertex' or 'edge'" % elm_type
			raise UserWarning(msg)
	elif isinstance(topo,Topomesh) :
		cfunc = centroid
		elms = topo.wisps(elm_type)
	else :
		raise UserWarning("undefined topo: %s" % type(topo) )
	
	for eid in elms :
		try :
			tens = prop[eid]
			
			cent = Vector3(cfunc(topo,pos,elm_type,eid) )
			w,v = eig(tens)
			l = [(wi,tuple(float(val) for val in v[:,i] * wi) ) \
			         for i,wi in enumerate(w)]
			l.sort(reverse = True)
			
			for i,(wi,vec) in enumerate(l) :
				geom = Polyline([cent - Vector3(vec) * scaling,
				                 cent + Vector3(vec) * scaling])
				shp = Shape(geom,axes_mat[i])
				shp.id = eid
				sc.add(shp)
		except KeyError :
			pass
	
	return sc

