#read outer limit
from vplants.plantgl.scenegraph import NurbsCurve

crv, = sc.get_layer("outer limit").elements()
ctrl_pts = [sc.natural_pos(*crv.scene_pos(pt) ) \
            for pt in crv.nurbs_ctrl_points()]
outer_limit = NurbsCurve.CBezier(ctrl_pts,
                                 False,
                                 200)

#find outer triangles
from openalea.vmanalysis import curve_intersect

segs = dict( (eid,tuple(pos[pid] for pid in mesh.borders(1,eid) ) ) \
             for eid in mesh.wisps(1) )

outer_triangles = set()
for eid in curve_intersect(outer_limit,segs) :
	outer_triangles.update(mesh.regions(1,eid) )

#remove outer triangles
from openalea.container import clean_orphans

for fid in outer_triangles :
	mesh.remove_wisp(2,fid)

clean_orphans(mesh)

