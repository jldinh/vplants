# -*- python -*-
# -*- coding: latin-1 -*-
#
#       Geometry : celltissue package
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
This module provide an implementation of a mesh
"""

__license__= "Cecill-C"
__revision__=" $Id: graph.py 116 2007-02-07 17:44:59Z tyvokka $ "

from openalea.container.topomesh import TopoMesh
from interface.mesh import IMesh,IAdvancedMesh,IMutableMesh,IGlobalChangeMesh

class Mesh (TopoMesh,IMesh,IAdvancedMesh,IMutableMesh,IGlobalChangeMesh) :
	"""
	same than topomesh but associate a position
	with each point
	"""
	def __init__ (self) :
		TopoMesh.__init__(self)
		self._positions={}
	
	#####################################################
	#
	#		mesh position
	#
	#####################################################
	def position (self, pid) :
		return self._positions[pid]
	position.__doc__=IMesh.position.__doc__
	
	def positions (self) :
		return self._positions.iteritems()
	positions.__doc__=IMesh.positions.__doc__
	
	def __iter__ (self) :
		return iter(self._positions)
	
	def __len__ (self) :
		return len(self._positions)
	#####################################################
	#
	#		advanced mesh
	#
	#####################################################
	def centroid (self, pid_iter) :
		med=None
		for ind,pid in enumerate(pid_iter) :
			if med is None : med=self.position(pid)
			else : med=med+self.position(pid)
		return med/float(ind+1)
	centroid.__doc__=IAdvancedMesh.centroid.__doc__
	#####################################################
	#
	#		mutable mesh
	#
	#####################################################
	def set_position (self, pid, pos) :
		self._positions[pid]=pos
	set_position.__doc__=IMutableMesh.set_position.__doc__
	
	def add_point (self, pos, pid=None) :
		pid=TopoMesh.add_point(self,pid)
		self._positions[pid]=pos
		return pid
	add_point.__doc__=IMutableMesh.add_point.__doc__
	
	def remove_point (self, pid) :
		TopoMesh.remove_point(self,pid)
		del self._positions[pid]
	
	#####################################################
	#
	#		global change mesh
	#
	#####################################################
	def __iadd__ (self, vector) :
		for v in self._positions.itervalues() :
			v+=vector
		return self
	__iadd__.__doc__=IGlobalChangeMesh.__iadd__.__doc__
	
	def __isub__ (self, vector) :
		for v in self._positions.itervalues() :
			v-=vector
		return self
	__isub__.__doc__=IGlobalChangeMesh.__isub__.__doc__
	
	def __imul__ (self, val) :
		for v in self._positions.itervalues() :
			v*=val
		return self
	__imul__.__doc__=IGlobalChangeMesh.__imul__.__doc__
	
	def __idiv__ (self, val) :
		for v in self._positions.itervalues() :
			v/=val
		return self
	__idiv__.__doc__=IGlobalChangeMesh.__idiv__.__doc__
	#####################################################
	#
	#		refine
	#
	#####################################################
	def refine (self, fid, edge=None) :
		"""
		refine a face of the mesh by subdividing the
		given edge using Rivara algorithm
		if edge is None (usual case) subdivide longuest
		edge
		divide linked faces if necessary to maintain
		conformity of the mesh
		"""
		edge_length=[]
		Elong=edge_length[0][1]

