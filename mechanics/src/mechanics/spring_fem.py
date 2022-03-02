# -*- python -*-
# -*- coding: latin-1 -*-
#
#       MassSpring : mechanics package
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
This module provide an interface for deformation of spring systems
"""

__license__= "Cecill-C"
__revision__=" $Id: spring_fem.py 9357 2010-07-31 08:06:03Z chopard $ "

from numpy import array,zeros,dot,tensordot,cross,log,arctan
from particule import Particule3D
from spring import Spring
from frame import triangle_frame,mean_frame,change_frame_tensor2
from openalea.container import triangulate_polygon

##############################################################
#
#	tensor functions
#
##############################################################
def kron (i, j) :
	"""Classical Kronecker function
	
	:Parameters:
	 - `i` (int) - left operand
	 - `j` (int) - right operand
	
	:Returns: 1 if i == j, 0 otherwise
	
	:Returns Type: int
	"""
	if i == j :
		return 1.
	else :
		return 0.
##############################################################
#
#	materials
#
##############################################################
def isotropic_material2D (E, nu) :
	"""Create a tensor of material properties
	
	:Parameters:
	 - `E` (float) - Young's modulus in unit
	 - `nu` (float) - Poisson ratio (no unit)
	
	:Returns Type: 2x2x2x2 array
	"""
	#create tensor of order 4
	mat = zeros( (2,2,2,2) )
	
	#fill coefficients
	alpha = E / (1 - nu * nu)
	mat[0,0,0,0] = alpha
	mat[0,0,1,1] = alpha * nu
	
	mat[0,1,0,1] = alpha * (1 - nu) / 2.
	mat[0,1,1,0] = alpha * (1 - nu) / 2.
	
	mat[1,0,0,1] = alpha * (1 - nu) / 2.
	mat[1,0,1,0] = alpha * (1 - nu) / 2.
	
	mat[1,1,0,0] = alpha * nu
	mat[1,1,1,1] = alpha
	
	#return
	return mat

def axis_material2D (axis, E1, E2, nu1, G12) :
	"""Create tensor of material properties
	
	:Parameters:
	 - `axis` (Vector) - axis of symmetry of the material (e.g. fiber axis).
	                     Must be normalized.
	 - `E1` (float) - Young's modulus along the given axis
	 - `E2` (float) - Young's modulus perpendicular to the given axis
	 - `nu1` (float) - Poisson's ratio such that:
	     nu1 / E1 = nu2 / E2
	 - `G12` (float) - shear modulus
	
	:Returns Type:  2x2x2x2 array
	"""
	nu2 = nu1 * E2 / E1
	
	#create tensor of order 4
	mat = zeros( (2,2,2,2) )
	
	#fill coefficients
	a = E1 / (1 - nu1 * nu2)
	mat[0,0,0,0] = a
	mat[0,0,1,1] = a * nu2
	
	a = E2 / (1 - nu1 * nu2)
	mat[1,1,0,0] = a * nu1
	mat[1,1,1,1] = a
	
	mat[0,1,0,1] = G12
	mat[0,1,1,0] = G12
	
	mat[1,0,0,1] = G12
	mat[1,0,1,0] = G12
	
	#rotate tensor
	fr = triangle_frame( (0.,0.,0.),
	                     (axis[0],axis[1],0),
	                     (-axis[1],axis[0],0) )
	
	return fr.global_tensor2(mat)

##############################################################
#
#	membrane spring equivalent to FEM
#	formulation of continuous mechanics
#	on an elastic membrane
#
##############################################################
class Membrane3D (Spring) :
	"""Finite element formulation of a piece fo membrane
	
	no bending tork in this formulation
	"""
	def __init__ (self, pids, mat, ref_shape, thickness) :
		"""Constructor
		
		Create the elastic polygonal element.
		
		.. warning:: the given polygon must be convex
		
		:Parameters:
		 - `pids` (list of pid) - defines a closed polygon
		 - `mat` (2x2x2x2 array) - material properties of the membrane
		                expressed in the reference configuration frame
		 - `ref_shape` (3x2 array of float) - coordinates of points
		       in the reference configuration in 2D. First column correspond
		       to the position of pids[0].
		 - `thickness` (float) - thickness of the membrane
		"""
		self._pids = pids
		self.set_ref_shape(ref_shape)
		self.set_material(mat)
		self._thickness = thickness
	
	##########################################
	#
	#		serialization
	#
	##########################################
	def __getstate__ (self) :
		return (self._pids,
		        self._material,
		        self._ref_shape,
		        self._thickness)
	
	def __setstate__ (self, state) :
		self._pids,mat,refshp,self._thickness = state
		self.set_ref_shape(refshp)
		self.set_material(mat)
	
	##########################################
	#
	#		accessors
	#
	##########################################
	def extremities (self) :
		"""Iterator on corners of the membrane
		
		:Returns Type: iter of pid
		"""
		return iter(self._pids)
	
	def material (self) :
		"""Retrieves the material associated with the spring
		
		:Returns Type: 2x2x2x2 array
		"""
		return self._material
	
	def set_material (self, mat) :
		"""Set the material of the spring
		
		:Parameters:
		 - `mat` (2x2x2x2 array) - material properties of the membrane
		                expressed in the reference configuration frame
		"""
		self._material = mat
	
	def ref_shape (self) :
		"""Retrieves the reference shape of this spring
		
		:Return: position of corners in the reference frame in 2D
		
		:Returns Type: 3x2 array of float
		"""
		return self._ref_shape
	
	def set_ref_shape (self, shape) :
		"""Set the reference (or rest) shape
		
		:Parameters:
		 - `shape` (3x2 array of float) - position of corners in the reference
		                                 frame
		"""
		self._ref_shape = shape
	
	def thickness (self) :
		"""Retrieves the thickness of the membrane
		
		:Returns Type: float
		"""
		return self._thickness
	
	def set_thickness (self, thickness) :
		"""Set the thickness of the membrane
		
		:Parameters:
		 - `thickness` (float) - thickness of the membrane
		"""
		self._thickness = thickness
	
	##########################################
	#
	#		geometry accessors
	#
	##########################################
	def local_frame (self, particules) :
		"""Compute local frame associated with this spring
		
		:Parameters:
		 - `particules` (dict of (pid|Particule) )
		
		:Returns Type: :class:`Frame`
		"""
		raise NotImplementedError
	
	def surface (self) :
		"""Compute surface of the membrane in ref configuration
		
		:Returns Type: float
		"""
		raise NotImplementedError
	
	##########################################
	#
	#		mechanics computations
	#
	##########################################
	def strain (self, state, t = None) :
		"""Compute actual strain of the spring
		
		:Parameters:
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Returns: [(Er0r0,Er0r1),(Er1r0,Er1r1)]
		
		:Returns Type: 2x2 array
		"""
		raise NotImplementedError
	
	def stress (self, state, t = None) :
		"""Compute actual stress of the spring
		
		:Parameters:
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Returns: [(Sr0r0,Sr0r1),(Sr1r0,Sr1r1)]
		
		:Returns Type: 2x2 array
		"""
		raise NotImplementedError
	
	def energy (self, state, t = None) :
		"""Compute the elastic energy stored in the spring
		
		:Parameters:
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Returns: strain * stress * volume
		
		:Returns Type: float
		"""
		raise NotImplementedError

class TriangleMembrane3D (Membrane3D) :
	"""Triangle finite element of membrane
	
	no bending tork in this formulation
	"""
	##########################################
	#
	#		geometry accessors
	#
	##########################################
	def set_ref_shape (self, shape) :
		"""Set the reference (or rest) shape
		
		:Parameters:
		 - `shape` (3x2 array of float) - position of corners in the reference
		                                 frame
		"""
		Membrane3D.set_ref_shape(self,shape)
		
		#compute derivatives
		pt0,pt1,pt2 = zeros( (3,3) )
		pt0[:2],pt1[:2],pt2[:2] = self._ref_shape
		fr = triangle_frame(pt0,pt1,pt2)
		
		r1,s1,t1 = fr.local_point(pt1)
		r2,s2,t2 = fr.local_point(pt2)
		
		self._ref_coords = r1,r2,s2
		
		self.dN = array([(- 1. / r1, (r2 - r1) / (r1 * s2) ),
		                 (  1. / r1,      - r2 / (r1 * s2) ),
		                 (  0.     ,        1. / s2)])
	
	def set_material (self, mat) :
		"""Set the material of the spring
		
		:Parameters:
		 - `mat` (2x2x2x2 array) - material properties of the membrane
		                expressed in the reference configuration frame
		"""
		Membrane3D.set_material(self,mat)
		
#		#compute local material
#		pt0,pt1,pt2 = zeros( (3,3) )
#		pt0[:2],pt1[:2],pt2[:2] = self._ref_shape
#		fr = triangle_frame(pt0,pt1,pt2)
#		
#		self._local_mat = fr.local_tensor2(self._material)
		self._local_mat = self._material
	
	def local_frame (self, state) :
		"""Compute local frame associated with this spring
		
		.. seealso:: :func:`triangle_frame`
		
		:Parameters:
		 - `state` (array of float) - current position and velocity of points
		
		:Returns Type: :class:`Frame`
		"""
		pt0,pt1,pt2 = (state[0,pid,:] for pid in self._pids)
		return triangle_frame(pt0,pt1,pt2)
	
	def surface (self) :
		"""Compute surface of the triangle in ref configuration
		
		:Returns: r1 * s2 / 2.
		
		:Returns Type: float
		"""
		r1,r2,s2 = self._ref_coords
		return r1 * s2 / 2.
	
	##########################################
	#
	#		mechanics computations
	#
	##########################################
	def gradU (self, state, local_frame = None) :
		"""compute gradient of the displacement in reference frame
		
		compute actual local frame if not given.
		
		:Parameters:
		 - `state` (array of float) - current position and velocity of points
		 - `local_frame` (:class:`Frame`) - the frame associated
		         with the actual position of the triangle
		"""
		pt0,pt1,pt2 = (state[0,pid,:] for pid in self._pids)
		
		#compute local actual frame
		if local_frame is None :
			local_frame = triangle_frame(pt0,pt1,pt2)
		O = local_frame.origin()
		er = local_frame.axis(0)
		es = local_frame.axis(1)
		
		#compute displacement of points
		r1,r2,s2 = self._ref_coords
		U = array([(0.,0.),
		           (dot(pt1 - O,er) - r1,0.),
		           (dot(pt2 - O,er) - r2,dot(pt2 - O,es) - s2)])
		
		#return
		return dot(U.transpose(),self.dN)
	
	def _strain (self, dU) :
		"""Compute strain in the local reference frame
		
		Internal function
		
		return [(Er0r0,Er0r1),(Er1r0,Er1r1)]
		"""
		return (dU + dU.transpose() + dot(dU.transpose(),dU) ) * 0.5
	
	def strain (self, state, t = None) :
		"""Compute actual strain of the spring
		
		:Parameters:
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Returns: [(Er0r0,Er0r1),(Er1r0,Er1r1)]
		
		:Returns Type: 2x2 array
		"""
		return self._strain(self.gradU(state) )
	
	def _strain_derivative (self, dU) :
		"""Compute derivative of strain according to displacements
		
		internal function
		
		return a 3x2x2x2 array
		"""
		#initialise
		dE = zeros( (3,2,2,2) )
		
		#fill coefficients
		dN = self.dN
		for n in (0,1,2) :
			for m in (0,1) :
				for i in (0,1) :
					for j in (0,1) :
						dE[n,m,i,j] = (m == i) * dN[n,j] \
						            + (m == j) * dN[n,i] \
						            + dN[n,i] * dU[m,j] \
						            + dU[m,i] * dN[n,j]
		
		#return
		return dE / 2.
	
	def _stress (self, E) :
		"""Compute stress in the local reference frame
		
		internal function
		
		return [(Sr0r0,Sr0r1),(Sr1r0,Sr1r1)]
		"""
		return tensordot(self._local_mat,E,2)
	
	def stress (self, state, t = None) :
		"""Compute actual stress of the spring
		
		:Parameters:
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Returns: [(Sr0r0,Sr0r1),(Sr1r0,Sr1r1)]
		
		:Returns Type: 2x2 array
		"""
		return self._stress(self.strain(state) )
	
	def _stress_derivative (self, dE) :
		"""compute derivative of stress according to displacements
		
		internal function
		
		return a 3x2x2x2 tensor
		"""
		return tensordot(dE,self._local_mat,[(2,3),(2,3)])
		#initialise
		dS = zeros( (3,2,2,2) )
		
		#fill coefficients
		mat = self._local_mat
		for n in (0,1,2) :
			for m in (0,1) :
				for i in (0,1) :
					for j in (0,1) :
						dS[n,m,i,j] = sum(sum(mat[i,j,k,l] * dE[n,m,k,l] for l in (0,1) ) for k in (0,1))
		
		#return
		return dS
	
	def energy (self, state, t = None) :
		"""Compute the elastic energy stored in the spring
		
		:Parameters:
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Returns: strain * stress * volume
		
		:Returns Type: float
		"""
		#strain / stress
		E = self.strain(state)
		S = self._stress(E)
		
		#volume for the integration
		V = self.surface() * self._thickness
		
		#compute energy
		W = 0.5 * V * tensordot(S,E)
		
		#return
		return W
	
	def assign_forces (self, forces, state, t = None) :
		"""Compute local forces and insert them into forces
		
		Compute local forces generated by this actor
		according to current state.
		
		:Parameters:
		 - `forces` (array of float) - an array that store force vectors
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Return: None, modify forces in place
		"""
		#local actual frame
		pt0,pt1,pt2 = (state[0,pid,:] for pid in self._pids)
		local_frame = triangle_frame(pt0,pt1,pt2)
		
		#displacement
		dU = self.gradU(state,local_frame)
		
		#strain / stress
		E = self._strain(dU)
		S = self._stress(E)
		
		#strain / stress derivatives
		dE = self._strain_derivative(dU)
		dS = self._stress_derivative(dE)
		
		#volume for the integration
		V = self.surface() * self._thickness
		
		#compute local forces
		dW = (tensordot(dS,E,2) + tensordot(S,dE,[(0,1),(2,3)]) ) * (V / 2.)
#		dW = zeros( (3,2) )
#		for n in (0,1,2) :
#			for m in (0,1) :
#				dW[n,m] = 0.5 * V * (
#							sum(
#								sum( 
#									(dS[n,m,i,j] * E[i,j] \
#									+ S[i,j] * dE[n,m,i,j])
#									for j in (0,1)
#								)
#								for i in (0,1)
#							) )
		
		
		#assign global forces
		er = local_frame.axis(0)
		es = local_frame.axis(1)
		
		for n,pid in enumerate(self._pids) :
			forces[pid] -= er * dW[n,0] + es * dW[n,1]
	
	def assign_jacobian (self, jacobian, state, t = None) :
		"""Compute jacobian contribution of this actor
		
		:Parameters:
		 - `jacobian` (array of float) - an array that store jacobian
		 - `state` (array of float) - current position and velocity of points
		 - `t` (float) - current time
		
		:Return: None, modify jacobian in place
		"""
		raise NotImplementedError


class PolygonMembrane3D (Membrane3D) :
	"""Polygonal finite element of membrane
	
	no bending tork in this formulation
	
	will use a set of TriangleMembrane3D
	"""
	def update (self) :
		mat = self._material
		ref_shape = self._ref_shape
		thickness = self._thickness
		
		self._sub_triangles = []
		for pids in triangulate_polygon(self._pids,ref_shape) :
			tr = TriangleMembrane3D(pids,
			                        mat,
			                        dict( (pid,ref_shape[pid]) for pid in pids),
			                        thickness)
			self._sub_triangles.append(tr)
	
	##########################################
	#
	#		geometry accessors
	#
	##########################################
	def local_frame (self, particules) :
		"""Compute local frame associated with this spring
		
		.. seealso:: :func:`triangle_frame`
		
		:Parameters:
		 - `particules` (dict of (pid|Particule) )
		
		:Returns Type: :class:`Frame`
		"""
		return mean_frame([sp.local_frame(particules) for sp in self._sub_triangles])
	
	def surface (self) :
		"""Compute surface of the membrane in ref configuration
		
		:Returns Type: float
		"""
		return sum(sp.surface() for sp in self._sub_triangles)
	
	##########################################
	#
	#		mechanics computations
	#
	##########################################
	def strain (self, particules) :
		"""Compute strain in the local reference frame
		
		:Parameters:
		 - `particules` (dict of (pid|Particule) )
		
		:Returns: [(Er0r0,Er0r1),(Er1r0,Er1r1)]
		
		:Returns Type: 2x2 array
		"""
		fr = self.local_frame(particules)
		st = zeros( (2,2) )
		for sp in self._sub_triangles :
			st += change_frame_tensor2(sp.strain(particules) * sp.surface(),
			                           sp.local_frame(particules),
			                           fr)
		
		return st / self.surface()
	
	def stress (self, particules) :
		"""Compute stress in the local reference frame
		
		:Parameters:
		 - `particules` (dict of (pid|Particule) )
		
		:Returns: [(Sr0r0,Sr0r1),(Sr1r0,Sr1r1)]
		
		:Returns Type: 2x2 array
		"""
		fr = self.local_frame(particules)
		st = zeros( (2,2) )
		for sp in self._sub_triangles :
			st += change_frame_tensor2(sp.stress(particules) * sp.surface(),
			                           sp.local_frame(particules),
			                           fr)
		
		return st / self.surface()
	
	def energy (self, particules) :
		"""Compute energy stored in the membrane
		
		:Parameters:
		 - `particules` (dict of (pid|Particule) )
		
		:Returns: strain * stress * volume
		
		:Returns Type: float
		"""
		return sum(sp.energy(particules) for sp in self._sub_triangles)
	
	def assign_forces (self, forces, particules) :
		for sp in self._sub_triangles :
			sp.assign_forces(forces,particules)

