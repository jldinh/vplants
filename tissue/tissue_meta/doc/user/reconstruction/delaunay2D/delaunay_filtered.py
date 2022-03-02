from openalea.vmanalysis import centroid,circum_center2D,curve_intersect

#read outer boundary curve
crv, = sc.get_layer("outer boundary").elements()
ctrl_pts = [sc.natural_pos(*crv.scene_pos(pt) ) \
            for pt in crv.nurbs_ctrl_points()]
outer_boundary = NurbsCurve.CBezier(ctrl_pts,
                                    False,
                                    200)

#find all circum centers
segs = {}

for fid in mesh.wisps(2) :
	tr = tuple(pos[pid] for pid in mesh.borders(2,fid,2) )
	G = centroid(mesh,pos,2,fid)
	H = circum_center2D(*tr)
	segs[fid] = (G,H)

#test intersection with curve
for fid in curve_intersect(outer_limit,segs) :
	mesh.remove_wisp(2,fid)

clean_orphans(mesh)

