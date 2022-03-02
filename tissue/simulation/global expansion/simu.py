# -*- python -*-
#
#       simulation.template: example simulation package
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
This module launch the simulation
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

###################################################
#
print "read expansion field"
#
###################################################
from pickle import load
from vplants.plantgl.math import Vector4
from vplants.plantgl.scenegraph.nurbspatch_nd import NurbsPatch3D

py_ctrl_pts = load(open("expansion_field.txt",'r'))
ctrl_pts = [[[Vector4(*v) for v in l] for l in ll] for ll in py_ctrl_pts]
field = NurbsPatch3D(ctrl_pts)

###################################################
#
print "read tissue and properties"
#
###################################################
from vplants.plantgl.math import Vector3
from openalea.celltissue import topen

f = topen("tissue.zip",'r')
t,descr = f.read()
pos,descr = f.read("position")
cfg = f.read_config("config")
f.close()

pos = dict( (pid,Vector3(*tup)) for pid,tup in pos.iteritems() )
###################################################
#
print "find uv pos"
#
###################################################
from scipy.optimize import fmin
from openalea.plantgl.math import norm

def uv (patch, vec) :
	"""
	find uv coordinates of a cartesain vector
	"""
	#define error function
	def err (coords) :
		v = patch.getPointAt(coords[0],coords[1])
		return norm(v-vec)
	#hypercube to find a first rought estimate
	err_list = []
	for i in xrange(11) :
		u = i/10.
		for j in xrange(11) :
			v = j/10.
			err_list.append( (err( (u,v) ), (u,v) ) )
	err_list.sort()
	guess = err_list[0][1]
	#refinement using fmin
	res = fmin(err,guess,disp=0)
	#return vector
	return tuple(res)

uvpos = {}
patch = field.getUPatch(0.)

for pid,vec in pos.iteritems() :
	uvpos[pid] = uv(patch,vec)
###################################################
#
print "GUI"
#
###################################################
from simu_view import SimuView
from simu_gui import SimuGUI

sc = SimuView(vars())
gui = SimuGUI(sc)

###################################################
#
print "processes"
#
###################################################
def expand (time, dt) :
	patch = field.getUPatch(time)
	for pid,uv in uvpos.iteritems() :
		pos[pid] = patch.getPointAt(*uv)

def redraw (time, *args) :
	sc.redraw(time)
###################################################
#
#	simulation loop
#
###################################################
from openalea.pglviewer import QApplication,Viewer
from openalea.pglviewer.data import RangeSimu,RangeSimuGUI

simu = RangeSimu([i*0.01 for i in xrange(101)])
simu.add_process(expand,"expand")
simu.add_process(redraw,"redraw")
redraw(0.)

qapp = QApplication([])
v = Viewer(vars())
v.set_world(sc)
v.set_loop(simu)
v.add_gui(RangeSimuGUI(simu))
v.add_gui(gui)
v.show()
v.set_2D()
qapp.exec_()


