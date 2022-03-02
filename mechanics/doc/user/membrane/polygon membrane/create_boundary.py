F = 1e6 #(N) #force applied on one side

def bound (solver) :
	for pid in (0,5) :
		solver.set_force(pid,
		          solver.force(pid) + (F / 2.,0,0) )
	
	for pid in (2,3) :
		solver.set_force(pid,
		          solver.force(pid) + (- F / 2.,0,0) )

