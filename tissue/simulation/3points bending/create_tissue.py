# -*- python -*-
#
#       simulation.3points bending: example of use of mass springs
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
file used to create a regular tissue
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.container import merge_wisps,clean_duplicated_borders
from openalea.celltissue import topen,Tissue,ConfigFormat
from openalea.tissueshape import merge_cells_2D

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
NBX,NBY = 30,5
vgrid = Grid( (NBX+1,NBY+1) )
cgrid = Grid( (NBX,NBY) )
mesh = t.relation(mesh_id)

#points
points = [mesh.add_wisp(0) for i in vgrid]
pos = dict( (pid,vgrid.coordinates(i)) for i,pid in enumerate(points) )

#cells
cells = [mesh.add_wisp(2) for i in cgrid]

#walls
#vertical ones
for i in xrange(NBX+1) :
	for j in xrange(NBY) :
		eid = mesh.add_wisp(1)
		pid1 = points[vgrid.index( (i,j) )]
		pid2 = points[vgrid.index( (i,j+1) )]
		mesh.link(1,eid,pid1)
		mesh.link(1,eid,pid2)
		if i<NBX :
			cid = cells[cgrid.index( (i,j) )]
			mesh.link(2,cid,eid)
		if i>0 :
			cid = cells[cgrid.index( (i-1,j) )]
			mesh.link(2,cid,eid)
#horizontal ones
for i in xrange(NBX) :
	for j in xrange(NBY+1) :
		eid = mesh.add_wisp(1)
		pid1 = points[vgrid.index( (i,j) )]
		pid2 = points[vgrid.index( (i+1,j) )]
		mesh.link(1,eid,pid1)
		mesh.link(1,eid,pid2)
		if j<NBY :
			cid = cells[cgrid.index( (i,j) )]
			mesh.link(2,cid,eid)
		if j>0 :
			cid = cells[cgrid.index( (i,j-1) )]
			mesh.link(2,cid,eid)

########################################
#
print "alternate cells"
#
########################################
for j in xrange(NBY) :
	imax = (NBX - (j%2) * (1 - NBX % 2)) / 2
	for i in xrange(imax) :
		cid1 = cells[cgrid.index( (j%2 + 2*i,j) )]
		cid2 = cells[cgrid.index( (j%2 + 2*i+1,j) )]
		#merge_cells_2D(mesh,pos,cid1,cid2)
		merge_wisps(mesh,2,cid1,cid2)

clean_duplicated_borders(mesh)
pos = dict( (pid,pos[pid]) for pid in mesh.wisps(0) )
########################################
#
print "additional info"
#
########################################
top_points = []
for i in xrange(NBX+1) :
	pid = points[vgrid.index( (i,NBY) )]
	if mesh.has_wisp(0,pid) :
		top_points.append(pid)

bottom_points = []
for i in xrange(NBX+1) :
	pid = points[vgrid.index( (i,0) )]
	if mesh.has_wisp(0,pid) :
		bottom_points.append(pid)
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
cfg.add_section("meca info")
cfg.add("top_points")
cfg.add("bottom_points")

f=topen("tissue.zip",'w')
f.write(t)
f.write(pos,"position","position of vertices")
f.write_config(cfg.config(),"config")
f.close()


