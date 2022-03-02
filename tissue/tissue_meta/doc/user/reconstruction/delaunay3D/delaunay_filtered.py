from vplants.plantgl.scenegraph import TriangleSet
from openalea.vmanalysis import centroid,circum_center3D,mesh_intersect
from openalea.container import clean_remove

#read outer boundary mesh
pts,trs = load(open("surface mesh.pkl",'rb') )
outer_boundary = TriangleSet(pts,trs)

#find all circum centers
segs = {}

for cid in mesh.wisps(3) :
	tet = tuple(pos[pid] for pid in mesh.borders(3,cid,3) )
	G = centroid(mesh,pos,3,cid)
	H = circum_center3D(*tet)
	segs[cid] = (G,H)

#test intersection with surface
#for cid in mesh_intersect(outer_limit,segs) :
#	mesh.remove_wisp(3,cid)

flat_tet = load(open("flat tet.pkl",'rb') )
for cid in flat_tet :
	mesh.remove_wisp(3,cid)

clean_orphans(mesh)

#test for edges
topo_error_eids = set([None])
while len(topo_error_eids) > 0 :
	topo_error_eids.clear()
	
	surf_fids = set(fid for fid in mesh.wisps(2) \
	                if mesh.nb_regions(2,fid) == 1)
	surf_eids = set()
	for fid in surf_fids :
		surf_eids.update(mesh.borders(2,fid) )
	
	for eid in surf_eids :
		if mesh.has_wisp(1,eid) :
			loc_surf_fids = set(mesh.regions(1,eid) ) \
					        & surf_fids
			if len(loc_surf_fids) > 2 :
				topo_error_eids.add(eid)
				
				to_rem = set()
				for fid in mesh.regions(1,eid) :
					to_rem.update(mesh.regions(2,fid) )
				
				for cid in to_rem :
					clean_remove(mesh,3,cid)

