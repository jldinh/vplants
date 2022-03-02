# -*- python -*-
#
#       growth: geometrical transformations to grow tissues
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#

__doc__="""
node definition for growth package
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from vplants.plantgl.math import Vector2,Vector3
from openalea.core import ScriptLibrary
from openalea.growth import Uniform1D,Uniform2D,Uniform3D,\
                            Radial,Linear,Unconstrained

#########################################
#
#	algo
#
#########################################
def uniform (pos, scaling, dt) :
	def func () :
		#defines algo
		if type(scaling) == float :
			algo = Uniform1D(scaling)
		elif len(scaling) == 1 :
			algo = Uniform1D(scaling[0])
		elif len(scaling) == 2 :
			algo = Uniform2D(scaling)
		elif len(scaling) == 3 :
			algo = Uniform3D(scaling)
		else :
			raise UserWarning("unrecognized dimension %s" % str(scaling) )
		
		#grow
		algo.grow(pos,dt)
	#return
	return func,

def uniform_script (inputs, outputs) :
	lib = ScriptLibrary()
	pos, scaling, dt = inputs
	pos,script = lib.name(pos,"")
	func, = outputs
	func = lib.register(func,"func")
	
	script += "def %s () :\n" % func
	#defines algo
	if type(scaling) == float :
		script += "\tfrom openalea.growth import Uniform1D\n"
		script += "\t\n"
		script += "\talgo = Uniform1D(%f)\n" % scaling
	elif len(scaling) == 1 :
		script += "\tfrom openalea.growth import Uniform1D\n"
		script += "\t\n"
		script += "\talgo = Uniform1D(%f)\n" % scaling[0]
	elif len(scaling) == 2 :
		script += "\tfrom openalea.growth import Uniform2D\n"
		script += "\t\n"
		script += "\talgo = Uniform2D(%s)\n" % str(scaling)
	elif len(scaling) == 3 :
		script += "\tfrom openalea.growth import Uniform3D\n"
		script += "\t\n"
		script += "\talgo = Uniform3D(%s)\n" % str(scaling)
	else :
		raise UserWarning("unrecognized dimension %s" % str(scaling) )
	
	#grow
	script += "\talgo.grow(%s,%f)\n\n" % (pos,dt)
	
	#return
	return script

def radial (pos, center, speed_rate, dt) :
	def func () :
		#defines algo
		algo = Radial(center,speed_rate)
		#grow
		algo.grow(pos,dt)
	#return
	return func,

def radial_script (inputs, outputs) :
	lib = ScriptLibrary()
	pos,center,speed_rate,dt = inputs
	pos,script = lib.name(pos,"")
	func, = outputs
	func = lib.register(func,"func")
	
	script += "def %s () :\n" % func
	script += "\tfrom openalea.growth import Radial\n"
	script += "\t\n"
	script += "\talgo = Radial(%s,%f)\n" % (center,speed_rate)
	script += "\talgo.grow(%s,%f)\n\n" % (pos,dt)
	
	return script

def linear (pos, displacement_func, axis, center, dt) :
	def func () :
		#defines algo
		algo = Linear(displacement_func,axis,center)
		#grow
		algo.grow(pos,dt)
	#return
	return func,

def linear_script (inputs, outputs) :
	lib = ScriptLibrary()
	pos,displacement_func,axis,center,dt = inputs
	pos,script = lib.name(pos,"")
	dfunc,script = lib.name(displacement_func,script)
	func, = outputs
	func = lib.register(func,"func")
	
	script += "def %s () :\n" % func
	script += "\tfrom openalea.growth import Linear\n"
	script += "\t\n"
	script += "\talgo = Linear(%s,%s,%s)\n" % (dfunc,axis,center)
	script += "\talgo.grow(%s,%f)\n\n" % (pos,dt)
	
	return script

def unconstrained (pos, mesh, root, growth_speed, dt) :
	def func () :
		#defines algo
		algo = Unconstrained(mesh,root,growth_speed)
		#grow
		algo.grow(pos,dt)
	#return
	return func,

def unconstrained_script (inputs, outputs) :
	lib = ScriptLibrary()
	pos,mesh,root,growth_speed,dt = inputs
	pos,script = lib.name(pos,"")
	mesh,script = lib.name(mesh,script)
	root,script = lib.name(root,script)
	growth_speed,script = lib.name(growth_speed,script)
	func, = outputs
	func = lib.register(func,"func")
	
	script += "def %s () :\n" % func
	script += "\tfrom openalea.growth import unconstrained\n"
	script += "\t\n"
	script += "\talgo = unconstrained(%s,%s,%s)\n" % (mesh,root,growth_speed)
	script += "\talgo.grow(%s,%f)\n\n" % (pos,dt)
	
	return script

#########################################
#
#	pgl
#
#########################################
def vectorize (x, y, z) :
	if z is None :
		return Vector2(x,y),
	else :
		return Vector3(x,y,z),

def vectorize_script (inputs, outputs) :
	lib = ScriptLibrary()
	x,y,z = inputs
	vec, = outputs
	vec = lib.register(vec,"vec")
	
	if z is None :
		script = "from vplants.plantgl.math import Vector2\n"
		script += "%s = Vector2(%f,%f)\n" % (vec,x,y)
	else :
		script = "from vplants.plantgl.math import Vector3\n"
		script += "%s = Vector3(%f,%f,%f)\n" % (x,y,z)
	
	return script

