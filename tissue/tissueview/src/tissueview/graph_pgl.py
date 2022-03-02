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
This module defines functions to convert graph elements
into geometrical pgl objects
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from numpy import ndarray
from vplants.plantgl.math import Vector2,Vector3,norm,Matrix3
from vplants.plantgl.scenegraph import (Sphere,Polyline,Cylinder,
                                        Translated,Oriented,Scaled)

def vertex_geom (graph, pos, vid, scaling = 1) :
	"""PGL geometry of a vertex
	
	This function will create a deformed sphere centered on the position
	of the vertex
	
	:Parameters:
	 - `graph` (Graph)
	 - `pos` (dict of vid|array) - position of vertices
	 - `vid` (vid) - id of vertex to draw
	 - `scaling` (float or array of float) - scaling factor:
	                - if float, scaling will be the radius of the sphere
	                - if array of float, scaling will represent a matrix of
	                  deformation of the sphere
	
	:Returns Type: pgl.Transformed(pgl.Sphere)
	"""
	#shape
	sph = Sphere(1.)
	
	#position
	vpos = pos[vid]
	
	#transformation
	if isinstance(scaling,ndarray) : #main axes
		v1 = Vector3(*scaling[:,0].tolist() )
		l1 = v1.normalize()
		v2 = Vector3(*scaling[:,1].tolist() )
		l2 = v2.normalize()
		v3 = Vector3(*scaling[:,2].tolist() )
		l3 = v3.normalize()
		geom = Oriented(v1,v2,Scaled( (l1,l2,l3),sph) )
		
	else :#radius
		geom = Scaled( (scaling,scaling,scaling),sph)
	
	return Translated(vpos,geom)

def edge_geom (graph, pos, eid, radius = 0) :
	"""PGL geometry of an edge
	
	Construct a cylinder oriented oriented according to the edge
	
	:Parameters:
	 - `graph` (:class:`Graph`)
	 - `pos` (dict of vid|array) - position of vertices in space
	 - `eid` (eid) - id of the edge to draw
	 - `radius` (float) - radius of the cylinder. If radius is 0, a polyline
	                      will be drawn, else a cylinder with the given radius
	
	:Returns Type: pgl.Transformed(gl.Cylinder)
	"""
	vpos1 = pos[graph.source(eid)]
	vpos2 = pos[graph.target(eid)]
	if radius == 0 :
		geom = Polyline([vpos1,vpos2])
	else :
		v1 = vpos2 - vpos1
		l = norm(v1)
		v1 /= l
		
		v2 = Vector3.OZ ^ v1
		if (norm(v2) / l) < 1e-4 :
			v2 = Vector3.OX ^ v1
		
		v2 /= norm(v2)
		
		cyl = Scaled( (radius,radius,l),Cylinder(1.) )
		geom = Translated(vpos1,Oriented(v2,v1 ^ v2,cyl) )
	
	return geom







