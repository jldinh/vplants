# -*- python -*-
#
#       wusmodel: repressor model
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#                       Yassin Refahi <yassin.refahi@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
"""
This module develops the organization of the WUS expression zone according the 
repressor model proposed by Jonsson et al.
"""

from numpy import array,zeros,sqrt,concatenate
from scipy.integrate import ode
from vplants.plantgl.math import norm
from openalea.tissueshape import centroid,face_surface_3D,\
                                 cell_volume

class Parameters (object):
    """Parameters class
    
    this is just a data structure
    for parameters used in the
    repressor model
    """
    k_y2 = 0.1    #(unit) #meaning
    d_y2 = 0.002
    D_y2 = 0.052
    k_y1 = 0.1
    d_y1 = 0.008
    D_y1 = 0.009
    T_w = 10.0
    d_w = 0.1
    h_w = 2.0
    T_wy = -10.0

def G(x):
    return (1. + (x / sqrt( 1. + x * x ) ) ) / 2.

class RepressorModel (object) :
	"""Implementation of the Repressor model
	proposed by Jonsson et al.
	"""
	
	def __init__ (self, mesh, pos, params, L1, STEM, dt_hint = 0.1) :
		"""Constructor
		
		:Parameters:
		 - `mesh` (:class:`openalea.container.Topomesh`)
		 - `pos` (dict of (pid|Vector) ) - geometrical
		         position of points in space
		 - `params` (`Parameters`) - custom parameters
		         used in the model
		 - `L1` (iter of cid) - a list of cells in L1
		 - `STEM` (iter of cid) - a list of cells in STEM
		 - `dt_hint` (float) - time step in 's' used to
		                      perform the computation
		"""
		self._params = params
		self._dt_hint = dt_hint
		
		#initialise custom representation
		#of the tissue to accelerate computations
		
		#flatten cells
		trans = {}
		cell_inds = []
		for cid in mesh.wisps(3) :
			trans[cid] = len(cell_inds)
			cell_inds.append(cid)
		
		self._cell_inds = cell_inds
		
		#cell volume
		self.V = array([cell_volume(mesh,pos,cid) for cid in cell_inds])
		
		#wall diffusivity
		self.WD = []
		for wid in mesh.wisps(2) :
			if mesh.nb_regions(2,wid) == 2 :
				cid1,cid2 = mesh.regions(2,wid)
				l = norm(centroid(mesh,pos,3,cid2) \
				       - centroid(mesh,pos,3,cid1) )
				S = face_surface_3D(mesh,pos,wid)
				self.WD.append( (trans[cid1],
				                 trans[cid2],
				                 S / l) )
		
		#creation parameters
		self.alphaY1 = zeros( (len(cell_inds),) )
		for cid in L1 :
			self.alphaY1[trans[cid] ] = params.k_y1
		
		self.alphaY2 = zeros( (len(cell_inds),) )
		for cid in STEM :
			self.alphaY2[trans[cid] ] = params.k_y2
		
	
	def react (self, Y1, Y2, W, dt) :
		"""Modify substance quantities
		
		Perform the modification in place.
		
		:Return: None
		"""
		nb = len(self._cell_inds)
		#create custom representation
		#of Y1, Y2, W
		Xini = zeros( (3,nb) )
		for ind,cid in enumerate(self._cell_inds) :
			Xini[0,ind] = Y1[cid]
			Xini[1,ind] = Y2[cid]
			Xini[2,ind] = W[cid]
		
		Xini = Xini.flatten()
		
		#create diff function
		def xdot (t, X) :
			X = X.reshape( (3,nb) )
			
			#compute diffusion
			DY1 = zeros( (nb,) )
			DY2 = zeros( (nb,) )
			for cid1,cid2,Dcoeff in self.WD :
				flux = Dcoeff * (X[0,cid1] - X[0,cid2])
				DY1[cid1] -= flux
				DY1[cid2] += flux
				
				flux = Dcoeff * (X[1,cid1] - X[1,cid2])
				DY2[cid1] -= flux
				DY2[cid2] += flux
			
			#compute derivative
			p = self._params
			dY1 = self.alphaY1 \
			      + p.D_y1 * DY1 / self.V \
			      - p.d_y1 * X[0,:]
			dY2 = self.alphaY2 \
			      + p.D_y2 * DY2 / self.V \
			      - p.d_y2 * X[1,:]
			dW = 1. / p.T_w * G(p.h_w + p.T_wy * (X[0,:] + X[1,:]) ) \
			     - p.d_w * X[2,:]
			
			#return
			return concatenate( (dY1,dY2,dW) )
		
		#compute evolution of concentrations
		dt_hint = self._dt_hint
		r = ode(xdot)
		r.set_initial_value(Xini,0.)
		
		while r.successful() and r.t < dt:
			r.integrate(r.t + dt_hint)
		
		Xend = r.y.reshape( (3,nb) )
		
		#fill back in Y1,Y2 and W
		for ind,cid in enumerate(self._cell_inds) :
			Y1[cid] = Xend[0,ind]
			Y2[cid] = Xend[1,ind]
			W[cid] = Xend[2,ind]


