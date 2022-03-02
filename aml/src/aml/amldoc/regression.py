# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Regression
	Simple regression (with a single explanatory variable).
  Usage
	Regression(vec, "Linear", explanatory_variable,
	response_variable)   
	
	Regression(vec, "MovingAverage", explanatory_variable,
	response_variable, filter,   
	Algorithm->"LeastSquares")   
	Regression(vec, "MovingAverage", explanatory_variable,
	response_variable, frequencies,   
	Algorithm->"LeastSquares")   
	Regression(vec, "MovingAverage", explanatory_variable,
	response_variable, dist, Algorithm->"LeastSquares")   
	
	Regression(vec, "NearestNeighbours", explanatory_variable,
	response_variable, span, Weighting->False)   
	
  Arguments
	vec (vectors): vectors,
	explanatory_variable (int): index of the explanatory variable,
	response_variable (int): index of the response variable,
	
	filter (array(real)): filter values on the half width i.e. from one extremity to the central value (with the constraintfilter@i + filter@m = 1),
	frequencies (array(int)): frequencies defining the filter,
	dist (distribution, mixture, convolution, compound): symmetric distribution, whose size of the support is even, defining the filter (for instance Distribution("BINOMIAL",0,4,0.5)),
	
	span (real): proportion of individuals in each neighbourhood.
	
  Optional Arguments 
	Algorithm (string): type of algorithm: "Averaging" (the default) or "LeastSquares". This optional argument can only be used if the second mandatory argument specifying the regression type is "MovingAverage".
	
	Weighting (bool): weighting or not of the neighbours according to their distance to the computed point (default value: True). This optional argument can only be used if the second mandatory argument specifying the regression type is "NearestNeighbours".
	
  Returned Object
	An object of type regression is returned.
"""
