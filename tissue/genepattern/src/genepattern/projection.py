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
This module defines algorithms to project genepatterns on a structure
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from math import sin,cos
from openalea.plantgl.math import Vector2,Vector3,norm
from openalea.plantgl.algo import Octree,Ray
from openalea.plantgl.scenegraph import Scene,Shape,Material,TriangleSet
from openalea.container import expand,border,shrink,external_border
from openalea.tissueshape import centroid,face_normal
from openalea.tissueview import cell_geom
from abstract_geometry import AbsAll,AbsEmpty,AbsFixed,AbsUnknown,\
							  AbsSphere,AbsGeomSphere,AbsTopoSphere,\
							  AbsHalfSpace,AbsCone,\
							  AbsGeomCylinder,AbsTopoCylinder,\
							  AbsUnaryOperation,AbsBinaryOperation

class PatternProjector (object) :
	"""
	a base class for all algo aiming at projecting a pattern
	on a mockup
	"""
	def __init__ (self) :
		"""
		initialization of the projector with a given mockup
		and parameters to perform the projection
		"""
	
	def _project (self, pattern, already_projected) :
		"""
		method that actually project the pattern
		must be subclassed
		"""
		if isinstance(pattern,AbsFixed) :
			return pattern.cells
		elif isinstance(pattern,AbsEmpty) :
			return set()
		elif isinstance(pattern,AbsBinaryOperation) :
			act1 = self.project(pattern.pattern1)
			act2 = self.project(pattern.pattern2)
			op = pattern.operator
			if op == "+" :
				return act1 | act2
			elif op == "-" :
				return act1 - act2
			elif op == "&" :
				return act1 & act2
			elif op == "|" :
				return act1 | act2
		else :
			return None
		
	def project (self, pattern, already_projected={}) :
		"""
		project the given pattern on the stored mockup
		pattern: an instance of AbsGeometry
		return : a set of of id of elements filled by the pattern
		"""
		try :
			return already_projected[pattern]
		except KeyError :
			if isinstance(pattern,AbsUnknown) :
				raise NotImplementedError("pattern defined as unknown")
			proj = self._project(pattern,already_projected)
			already_projected[pattern] = proj
			return proj

def nearest_cell (mesh, pos, point, scale) :
	dist = [(norm(centroid(mesh,pos,scale,cid)-point),cid) for cid in mesh.wisps(scale)]
	dist.sort()
	return dist[0][1]

def adaxial (mesh, pos, dim, point, pattern) :
	"""
	compute the adaxial subdivision of the pattern
	"""
	#compute border
	border_faces = set(external_border(mesh,3,pattern))
	border_cells = set()
	for fid in border_faces :
		border_cells.update(mesh.regions(2,fid))
	border_cells &= pattern
	#compute normal to decide repartition of cells on the surface
	adaxial_cells = set()
	abaxial_cells = set()
	for cid in border_cells :
		normal_list = [face_normal(mesh,pos,fid,cid) for fid in (set(mesh.borders(3,cid)) & border_faces)]
		bary = centroid(mesh,pos,3,cid)
		n = sum(normal_list,Vector3())
		if (bary - point) * n < 0 :
			adaxial_cells.add(cid)
		else :
			abaxial_cells.add(cid)
	#fill internal cells
	#by expanding zones
	while len(adaxial_cells) + len(abaxial_cells) < len(pattern) :
		abaxial_cells = (expand(mesh,3,abaxial_cells) & pattern) - adaxial_cells
		adaxial_cells = (expand(mesh,3,adaxial_cells) & pattern) - abaxial_cells
	#return
	return adaxial_cells
 
default_mat = Material()

