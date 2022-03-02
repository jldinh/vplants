# -*- python -*-
# -*- coding: latin-1 -*-
#
#       Mesh : physics package
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
This module provide a point set concepts to express a mesh in space
"""

__license__= "Cecill-C"
__revision__=" $Id: mesh.py 7882 2010-02-08 18:36:38Z cokelaer $ "

class MeshError (Exception) :
	"""
	base class for all exceptions in a mesh
	"""

class InvalidFace (MeshError,KeyError) :
	"""
	exception raised when a wrong face id is provided
	"""

class InvalidEdge (MeshError,KeyError) :
	"""
	exception raised when a wrong edge id is provided
	"""

class InvalidPoint (MeshError,KeyError) :
	"""
	exception raised when a wrong point id is Provided
	"""

class IMesh2D (object) :
	"""
	interface for a mesh composed of face,edge,point
	"""
	def is_valid (self) :
		"""
		test wether the mesh fulfill all mesh properties
		"""
		raise NotImplementedError
	
	def has_face (self, fid) :
		"""
		return True if the face is in the mesh
		"""
		raise NotImplementedError
	
	def has_edge (self, eid) :
		"""
		return True if the edge is in the mesh
		"""
		raise NotImplementedError
	
	def has_point (self, pid) :
		"""
		return True if the point is in the mesh
		"""
		raise NotImplementedError

class IFaceListMesh (object) :
	"""
	mesh seen as a list of faces
	"""
	def faces (self, eid=None, pid=None) :
		"""
		iterator on all faces
		linked to an edge if eid is provided
		linked to a point if pid is provided
		"""
		raise NotImplementedError
	
	def nb_faces (self, eid=None, pid=None) :
		"""
		total number of faces
		linked to an edge if eid is provided
		linked to a point if pid is provided
		"""
		raise NotImplementedError

class IEdgeListMesh (object) :
	"""
	mesh seen as a list of edges
	"""
	def edges (self, fid=None, pid=None) :
		"""
		iterator on all edges
		linked to a face if fid is provided
		linked to a point if pid is provided
		"""
		raise NotImplementedError
	
	def nb_edges (self, fid=None, pid=None) :
		"""
		total number of edges
		linked to a face if eid is provided
		linked to a point if pid is provided
		"""
		raise NotImplementedError

class IPointListMesh (object) :
	"""
	mesh seen as a list of points
	"""
	def points (self, fid=None, eid=None) :
		"""
		iterator on all points
		linked to a face if fid is provided
		linked to an edge if eid is provided
		"""
		raise NotImplementedError
	
	def nb_points (self, eid=None, pid=None) :
		"""
		total number of points
		linked to a face if fid is provided
		linked to an edge if eid is provided
		"""
		raise NotImplementedError

class IPositionMesh (object) :
	"""
	interface for a mesh
	associate a position with each point of a topomesh
	"""
	def position (self, pid) :
		"""
		return position of a point
		:rtype: space vector
		"""
		raise NotImplementedError
	
	def __getitem__ (self, pid) :
		return self.position(pid)
	
	def positions (self) :
		"""
		iterator on all positions in the point set
		:rtype: iter of (pid,pos)
		"""
		raise NotImplementedError
	
	def iteritems (self) :
		return self.positions()
	

class IMutableMesh (object) :
	"""
	interface for function modifying mesh composition
	"""
	def add_face (self, fid=None) :
		"""
		add a new unconnected face
		return id used (=fid if provided)
		"""
		raise NotImplementedError
	
	def add_edge (self, eid=None) :
		"""
		add a new unconnected edge
		return id used (=eid if provided)
		"""
		raise NotImplementedError
	
	def add_point (self, pos, pid=None) :
		"""
		create a new pid for the point
		and position it to pos
		return this pid
		"""
		raise NotImplementedError
	
	def set_position (self, pid, pos) :
		"""
		affect position to a point
		"""
		raise NotImplementedError
	
	def __setitem__ (self, pid, pos) :
		try :
			self.add_point(pos,pid)
		except IndexError :
			self.set_position(pid,pos)
	
	def add_border (self, fid, eid) :
		"""
		connect a face to an edge
		"""
		raise NotImplementedError
	
	def add_corner (self, eid, pid) :
		"""
		connect an edge to a point
		"""
		raise NotImplementedError
	
	def remove_face (self, fid) :
		"""
		remove the specified face and all links
		connected to this face
		"""
		raise NotImplementedError
	
	def remove_edge (self, eid) :
		"""
		remove the specified edge and all links
		connected to this edge
		"""
		raise NotImplementedError
	
	def remove_point (self, pid) :
		"""
		remove the specified point and all links
		connected to this point
		remove the position associated to this point too
		"""
		raise NotImplementedError

class IGlobalChangeMesh (object) :
	"""
	global modification of mesh geometry
	"""
	def __iadd__ (self, vector) :
		"""
		translate all points according to vector
		"""
		raise NotImplementedError
	
	def __isub__ (self, vector) :
		"""
		translate all points in opposite direction of vector
		"""
		raise NotImplementedError
	
	def __imul__ (self, val) :
		"""
		scale each point using val
		"""
		raise NotImplementedError
	
	def __idiv__ (self, val) :
		"""
		scale each point using val
		"""
		raise NotImplementedError

class IAdvancedMesh (object) :
	"""
	provide a set of usefull geometrical functions on mesh
	"""
	def centroid (self, pid_iter) :
		"""
		compute centroid of a set of points
		:type pid_list: iter of pid
		:rtype: pos
		"""
		raise NotImplementedError


