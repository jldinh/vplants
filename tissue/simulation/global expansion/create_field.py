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
file used to read a sequence of svg file and create a nurbs object
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "
from vplants.plantgl.math import Vector4
from openalea.svgdraw import open_svg

upos = [i/100. for i in xrange(101)] 
#ucoord of interpolation points
#required because nothing garanty that two drawn curves
#have the same knot list of number of ctrl points
####################################################
#
print "open svg file"
#
####################################################
f = open_svg("expansion.svg",'r')
sc = f.read()
f.close()

####################################################
#
print "read origin"
#
####################################################
lay = sc.get_layer("amers")
elm, = lay.elements()
origin = Vector4(elm.center(),0)
####################################################
#
print "read base line common to all curves"
#
####################################################
lay = sc.get_layer("base")
svg_base, = lay.elements()
base = svg_base.nurbs()

base_pts = [Vector4(base.getPointAt(u*base.lastKnot),0,1) for u in upos]
####################################################
#
print "read each curve and create patch"
#
####################################################
ctrl_pts3D = []
for i in xrange(1,6) :
	lay = sc.get_layer("stade%d" % i)
	svg_crv, = lay.elements()
	crv = svg_crv.nurbs()
	top_pts = [Vector4(crv.getPointAt(u*crv.lastKnot),0,1) for u in upos]
	nb = len(top_pts)
	ctrl_pts = [[base_pts[ind]*(i/4.) + top_pts[ind]*(1-(i/4.)) for ind in xrange(nb)] for i in xrange(5)]
	ctrl_pts3D.append(ctrl_pts)

####################################################
#
print "write"
#
####################################################
from pickle import dump
py_ctrl_pts = [[[tuple(v-origin) for v in l] for l in ll] for ll in ctrl_pts3D]

dump(py_ctrl_pts,open("expansion_field.txt",'w'))


