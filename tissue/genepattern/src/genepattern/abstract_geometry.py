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
This module defines abstract geometries
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from units import change_unit

def working_unit (value, unit, info) :
	try :
		return change_unit(value,unit,info.spatial_unit)
	except AttributeError :
		return change_unit(value,unit,"m")

class AbsGeometry (object) :
	"""
	definition of geometry using text identifiers
	"""
	def __init__ (self) :
		pass
	
	def _resolution (self, info, already_resolved) :
		"""
		resolution method
		must subclass this one
		"""
		return self
	
	def resolution (self, info, already_resolved={}) :
		"""
		return the same object with real descriptor
		instead of anchors names
		"""
		try :
			return already_resolved[self]
		except KeyError :
			reso = self._resolution(info,already_resolved)
			already_resolved[self] = reso
			return reso
	##############################################
	#
	#		arithmetic
	#
	##############################################
	def __add__ (self, zone) :
		"""
		union of two zones
		"""
		return AbsBinaryOperation(self,zone,'+')
	
	def __or__ (self, zone) :
		"""
		union of two zones
		"""
		return AbsBinaryOperation(self,zone,'|')
	
	def __sub__ (self, zone) :
		"""
		difference of two zones
		"""
		return AbsBinaryOperation(self,zone,'-')
	
	def __and__ (self, zone) :
		"""
		intersection between two zones
		"""
		return AbsBinaryOperation(self,zone,'&')
	
	def __xor__ (self, zone) :
		"""
		exclusion of two zones
		"""
		return AbsBinaryOperation(self,zone,'^')

class AbsUnaryOperation (AbsGeometry) :
	"""
	defines a unary operation on an abstract geometry
	"""
	def __init__ (self, pattern, operator) :
		AbsGeometry.__init__(self)
		self.pattern = pattern
		self.operator = operator
	
	def _resolution (self, info, already_resolved) :
		pattern = self.pattern.resolution(info,already_resolved)
		return AbsUnaryOperation(pattern,self.operator)

class AbsBinaryOperation (AbsGeometry) :
	"""
	defines a binary operation on two abstract geometries
	"""
	def __init__ (self, pattern1, pattern2, operator) :
		AbsGeometry.__init__(self)
		self.pattern1 = pattern1
		self.pattern2 = pattern2
		self.operator = operator
	
	def _resolution (self, info, already_resolved) :
		pattern1 = self.pattern1.resolution(info,already_resolved)
		pattern2 = self.pattern2.resolution(info,already_resolved)
		return AbsBinaryOperation(pattern1,pattern2,self.operator)

########################################
#
#	pattern object interface
#
########################################
class AbsUnknown (AbsGeometry) :
	"""
	a clean way to specify that you don't know the pattern
	"""

class AbsFixed (AbsGeometry) :
	"""
	a fixed pattern that is already projected
	"""
	def __init__ (self, cells) :
		AbsGeometry.__init__(self)
		self.cells = cells

class AbsAll (AbsGeometry) :
	"""
	a simple alias
	"""

class AbsEmpty (AbsGeometry) :
	"""
	a simple alias
	"""

class AbsSphere (AbsGeometry) :
	"""
	a simple sphere
	"""
	def __init__ (self, center, radius) :
		AbsGeometry.__init__(self)
		self.center=center
		self.radius=radius
	
	def _resolution (self, info, already_resolved) :
		if type(self.center) == str :
			center = info[self.center]
		else :
			center = self.center
		if type(self.radius) == str :
			radius = info[self.radius]
		else :
			radius = self.radius
		if radius[1] == "cell" :
			return AbsTopoSphere(center,radius[0])
		else :
			return AbsGeomSphere(center,working_unit(radius[0],radius[1],info))

class AbsGeomSphere (AbsSphere) :
	"""
	a simple geometrical sphere
	"""

class AbsTopoSphere (AbsSphere) :
	"""
	a simple topological sphere
	"""

class AbsHalfSpace (AbsGeometry) :
	"""
	half space
	"""
	def __init__ (self, point, normal) :
		AbsGeometry.__init__(self)
		self.point=point
		self.normal=normal
	
	def _resolution (self, info, already_resolved) :
		if type(self.point) == str :
			point = info[self.point]
		else :
			point = self.point
		if type(self.normal) == str :
			normal = info[self.normal]
		else :
			normal = self.normal
		return AbsHalfSpace(point,normal)

class AbsCone (AbsGeometry) :
	"""
	a simple cone
	"""
	def __init__ (self, point, axis, angle) :
		AbsGeometry.__init__(self)
		self.point = point
		self.axis = axis
		self.angle = angle
	
	def _resolution (self, info, already_resolved) :
		if type(self.point) == str :
			point = info[self.point]
		else :
			point = self.point
		if type(self.axis) == str :
			axis = info[self.axis]
		else :
			axis = self.axis
		if type(self.angle) == str :
			angle = info[self.angle]
		else :
			angle = self.angle
		return AbsCone(point,axis,angle)

class AbsCylinder (AbsGeometry) :
	"""
	a simple cylinder
	"""
	def __init__ (self, point, axis, radius) :
		AbsGeometry.__init__(self)
		self.point = point
		self.axis = axis
		self.radius = radius
	
	def _resolution (self, info, already_resolved) :
		if type(self.point) == str :
			point = info[self.point]
		else :
			point = self.point
		if type(self.axis) == str :
			axis = info[self.axis]
		else :
			axis = self.axis
		if type(self.radius) == str :
			radius = info[self.radius]
		else :
			radius = self.radius
		if radius[1] == "cell" :
			return AbsTopoCylinder(point,axis,radius[0])
		else :
			return AbsGeomCylinder(point,axis,working_unit(radius[0],radius[1],info))

class AbsGeomCylinder (AbsCylinder) :
	"""
	a simple geometrical Cylinder
	"""

class AbsTopoCylinder (AbsCylinder) :
	"""
	a simple topological Cylinder
	"""
########################################
#
#	operation
#
########################################
class Border (AbsUnaryOperation) :
	"""
	compute the 1 cell wide layer
	around a geometry
	"""
	def __init__ (self, pattern) :
		AbsUnaryOperation.__init__(self,pattern,"border")

class Shrink (AbsUnaryOperation) :
	"""
	compute the 1 cell wide layer
	around a geometry
	"""
	def __init__ (self, pattern) :
		AbsUnaryOperation.__init__(self,pattern,"shrink")

class Expand (AbsUnaryOperation) :
	"""
	compute the 1 cell wide layer
	around a geometry
	"""
	def __init__ (self, pattern) :
		AbsUnaryOperation.__init__(self,pattern,"expand")

class Adaxial (AbsUnaryOperation) :
	"""
	compute the adaxial subdivision of a pattern
	according to an axis
	"""
	def __init__ (self, point, pattern) :
		AbsUnaryOperation.__init__(self,pattern,"adaxial")
		self.point = point
	
	def _resolution (self, info, already_resolved) :
		pattern = self.pattern.resolution(info,already_resolved)
		if type(self.point) == str :
			point = info[self.point]
		else :
			point = self.point
		return Adaxial(point,pattern)

