# This file has been extracted from AMAPmod documentation (refermanual 18)
"""
ExtractDistribution
	Extraction of a distribution from an object of type 'model'.
  Usage
	ExtractDistribution(mixt, mixt_type)
	ExtractDistribution(mixt, "Component", index)
	ExtractDistribution(convol, "Elementary", index)
	ExtractDistribution(convol, "Convolution")
	ExtractDistribution(compound, compound_type)
	
	ExtractDistribution(renew, renew_type)
	ExtractDistribution(renew, "NbEvent", time)
	
	ExtractDistribution(markov, markov_type, state)
	ExtractDistribution(markov, markov_type, variable, output)
	
	ExtractDistribution(top_param, position)	
  Arguments
	mixt (mixture),
	mixt_type (string): type of distribution: "Weight" or "Mixture",
	index (int): index of the elementary distribution,
	convol (convolution),
	compound (compound),
	compound_type (string): type of distribution: "Sum", "Elementary" or "Compound",
	
	renew (renewal),
	renew_type (string): type of distribution: "InterEvent", "Backward", "Forward", "LengthBias" or "Mixture",
	time (int): observation period,
	
	markov (markov, semi-markov, hidden_markov, hidden_semi-markov),
	markov_type (string): type of distribution: "Observation", "FirstOccurrence", "Recurrence", "Sojourn", "NbRun" or "NbOccurrence",
	state (int): state,
	variable (int): variable index,
	output (int): output,
	
	top_param (top_parameters),
	position (int): position.
	
  Returned Object
	If the arguments (mixt_type, index, compound_type, renew_type, time, markov_type, state, variable, output, position) defined an existing distribution, an object of type distribution is returned, otherwise no object is returned.
	
  See Also
	Plot, 
	Fit, 
	Simulate (distributions),
	Simulate (renewal process),
	Simulate (Markovian models),
	Simulate ('top' parameters).
"""
