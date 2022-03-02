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
This module launch the simulation
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

###################################################
#
#	zone definition
#
###################################################
from openalea.genepattern import AbsSphere,AbsHalfSpace,Border

Z1 = AbsSphere("center",(4,"cell"))
Z2 = AbsHalfSpace("center","vertical")
###################################################
#
#	gene expression pattern
#
###################################################
GEN = Border(Z1) + (Z1 & Z2)
###################################################
#
#	abstract resolution
#
###################################################
d = {"center":(5.5,5.5),"vertical":(0,1)}
RGEN = GEN.resolution(d)
###################################################
#
#	read the mesh description of a tissue
#
###################################################
from vplants.plantgl.math import Vector2
from openalea.celltissue import topen

f = topen("tissue.zip",'r')
t,descr = f.read()
pos,descr = f.read("position")
cfg = f.read_config("config")
f.close()
mesh = t.relation(cfg.mesh_id)
pos = dict( (pid,Vector2(*tup)) for pid,tup in pos.iteritems() )
###################################################
#
#	projection on the mesh
#
###################################################
from openalea.genepattern import MeshProjector

projector = MeshProjector(mesh,pos,2)
PGEN = projector.project(RGEN)

###################################################
#
#	draw
#
###################################################
from simu_view import SimuView

sc = SimuView(mesh,pos,PGEN)

###################################################
#
#	display
#
###################################################
from openalea.pglviewer import QApplication,Viewer

qapp = QApplication([])
v = Viewer()
v.set_world(sc)
v.show()
v.set_2D()
qapp.exec_()


