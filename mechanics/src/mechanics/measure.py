# -*- python -*-
# -*- coding: latin-1 -*-
#
#       measure : mechanics package
#
#       Copyright or © or Copr. 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       VPlants WebSite : https://gforge.inria.fr/projects/vplants/
#

__doc__ = """
This module provide functions to measure deformations
"""

__license__ = "Cecill-C"
__revision__ = " $Id: division.py 116 2007-02-07 17:44:59Z tyvokka $ "

from numpy import array,zeros,dot,transpose,real,add,divide,outer
from scipy.linalg import lstsq,logm

def _centroid (ps) :
	return reduce(add,ps) / len(ps)

def inertia (point_set) :
	"""Compute the inertia matrix of a shape
	
	The shape is defined by a set of points located inside the shape.
	
	.. note:: this function works in space of dimension n
	
	:Parameters:
	 - `point_set` (list of array) - a list of points in dimension n
	                                  contained inside a shape
	
	:Returns Type: nxn array
	"""
	#compute local points according to barycenter
	bary = _centroid(point_set)
	pts = [vec - bary for vec in point_set]
	
	#compute inertia
	I = divide(reduce(add,[outer(pt,pt) for pt in pts]),float(len(pts) ) )
	
	#return
	return I

def solid_transformation (ref_pts, cur_pts) :
	"""Compute the best solid transfo that match points
	from ref_pts into points in cur_pts.
	
	.. note:: this function works in space of dimension n
	
	:Parameters:
	 - `ref_pts` (list of array) - a list of points in the
	    reference configuration
	 - `cur_pts` (list of array) - a list of points in the
	    current configuration. Points are ordered such as
	    ref_pts[0] becomes cur_pts[0] and so forth.
	
	:Return: a tuple translation,deformation
	
	:Returns Type: array,nxn array
	"""
	#compute translation
	c_ref = _centroid(ref_pts)
	c_cur = _centroid(cur_pts)
	
	#find deformation
	a = array([tuple(vec - c_ref) for vec in ref_pts])
	b = array([tuple(vec - c_cur) for vec in cur_pts])
	
	res,resids,rank,s = lstsq(a,b)
	
	#return
	F = transpose(res)
	T = c_cur - dot(F,c_ref)
	return T,F

def measure_strain (ref_pts, cur_pts) :
	"""Compute the strain between the 2 point sets
	
	The computed strain reflects the deformation that transform 
	the reference shape described by ref_point_set into the
	shape described by actual_point_set.
	
	Use the average solid transformation between
	the 2 points sets to compute the strain.
	
	:Parameters:
	 - `ref_pts` (list of array) - a list of points in the
	    reference configuration
	 - `cur_pts` (list of array) - a list of points in the
	    current configuration. Points are ordered such that
	    ref_pts[0] becomes cur_pts[0] and so forth.
	
	:Return: log(S) where S is the deformation part of the solid transformation
	         that transform ref_pts into cur_pts
	
	:Returns Type: 2x2 array
	"""
	T,F = solid_transformation(ref_pts,cur_pts)
	
	return real(logm(dot(transpose(F),F) ) ) * 0.5




