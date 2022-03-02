from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QAction,QIcon
from pglviewer.interface import ElmGUI,MouseTool
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

		main_window.connect(ui.actionDisplayAuxin,SIGNAL("toggled(bool)"),root.display_auxin)
		main_window.connect(root,SIGNAL("display auxin"),self.display_auxin)
		main_window.connect(ui.actionDisplayWalls,SIGNAL("toggled(bool)"),root.display_walls)
		main_window.connect(root,SIGNAL("display walls"),self.display_walls)
		main_window.connect(ui.actionDisplayPumps,SIGNAL("toggled(bool)"),root.display_pumps)
		main_window.connect(root,SIGNAL("display pumps"),self.display_pumps)

		#tools
		ui.selectCellTool=SelectCellTool(root,main_window)
		ui.selectWallTool=SelectWallTool(root,main_window)
		ui.sepToolAction=QAction(main_window)
		ui.sepToolAction.setSeparator(True)
		ui.selectSinkTool=SelectSinkTool(root,main_window)
		ui.selectSourceTool=SelectSourceTool(root,main_window)
		ui.sepToolAction2=QAction(main_window)
		ui.sepToolAction2.setSeparator(True)
		ui.laserCellTool=LaserCellTool(root,main_window)
		ui.laserWallTool=LaserWallTool(root,main_window)
		ui.sepToolAction3=QAction(main_window)
		ui.sepToolAction3.setSeparator(True)
		ui.auxinContentTool=AuxinContentTool(root,main_window)
		ui.auxinFluxTool=AuxinFluxTool(root,main_window)

	def menu_items (self) :
		return (self.ui.menuRoot,)

	def setup_actionbar (self, actionbar) :
		ElmGUI.setup_actionbar(self,actionbar)
		ui=self.ui
		for action in (ui.actionDisplayAuxin,ui.actionDisplayWalls,ui.actionDisplayPumps,ui.actionAutoamplifiedPumps) :
			actionbar.addAction(action)

	def toolbar_items (self) :
		ui=self.ui
		return [ui.selectCellTool,ui.selectWallTool,ui.sepToolAction,ui.selectSinkTool,ui.selectSourceTool,ui.sepToolAction2,ui.laserCellTool,ui.laserWallTool,ui.sepToolAction3,ui.auxinContentTool,ui.auxinFluxTool]

	##############################################################
	#
	#		specific actions
	#
	##############################################################
	def display_auxin (self, display) :
		self.ui.actionDisplayAuxin.setChecked(display)
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
		self.setIcon(QIcon(":/images/icons/fishy07.png"))
	
	def draw_with_names (self, view) :
		self._root.select_cell_draw(view)
	
	def post_selection (self, view, point) :
		ind=view.selectedName()
		if ind==-1 :
			print None
		else :
			scale,cid=self._root.gt_select_cell.get_id(ind)
			print scale,cid

class SelectWallTool (SelectTool) :
	"""
	select a wall
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"select wall")
		self.setIcon(QIcon(":/images/icons/fishy08.png"))
	
	def draw_with_names (self, view) :
		self._root.select_wall_draw(view)
	
	def post_selection (self, view, point) :
		ind=view.selectedName()
		if ind==-1 :
			print None
		else :
			scale,cid=self._root.gt_select_wall.get_id(ind)
			print scale,cid

class SelectSinkTool (SelectTool) :
	"""
	add a new sink to the simulation
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"select sink")
		self.setIcon(QIcon(":/images/icons/fishy11.png"))
	
	def draw_with_names (self, view) :
		self._root.select_cell_draw(view)
	
	def post_selection (self, view, point) :
		ind=view.selectedName()
		if ind==-1 :
			print None
		else :
			scale,cid=self._root.gt_select_cell.get_id(ind)
			assert scale==0
			self._root._root.fixed_conc[cid]=0.
			self._root._root.auxin[cid]=0.
			self._root.redraw()
			view.update()

class SelectSourceTool (SelectTool) :
	"""
	add a new source to the simulation
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"select source")
		self.setIcon(QIcon(":/images/icons/fishy09.png"))

	def draw_with_names (self, view) :
		self._root.select_cell_draw(view)

	def post_selection (self, view, point) :
		ind=view.selectedName()
		if ind==-1 :
			print None
		else :
			scale,cid=self._root.gt_select_cell.get_id(ind)
			assert scale==0
			self._root._root.fixed_conc[cid]=1.
			self._root._root.auxin[cid]=1.
			self._root.redraw()
			view.update()

class LaserCellTool (SelectTool) :
	"""
	burn a cell - effectively shutting down all exchanges with this cell
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"Laser cell")
		self.setIcon(QIcon(":/images/icons/fishy13.png"))

	def draw_with_names (self, view) :
		self._root.select_cell_draw(view)

	def post_selection (self, view, point) :
		ind=view.selectedName()
		if ind==-1 :
			print None
		else :
			scale,cid=self._root.gt_select_cell.get_id(ind)
			assert scale==0
			for nid in self._root._root.tissue.neighbors(0,cid) :
                            self._root._root.eP[self._root._root.wallgraph.edge(cid,nid)]=0
                            self._root._root.eP[self._root._root.wallgraph.edge(nid,cid)]=0
			self._root.redraw()
			view.update()


class LaserWallTool (SelectTool) :
	"""
	select a wall and shutdown the corresponding pumps
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"Laser wall")
		self.setIcon(QIcon(":/images/icons/fishy12.png"))

	def draw_with_names (self, view) :
		self._root.select_wall_draw(view)

	def post_selection (self, view, point) :
		ind=view.selectedName()
		if ind==-1 :
			print None
		else :
			scale,wid=self._root.gt_select_wall.get_id(ind)
			assert scale==1
			r1,r2 = self._root._root.tissue.regions(1,wid)
   			self._root._root.eP[self._root._root.wallgraph.edge(r1,r2)]=0
                        self._root._root.eP[self._root._root.wallgraph.edge(r2,r1)]=0
			self._root.redraw()
			view.update()
			
			
class AuxinContentTool (SelectTool) :
	"""
	follow the auxin content in selected cell
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"auxin content")
		self.setIcon(QIcon(":/images/icons/fishy03.png"))

	def draw_with_names (self, view) :
		self._root.select_cell_draw(view)

	def post_selection (self, view, point) :
		ind=view.selectedName()
		if ind==-1 :
			print None
		else :
			scale,cid=self._root.gt_select_cell.get_id(ind)
			assert scale==0
			self._root._root.aux_plot[cid]=[]
			self._root.redraw()
			view.update()
		

class AuxinFluxTool (SelectTool) :
	"""
	follow the auxin flux through the selected wall
	"""
	def __init__ (self, root_view, parent) :
		SelectTool.__init__(self,root_view,parent,"auxin flux")
		self.setIcon(QIcon(":/images/icons/fishy04.png"))

	def draw_with_names (self, view) :
		self._root.select_wall_draw(view)

	def post_selection (self, view, point) :
		ind=view.selectedName()
		if ind==-1 :
			print None
		else :
			scale,wid=self._root.gt_select_wall.get_id(ind)
			assert scale==1
			r1,r2 = self._root._root.tissue.regions(1,wid)
			self._root._root.flux_plot[(r1,r2)] = []
 			self._root._root.flux_plot[(r2,r1)] = []
			self._root.redraw()
			view.update()