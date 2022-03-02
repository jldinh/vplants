#find closest point on the curve
#for each dangling point
for pid in dangling_pids :
	vec,u = outer_boundary.findClosest( pos[pid] + (0,) )
	pos[pid] = (vec[0],vec[1])

