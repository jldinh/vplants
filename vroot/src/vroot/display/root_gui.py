from PyQt4.QtCore import Qt,SIGNAL,QSize
from PyQt4.QtGui import QFileDialog,QAction,QActionGroup,QIcon,QToolBar
from openalea.pglviewer import ElmGUI,MouseTool
from root_ui import Ui_MainWindow

class RootGUI (ElmGUI) :
	def __init__ (self, scene_view) :
		ElmGUI.__init__(self,scene_view)
		self.ui=Ui_MainWindow()
	
	###############################################################
	#
	#		IInteractive
	#
	###############################################################
	def setup_ui (self, main_window) :
		ElmGUI.setup_ui(self,main_window)
		ui=self.ui
		ui.setupUi(main_window)
		root=self.element()

		ui.actionAutoamplifiedPumps=QAction("autoamplified pumps",main_window)
		ui.actionAutoamplifiedPumps.setCheckable(True)
		ui.actionAutoamplifiedPumps.setChecked(False)
		main_window.connect(ui.actionAutoamplifiedPumps,SIGNAL("triggered(bool)"),root.autoamplified_pumps)
		main_window.connect(root,SIGNAL("autoamplified pumps"),self.autoamplified_pumps)

		main_window.connect(ui.actionDisplayBaseCells,SIGNAL("toggled(bool)"),root.display_base_cells)
		main_window.connect(root,SIGNAL("display base cells"),self.display_base_cells)
		main_window.connect(ui.actionDisplayWalls,SIGNAL("toggled(bool)"),root.display_walls)
		main_window.connect(root,SIGNAL("display walls"),self.display_walls)
		main_window.connect(ui.actionDisplayPumps,SIGNAL("toggled(bool)"),root.display_pumps)
		main_window.connect(root,SIGNAL("display pumps"),self.display_pumps)
		ui.displayActionGroup=QActionGroup(main_window)
		ui.display_toolbar=QToolBar()
		ui.display_toolbar.setOrientation(Qt.Horizontal)
		ui.display_toolbar.setIconSize(QSize(32,32))
		for action in (ui.actionDisplayBaseCells,ui.actionDisplayWalls,ui.actionDisplayPumps) :
			ui.displayActionGroup.addAction(action)
			ui.display_toolbar.addAction(action)
		#tools
		ui.selectCellTool=SelectCellTool(root,main_window)
  		ui.selectWallTool=SelectWallTool(root,main_window)
		ui.selectSinkTool=SelectSinkTool(root,main_window)
		ui.riseAIADegrTool=RiseAIADegrTool(root,main_window)
		ui.lowerAIADegrTool=LowerAIADegrTool(root,main_window)
		ui.selectSourceTool=SelectSourceTool(root,main_window)
		ui.riseAIAProdTool=RiseAIAProdTool(root,main_window)
		ui.lowerAIAProdTool=LowerAIAProdTool(root,main_window)
		ui.selectNormalizeTool=SelectNormalizeTool(root,main_window)
#		ui.laserCellTool=LaserCellTool(root,main_window)
#		ui.laserWallTool=LaserWallTool(root,main_window)
#		ui.auxinContentTool=AuxinContentTool(root,main_window)
#		ui.auxinFluxTool=AuxinFluxTool(root,main_window)
		ui.toolbar=QToolBar()
		ui.toolbar.setOrientation(Qt.Vertical)
		ui.toolbar.setIconSize(QSize(32,32))
		ui.toolbar.addAction(ui.selectCellTool)
		ui.toolbar.addAction(ui.selectWallTool)
		ui.toolbar.addSeparator()
		for action in (ui.selectSinkTool,ui.riseAIADegrTool,ui.lowerAIADegrTool) :
			ui.toolbar.addAction(action)
		ui.toolbar.addSeparator()
		for action in (ui.selectSourceTool,ui.riseAIAProdTool,ui.lowerAIAProdTool) :
			ui.toolbar.addAction(action)
		ui.toolbar.addSeparator()
		ui.toolbar.addAction(ui.selectNormalizeTool)
		#,ui.laserCellTool,ui.laserWallTool,ui.sepToolAction3,ui.auxinContentTool,ui.auxinFluxTool]

	def menu_items (self) :
		return (self.ui.menuRoot,)

	def toolbars (self) :
		return (self.ui.toolbar,self.ui.display_toolbar)

	##############################################################
	#
	#		specific actions
	#
	##############################################################
	def display_base_cells (self, display) :
		self.ui.actionDisplayBaseCells.setChecked(display)
		self.element().redraw()
		self.update_view()

	def display_walls (self, display) :
		self.ui.actionDisplayWalls.setChecked(display)
		self.element().redraw()
		self.update_view()

	def display_pumps (self, display) :
		self.ui.actionDisplayPumps.setChecked(display)
		self.element().redraw()
		self.update_view()

	def autoamplified_pumps (self, display) :
		self.ui.actionAutoamplifiedPumps.setChecked(display)
		self.element()._root.autoamplified_pumps = display
		self.element().redraw()
		self.update_view()


