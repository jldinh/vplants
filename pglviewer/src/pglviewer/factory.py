_view_factory = {}
_gui_factory = {}

def get_view (block) :
	return _view_factory[block]

def register_view (block, view) :
	_view_factory[block] = view

def get_gui (view) :
	return _gui_factory[view]

def register_gui (view, gui) :
	_gui_factory[view] = gui



