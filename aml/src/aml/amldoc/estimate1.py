# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Estimate
	Estimation of distributions.
  Usage
	Estimate(histo, "NON-PARAMETRIC")
	Estimate(histo, "NB", MinInfBound->1, InfBoundStatus->"Fixed")
	
	Estimate(histo, "MIXTURE", "B", dist,..., 
	MinInfBound->1, InfBoundStatus->"Fixed", 
	DistInfBoundStatus->"Fixed") 
	Estimate(histo, "MIXTURE", "B", "NB",..., 
	MinInfBound->1, InfBoundStatus->"Fixed", 
	DistInfBoundStatus->"Fixed", 
	NbComponent->"Estimated", Penalty->"AIC") 
	
	Estimate(histo, "CONVOLUTION", dist,
	MinInfBound->1, Parametric->False) 
	Estimate(histo, "CONVOLUTION", dist,
	InitialDistribution->initial_dist, Parametric->False) 
	
	Estimate(histo, "COMPOUND", dist, unknown,
	Parametric->False, MinInfBound->0) 
	Estimate(histo, "COMPOUND", dist, unknown,
	InitialDistribution->initial_dist, Parametric->False) 
	
  Arguments
	histo (histogram, mixture_data, convolution_data, compound_data),
	dist (distribution, mixture, convolution, compound),
	unknown (string): type of unknown distribution: "Sum" or "Elementary".
	
  Optional Arguments 
	MinInfBound (int): lower bound to the range of possible values (0 - default value - or 1). This optional argument cannot be used in conjunction with the optional argument InitialDistribution.
	InfBoundStatus (string): shifting or not of the distribution: "Free" (default value) or "Fixed". This optional argument cannot be used if the second mandatory argument giving the model type is "NON-PARAMETRIC" ("NP").
	
	DistInfBoundStatus (string): shifting or not of the subsequent components of the mixture: "Free" (default value) or "Fixed". This optional argument can only be used if the second mandatory argument giving the distribution type is "MIXTURE".
	NbComponent (string): estimation of the number of components of the mixture: "Fixed" (default value) or "Estimated". This optional argument can only be used if the second mandatory argument giving the distribution type is "MIXTURE". Le number of estimated components is comprised between 1 and a maximum number which is given by the number of specified parametric distributions in the mandatory arguments (all of these distributions are assumed to be unknown).
	Penalty (string): type of penalty function for model selection: "AIC" (Akaike Information Criterion), "AICc" (corrected Akaike Information Criterion - default value) or "BIC" (Bayesian Information Criterion). This optional argument can only be used if the second mandatory argument giving the distribution type is "MIXTURE" and if the optional argument NbComponent is set at "Estimated".
	
	Parametric (bool): reestimation of a discrete nonparametric or parametric distribution (default value: True). This optional argument can only be used if the second mandatory argument giving the distribution type is "CONVOLUTION" or "COMPOUND".
	InitialDistribution (distribution, mixture, convolution, compound): initial distribution for the EM deconvolution-type algorithm. This optional argument can only be used if the second mandatory argument giving the distribution type is "CONVOLUTION" or "COMPOUND". This optional argument cannot be used in conjunction with the optional argument MinInfBound.
	Remark: the optional arguments MinInfBound and InitialDistribution are mutually exclusive.
	
  Returned Object
	In case of success of the estimation procedure, the type of the returned object (chosen among distribution, mixture, convolution or compound) is given by the second mandatory argument. Otherwise no object is returned. The returned object of type distribution, mixture, convolution or compound contains both the estimated distribution and the data used in the estimation procedure. In the case of mixtures, convolutions, or compound (or stopped-sum) distributions, the returned object contains pseudo-data computed as a byproduct of the EM algorithm which can be extracted by the function ExtractData.
	
  See Also
	ExtractData, 
	ExtractDistribution.
"""