class SelectTool (MouseTool) :
	"""
	allow to select an item inside a scene
	"""
	def __init__ (self, root_view, parent, txt) :
		MouseTool.__init__(self,parent,txt)
		self._root=root_view

	def start (self, view) :
		MouseTool.start(self,view)
		view.set_select_functions(self.draw_with_names,self.post_selection)

	def stop (self, view) :
		MouseTool.stop(self,view)
		view.clear_select_functions()

	def draw_with_names (self, view) :
		pass

	def post_selection (self, view, point) :
		ind=view.selectedName()
		print ind

	def mousePressEvent (self, view, event) :
		self._moved=False

	def mouseMoveEvent (self, view, event) :
		self._moved=True

	def mouseReleaseEvent (self, view, event) :
		if self._moved :
			self._moved=False
		else :
			view.select(event.pos())
			view.update()

class SelectCellTool (SelectTool) :
	"""
	select a cell
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"select cell")
		self.setIcon(QIcon(":/images/icons/selectCell.png"))
	
	def draw_with_names (self, view) :
		self._root.select_cell_draw(view)
	
	def post_selection (self, view, point) :
		ind=view.selectedName()
		if ind==-1 :
			print None
			self.emit(SIGNAL("selected cell : "),None)
		else :
			print ind
			self.emit(SIGNAL("selected cell : "),ind)

class SelectWallTool (SelectTool) :    #deprecated
	"""
	select a wall
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"select wall")
		self.setIcon(QIcon(":/images/icons/selectWall.png"))
	
	def draw_with_names (self, view) :
		self._root.select_wall_draw(view)
	
	def post_selection (self, view, point) :
		ind=view.selectedName()
		if ind==-1 :
			print None
			self.emit(SIGNAL("selected wall : "),None)
		else :
			print ind
			self.emit(SIGNAL("selected wall : "),ind)

class SelectSinkTool (SelectTool) :
	"""
	add a new sink to the simulation
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"select sink")
		self.setIcon(QIcon(":/images/icons/selectAIASink.png"))

	def draw_with_names (self, view) :
		self._root.select_cell_draw(view)
	
	def post_selection (self, view, point) :
		cid=view.selectedName()
		if cid==-1 :
			print None
		else :
			self._root._root.fixed_concentration[cid]=0.
			self._root._root.auxin[cid]=0.
			#self._root._root.auxin_creation[cid]=0.
                        #self._root._root.auxin_degradation[cid]=0.
			self._root.redraw()
			view.update()

class SelectSourceTool (SelectTool) :
	"""
	add a new source to the simulation
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"select source")
		self.setIcon(QIcon(":/images/icons/selectAIASource.png"))

	def draw_with_names (self, view) :
		self._root.select_cell_draw(view)

	def post_selection (self, view, point) :
		cid=view.selectedName()
		if cid==-1 :
			print None
		else :
			self._root._root.fixed_concentration[cid]=1.
			self._root._root.auxin[cid]=1.
			#self._root._root.auxin_creation[cid]=0.
                        #self._root._root.auxin_degradation[cid]=0.
			self._root.redraw()
			view.update()

class RiseAIAProdTool (SelectTool) :
	"""
	rise aia production level in selected cell
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"rise AIA prod")
		self.setIcon(QIcon(":/images/icons/riseAIAProd.png"))

	def draw_with_names (self, view) :
		self._root.select_cell_draw(view)

	def post_selection (self, view, point) :
		cid=view.selectedName()
		if cid==-1 :
			print None
		else :
			self._root._root.auxin_creation[cid]+=0.1
			self._root.redraw()
			view.update()

class LowerAIAProdTool (SelectTool) :
	"""
	lower aia production level in selected cell
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"lower AIA prod")
		self.setIcon(QIcon(":/images/icons/lowerAIAProd.png"))

	def draw_with_names (self, view) :
		self._root.select_cell_draw(view)

	def post_selection (self, view, point) :
		cid=view.selectedName()
		if cid==-1 :
			print None
		else :
			self._root._root.auxin_creation[cid]=max(0, self._root._root.auxin_creation[cid]-0.1)
			self._root.redraw()
			view.update()

