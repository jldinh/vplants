from random import random
from physics.chemistry import Diffusion,Transport,Reaction
from celltissue.algo import TissueTopoMesh,TissueGraph,CellPropertyAdapter,PointPropertyAdapter,VertexPropertyAdapter
from celltissue.data import DensityProperty,UniformDensityProperty,EdgeUniformProperty,TPropertyMap


def prograde_auxin (root,dt) :
	root.progradation.react(VertexPropertyAdapter(root.auxin,root.wallgraph),dt)


def diffuse_auxin (root,dt) :
	root.diffusion.react(CellPropertyAdapter(root.auxin,root.topomesh),dt)


def transport_auxin (root,dt) :
        root.transport.react(VertexPropertyAdapter(root.auxin,root.wallgraph),dt)


def cap_auxin (root) :
    for kid in root.auxin.keys():
        if root.auxin[kid]>1. :
           root.auxin[kid]=1.


class Zeta (object) :   #augment pump production when delta [AIA]s-[AIA]t augment
	def __init__ (self, creation, morphograd, alpha, zeta) :
		self._creation=creation
		self._morphograd=morphograd
		self._alpha=alpha
		self._zeta=zeta

	def delta (self, eid) :
      	    delta = (self._morphograd[eid][0]-self._morphograd[eid][1])
            return delta

	def __getitem__ (self, eid) :
		return self._creation[eid]*(1+max(0.,self._zeta*self.delta(eid)))

	def iteritems (self) :
		for eid,self._alpha in self._creation.iteritems() :
			yield eid,self[eid]


class Yota (object) :   #augment pump degradation when [AIA] target augment
	def __init__ (self, decay, morphograd, beta, yota) :
		self._decay=decay
		self._morphograd=morphograd
		self._beta=beta
		self._yota=yota

	def target (self, eid) :
      	    target = self._morphograd[eid][1]
            return target

	def __getitem__ (self, eid) :
		return self._decay[eid]*(1+max(0.,self._yota*self.target(eid)))

	def iteritems (self) :
		for eid,self._beta in self._decay.iteritems() :
			yield eid,self[eid]


def fix_eP (root) :
    for eid in root.eP.keys():
    	if (root.fixed_eP[eid]>0):
    	   root.eP[eid] = root.fixed_eP[eid]


def orient_flux(root, side) : #only for tissue 2 whole root
    if (side==1):
       for eid in [(44,43),(17,18),(16,20),(21,22),(85,86),(45,44),(15,17),(14,16),(13,21),(84,85),(48,45),(46,15),(1,14),(12,13),(83,84),(49,48),(0,46),(2,1),(11,12),(82,83),(51,47),(3,0),(5,2),(10,11),(81,82)]:
           root.fixed_eP[eid] = root.alpha/root.beta
       for eid in [(47,51),(0,3),(2,5),(11,10),(82,81),(50,47),(49,47),(46,0),(1,2),(12,11),(83,82),(48,49),(45,48),(15,46),(14,1),(13,12),(84,83),(44,45),(17,15),(16,14),(21,13),(85,84),(43,44),(18,17),(20,16),(22,21),(86,85)]:
           root.fixed_eP[eid] = 0.000001
    else :
       for eid in [(47,51),(0,3),(2,5),(11,10),(82,81),(50,47),(49,47),(46,0),(1,2),(12,11),(83,82),(48,49),(45,48),(15,46),(14,1),(13,12),(84,83),(44,45),(17,15),(16,14),(21,13),(85,84),(43,44),(18,17),(20,16),(22,21),(86,85)]:
           root.fixed_eP[eid] = root.alpha/root.beta
       for eid in [(44,43),(17,18),(16,20),(21,22),(85,86),(45,44),(15,17),(14,16),(13,21),(84,85),(48,45),(46,15),(1,14),(12,13),(83,84),(49,48),(0,46),(2,1),(11,12),(82,83),(51,47),(3,0),(5,2),(10,11),(81,82)]:
           root.fixed_eP[eid] = 0.000001