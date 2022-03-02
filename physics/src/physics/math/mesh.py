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
__revision__=" $Id: mesh.py 7882 2010-02-08 18:36:38Z cokelaer $ "

from scipy import matrix
from openalea.container import Topomesh
from tensor import Tensor
from interface.mesh import InvalidFace,InvalidEdge,InvalidPoint,\
				IMesh2D,\
				IFaceListMesh,IEdgeListMesh,IPointListMesh,\
				IPositionMesh,\
				IMutableMesh,IGlobalChangeMesh,IAdvancedMesh

class StrInvalidFace (InvalidFace) :
	def __init__ (self, fid) :
		InvalidFace.__init__(self,"face %d does not exist" % fid)

class StrInvalidEdge (InvalidEdge) :
	def __init__ (self, eid) :
		InvalidEdge.__init__(self,"edge %d does not exist" % eid)

class StrInvalidPoint (InvalidPoint) :
	def __init__ (self, pid) :
		InvalidPoint.__init__(self,"point %d does not exist" % pid)

class Mesh2D (IMesh2D,\
				IFaceListMesh,IEdgeListMesh,IPointListMesh,\
				IPositionMesh,\
				IMutableMesh,IGlobalChangeMesh,IAdvancedMesh) :
	"""
	implementation of a mesh as two topomesh
	plus a position map
	"""
	def __init__ (self) :
		self._faces=Topomesh()
		self._edges=Topomesh()
		self._positions={}
	
	#####################################################
	#
	#		IMesh2D
	#
	#####################################################
	def is_valid (self) :
		return True
	is_valid.__doc__=IMesh2D.is_valid.__doc__
	
	def has_face (self, fid) :
		return self._faces.has_cell(fid)
	has_face.__doc__=IMesh2D.has_face.__doc__
	
	def has_edge (self, eid) :
		return self._edges.has_cell(eid)
	has_edge.__doc__=IMesh2D.has_edge.__doc__
	
	def has_point (self, pid) :
		return self._edges.has_point(pid)
	has_point.__doc__=IMesh2D.has_point.__doc__
	#####################################################
	#
	#		IFaceListMesh
	#
	#####################################################
	def faces (self, eid=None, pid=None) :
		if pid is None :
			return self._faces.cells(eid)
		else :
			fcs=set()
			for eid in self._edges.cells(pid) :
				fcs|=set(self._faces.cells(eid))
			return iter(fcs)
	faces.__doc__=IFaceListMesh.faces.__doc__
	
	def nb_faces (self, eid=None, pid=None) :
		if pid is None :
			return self._faces.nb_cells(eid)
		else :
			fcs=set()
			for eid in self._edges.cells(pid) :
				fcs|=set(self._faces.cells(eid))
			return len(fcs)
	nb_faces.__doc__=IFaceListMesh.nb_faces.__doc__
	#####################################################
	#
	#		IEdgeListMesh
	#
	#####################################################
	def edges (self, fid=None, pid=None) :
		if pid is None :
			return self._faces.points(fid)
		else :
			return self._edges.cells(pid)
	edges.__doc__=IEdgeListMesh.edges.__doc__
	
	def nb_edges (self, fid=None, pid=None) :
		if pid is None :
			return self._faces.nb_points(fid)
		else :
			return self._edges.nb_cells(pid)
	nb_edges.__doc__=IEdgeListMesh.nb_edges.__doc__
	#####################################################
	#
	#		IPointListMesh
	#
	#####################################################
	def points (self, fid=None, eid=None) :
		if fid is None :
			return self._edges.points(eid)
		else :
			pts=set()
			for eid in self._faces.points(fid) :
				pts|=set(self._edges.points(eid))
			return iter(pts)
	points.__doc__=IPointListMesh.points.__doc__
	
	def nb_points (self, fid=None, eid=None) :
		if fid is None :
			return self._edges.nb_points(eid)
		else :
			pts=set()
			for eid in self._faces.points(fid) :
				pts|=set(self._edges.points(eid))
			return len(pts)
	nb_points.__doc__=IPointListMesh.nb_points.__doc__
	#####################################################
	#
	#		mesh IPositionMesh
	#
	#####################################################
	def position (self, pid) :
		return self._positions[pid]
	position.__doc__=IPositionMesh.position.__doc__
	
	def positions (self) :
		return self._positions.iteritems()
	positions.__doc__=IPositionMesh.positions.__doc__
	
	def __iter__ (self) :
		return iter(self._positions)
	
	def __len__ (self) :
		return len(self._positions)
	#####################################################
	#
	#		IMutableMesh
	#
	#####################################################
	def add_face (self, fid=None) :
		return self._faces.add_cell(fid)
	add_face.__doc__=IMutableMesh.add_face.__doc__
	
	def add_edge (self, eid=None) :
		eid1=self._faces.add_point(eid)
		eid2=self._edges.add_cell(eid1)
		if eid1!=eid2 :
			raise UserWarning ("mismatch between edge ids")
		return eid2
	add_edge.__doc__=IMutableMesh.add_edge.__doc__
	
	def add_point (self, pos, pid=None) :
		pid=self._edges.add_point(pid)
		self._positions[pid]=pos
		return pid
	add_point.__doc__=IMutableMesh.add_point.__doc__
	
	def set_position (self, pid, pos) :
		self._positions[pid]=pos
	set_position.__doc__=IMutableMesh.set_position.__doc__
	
	def add_border (self, fid, eid) :
		self._faces.add_link(fid,eid)
	add_border.__doc__=IMutableMesh.add_border.__doc__
	
	def add_corner (self, eid, pid) :
		self._edges.add_link(eid,pid)
	add_corner.__doc__=IMutableMesh.add_corner.__doc__
	
	def remove_face (self, fid) :
		self._faces.remove_cell(fid)
	remove_face.__doc__=IMutableMesh.remove_face.__doc__
	
	def remove_edge (self, eid) :
		self._faces.remove_point(eid)
		self._edges.remove_cell(eid)
	remove_edge.__doc__=IMutableMesh.remove_edge.__doc__
	
	def remove_point (self, pid) :
		self._edges.remove_point(pid)
		del self._positions[pid]
	remove_point.__doc__=IMutableMesh.remove_point.__doc__
	
	def destruct_faces (self, faces) :
		"""
		remove a list of faces and all orphan edges and points
		"""
		modified_edges=set()
		for fid in list(faces) :
			modified_edges|=set(self.edges(fid=fid))
			self.remove_face(fid)
		modified_points=set()
		for eid in modified_edges :
			if self.nb_faces(eid=eid)==0 :
				modified_points|=set(self.points(eid=eid))
				self.remove_edge(eid)
		for pid in modified_points :
			if self.nb_edges(pid=pid)==0 :
				self.remove_point(pid)
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

