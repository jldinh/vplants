# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Mixture
	Construction of a mixture of distributions from elementary distributions and associated weights or from an ASCII file.
  Usage
	Mixture(weight1, dist1, weight2, dist2,...)
	
	Mixture(file_name)	
  Arguments
	weight1, weight2, ... (real): weights of each component. These weights should sum to one (they constitute a discrete distribution).
	dist1, dist2, ... (distribution, mixture, convolution, compound): elementary distributions (or components).
	
	file_name (string).
	
  Returned Object
	If the construction succeeds, an object of type mixture is returned, otherwise no object is returned.	
  Background
	A mixture is a parametric model of classification where each elementary distribution or component represents a class with its associated weight.
	
  See Also
	Save, 
	Estimate (distributions), 
	Simulate (distributions).
"""
