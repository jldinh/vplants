from numpy import zeros, concatenate
from scipy.integrate import odeint

def simple_root_reaction(graph, D, Auxin, dt, PIN, P, V, S, edges_to_wall, production, decay):
	"""Compute diffusion (permeability D)
	and transport (pump strength P) of a 
	substance along the edges of an oriented graph.
	
	V is cell volume,
	S is wall surface,
	edges_to_wall the correspondancy between edges and wall,
	alpha & beta substance synthesis and degradation rates.
	"""
	tointegrate = zeros( (len(Auxin,) ) )

	#building map of index to find back the values that will go into the integrated 1D array
	subst_map = {}
	for ind,cid in enumerate(graph.vertices() ) :
		tointegrate[ind] = Auxin[cid]
		subst_map[cid] = ind

	def deriv (y, t) :
		ret = zeros( (len(y),) )
		for eid in graph.edges() :
			surf = S[edges_to_wall[eid]]
			pin_amount = PIN[eid] * surf
			permeability = D[eid] / 10 * surf
			sid = graph.source(eid)
			tid = graph.target(eid)
			flux = ( ( y[subst_map[sid]] - y[subst_map[tid]] ) * permeability ) + ( pin_amount * P * y[subst_map[sid]] )
			ret[subst_map[sid]] += production[sid] - decay[sid]*y[subst_map[sid]] - flux
			ret[subst_map[tid]] += production[tid] - decay[tid]*y[subst_map[tid]] + flux
		return ret

	integrated = odeint(deriv,tointegrate,[0.,dt])

	for cid,ind in subst_map.iteritems() :
		Auxin[cid] = float(integrated[-1,ind])

	return None,

