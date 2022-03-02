# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Estimate
	Estimation of 'top' parameters.
  Usage
	Estimate(top, MinPosition->1, MaxPosition->5, Neighbourhood->2,
	EqualProba->True) 
	
  Arguments
	top (tops),
	
  Optional Arguments 
	MinPosition (int): lower position taken into account for the estimation of 'top' parameters.
	MaxPosition (int): upper position taken into account for the estimation of 'top' parameters.
	Neighbourhood (int): neighbourhood taken into account for the estimation of 'top' parameters.
	EqualProba (bool): growth probabilities of the parent shoot and of the offspring shoots equal or not (default value: False).
	
  Returned Object
	In case of success of the estimation procedure, an object of type top_parameters is returned, otherwise no object is returned. The returned object of type top_parameters contains both the estimated model and the data used for the estimation.	
  Background
	The aim of the model of 'tops' is to related the growth of offspring shoots to the growth of their parent shoot in the case of immediate branching. A model of 'tops' is defined by three parameters, namely the growth probability of the parent shoot, the growth probability of the offspring shoots (both in the sense of Bernoulli processes) and the growth rhythm ratio offspring shoots / parent shoot.
	
  See Also
	
	ExtractDistribution.
"""
