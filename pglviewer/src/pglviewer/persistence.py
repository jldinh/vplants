from PyQt4.QtGui import QColor
from PyQGLViewer import Vec,Quaternion

def save_state (viewer) :
	"""Save state of objects actually displayed
	
	:Return: a map that store a set of attributes
	         for each element in the viewer
	:Returns Type: dict of (str|dict of (str|val) )
	"""
	state = {}
	
	#mainwindow
	mw = {}
	state["mainwindow"] = mw
	mw["width"] = viewer.width()
	mw["height"] = viewer.height()
	mw["x"] = viewer.x()
	mw["y"] = viewer.y()
	
	#view3d
	v = viewer.view()
	v3d = {}
	state["view3d"] = v3d
	v3d["dim"] = v.dimension()
	v3d["cursorx"],v3d["cursory"],v3d["cursorz"] = v.cursor().position()
	v3d["cursorvisible"] = v.cursor_visibility()
	v3d["cameratype"] = int(v.camera().type() )
	v3d["camerax"],v3d["cameray"],v3d["cameraz"] = v.camera().position()
	v3d["cameraa"],v3d["camerab"],v3d["camerac"],v3d["camerad"] = v.camera().orientation()
	v3d["background"] = int(v.backgroundColor().rgb() )
	v3d["rotcenter"] = int(v.rotation_center() )
	
	#worlds
	for world in viewer.view().worlds() :
		world.save_state(state,viewer)
	
	#return
	return state

def restore_state (viewer, state) :
	"""Restore the state of the viewer
	
	Try to use informations previously
	stored in state to update the state
	of the viewer:
	 - if informations are lacking, do
	   nothing regarding this special
	   item of information
	 - if informations are not related
	   to the currently displayed elements
	   do nothing either (do not attempt
	   to open new worlds for example)
	"""
	#mainwindow
	mw = state["mainwindow"]
	w,h = mw["width"],mw["height"]
	x,y = mw["x"],mw["y"]
	viewer.setGeometry(x,y,w,h)
	
	#view3d
	v = viewer.view()
	v3d = state["view3d"]
	v.set_dimension(v3d["dim"])
	cx,cy,cz = v3d["cursorx"],v3d["cursory"],v3d["cursorz"]
	v.cursor().set_position(Vec(cx,cy,cz) )
	v.set_cursor_visibility(v3d["cursorvisible"])
	v.camera().setType(v3d["cameratype"])
	cx,cy,cz = v3d["camerax"],v3d["cameray"],v3d["cameraz"]
	v.camera().setPosition(Vec(cx,cy,cz) )
	a,b,c,d = v3d["cameraa"],v3d["camerab"],v3d["camerac"],v3d["camerad"]
	v.camera().setOrientation(Quaternion(a,b,c,d) )
	col = QColor(v3d["background"])
	v.setBackgroundColor(col)
	v.set_rotation_center(v3d["rotcenter"])
	
	#worlds
	for world in viewer.view().worlds() :
		world.restore_state(state,viewer)