class TriangleMesh (Mesh2D) :
	"""
	a Mesh2D using only triangles
	"""
	def is_valid (self) :
		ret=Mesh2D.is_valid(self)
		for fid in self.faces() :
			if self.nb_edges(fid=fid)!=3 :
				return False
		return ret
	
	def points (self, fid=None, eid=None) :
		pts=list(Mesh2D.points(self,fid,eid))
		if len(pts)==3 :
			pid1,pid2,pid3=pts
			if (self.position(pid2)-self.position(pid1)).cross(self.position(pid3)-self.position(pid1))<0 :
				pts=[pid1,pid3,pid2]
		return iter(pts)
	
	def length (self, eid) :
		pos1,pos2=(self.position(pid) for pid in self.points(eid=eid))
		return (pos2-pos1).norm()
	
	def surface (self, fid) :
		v=[self.position(pid) for pid in self.points(fid=fid)]
		A=Tensor([[1,v[0].x,v[0].y],\
				  [1,v[1].x,v[1].y],\
				  [1,v[2].x,v[2].y]])
		return abs(A.det())/2.
	
	def local_basis (self, fid) :
		"""
		compute local basis associated to the given face
		"""
		v1,v2,v3=(self.position(pid) for pid in self.points(fid=fid))
		e1=v2-v1
		e1/=e1.norm()
		e3=e1.cross(v3-v1)
		e3/=e3.norm()
		e2=e3.cross(e1)
		return matrix( [[e1.x,e2.x,e3.x],
					    [e1.y,e2.y,e3.y],
					    [e1.z,e2.z,e3.z]] )
	
	def _opposite_point (self, eid, pid) :
		"""
		return opposite point of edge
		"""
		corners=list(self.points(eid=eid))
		corners.remove(pid)
		return corners[0]
	
	def _opposite_edge (self, fid, eid, pid) :
		"""
		return opposite edge of a point in a face
		"""
		edges=set(self.edges(pid=pid))&set(self.edges(fid=fid))
		edges.remove(eid)
		return edges.pop()
	
	def refine (self, fid) :
		"""
		refine a face of the mesh by subdividing the
		longest edge of the face using Rivara algorithm
		divide linked faces if necessary to maintain
		conformity of the mesh
		"""
		already_divided_edges={}
		to_divide_face=set([fid])
		divided_faces=[]
		divided_edges=[]
		while len(to_divide_face)>0 :
			fid=to_divide_face.pop()
			edges=list(self.edges(fid=fid))
			#calcul de la longueur de chacune de aretes
			edge_length={}
			for eid in edges :
				pid1,pid2=self.points(eid=eid)
				edge_length[eid]=(self.position(pid1)-self.position(pid2)).norm()
			real_length=[]
			for eid in edges :
				if eid in already_divided_edges and already_divided_edges[eid] in edges :
					real_length.append( (edge_length[eid]+edge_length[already_divided_edges[eid]],eid) )
				else :
					real_length.append( (edge_length[eid],eid) )
			real_length.sort()
			div_eid=real_length[-1][1]
			if div_eid not in already_divided_edges :
				#subdivision de l'edge
				pid1,pid2=self.points(eid=div_eid)
				pid=self.add_point( (self.position(pid1)+self.position(pid2))/2. )
				eid1=self.add_edge()
				self.add_corner(eid1,pid1)
				self.add_corner(eid1,pid)
				eid2=self.add_edge()
				self.add_corner(eid2,pid2)
				self.add_corner(eid2,pid)
				#raccord avec les faces
				faces=set(self.faces(eid=div_eid))
				for bid in faces :
					self.add_border(bid,eid1)
					self.add_border(bid,eid2)
				#ajout a la liste des faces a traiter
				faces.remove(fid)
				to_divide_face|=faces
				#retrait de l'ancienne edge
				self.remove_edge(div_eid)
				divided_edges.append( (div_eid,(eid1,eid2)) )
				#mise a jour de div_eid
				div_eid=eid1
				already_divided_edges[eid1]=eid2
				already_divided_edges[eid2]=eid1
			#division de la face en deux
			#recherche du sommet oppose a div_eid
			#recherche des trois sommets du triangle
			face_corners=set(self.points(fid=fid))
			edges=list(self.edges(fid=fid))
			for eid in edges :
				if eid in already_divided_edges :
					eid2=already_divided_edges[eid]
					if eid2 in edges :
						edges.remove(eid2)
						#recherche point commun aux deux edges
						common_pid=set(self.points(eid=eid))&set(self.points(eid=eid2))
						face_corners-=common_pid
			assert len(face_corners)==3
			#retrait des deux points de la edge divisee
			eid2=already_divided_edges[div_eid]
			edge_pts=set(self.points(eid=div_eid))|set(self.points(eid=eid2))
			face_corners-=edge_pts
			top_pid=face_corners.pop()
			#creation de la nouvelle edge
			new_eid=self.add_edge()
			self.add_corner(new_eid,top_pid)
			common_pid=set(self.points(eid=div_eid))&set(self.points(eid=eid2))
			common_pid=common_pid.pop()
			self.add_corner(new_eid,common_pid)
			#division de la face
			fid1=self.add_face()
			self.add_border(fid1,new_eid)
			self.add_border(fid1,div_eid)
			eid=div_eid
			pid=self._opposite_point(eid,common_pid)
			while pid!=top_pid :
				eid=self._opposite_edge(fid,eid,pid)
				self.add_border(fid1,eid)
				pid=self._opposite_point(eid,pid)
			fid2=self.add_face()
			self.add_border(fid2,new_eid)
			self.add_border(fid2,eid2)
			eid=eid2
			pid=self._opposite_point(eid,common_pid)
			while pid!=top_pid :
				eid=self._opposite_edge(fid,eid,pid)
				self.add_border(fid2,eid)
				pid=self._opposite_point(eid,pid)
			#retrait de l'ancienne face
			self.remove_face(fid)
			#mise a jour des faces modifiees
			divided_faces.append( (fid,[fid1,fid2]) )
			#ajout des faces à la liste des faces à traiter si necessaire
			for fid in (fid1,fid2) :
				if self.nb_edges(fid=fid)>3 :
					to_divide_face.add(fid)
		return divided_faces,divided_edges
