from openalea.plantgl.math import Vector3
from openalea.plantgl.scenegraph import Color4,Shape,Material,Polyline
from openalea.celltissue import Tissue,topen
#from openalea.celltissue.data import PropertyMap

class Root (object) :
	"""
	a simple container for root simulation
	"""
	def __init__ (self) :
		#tissue
		self.tissue=Tissue()
		self.CELL=self.tissue.add_type("cell")
		self.WALL=self.tissue.add_type("wall")
		self.CORNER=self.tissue.add_type("corner")
		self.PUMP=self.tissue.add_type("pump")
		self.corner_graph_id=self.tissue.add_relation("graph",(self.CORNER,self.WALL))
		self.diffusion_graph_id=self.tissue.add_relation("graph",(self.CELL,self.WALL))
		self.transport_graph_id=self.tissue.add_relation("graph",(self.CELL,self.PUMP))
		self.pump_wall_rel_id=self.tissue.add_relation("relation",(self.PUMP,self.WALL,None))

		#take wall compartement into account
		#self.CW_diffusion_graph_id = self.tissue.add_relation("graph",(self.CELL,self.WALL,self.WALL))
		self.WW_diffusion_graph_id = self.tissue.add_relation("graph",(self.WALL,self.CORNER))
		#self.CW_transport_graph_id=self.tissue.add_relation("graph",(self.CELL,self.WALL,self.PUMP))

		#geometry
		self.position={}
		self.cell_corners={}
		self.cell_volume={}
		self.wall_surface={}

		#physio
		self.auxin={}#percentage of auxin in cell and walls
		self.auxin_creation={}
		self.auxin_degradation={}
		self.diffusion_coeff={}

		self.pump_creation={}
		self.pump_degradation={}
		self.relative_pumps={}#percentage of pumps for each edge of pump_graph

		self.fixed_concentration={}
		self.fixed_flux={}

		self.cells_of_wall={}
		self.walls_of_cell={}

	def cells (self) :
		return self.tissue.elements(self.CELL)

	def walls (self) :
		return self.tissue.elements(self.WALL)

	def corners (self) :
		return self.tissue.elements(self.CORNER)

	def pumps (self) :
		return self.tissue.elements(self.PUMP)

	def corner_graph (self) :
		return self.tissue.relation(self.corner_graph_id)

	def diffusion_graph (self) :
		return self.tissue.relation(self.diffusion_graph_id)

	#def CW_diffusion_graph (self) :
	#	return self.tissue.relation(self.CW_diffusion_graph_id)

	def WW_diffusion_graph (self) :
		return self.tissue.relation(self.WW_diffusion_graph_id)

	def transport_graph (self) :
		return self.tissue.relation(self.transport_graph_id)

	#def CW_transport_graph (self) :
	#	return self.tissue.relation(self.CW_transport_graph_id)

	def wall (self, pump_id) :
		"""
		return id of the wall supporting the given pump
		"""
		rel=self.tissue.relation(self.pump_wall_rel_id)
		wid,=(rel.right(lid) for lid in rel.from_left(pump_id))
		return wid

	def associated_pumps (self, wall_id) :
		"""
		return ids of the pumps supported by the given wall
		"""
		rel=self.tissue.relation(self.pump_wall_rel_id)
		for lid in rel.from_right(wall_id) :
			yield rel.left(lid)

	def associated_cells (self, wall_id) :
		"""
		return ids of the cells associated with the given wall
		"""
		cg = self.corner_graph()
		swc = cg.source(wall_id)
		twc = cg.target(wall_id)
		cells = []
		for cid in self.cells() :
			if (swc in self.cell_corners[cid]) and (twc in self.cell_corners[cid]) :
				cells.append(cid)
		return cells

	def associated_walls (self, cell_id) :
		"""
		return ids of the walls associated with the given cell
		"""
		cg = self.corner_graph()
		corners = self.cell_corners[cell_id]
		walls = []
		for wid in self.walls():
			swc = cg.source(wid)
			twc = cg.target(wid)
			if (swc in corners) and (twc in corners):
				walls.append(wid)
		return walls

	######################################################
	#
	#		in out
	#
	######################################################
	def write (self, tissuename) :
		f=topen(tissuename,'w')
		f.write(self.tissue,description="root tissue")
		f.write(dict( (pid,tuple(v)) for pid,v in self.position.iteritems() ),"positions","positions of cell vertices")
		f.write(self.cell_corners,"corners","cell corners")
		f.write(self.cell_volume,"volume","cell volume")
		f.write(self.wall_surface,"surface","wall surface")
		
		f.write(self.auxin,"IAA","auxin concentration in walls and cells")
		f.write(self.auxin_creation,"IAAcreation","auxin creation coefficient in each cell")
		f.write(self.auxin_degradation,"IAAdegradation","auxin degradation coefficient in each cell")
		f.write(self.diffusion_coeff,"IAAdiffusion","auxin diffusion coefficient")
		f.write(self.relative_pumps,"IAApumps","auxin pumps")
		f.close()

	def read (self, tissuename) :
		f=topen(tissuename,'r')
		tissue,d=f.read()
		assert tissue.type_name(self.CELL)=="cell"
		assert tissue.type_name(self.WALL)=="wall"
		assert tissue.type_name(self.CORNER)=="corner"
		assert tissue.type_name(self.PUMP)=="pump"
		self.tissue=tissue
		pos,d=f.read("positions")
		self.position=dict( (pid,Vector3(*tup)) for pid,tup in pos.iteritems() )
		prop,d=f.read("corners")
		self.cell_corners=prop
		for propname,filename in [("cell_volume","volume"),
								  ("wall_surface","surface"),
								  ("auxin","IAA"),
								  ("auxin_creation","IAAcreation"),
								  ("auxin_degradation","IAAdegradation"),
								  ("diffusion_coeff","IAAdiffusion"),
								  ("relative_pumps","IAApumps")] :
			prop,d=f.read(filename)
			getattr(self,propname).clear()
			for k,v in prop.iteritems() :
				getattr(self,propname)[k]=v
		f.close()