class MeshProjector (PatternProjector) :
	"""
	project a pattern on a flat mesh in 2D space
	"""
	def __init__ (self, mesh, pos, dim = 2, method = "centroid") :
		"""
		mesh: a container.TopoMesh
		pos: a dict of {pid:Vector) position of mesh points
		dim: the dimension of space either 2 or 3
		method : the method used to say that a cell belong to a pattern
		"""
		PatternProjector.__init__(self)
		if dim == 2 :
			self.Vector = Vector2
		elif dim == 3 :
			self.Vector = Vector3
		else :
			raise NotImplementedError("unable to use space of dimension %d" % dim)
		self.mesh = mesh
		self.pos = pos
		self.dim = dim
		self.method = method
	
	def cells (self) :
		return self.mesh.wisps(self.dim)
	
	def _project (self, pattern, already_projected={}) :
		proj = PatternProjector._project(self,pattern,already_projected)
		if proj is not None :
			return proj
		else :
			##########################################
			#
			#		topology
			#
			##########################################
			if isinstance(pattern,AbsAll) :
				return set(self.mesh.wisps(self.dim))
			elif isinstance(pattern,AbsTopoSphere) :
				mesh = self.mesh
				if type(pattern.center) == int :
					mcid = pattern.center
				else :
					mcid = nearest_cell(mesh,self.pos,self.Vector(*pattern.center),self.dim)
				inside_cells = set([mcid])
				for i in xrange(pattern.radius - 1) :
					inside_cells = expand(mesh,self.dim,inside_cells)
				return inside_cells
			elif isinstance(pattern,AbsTopoCylinder) :
				mesh = self.mesh
				pos = self.pos
				point = self.Vector(*pattern.point)
				axis = self.Vector(*pattern.axis)
				cell_axis = []
				if self.dim == 2 :
					for cid in self.cells() :
						point_side = set( (pos[pid] - point) ^ axis > 0 for pid in mesh.borders(self.dim,cid,self.dim) )
						if len(point_side) == 2 :
							cell_axis.append(cid)
				else :
					ray1 = Ray(point,axis)
					ray2 = Ray(point,-axis)
					for cid in self.cells() :
						geom = cell_surface_geom(mesh,pos,cid)
						sc = Scene()
						sc.add(Shape(geom,default_mat))
						octree = Octree(sc,4,3)
						if octree.intersection(ray1) or octree.intersection(ray2) :
							cell_axis.append(cid)
				inside_cells = set(cell_axis)
				for i in xrange(pattern.radius - 1) :
					inside_cells = expand(mesh,self.dim,inside_cells)
				return inside_cells
			elif isinstance(pattern,AbsUnaryOperation) :
				mesh = self.mesh
				proj = self.project(pattern.pattern)
				op = pattern.operator
				if op == "border" :
					return border(mesh,self.dim,proj)
				elif op == "shrink" :
					return shrink(mesh,self.dim,proj)
				elif op == "expand" :
					return expand(mesh,self.dim,proj)
				elif op == "adaxial" :
					return adaxial(mesh,self.pos,self.dim,pattern.point,proj)
				else :
					return None
			##########################################
			#
			#		geometry
			#
			##########################################
			elif isinstance(pattern,AbsGeomSphere) :
				mesh = self.mesh
				cent = self.Vector(*pattern.center)
				inside_cells = set(cid for cid in mesh.wisps(self.dim) if norm(centroid(mesh,pos,self.dim,cid)-cent) <= pattern.radius)
				return inside_cells
			elif isinstance(pattern,AbsHalfSpace) :
				mesh = self.mesh
				pos = self.pos
				point = self.Vector(*pattern.point)
				normal = self.Vector(*pattern.normal)
				proj = set(cid for cid in mesh.wisps(self.dim) if ((centroid(mesh,pos,self.dim,cid) - point) * normal) >= 0)
				return proj
			elif isinstance(pattern,AbsGeomCylinder) :
				mesh = self.mesh
				pos = self.pos
				point = self.Vector(*pattern.point)
				axis = self.Vector(*pattern.axis)
				axis.normalize()
				def axis_dist (vec) :
					tmp = vec - point
					return norm( tmp - axis*(tmp*axis) )
				proj = set(cid for cid in mesh.wisps(self.dim) if axis_dist(centroid(mesh,pos,self.dim,cid)) <= pattern.radius)
				return proj
			else :
				return None

