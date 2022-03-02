from numpy import zeros, concatenate
from scipy.integrate import odeint

def correct_root_reaction(graph, edges_to_wall, Auxin, production, decay, PIN, AUX1, S, V, dt):
	"""Compute diffusion (permeability D)
	and transport (both from PIN and AUX1)
	of a substance (auxin) along the edges of an oriented graph
	coupled with an explicite auxin-perception gene network.

	V is cell volume in square pixel,
	S is wall surface in pixel,
	edges_to_wall the correspondancy between edges and wall,
	production/decay are auxin metabolic rates
	"""

       	# Parameters in the reaction/diffusion/transport equations.

	A1=0.24  # A1, A2, A3, B1, B2, B3 are dimensionless
	A2=3.57
	A3=0.034
	B1=0.008
	B2=0.045
	B3=4.68

	# The permeability coefficients - the permeabilities due to active transport are not well characterised, but these are the values Eric Kramer uses.

	speedup_factor = 10000000.  # TO REMOVE ONCE THE VOLUMES AND SURFACES ARE IN CORRECT UNITS
	PIAAH= 5.6*10**(-7) * speedup_factor # Diffusion coefficient of IAAH
	PAUX1= 5.6*10**(-7) * speedup_factor # Permeability of anionic auxin due to active influx carriers, for an AUX1 concentration equal to 1.
	PPIN= 3.3*10**(-6)  * speedup_factor # Permeability of anionic auxin due to active efflux carriers, for a PIN concentration equal to 1.

	substAuxin = zeros( len(Auxin) )
	substPIN = zeros( len(PIN) )
	substAUX1 = zeros( len(AUX1) )

	# Building maps of indices to find back the values that will go into the integrated 1D array
	Auxin_map = {}
	PIN_map = {}
	AUX1_map = {}

	for ind,cid in enumerate(graph.vertices()) :
		substAuxin[ind] = Auxin[cid]
		Auxin_map[cid] = ind

	for ind,eid in enumerate(graph.edges()):
		substPIN[ind]=PIN[eid]
		PIN_map[eid]=len(Auxin)++ind

		substAUX1[ind]=AUX1[eid]
		AUX1_map[eid]=len(Auxin)+len(PIN)+ind

	to_integrate = concatenate((substAuxin,substPIN,substAUX1))


	# Map wall to edges
	wall_decomposition = {}
	for eid in edges_to_wall :
		if edges_to_wall[eid] not in wall_decomposition:
			wall_decomposition[edges_to_wall[eid]] = [eid]
		else :
			wall_decomposition[edges_to_wall[eid]].append(eid)


	# Derivative function stating the evolution rules the diffusion, transport, and perception gene network
	def deriv (y, t) :

		ret = zeros( (len(y),) )

		for wid,(eid1,eid2) in wall_decomposition.iteritems() :
			cell1 = graph.source(eid1)
			cell2 = graph.target(eid1)
			index_cell1 = Auxin_map[cell1]
			index_cell2 = Auxin_map[cell2]
			Pid1=PIN_map[eid1]
			Pid2=PIN_map[eid2]
			Aid1=AUX1_map[eid1]
			Aid2=AUX1_map[eid2]
			Swall=S[wid]
			Vcell1=V[cell1]
			Vcell2=V[cell2]

			term_perm = B1*PIAAH
			term_AUX1_cell1 = B2*PAUX1*y[Aid1]
			term_PIN_cell1 = B3*PPIN*y[Pid1]
			term_AUX1_cell2 = B2*PAUX1*y[Aid2]
			term_PIN_cell2 = B3*PPIN*y[Pid2]

			wallconc=(   (term_perm + term_AUX1_cell1 + term_PIN_cell1) * y[index_cell1] \
			           + (term_perm + term_AUX1_cell2 + term_PIN_cell2) * y[index_cell2] ) \
				   / (2*A1*PIAAH + A2*PAUX1*(y[Aid1]+y[Aid2]) + A3*PPIN*(y[Pid1]+y[Pid2]) )

			ret[index_cell1] += Swall/Vcell1 * (wallconc * (A1*PIAAH + A2*PAUX1*y[Aid1] + A3*PPIN*y[Pid1]) \
			                  - (term_perm + term_AUX1_cell1 + A3*PPIN*y[Pid1])*y[index_cell1]) \
				          + production[cell1] \
				          - decay[cell1]*y[index_cell1]

			ret[index_cell2] += Swall/Vcell2 * (wallconc * (A1*PIAAH + A2*PAUX1*y[Aid2] + A3*PPIN*y[Pid2]) \
			                  - (term_perm + term_AUX1_cell2 + A3*PPIN*y[Pid2])*y[index_cell2]) \
				          + production[cell2] \
				          - decay[cell2]*y[index_cell2]

		return ret

	integrated = odeint(deriv,to_integrate,[0.,dt])

        # Find back the integrated values in the 2D array (timestep x values)
	for cid,ind in Auxin_map.iteritems() :
		Auxin[cid] = float(integrated[-1,ind])
	for eid,ind in PIN_map.iteritems() :
		PIN[eid] = float(integrated[-1,ind])
	for eid,ind in AUX1_map.iteritems() :
		AUX1[eid] = float(integrated[-1,ind])


	return None,
