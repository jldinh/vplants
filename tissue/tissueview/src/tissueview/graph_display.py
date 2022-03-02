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
This module defines functions to display a graph
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from vplants.plantgl.math import Vector3
from vplants.plantgl.scenegraph import Scene,Shape,Material
from graph_pgl import vertex_geom,edge_geom

def draw_graph (graph, pos, elm_type, scaling, material) :
	"""Draw elements of a graph
	
	:Parameters:
	 - `graph` (:class:`Graph`)
	 - `pos` (dict of vid,array) - position of vertices in space
	 - `elm_type` ("vertex" or "edge") - type of elements to display
	 - `scaling` :
	    - (func) - a shape for each element
	    - (float) - the same shape for each elements
	 - `material` :
	    - (func) - a colormap for each element
	    - (:class:`Material`) - unique color for each element
	
	:Returns Type: :class:`Scene`
	"""
	#material
	if isinstance(material,Material) :
		def cmap (*args) :
			return material
	else :
		cmap = material
	
	#positions
	pos = dict( (pid,Vector3(*(float(v) for v in vec) ) ) \
	             for pid,vec in pos.iteritems() )
	
	#scaling
	if callable(scaling) :
		scal = scaling
	else :
		def scal (*args) :
			return scaling
	
	#geometry
	sc = Scene()
	
	if elm_type == "vertex" :
		for vid in graph.vertices() :
			try :
				#material
				mat = cmap(vid)
				sca = scal(vid)
				if mat is not None :
					#geometry
					geom = vertex_geom(graph,pos,vid,sca)
					
					#shape
					shp = Shape(geom,mat)
					shp.id = vid
					sc.add(shp)
			except KeyError :
				pass
	elif elm_type == "edge" :
		for eid in graph.edges() :
			try :
				#material
				mat = cmap(eid)
				sca = scal(eid)
				if mat is not None :
					#geometry
					geom = edge_geom(graph,pos,eid,sca)
					
					#shape
					shp = Shape(geom,mat)
					shp.id = eid
					sc.add(shp)
			except KeyError :
				pass
	else :
		msg = "elm_type must be either 'vertex' or 'edge' not %s" % elm_typ
		raise ValueError(msg)
	
	return sc


