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
non mandatory file to create a tissue
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

####################################################
#
print "create tissue"
#
####################################################
from openalea.celltissue import Tissue

t=Tissue()
point = t.add_type("point")
wall = t.add_type("wall")

mesh_id = t.add_relation("mesh",(point,wall))
mesh = t.relation(mesh_id)

pos = {}
####################################################
#
print "open svg file"
#
####################################################
from openalea.svgdraw import open_svg

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
origin = elm.center()
####################################################
#
print "read points"
#
####################################################
lay = sc.get_layer("pts")
point_id = {}
for elm in lay.elements() :
	pid = mesh.add_wisp(0)
	pos[pid] = elm.center() - origin
	point_id[elm.id()] = pid
####################################################
#
print "read walls"
#
####################################################
lay = sc.get_layer("walls")
for elm in lay.elements() :
	wid = mesh.add_wisp(1)
	mesh.link(1,wid,point_id[elm.source()])
	mesh.link(1,wid,point_id[elm.target()])
####################################################
#
print "write tissue"
#
####################################################
from openalea.celltissue import topen,ConfigFormat

cfg = ConfigFormat(vars())
cfg.add_section("tissue elements")
cfg.add("point")
cfg.add("wall")
cfg.add("mesh_id")

pos = dict( (pid,tuple(v)) for pid,v in pos.iteritems() )

f=topen("tissue.zip",'w')
f.write(t)
f.write(pos,"position","position of points")
f.write_config(cfg.config(),"config")
f.close()


