#find closest point on the surface
#for each dangling point
for pid in dangling_pids :
	vec,u = outer_boundary.pointList.findClosest(pos[pid])
	pos[pid] = (vec[0],vec[1],vec[2])

