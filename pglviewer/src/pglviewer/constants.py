import OpenGL.GL as ogl

class ROTATION_ANCHOR (object) :
	"""Enumeration of different anchors for rotation
	"""
	CURSOR = 0 #around the actual position of the 3D cursor
	WORLD = 1  #around the center of the current displayed world
	SPACE = 2  #around the origin of space


class VIEW (object) :
	"""Enumeration of different types of view
	"""
	SPACE = 0  #3D view
	RIGHT = 1
	LEFT = 2
	FRONT = 3
	BACK = 4
	TOP = 5
	BOTTOM = 6

class DRAW_MODE (object) :
	"""Enumeration of possible drawing modes
	"""
	NORMAL = 0 #used to display an object
	SELECT = 1 #used to select something inside the world
	DRAFT = 2  #used to fast display the world

class FACE (object) :
	"""Enumeration of type of faces
	"""
	FRONT = ogl.GL_FRONT
	BACK = ogl.GL_BACK

