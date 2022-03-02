from celltissue.algo.structure import MainAxisPolyhedral2D
from celltissue.simulation import Process

class CellDivision (Process) :
	def __init__ (self, tissue, pos, Vref, prop_list) :
		Process.__init__(self,"division")
		self._tissue=tissue
		self._pos=pos
		self._Vref=Vref
		self._prop_list=prop_list
	
	def __call__ (self, *args) :
		Vref=self._Vref
		t=self._tissue
		pos=self._pos
		plist=self._prop_list
		for cid in list(t.wisps(0)) :
			if t.geometry(0,cid).volume(pos)>Vref :
				print "div",cid
				division=MainAxisPolyhedral2D(cid,pos,-1.)
				division.initialize(t)
				pos.structural_init(division)
				for prop in plist :
					prop.structural_init(division)
				division.modify(t)
				pos.structural_update(division)
				for prop in plist :
					prop.structural_update(division)