class RiseAIADegrTool (SelectTool) :
	"""
	rise aia production level in selected cell
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"rise AIA Degr")
		self.setIcon(QIcon(":/images/icons/riseAIADegr.png"))

	def draw_with_names (self, view) :
		self._root.select_cell_draw(view)

	def post_selection (self, view, point) :
		cid=view.selectedName()
		if cid==-1 :
			print None
		else :
			self._root._root.auxin_degradation[cid]+=0.1
			self._root.redraw()
			view.update()

class LowerAIADegrTool (SelectTool) :
	"""
	lower aia production level in selected cell
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"lower AIA Degr")
		self.setIcon(QIcon(":/images/icons/lowerAIADegr.png"))

	def draw_with_names (self, view) :
		self._root.select_cell_draw(view)

	def post_selection (self, view, point) :
		cid=view.selectedName()
		if cid==-1 :
			print None
		else :
			self._root._root.auxin_degradation[cid]=max(0, self._root._root.auxin_degradation[cid]-0.1)
			self._root.redraw()
			view.update()

class SelectNormalizeTool (SelectTool) :
	"""
	return a source or sink to normal behaviour
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"normalize")
		self.setIcon(QIcon(":/images/icons/normalize.png"))

	def draw_with_names (self, view) :
		self._root.select_cell_draw(view)

	def post_selection (self, view, point) :
		cid=view.selectedName()
		if cid==-1 :
			print None
		else :
			if (cid in self._root._root.fixed_concentration) :
				del (self._root._root.fixed_concentration[cid])
				self._root.redraw()
				view.update()
			else :
				view.update()

class LaserCellTool (SelectTool) :  #deprecated
	"""
	burn a cell - effectively shutting down all exchanges with this cell
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"Laser cell")
		self.setIcon(QIcon(":/images/icons/fishy13.png"))

	def draw_with_names (self, view) :
		self._root.select_cell_draw(view)

	def post_selection (self, view, point) :
		cid=view.selectedName()
		if cid==-1 :
			print None
		else :
			#for nid in self._root._root.tissue.neighbors(cid) :
                        #	self._root._root.eP[self._root._root.wallgraph.edge(cid,nid)]=0
                        #	self._root._root.eP[self._root._root.wallgraph.edge(nid,cid)]=0
			self._root.redraw()
			view.update()


class LaserWallTool (SelectTool) :    #deprecated
	"""
	select a wall and shutdown the corresponding pumps
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"Laser wall")
		self.setIcon(QIcon(":/images/icons/fishy12.png"))

	def draw_with_names (self, view) :
		self._root.select_wall_draw(view)

	def post_selection (self, view, point) :
		wid=view.selectedName()
		if wid==-1 :
			print None
		else :
			#r1,r2 = self._root._root.tissue.regions(1,wid)
   			#self._root._root.eP[self._root._root.wallgraph.edge(r1,r2)]=0
                        #self._root._root.eP[self._root._root.wallgraph.edge(r2,r1)]=0
			self._root.redraw()
			view.update()
			
			
class AuxinContentTool (SelectTool) :   #deprecated
	"""
	follow the auxin content in selected cell
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"auxin content")
		self.setIcon(QIcon(":/images/icons/fishy03.png"))

	def draw_with_names (self, view) :
		self._root.select_cell_draw(view)

	def post_selection (self, view, point) :
		cid=view.selectedName()
		if cid==-1 :
			print None
		else :
			#self._root._root.aux_plot[cid]=[]
			#self._root.redraw()
			view.update()


class AuxinFluxTool (SelectTool) :     #deprecated
	"""
	follow the auxin flux through the selected wall
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"auxin flux")
		self.setIcon(QIcon(":/images/icons/fishy04.png"))

	def draw_with_names (self, view) :
		self._root.select_wall_draw(view)

	def post_selection (self, view, point) :
		wid=view.selectedName()
		if wid==-1 :
			print None
		else :
			#r1,r2 = self._root._root.tissue.regions(1,wid)
			#self._root._root.flux_plot[(r1,r2)] = []
 			#self._root._root.flux_plot[(r2,r1)] = []
			#self._root.redraw()
			view.update()
