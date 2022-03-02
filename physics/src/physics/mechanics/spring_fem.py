# -*- python -*-
# -*- coding: latin-1 -*-
#
#       MassSpring : physics package
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

__doc__="""
This module provide an interface for deformation of spring systems
"""

__license__= "Cecill-C"
__revision__=" $Id: spring_fem.py 7882 2010-02-08 18:36:38Z cokelaer $ "

from numpy import array,zeros
from spring import Spring

##############################################################
#
#	tensor functions
#
##############################################################
def triangle_frame (pt1, pt2, pt3) :
	"""Compute the local frame of a triangle.
	
	Origine will be pt1
	local Ox will be pt2 - pt1 (normalized)
	local 0y is in the plane of the triangle
	local Oz is normal to the plane of the triangle
	return O,(lOx,lOy,lOz)
	"""
	er = pt2 - pt1
	er.normalize()
	et = er ^ (pt3 - pt1)
	et.normalize()
	es = et ^ er
	return pt1,(er,es,et)

def change_frame (tensor, Ox, Oy) :
	"""Change reference frame of a 2x2 tensor
	
	Ox and Oy are the coordinates of the old frame
	axes in the new frame
	"""
	#rotation matrix
	R = zeros( (2,2) )
	R[0,0] = Ox[0]
	R[0,1] = Oy[0]
	R[1,0] = Ox[1]
	R[1,1] = Oy[1]
	#create new tensor
	ret = zeros( (2,2) )
	
	#fill coefficients
	for i in (0,1) :
		for j in (0,1) :
			ret[i,j] = sum(
							sum(tensor[k,l] * R[i,k] * R[j,l]
								for l in (0,1)
							)
							for k in (0,1)
						)
	
	#return
	return ret

def tensor_product (T1, T2) :
	"""Compute dot product between two tensors.
	
	T1: tensor 2x2x2x2
	T2: tensor 2x2
	return a 2x2 tensot
	"""
	S = zeros( (2,2) )
	for i in (0,1) :
		for j in (0,1) :
			S[i,j] = sum(sum(T1[i,j,k,l] * T2[k,l] for l in (0,1) ) for k in (0,1))
	
	return S

def kron (i, j) :
	"""Classical Kronecker function.
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
	"""tensor of order 4 of material properties.
	
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

#TODO
def axis_material2D (axis, E1, E2, nu) :
	"""Tensor of order 4 of material porperties.
	
	material properties are characterized by E1
	along axis
	and E2 in a direction perpendicular to axis
	axis: a normalized 2D vector
	"""
	#create tensor of order 4
	mat = zeros( (2,2,2,2) )
	
	#fill coefficients
	mat[0,0,0,0] = E1
	mat[1,1,1,1] = E2
	
	#rotate tensor
	R = zeros( (2,2) )
	R[0,0] = axis[0]
	R[0,1] = -axis[1]
	R[1,0] = axis[1]
	R[1,1] = axis[0]
	#create new tensor
	Rmat = zeros( (2,2,2,2) )
	
	#fill coefficients
	for i in (0,1) :
		for j in (0,1) :
			for k in (0,1) :
				for l in (0,1) :
					Rmat[i,j,k,l] = sum(
										sum(
											sum(
												sum(mat[a,b,c,d] * R[i,a] * R[j,b] * R[k,c] * R[l,d]
													for d in (0,1)
												)
												for c in (0,1)
											)
											for b in (0,1)
										)
										for a in (0,1)
									)
	
	#return
	return Rmat

