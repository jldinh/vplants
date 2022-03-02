# -*- python -*-
#
#       simulation.gene pattern: example simulation package to display a gene expression pattern
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
t=Tissue()
vertex = t.add_type("vertex")
wall = t.add_type("wall")
cell = t.add_type("cell")

mesh_id = t.add_relation("mesh",(vertex,wall,cell))

pos = {}

########################################
#
print "create grid"
#
########################################
from openalea.container import Grid
NB = 11
vgrid = Grid( (NB+1,NB+1) )
cgrid = Grid( (NB,NB) )
mesh = t.relation(mesh_id)

#points
points = [mesh.add_wisp(0) for i in vgrid]
pos = dict( (pid,vgrid.coordinates(i)) for i,pid in enumerate(points) )

#cells
cells = [mesh.add_wisp(2) for i in cgrid]

#walls
#vertical ones
for i in xrange(NB+1) :
	for j in xrange(NB) :
		eid = mesh.add_wisp(1)
		pid1 = points[vgrid.index( (i,j) )]
		pid2 = points[vgrid.index( (i,j+1) )]
		mesh.link(1,eid,pid1)
		mesh.link(1,eid,pid2)
		if i<NB :
			cid = cells[cgrid.index( (i,j) )]
			mesh.link(2,cid,eid)
		if i>0 :
			cid = cells[cgrid.index( (i-1,j) )]
			mesh.link(2,cid,eid)
#horizontal ones
for i in xrange(NB) :
	for j in xrange(NB+1) :
		eid = mesh.add_wisp(1)
		pid1 = points[vgrid.index( (i,j) )]
		pid2 = points[vgrid.index( (i+1,j) )]
		mesh.link(1,eid,pid1)
		mesh.link(1,eid,pid2)
		if j<NB :
			cid = cells[cgrid.index( (i,j) )]
			mesh.link(2,cid,eid)
		if j>0 :
			cid = cells[cgrid.index( (i,j-1) )]
			mesh.link(2,cid,eid)
########################################
#
print "write result"
#
########################################
cfg=ConfigFormat(vars())
cfg.add_section("tissue elements")
cfg.add("vertex")
cfg.add("wall")
cfg.add("cell")
cfg.add("mesh_id")

f=topen("tissue.zip",'w')
f.write(t)
f.write(pos,"position","position of vertices")
f.write_config(cfg.config(),"config")
f.close()


