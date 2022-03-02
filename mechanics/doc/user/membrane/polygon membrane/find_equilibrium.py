from openalea.mechanics import ForwardMarching3D

Fthreshold = 1e-6 #(N) #minimal force below which a point
                       #is considered as not moving

dt_hint = 0.1 #(s) #step size suggestion to help the algorithm

algo = ForwardMarching3D(dict( (pid,1.) for pid in mesh.wisps(0) ),
                         [spring],
                         bound)

for pid,vec in pos.iteritems() :
	algo.set_position(pid,vec)

algo.deform_to_equilibrium(dt_hint,Fthreshold)

for pid in pos :
	pos[pid] = algo.position(pid)
