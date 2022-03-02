from vplants.plantgl.scenegraph import Material
from vplants.plantgl.ext.color import random
from openalea.celltissue import TissueDB
from openalea.tissueshape import tovec
from openalea.tissueview import MeshView
from openalea.pglviewer import display2D

db = TissueDB()
db.read("tissue.zip")

cfg = db.get_config("config")
mesh = db.tissue().relation(cfg.mesh_id)
pos = tovec(db.get_property("position"),centered = True)


def cmap (cid) :
	return Material(random().i3tuple() )

sc = MeshView(mesh,pos,2,10,cmap)
sc.redraw()

display2D(sc)

