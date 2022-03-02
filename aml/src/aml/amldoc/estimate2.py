# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Estimate
	Estimation of a renewal process from count data.
  Usage
	Estimate(timev, type, NbIteration->10,Parametric->True)
	Estimate(timev, type, InitialInterEvent->initial_dist,
	NbIteration->10, Parametric->True) 	
  Arguments
	timev (time_events, renewal_data),
	type (string): type or renewal process: "Ordinary" or "Equilibrium".
	
  Optional Arguments 
	
	InitialInterEvent (distribution, mixture, convolution, compound): initial inter-event distribution for the EM algorithm.
	NbIteration (int): number of iterations of the EM algorithm.
	Parametric (bool): reestimation of a discrete nonparametric or parametric distribution (default value: False).
	
  Returned Object
	In case of success of the estimation procedure, an object of type renewal is returned, otherwise no object is returned. The returned object of type renewal contains both the estimated renewal process and the count data used in the estimation procedure.
	
  See Also
	ExtractDistribution.
"""
