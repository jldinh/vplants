# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Compound
	Construction of an object of type compound from a ‘sum’ distribution and an ‘elementary’ distribution or from an ASCII file.
  Usage
	Compound(file_name)
	
	Compound(sum_dist, dist)	
  Arguments
	sum_dist (distribution, mixture, convolution, compound): sum distribution,
	dist (distribution, mixture, convolution, compound): elementary distribution,
	
	file_name (string).
	
  Returned Object
	If the construction succeeds, an object of type compound is returned, otherwise no object is returned.	
  Background
	A compound (or stopped-sum) distribution is defined as the distribution of the sum of n independent and identically distributed random variables Xi where n is the value taken by the random variable N. The distribution of N is referred to as the sum distribution while the distribution of the Xi is referred to as the elementary distribution.
	
  See Also
	Save,
	 Estimate (distributions),
	 Simulate (distributions).
"""