##############################################################
#
#	springs equivalent to FEM
#	formulation of continuous mechanics
#
##############################################################
class TriangleMembrane3D (Spring) :
	"""Triangle finite element.
	
	no bending tork in this formulation
	"""
	def __init__ (self, pids, mat, ref_coords, thickness) :
		"""Defines a triangle in 3D by three point ids.
		
		mat is a 2x2x2x2 tensor of material properties
		ref_coords refers to the position of points
		in the reference configuration in 2D (r,s)
		hence, only (r2,r3,s3) are given
		r1,s1,s2 are assumed equal to 0
		"""
		self._big_displacements = 1. #tells wether or not to take into account
									 #big displacements (1 take account, 0 don't)
		self._pids = pids
		self._material =mat
		self._ref_coords = ref_coords
		self._thickness = thickness
		#
		self.compute_local_derivatives()
	
	def compute_local_derivatives (self) :
		"""Compute dNdr0,dNdr1 for each point.
		
		store it as local attributes
		"""
		r1,r2,s2 = self._ref_coords
		self.dN = array(
				[(- 1. / r1, (r2 - r1) / (r1 * s2) ),
				 (  1. / r1,      - r2 / (r1 * s2) ),
				 (  0.     ,        1. / s2)]
				 )
	
	def surface (self) :
		"""Compute surface of the triangle in ref configuration.
		"""
		r1,r2,s2 = self._ref_coords
		return r1 * s2 / 2.
	
	def displacement (self, pos, local_frame = None) :
		"""compute displacement in reference frame.
		
		compute actual local frame if not given
		"""
		pt0,pt1,pt2 = (pos[pid] for pid in self._pids)
		#compute local actual frame
		if local_frame is None :
			local_frame = triangle_frame(pt0,pt1,pt2)
		O,(er,es,et) = local_frame
		
		#compute displacement of points
		r1,r2,s2 = self._ref_coords
		U = array(
			[(0.,0.),
			 ((pt1 - O) * er - r1,0.),
			 ((pt2 - O) * er - r2,(pt2 - O) * es - s2)]
			 )
		
		#return
		return U
	
	def gradU (self, U) :
		"""Compute gradient of the displacement.
		"""
		#compute gradient of U
		dN = self.dN
		dU = zeros( (2,2) )
		for i in (0,1) :
			for j in (0,1) :
				dU[i,j] = sum( U[n,i] * dN[n,j] for n in (0,1,2) )
		
		#return
		return dU
	
	def _strain (self, dU) :
		"""Compute strain in the local reference frame.
		
		return [(Er0r0,Er0r1),(Er1r0,Er1r1)]
		"""
		bd = self._big_displacements
		#compute strain
		E = zeros( (2,2) )
		for i in (0,1) :
			for j in (0,1) :
				E[i,j] = 0.5 * (dU[j,i] + dU[i,j] + bd * sum( dU[k,i] * dU[k,j] for k in (0,1) ) )
		
		#return
		return E
	
	def strain (self, pos) :
		"""compute strain in the local reference frame.
		
		compute gradient of displacement if not given
		return [(Er0r0,Er0r1),(Er1r0,Er1r1)]
		"""
		U = self.displacement(pos)
		dU = self.gradU(U)
		return self._strain(dU)
	
	def _strain_derivative (self, dU) :
		"""Compute derivative of strain according to displacements.
		
		return a 3x2x2x2 tensor
		"""
		bd = self._big_displacements
		#initialise
		dE = zeros( (3,2,2,2) )
		
		#fill coefficients
		dN = self.dN
		for n in (0,1,2) :
			for m in (0,1) :
				for i in (0,1) :
					for j in (0,1) :
						dE[n,m,i,j] = 0.5 * (
								  dN[n,i] * (kron(m,j) + bd * dU[m,j])
								+ dN[n,j] * (kron(m,i) + bd * dU[m,i]) )
		
		#return
		return dE
	
	def _stress (self, E) :
		"""Compute stress in the local reference frame.
		
		return [(Sr0r0,Sr0r1),(Sr1r0,Sr1r1)]
		"""
		return tensor_product(self._material,E)
	
	def stress (self, pos) :
		"""Compute stress in the local reference frame.
		
		return [(Sr0r0,Sr0r1),(Sr1r0,Sr1r1)]
		"""
		E = self.strain(pos)
		return self._stress(E)
	
	def _stress_derivative (self, dE) :
		"""compute derivative of stress according to displacements.
		
		return a 3x2x2x2 tensor
		"""
		#initialise
		dS = zeros( (3,2,2,2) )
		
		#fill coefficients
		mat = self._material
		for n in (0,1,2) :
			for m in (0,1) :
				for i in (0,1) :
					for j in (0,1) :
						dS[n,m,i,j] = sum(sum(mat[i,j,k,l] * dE[n,m,k,l] for l in (0,1) ) for k in (0,1))
		
		#return
		return dS
	
	def energy (self, pos) :
		"""Compute energy stored in the membrane.
		"""
		#strain / stress
		E = self.strain(pos)
		S = self._stress(E)
		
		#volume for the integration
		V = self.surface() * self._thickness
		
		#compute energy
		W = 0.
		for i in (0,1) :
			for j in (0,1) :
				W += E[i,j] + S[i,j]
		W *= V
		
		#return
		return W
	
	def assign_forces (self, forces, pos) :
		"""Compute local forces and put them into forces.
		
		modify forces in place
		"""
		#local actual frame
		pt0,pt1,pt2 = (pos[pid] for pid in self._pids)
		O,(er,es,et) = triangle_frame(pt0,pt1,pt2)
		
		#displacement
		U = self.displacement(pos, (O,(er,es,et)) )
		dU = self.gradU(U)
		
		#strain / stress
		E = self._strain(dU)
		S = self._stress(E)
		
		#strain / stress derivatives
		dE = self._strain_derivative(dU)
		dS = self._stress_derivative(dE)
		
		#volume for the integration
		V = self.surface() * self._thickness
		
		#compute local forces
		dW = zeros( (3,2) )
		for n in (0,1,2) :
			for m in (0,1) :
				dW[n,m] = 0.5 * V * (
							sum(
								sum( 
									(dS[n,m,i,j] * E[i,j] + S[i,j] * dE[n,m,i,j])
									for j in (0,1)
								)
								for i in (0,1)
							) )
		
		
		#assign global forces
		for n,pid in enumerate(self._pids) :
			forces[pid] -= er * dW[n,0] + es * dW[n,1]

