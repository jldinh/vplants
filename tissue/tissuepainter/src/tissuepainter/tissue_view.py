# -*- python -*-
# -*- coding: utf-8 -*-
#
#       TissueView : tissuepainter package
#
#       Copyright or  or Copr. 2006 INRIA - CIRAD - INRA
#
#       File author(s): Jerome Chopard <revesansparole@gmail.com>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       VPlants WebSite : https://gforge.inria.fr/projects/vplants/
#

__doc__="""
This module provides a view on a tissue used by pglviewer
"""

__license__= "Cecill-C"
__revision__=" $Id: topomesh_algo.py 8560 2010-03-29 20:51:18Z chopard $ "


from PyQt4.QtCore import SIGNAL
from vplants.plantgl.math import Vector3
from vplants.plantgl.scenegraph import (Scene, Shape, Material, TriangleSet)
from openalea.container import IdDict, triangulate
from openalea.pglviewer import SceneView

DEFAULT_MAT = Material()

def tovec (tup) :
	return Vector3(*tuple(float(v) for v in tup) )

class TissueView (SceneView) :
	"""Display a tissue
	"""
	def __init__ (self) :
		SceneView.__init__(self)
		self.idmode = self.IDMODE.SHAPE
		
		#display_informations
		self._color_map = IdDict()
		self._color_description = {}
		self._normal_inside = False
		
		#mesh informations
		self.clear()
	
	def clear (self) :
		"""Clear all properties
		"""
		#mesh information
		self._tissue = None
		
		#mesh geometry
		self._geom = {}
		
		#color information
		self._color = {}
		
		#display information
		self._displayed = {}
	
	########################################################
	#
	#	tissue accessor
	#
	########################################################
	def tissue (self) :
		return self._tissue
	
	def set_tissue (self, tissue) :
		"""Set a new tissue for this view
		
		:Warning: potentially long operation since all
		cell geometries have to be recomputed
		"""
		old_tissue = self._tissue
		
		self.clear()
		
		self._tissue = tissue
		if tissue is not None :
			self.cache_geometry()
			mesh = tissue.geometry()
			for cid in mesh.darts(3) :
				self._color[cid] = None
				self._displayed[cid] = True
			
			self.redraw()
		
		self.emit(SIGNAL("tissue_setted"), tissue, old_tissue)
	
	def state (self) :
		"""Return the current paint state of the tissue
		"""
		return self._color
	
	def set_state (self, state) :
		"""Set the current state of the tissue
		"""
		color = self._color
		
		modif = []
		for cid, color_id in state.iteritems() :
			col = color[cid]
			if col != color_id :
				color[cid] = color_id
				modif.append( (cid, col, color_id) )
		
		if len(modif) > 0 :
			self.emit(SIGNAL("set_state"), state)
		return modif
	
	########################################################
	#
	#	cell accessor
	#
	########################################################
	def color (self, cid) :
		"""Returns color id associated to a cell
		"""
		return self._color[cid]
	
	def set_color (self, cid, color_id) :
		"""Associate a new color to a cell
		"""
		col = self._color[cid]
		if col == color_id :
			return []
		else :
			self._color[cid] = color_id
			self.emit(SIGNAL("set_color"), cid, color_id)
			return [(cid, col, color_id)]
	
	def update_colors (self, colors) :
		"""Update colors
		
		:Parameters:
		 - `colors` (list of (cid|color_id) )
		"""
		color = self._color
		modifs = []
		for cid, color_id in colors :
			col = color[cid]
			if col != color_id :
				modifs.append( (cid, col, color_id) )
				color[cid] = color_id
		
		if len(modifs) > 0 :
			self.emit(SIGNAL("update_colors") )
		return modifs
	
	def is_displayed (self, cid) :
		"""Test wether this cell is displayed
		"""
		return self._displayed[cid]
	
	def display (self, cid, display) :
		"""Set wether this cell must be displayed
		"""
		self._displayed[cid] = display
		self.emit(SIGNAL("display"), cid, display)

	def update_display (self, display_list) :
		"""Update display of a list of cells
		"""
		for cid, state in display_list :
			self._displayed[cid] = state
		
		self.emit(SIGNAL("update_display") )
	
	########################################################
	#
	#	colors
	#
	########################################################
	def colors (self) :
		"""Iterator on all available color id
		"""
		return self._color_map.iterkeys()

	def color_def (self, color_id) :
		"""Return actual color corresponding to this
		color id
		"""
		if color_id is None :
			return None
		else :
			return self._color_map[color_id]
	
	def add_color (self, color, color_id = None) :
		"""Add (or set if not already defined) a color
		into the color map. Return the id used to store the color
		"""
		color_id = self._color_map.add(color, color_id)
		self._color_description[color_id] = None
		self.emit(SIGNAL("add_color"), color_id)
		return color_id
	
	def del_color (self, color_id) :
		"""Remove a color from the color map
		all cells with this color will be turned to None
		"""
		if color_id is None :
			return [] #Does nothing
		
		color = self._color
		
		#set color to None
		modif = []
		for cid, col in color.iteritems() :
			if col == color_id :
				modif.append( (cid, color_id, None) )
				color[cid] = None
		
		#remove color
		mat = self._color_map.pop(color_id)
		del self._color_description[color_id]
		
		self.emit(SIGNAL("del_color"), color_id, mat)
		return modif
	
	def color_description (self, color_id) :
		"""Return the description associated with a color
		"""
		return self._color_description[color_id]
	
	def set_color_description (self, color_id, description) :
		"""Associate a textual description to a color
		"""
		self._color_description[color_id] = description
		self.emit(SIGNAL("set_color_description"), color_id)
	
	########################################################
	#
	#	geom functions
	#
	########################################################
	def set_normal_inside (self, inside) :
		"""Set wether normals for cell display are inside or not
		"""
		if self._normal_inside == inside :#nothing to do
			return
		
		#flip order of points in triangles
		for ts in self._geom.itervalues() :
			ts.indexList = [ (i1,i3,i2) for i1,i2,i3 in tuple(ts.indexList) ]
		
		self.emit(SIGNAL("set_normal_inside"), inside)
	
	def cache_geometry (self) :
		"""Compute geom representation of each cell and
		store it for further usage
		"""
		if self._tissue is None :
			return #nothing to do
		
		#clear previous cache
		self._geom.clear()
		
		#recompute
		mesh = self._tissue.geometry()
		mesh.apply_geom_transfo(tovec)
		
		for cid in mesh.darts(3) :#iterate on cells
			m = mesh.local_view(cid).instance()
			for fid in tuple(m.borders(cid) ) :
				triangulate(m, fid)
			
			pos = []
			pid_to_ind = {}
			for pid in m.darts(0) :
				pid_to_ind[pid] = len(pos)
				pos.append(m.position(pid) )
			
			bary = reduce(lambda x, y: x + y, pos) / len(pos)
			
			#scale geometry
			pos = [bary + (vec - bary) * 0.9 for vec in pos]
			
			#create triangle indexes
			triangles = []
			for fid in m.darts(2) :
				i1, i2, i3 = (pid_to_ind[pid] for pid in m.borders(fid, 2) )
				ori = (pos[i1] + pos[i2] + pos[i3]) / 3. - bary
				test = (pos[i2] - pos[i1])^(pos[i3] - pos[i1])
				if ori * test > 0 :#correct order of points
					inds = (i1, i2, i3)
				else :#flip order of points
					inds = (i1, i3, i2)
				
				if self._normal_inside :
					inds = (inds[0], inds[2], inds[1])
				
				triangles.append(inds)
			
			#create TriangleSet
			self._geom[cid] = TriangleSet(pos, triangles)
	
	########################################################
	#
	#	geom functions
	#
	########################################################
	def clear_scene (self) :
		SceneView.clear(self, False)
	
	def material (self, cid) :
		"""Find the material associated to a cell
		"""
		color_id = self.color(cid)
		if color_id is None :
			return DEFAULT_MAT
		else :
			return self._color_map[color_id]
	
	def redraw (self) :
		"""Redraw the mesh
		"""
		sc = Scene()
		for cid, geom in self._geom.iteritems() :
			if self._displayed[cid] :
				sc.add(Shape(geom, self.material(cid), cid) )
		
		self.clear_scene()
		self.merge(sc)
	
	########################################################
	#
	#	edition
	#
	########################################################
	def clear_colors (self) :
		"""Set color of all cells to None
		"""
		if self._tissue is None :
			return None
		
		mesh = self._tissue.geometry()
		
		modifs = []
		for cid in mesh.darts(3) :
			col = self._color[cid]
			if col is not None :
				self._color[cid] = None
				modifs.append( (cid, col, None) )
		
		self.emit(SIGNAL("clear_colors") )
		return modifs
	
	def expand (self, color_id) :
		"""Expand current color zone with a layer of cells
		Works only on visible cells
		"""
		mesh = self._tissue.geometry()
		displayed = self._displayed
		color = self._color
		
		inside = set()
		border = set()
		for cid in mesh.darts(3) :
			if displayed[cid] and (color[cid] == color_id) :
				inside.add(cid)
				border.update(mesh.border_neighbors(cid) )
		
		modifs = []
		for bid in (border - inside) :
			if displayed[bid] :
				modifs.append( (cid, color[bid], color_id) )
				color[bid] = color_id
		
		self.emit(SIGNAL("expand"), color_id)
		return modifs
	
	def shrink (self, color_id) :
		"""Remove a layer of cells around zone with current color
		"""
		mesh = self._tissue.geometry()
		displayed = self._displayed
		color = self._color
		
		inside = set()
		for cid in mesh.darts(3) :
			if displayed[cid] and (color[cid] == color_id) :
				inside.add(cid)
		
		border = set()
		for cid in inside :
			for fid in mesh.borders(cid) :
				if mesh.nb_regions(fid) == 1 :
					border.add(cid)
				elif any(rid not in inside and displayed[rid] \
				         for rid in mesh.regions(fid) ) :
					border.add(cid)
		
		modifs = []
		for cid in border :
			modifs.append( (cid, color[cid], None) )
			color[cid] = None
		
		self.emit(SIGNAL("shrink"), color_id)
		return modifs
	
	def fill_region (self, cid, color_id) :
		"""Repaint all cells which are both visible and in 
		the same color region than the given cell
		"""
		mesh = self._tissue.geometry()
		displayed = self._displayed
		color = self._color
		
		ref_color = color[cid]
		if ref_color == color_id :
			return []
		
		front = set([cid])
		modifs = []
		while len(front) > 0 :
			cid = front.pop()
			modifs.append( (cid, color[cid], color_id) )
			color[cid] = color_id
			for nid in mesh.border_neighbors(cid) :
				if displayed[nid] and (color[nid] == ref_color) \
				                  and (color[nid] != color_id) :
					front.add(nid)
		
		self.emit(SIGNAL("fill_region"), color_id)
		return modifs

















