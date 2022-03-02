# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Simulate
	Generation of a random sample from a renewal process.
  Usage
	Simulate(renew, type, time_histo)
	Simulate(renew, type, size, time)
	Simulate(renew, type, size, timev)	
  Arguments
	renew (renewal),
	type (string): type of renewal process: "Ordinary" or "Equilibriun",
	time_histo (histogram, mixture_data, convolution_data, compound_data): frequency distribution of the length of the observation period,
	size (int): sample size,
	time (int): length of the observation period,
	timev (time_events, renewal_data),
	
  Returned Object
	If 0 < (sample size) £ 1000000, if (minimum length of the observation period) ³ 2 and if (maximum length of the observation period) £ 1000, an object of type renewal_data is returned, otherwise no object is returned. The returned object contains both the simulated sample (not only count data but also time sequences) and the model used for simulation.
  Description
	If the fourth argument is of type time_events or renewal_data, the simulated sample has the same distribution of length of the observation period than the original sample given by this fourth argument. This simulation mode is particularly useful to study the effects of length biasing.
	
  See Also
	
	Renewal,
	ExtractHistogram.
"""
