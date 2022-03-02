from numpy import zeros, concatenate
from scipy.integrate import odeint

def leah_root_reaction(graph, edges_to_wall, Auxin, IAAmRNA, IAApro, AuxinIAApcomplex, AUX1, PIN, dt, production, decay, D, S, V, K):
	"""Compute diffusion (permeability D)
	and transport (both from PIN and AUX1)
	of a substance (auxin) along the edges of an oriented graph
	coupled with an explicite auxin-perception gene network.

	V is cell volume in square pixel,
	S is wall surface in pixel,
	edges_to_wall the correspondancy between edges and wall,
	production/decay are auxin metabolic rates
	"""

       	# Parameters in the gene network.
	theta=0.1
	lamb=1
	mumRNA=1
	delta=1
	la=1
	ld=1
	lm=1

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
	substIAAmRNA = zeros( len(IAAmRNA) )
	substIAApro = zeros( len(IAApro) )
	substAuxinIAApcomplex = zeros( len(AuxinIAApcomplex) )
	substPIN = zeros( len(PIN) )
	substAUX1 = zeros( len(AUX1) )

	# Building maps of indices to find back the values that will go into the integrated 1D array
	Auxin_map = {}
	IAAmRNA_map = {}
	IAApro_map = {}
	AuxinIAApcomplex_map = {}
	PIN_map = {}
	AUX1_map = {}

	for ind,cid in enumerate(graph.vertices()) :
		substAuxin[ind] = Auxin[cid]
		Auxin_map[cid] = ind

		substIAAmRNA[ind] = IAAmRNA[cid]
		IAAmRNA_map[cid] =len(Auxin)+ ind

		substIAApro[ind] = IAApro[cid]
		IAApro_map[cid] = len(Auxin)+len(IAAmRNA)+ind

		substAuxinIAApcomplex[ind] = AuxinIAApcomplex[cid]
		AuxinIAApcomplex_map[cid] = len(Auxin)+len(IAAmRNA)+len(IAApro)+ ind

	for ind,eid in enumerate(graph.edges()):
		substPIN[ind]=PIN[eid]
		PIN_map[eid]=len(Auxin)+len(IAAmRNA)+len(IAApro)+len(AuxinIAApcomplex)+ind

		substAUX1[ind]=AUX1[eid]
		AUX1_map[eid]=len(Auxin)+len(IAAmRNA)+len(IAApro)+len(AuxinIAApcomplex)+len(PIN)+ind

	to_integrate = concatenate((substAuxin,substIAAmRNA,substIAApro,substAuxinIAApcomplex,substPIN,substAUX1))


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


		for cid in graph.vertices():
			Auxinid=Auxin_map[cid]
			IAAmRNAid=IAAmRNA_map[cid]
			IAAproid=IAApro_map[cid]
			AuxIAApcomid=AuxinIAApcomplex_map[cid]

			term_decomplexation = (ld+lm) * y[AuxIAApcomid]
			term_complexation = la * y[IAAproid] * y[Auxinid]
			term_transcription = lamb * theta / (theta + y[IAAproid])
			term_degradationRNA = mumRNA * y[IAAmRNAid]
			term_traduction = delta * y[IAAmRNAid]

			ret[Auxinid]+= term_decomplexation - term_complexation
			ret[IAAmRNAid]+= term_transcription - term_degradationRNA
			ret[IAAproid]+= term_traduction + ld*y[AuxIAApcomid] - term_complexation
			ret[AuxIAApcomid]+= term_complexation - term_decomplexation
		return ret

	integrated = odeint(deriv,to_integrate,[0.,dt])

        # Find back the integrated values in the 2D array (timestep x values)
	for cid,ind in Auxin_map.iteritems() :
		Auxin[cid] = float(integrated[-1,ind])
	for cid,ind in IAAmRNA_map.iteritems() :
		IAAmRNA[cid] = float(integrated[-1,ind])
	for cid,ind in IAApro_map.iteritems() :
		IAApro[cid] = float(integrated[-1,ind])
	for cid,ind in AuxinIAApcomplex_map.iteritems() :
		AuxinIAApcomplex[cid] = float(integrated[-1,ind])

	for eid,ind in PIN_map.iteritems() :
		PIN[eid] = float(integrated[-1,ind])
	for eid,ind in AUX1_map.iteritems() :
		AUX1[eid] = float(integrated[-1,ind])


	return None,
