from physics.chemistry import Reaction,Diffusion
from celltissue.data.wisp_border_mesh import WispBorderMesh,CellMap,PointMap
from celltissue.simulation import Process

class Physiology (Process) :
	"""
	a container for physiology
	"""
	def __init__ (self, tissue, wt, D, B, fixed, substance) :
		Process.__init__(self,"physio")
		self.tissue=tissue
		self.tm=WispBorderMesh(0,tissue)
		self.wt=wt
		self.D=D
		self.B=B
		self.fixed=fixed
		self.substance=substance
		self.algoR=None
		self.algoD=None
	
	def react (self, dt) :
		substance=CellMap(self.substance,self.tm)
		self.algoR.react(substance,dt)
		self.algoD.react(substance,dt)
	
	def set_algo (self) :
		tm=self.tm
		t=self.tissue
		wt=self.wt
		cV=dict( (cid,t.geometry(0,tm.cell_to_wisp(cid)).volume(wt)) for cid in tm.cells() )
		self.algoR=Reaction({},self.B)
		self.algoD=Diffusion(tm,
						cV,
						PointMap(self.D,tm),
						CellMap(self.fixed,tm),{})
	
	def __call__ (self, dt, *args) :
		self.set_algo()
		self.react(dt)
