# -*- python -*-
#
#       simulation.global growth: example simulation package of global growth field
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
from openalea.celltissue import topen,Tissue,ConfigFormat

########################################
#
print "create tissue"
#
########################################
t = Tissue()
cell = t.add_type("cell")
wall = t.add_type("wall")
point = t.add_type("point")

mesh_id = t.add_relation("mesh",(point,wall,cell))
mesh = t.relation(mesh_id)

pos = {}
########################################
#
print "create hexagonal cell"
#
########################################
from math import sin,cos,pi
R = 1. #(mum) size of cell

points = []
for i in xrange(6) :
	pid = mesh.add_wisp(0)
	pos[pid] = (R*cos(2*pi*i/6),R*sin(2*pi*i/6))
	points.append(pid)

walls = []
for i in xrange(6) :
	wid = mesh.add_wisp(1)
	mesh.link(1,wid,points[i])
	mesh.link(1,wid,points[(i+1)%6])
	walls.append(wid)

cid = mesh.add_wisp(2)
for wid in walls :
	mesh.link(2,cid,wid)
########################################
#
print "write result"
#
########################################
cfg=ConfigFormat(vars())
cfg.add_section("tissue elements")
cfg.add("point")
cfg.add("wall")
cfg.add("cell")
cfg.add("mesh_id")
cfg.add_section("info")

f=topen("tissue.zip",'w')
f.write(t)
f.write(pos,"position","position of points")
f.write_config(cfg.config(),"config")
f.close()


