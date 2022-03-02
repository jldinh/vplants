# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
ComputeWhiteNoiseCorrelation
	Computation of the sample autocorrelation or cross-correlation function induced on a white noise sequence by filtering.
  Usage
	ComputeWhiteNoiseAutoCorrelation(cf, order)
	
	ComputeWhiteNoiseAutoCorrelation(cf, filter)
	ComputeWhiteNoiseAutoCorrelation(cf, frequencies)
	ComputeWhiteNoiseAutoCorrelation(cf, dist)
	
  Arguments
	cf (correlation): sample autocorrelation or cross-correlation function (in the Pearson’s sense),
	
	order (int): order of differencing,
	
	filter (array(real)): filter values on a half width i.e. from one extremity to the central value (with the constraint that filteri + filterm = 1),
	frequencies (array(int)): frequencies defining the filter,
	dist (distribution, mixture, convolution, compound): symmetric distribution whose size of the support is even defining the filter (for instance Distribution("BINOMIAL", 0, 4, 0.5)),
	
  Returned Object
	No object is returned.	
  Background
	The application of linear filters for trend removal induces an autocorrelation structure. The effect of a given linear filter on the autocorrelation structure of the residual sequence can be roughly described as follows: the number of non-zero induced autocorrelation coefficients increase with the width of the filter while their numerical magnitudes decrease.
	
  See Also
	ComputeCorrelation.
"""
