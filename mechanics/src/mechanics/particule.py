# -*- python -*-
# -*- coding: latin-1 -*-
#
#       particule : mechanics package
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
This module provide a base structure for particules
"""

__license__ = "Cecill-C"
__revision__ = " $Id: division.py 116 2007-02-07 17:44:59Z tyvokka $ "

from numpy import array,zeros

class Particule (object) :
	"""Base class for a particule
	
	A particule associate a position with a mass
	"""
	dim = None
	
	def __init__ (self, weight = 1., pos = None) :
		"""Constructor
		
		:Parameters:
		 - `weight` (float) - weight of the particule in kg
		 - `pos` (float,float,(float) ) - position of the particule
		    if None, the particule will be positioned on the origin
		"""
		self._weight = weight
		
		if pos is None :
			self._pos = zeros(self.dim)
		else :
			self._pos = array(pos)
		
		self._velocity = zeros(self.dim)
	
	def copy (self) :
		"""Create a copy of this particule
		"""
		ret = type(self)(self._weight,self._pos)
		ret._velocity = array(self._velocity)
		
		return ret
	
	####################################################
	#
	#	accessors
	#
	####################################################
	def weight (self) :
		"""Weight of the particule
		
		:Returns Type: float
		"""
		return self._weight
	
	def position (self) :
		"""Current position of the particule
		
		:Returns Type: array
		"""
		return self._pos
	
	def set_position (self, pos) :
		"""Set current position of the particule
		
		:Parameters:
		 - `pos` (array)
		"""
		self._pos = pos
	
	def velocity (self) :
		"""Current velocity of the particule
		
		:Returns Type: array
		"""
		return self._velocity
	
	def set_velocity (self, velocity) :
		"""Set current velocity of the particule
		
		:Parameters:
		 - `velocity` (array)
		"""
		self._velocity = velocity

class Particule2D (Particule) :
	dim = 2

class Particule3D (Particule) :
	dim = 3

def totup (particules) :
	"""convert particules into dict of tuples
	
	:Parameters:
	 - `particules` (dict of Particule)
	
	:Returns: weights,positions,velocities
	
	:Returns Type: dict of float,dict of tuple,dict of tuple
	"""
	wei = dict( (pid,p.weight() ) \
	             for pid,p in particules.iteritems() )
	pos = dict( (pid,tuple(p.position() ) ) \
	             for pid,p in particules.iteritems() )
	vel = dict( (pid,tuple(p.velocity() ) ) \
	             for pid,p in particules.iteritems() )
	
	return wei,pos,vel

def topart (weights, positions, velocities) :
	"""Convert dict into particules
	
	
	.. warning:: will create a particule for each pid in weights only
	
	:Parameters:
	 - `weights` (dict of float) - weight of particules
	 - `positions` (dict of tuple) - current position of particules
	 - `velocities` (dict of tuple) - current velocity of particules
	
	:Returns Type: dict of Particules
	"""
	test = len(positions[iter(positions).next()])
	if test == 2 :
		ptype = Particule2D
	else :
		ptype = Particule3D
	
	parts = dict( (pid,ptype(w) ) for pid,w in weights.iteritems() )
	
	for pid,p in parts.iteritems() :
		p.set_position(array(positions[pid]) )
		p.set_velocity(array(velocities[pid]) )
	
	return parts




















