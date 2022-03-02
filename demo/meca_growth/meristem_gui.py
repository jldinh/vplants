from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QAction,QIcon
from openalea.plantgl.algo import GLRenderer
from celltissue.gui import *
from celltissue.gui.pgl import draw2D,TissueView2D,TissueGUI,SelectWispTool
from celltissue.data import TissueProperty
import meristem_rc


class MeristemView2D (TissueView2D) :
	name="meris"
	def __init__ (self, t, pos, morpho, physio, meca) :
		TissueView2D.__init__(self,t,pos)
		self._morpho=morpho
		self._physio=physio
		self._meca=meca
		#display
		self._display_morphogen=True
		self._display_turgor_strain=False
		self._strain_min=1e-2
		self._strain_max=0.3
		self._display_turgor_stress=False
		self._stress_min=1.1e-7
		self._stress_max=2.e-6
	#########################################################
	#
	#		display
	#
	#########################################################
	def display_morphogen (self, display) :
		self._display_morphogen=display
		self.emit(SIGNAL("display morphogen"),display)
	
	def morphogen_displayed (self) :
		return self._display_morphogen
	
	def display_turgor_strain (self, display) :
		self._display_turgor_strain=display
		self.emit(SIGNAL("display turgor strain"),display)
	
	def turgor_strain_displayed (self) :
		return self._display_turgor_strain
	#########################################################
	#
	#		drawable
	#
	#########################################################
	def redraw (self, layer=0) :
		TissueView2D.redraw(self,3)
		t=self._tissue
		pos=self._pos
		meca=self._meca
		if self._display_morphogen :
			gt=GraphicalTissue()
			gt.add_description(IntensityFill(self._morpho,t,pos))
			draw2D(gt,self,layer)
			layer+=1
		if self._display_turgor_strain and meca.algo is not None :
			strain=TissueProperty(0)
			for wid in t.wisps(0) :
				strain[wid]=meca.turgor_strain(wid).trace()
			gt=GraphicalTissue()
			gt.add_description(IntensityFill(strain,t,pos,
					JetMap(self._strain_min,self._strain_max,True)))
			draw2D(gt,self,layer)
			layer+=1
		if self._display_turgor_stress and meca.algo is not None :
			stress=TissueProperty(0)
			for wid in t.wisps(0) :
				stress[wid]=meca.turgor_stress(wid).trace()
			gt=GraphicalTissue()
			gt.add_description(IntensityFill(stress,t,pos,
					JetMap(self._stress_min,self._stress_max,True)))
			draw2D(gt,self,layer)
			layer+=1

class MeristemGUI (TissueGUI) :
	def __init__ (self, meristem_view) :
		TissueGUI.__init__(self,meristem_view)
	
	###############################################################
	#
	#		IInteractive
	#
	###############################################################
	def setup_ui (self, main_window) :
		TissueGUI.setup_ui(self,main_window)
		ui=self.ui
		meris=self.element()
		ui.menuTissue.setTitle("Meristem")
		ui.actionDisplayMorphogen=QAction("IAA",main_window)
		ui.actionDisplayMorphogen.setCheckable(True)
		ui.actionDisplayMorphogen.setChecked(meris.morphogen_displayed())
		main_window.connect(ui.actionDisplayMorphogen,SIGNAL("toggled(bool)"),meris.display_morphogen)
		main_window.connect(meris,SIGNAL("display morphogen"),self.display_morphogen)
		ui.actionDisplayTurgorStrain=QAction("Tstrain",main_window)
		ui.actionDisplayTurgorStrain.setCheckable(True)
		ui.actionDisplayTurgorStrain.setChecked(meris.turgor_strain_displayed())
		main_window.connect(ui.actionDisplayTurgorStrain,SIGNAL("toggled(bool)"),meris.display_turgor_strain)
		main_window.connect(meris,SIGNAL("display turgor strain"),self.display_turgor_strain)
		#tools
		ui.sepToolAction=QAction(main_window)
		ui.sepToolAction.setSeparator(True)
		ui.selectSourceTool=SelectSourceTool(meris,main_window)
	
	def setup_actionbar (self, actionbar) :
		ui=self.ui
		for action in (ui.actionDisplayMorphogen,ui.actionDisplayTurgorStrain) :
			actionbar.addAction(action)
		actionbar.addSeparator()
		TissueGUI.setup_actionbar(self,actionbar)
	
	def toolbar_items (self) :
		items=TissueGUI.toolbar_items(self)
		ui=self.ui
		return [ui.selectSourceTool,ui.sepToolAction]+items
	##############################################################
	#
	#		specific actions
	#
	##############################################################
	def display_morphogen (self, display) :
		self.ui.actionDisplayMorphogen.setChecked(display)
		self.element().redraw()
		self.update_view()
	
	def display_turgor_strain (self, display) :
		self.ui.actionDisplayTurgorStrain.setChecked(display)
		self.element().redraw()
		self.update_view()

class SelectSourceTool (SelectWispTool) :
	"""
	add a new sink to the simulation
	"""
	def __init__ (self, meris_view, parent) :
		SelectWispTool.__init__(self,meris_view,parent,0)
		self.setIcon(QIcon(":/images/icons/Raratonga_Mask.png"))
		self.setText("select source")
		self.connect(self,SIGNAL("selection"),self.set_source)
	
	def set_source (self, scale, wid) :
		self._tissue._physio.fixed.clear()
		if wid is None :
			pass
		else :
			self._tissue._physio.fixed[wid]=0.9
			self._tissue._morpho[wid]=0.9
			self._tissue.redraw()


