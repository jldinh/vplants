# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Convolution
	Construction of an object of type convolution from elementary distributions or from an ASCII file.
  Usage
	Convolution(dist1, dist2,...)
	Convolution(file_name)	
  Arguments
	dist1, dist2, ...(distribution, mixture, convolution, compound): elementary distributions,
	file_name (string).
	
  Returned Object
	If the construction succeeds, the returned object is of type convolution, otherwise no object is returned.	
  Background
	The distribution of the sum of independent random variables is the convolution of the distributions of these elementary random variables.
	
  See Also
	Save, 
	Estimate (distributions), 
	Simulate (distributions).
"""
