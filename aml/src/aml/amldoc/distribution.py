# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Distribution
	Construction of a parametric discrete distribution (either binomial, Poisson, negative binomial or uniform) from the name and the parameters of the distribution or from an ASCII file.
  Usage
	Distribution("BINOMIAL", inf_bound, sup_bound, proba)
	Distribution("POISSON", inf_bound, param)
	Distribution("NEGATIVE_BINOMIAL", inf_bound, param, proba)
	Distribution("UNIFORM", inf_bound, sup_bound)
	
	Distribution(file_name)	
  Arguments
	inf_bound (int): lower bound to the range of possible values (shift parameter),
	sup_bound (int): upper bound to the range of possible values (only relevant for binomial or uniform distributions),
	param (int, real): parameter of either the Poisson distribution or the negative binomial distribution.
	proba (int, real): probability of ‘success’ (only relevant for binomial or negative binomial distributions),
	Remark: the names of the parametric discrete distributions can be summarized by their first letters: 'B' ('BINOMIAL'), 'P' ('POISSON'), 'NB' ('NEGATIVE_BINOMIAL'), 'U' ('UNIFORM'),
	
	file_name (string).
	
  Returned Object
	If the construction succeeds, an object of type distribution is returned, otherwise no object is returned.
  Description
	A supplementary shift parameter (argument inf_bound) is required with respect to the usual definitions of these discrete distributions. Constraints over parameters are given in the file syntax corresponding to the type distribution (cf. File Syntax).
	
  See Also
	Save, 
	Estimate (distributions), 
	Simulate (distributions).
"""
