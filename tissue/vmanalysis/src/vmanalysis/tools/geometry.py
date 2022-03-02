# -*- python -*-
#
#       vmanalysis: tools to analyse tissues
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

__doc__ = """
This module defines a set of function linked to
geometrical aspects
"""

__license__ = "Cecill-C"
__revision__ = " $Id: $ "

def centroid (mesh, pos, deg, wid) :
	"""Compute centroid of a wisp
	
	.. seealso:: openalea.tissueshape.centroid
	  This function do not depend on PlantGL
	"""
	pts = [pos[pid] for pid in mesh.borders(deg,wid,deg)]
	if len(pts[0]) == 2 :
		pt = reduce(lambda p1,p2: (p1[0] + p2[0],p1[1] + p2[1]),pts)
		return (float(pt[0]) / len(pts),
		        float(pt[1]) / len(pts) )
	elif len(pts[0]) == 3 :
		pt = reduce(lambda p1,p2: (p1[0] + p2[0],p1[1] + p2[1],p1[2] + p2[2]),pts)
		return (float(pt[0]) / len(pts),
		        float(pt[1]) / len(pts),
		        float(pt[2]) / len(pts) )
	else :
		raise NotImplementedError("point in dimension %d" % len(pts[0]) )

def circum_center2D (pt1, pt2, pt3) :
	"""Position of the circumcenter of a triangle
	
	The given point correspond to the
	intersection point of the normals
	of the triangle.
	
	:Parameters:
	 - `pti` (Vector) - ith corner
	
	:Returns Type: Vector
	"""
	side1 = (pt2[0] - pt1[0],pt2[1] - pt1[1])
	side2 = (pt3[0] - pt1[0],pt3[1] - pt1[1])
	d = 2 * (side1[0] * side2[1] - side1[1] * side2[0])
	d1 = side1[0] * side1[0] + side1[1] * side1[1]
	d2 = side2[0] * side2[0] + side2[1] * side2[1]
	
	H = ( (d2 * side1[1] - d1 * side2[1]) / (-d),
	      (d1 * side2[0] - d2 * side1[0]) / (-d) )
	
	return (pt1[0] + H[0],pt1[1] + H[1])

def circum_center3D (pt1, pt2, pt3, pt4) :
	"""Position of the circumcenter of a tetraedron
	
	:Parameters:
	 - `pti` (Vector) - ith corner
	
	:Returns Type: Vector
	"""
	from numpy import array
	from numpy.linalg import solve
	
	N1 = sum(c * c for c in pt1)
	N2 = sum(c * c for c in pt2)
	N3 = sum(c * c for c in pt3)
	N4 = sum(c * c for c in pt4)
	
	A = array([[pt2[0] - pt1[0],pt2[1] - pt1[1],pt2[2] - pt1[2]],
	           [pt3[0] - pt1[0],pt3[1] - pt1[1],pt3[2] - pt1[2]],
	           [pt4[0] - pt1[0],pt4[1] - pt1[1],pt4[2] - pt1[2]] ])
	
	B = array([(N2 - N1) / 2.,
	           (N3 - N1) / 2.,
	           (N4 - N1) / 2.])
	
	O = solve(A,B)
	
	return tuple(O)

def flatness2D (pt1, pt2, pt3) :
	"""Compute minimum ratio height/width
	of this triangle.
	
	:Parameters:
	 - `pti` (Vector) - ith corner
	    of the triangle
	
	:Returns Type: float
	"""
	tr = (pt1,pt2,pt3)
	vals = []
	for i in xrange(3) :
		s1 = (tr[(i + 1) % 3][0] - tr[i][0],
		      tr[(i + 1) % 3][1] - tr[i][1])
		s2 = (tr[(i + 2) % 3][0] - tr[i][0],
		      tr[(i + 2) % 3][1] - tr[i][1])
		
		ratio = abs(s1[0] * s2[1] - s1[1] * s2[0]) / (s1[0] * s1[0] + s1[1] * s1[1])
		vals.append(ratio)
	
	return min(vals)

def flatness3D (pt1, pt2, pt3, pt4) :
	"""Compute minimum ratio height/surf
	of this tetraedron.
	
	:Parameters:
	 - `pti` (Vector) - ith corner
	    of the tetraedron
	
	:Returns Type: float
	"""
	from vplants.plantgl.math import Vector3
	tet = tuple(Vector3(*pt) for pt in (pt1,pt2,pt3,pt4) )
	vals = []
	for i in xrange(4) :
		s1 = tet[(i + 1) % 4] - tet[i]
		s2 = tet[(i + 2) % 4] - tet[i]
		s3 = tet[(i + 3) % 4] - tet[i]
		
		N = s1 ^ s2
		S = N.normalize()
		h = abs(N * s3)
		#ratio = h / S
		ratio = h
		vals.append(ratio)
	
	return min(vals)

def flatness3D (pt1, pt2, pt3, pt4) :
	"""Compute minimum ratio height/surf
	of this tetraedron.
	
	:Parameters:
	 - `pti` (Vector) - ith corner
	    of the tetraedron
	
	:Returns Type: float
	"""
	from triangulation import circum_center3D
	from vplants.plantgl.math import Vector3,norm
	
	H = circum_center3D(pt1,pt2,pt3,pt4)
	tet = tuple(Vector3(*pt) for pt in (pt1,pt2,pt3,pt4) )
	
	G = sum(tet,Vector3() ) / 4.
	
	vals = []
	for i in xrange(4) :
		s1 = tet[(i + 1) % 4] - tet[i]
		s2 = tet[(i + 2) % 4] - tet[i]
		s3 = tet[(i + 3) % 4] - tet[i]
		
		N = s1 ^ s2
		S = N.normalize()
		h = abs(N * s3)
		vals.append(h)
	
	return norm(G - H) / min(vals)

def curve_intersect (curve, segments) :
	"""Iterate on segments that intersect a curve
	
	The curve must be 2D.
	
	:Parameters:
	 - `curve` (:class:`vplants.plantgl.LineicModel`)
	 - `segments` (dict of (sid|(Vector,Vector) ) ) -
	   a map of segment id, segment extemities
	
	:Return: a list of ids of segments that intersect
	         the curve
	:Returns Type: iter of sid
	"""
	from vplants.plantgl.math import Vector2
	from vplants.plantgl.algo import Discretizer,segmentIntersect
	
	d = Discretizer()
	curve.apply(d)
	dcurve = [Vector2(vec[0],vec[1]) for vec in d.result]
	nb_segs = len(dcurve) - 1
	
	for sid,(seg1,seg2) in segments.iteritems() :
		if any(segmentIntersect(seg1,seg2,dcurve[i],dcurve[i + 1]) \
		       for i in xrange(nb_segs) ) :
			yield sid

def mesh_intersect (mesh, segments) :
	"""Iterate on segments that intersect a mesh
	
	The mesh might be 3D.
	
	:Parameters:
	 - `mesh` (:class:`vplants.plantgl.TriangleSet`)
	 - `segments` (dict of (sid|(Vector,Vector) ) ) -
	   a map of segment id, segment extemities
	
	:Return: a list of ids of segments that intersect
	         the mesh
	:Returns Type: iter of sid
	"""
	from vplants.plantgl.algo import segmentIntersect
	
	def intersect (seg1, seg2) :
		for tr in mesh.indexList :
			pt1,pt2,pt3 = (mesh.pointList[i] for i in tr)
			if segmentIntersect(seg1,seg2,pt1,pt2,pt3) :
				return True
		return False
	
	for sid,(seg1,seg2) in segments.iteritems() :
		if intersect(seg1,seg2) :
			yield sid

def _is_point_inside_given_dir (point, octree, heading, threshold=1e-4) :
	from vplants.plantgl.algo import Octree,Ray
	
	ray = Ray(point,heading)
	count = 0
	intercept = octree.intersection(ray)
	while intercept :# is not None :
		count += 1
		ray.origin = intercept + heading * threshold
		intercept = octree.intersection(ray)
	return count % 2 != 0

def _is_point_inside (point, octree) :
	from vplants.plantgl.math import Vector3
	test=[_is_point_inside_given_dir(point,octree,heading) \
	       for heading in (Vector3.OX,Vector3.OY,Vector3.OZ)]
	
	return test.count(True) > test.count(False)

def is_inside_mesh (mesh, points) :
	"""Iterate through pids inside a mesh
	
	:Parameters:
	 - `mesh` (:class:`vplants.plantgl.TriangleSet`)
	 - `points` (dict of (sid|Vector) ) -
	   a map of point id, point position
	
	:Return: a list of ids of points that lies
	         inside the mesh
	:Returns Type: iter of pid
	"""
	from vplants.plantgl.scenegraph import Scene,Shape,Material
	from vplants.plantgl.algo import Octree,Ray
	
	sc = Scene()
	sc.add(Shape(mesh,Material() ) )
	octree = Octree(sc,4)
	
	for pid,vec in points.iteritems() :
		if _is_point_inside(vec,octree) :
			yield pid


