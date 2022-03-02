# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Display
	ASCII output of an object of the STAT module (Print: ASCII printing of an object of the STAT module. Print takes the same arguments as Display).
  Usage
	Display(obj, Detail->2)
	
	Display(vec, ViewPoint->"Data", Detail->2)
	Display(seq, ViewPoint->"Data", Format->"Line", Detail->2)
	
	Display(dist, ViewPoint->"Survival")
	Display(histo, ViewPoint->"Survival")
	
	Display(hmc, identifier, ViewPoint->"StateProfile")
	Display(hsmc, identifier, ViewPoint->"StateProfile")	
  Arguments
	obj: STAT module object,
	
	vec (vectors),
	seq (sequences, discrete_sequences, markov_data, semi-markov_data, tops),
	
	dist (distribution, mixture, convolution, compound),
	histo (histogram, mixture_data, convolution_data, compound_data),
	
	hmc (hidden_markov),
	hsmc (hidden_semi-markov),
	identifier (int): identifier of a sequence.
	
  Optional Arguments 
	ViewPoint (string): point of view on the object ("Survival" or "Data" or "StateProfile"). This optional argument can be set at "Data" only if the first argument is of type vectors, sequences, discrete_sequences, markov_data, semi-markov_data or tops, can be set at "Survival" only if the first argument is of type distribution, mixture, convolution, compound, histogram, mixture_data, convolution_data or compound_data and can be set at "StateProfile" only if the first argument is of type hidden_markov or hidden_semi-markov.
	Detail (int): level of detail: 1 (default value) or 2. This optional argument cannot be used if the optional argument ViewPoint is set at "Survival" or "StateProfile".
	Format (string): format of sequences (only relevant for multivariate sequences): "Column" (default value) or "Line". This optional argument can only be used if the optional argument ViewPoint is set at "Data", and hence, if the first argument is of type sequences, discrete_sequences, markov_data, semi-markov_data or tops.
	
  Description
	ASCII output of sets of sequences or tops (ViewPoint->"Data"): the format "Column" corresponds to the ASCII file syntax for objects of type sequences or tops. For a given value of the index parameter, the different variables are successively displayed. With the format "Line", the univariate sequence for each variable are displayed on consecutive lines. In the case of univariate sequences, the two formats give the same output.
	
	ASCII output of a (frequency) distribution and the associate hazard or survival rates (ViewPoint->"Survival"): It is assumed that the (frequency) distribution represents lifetime and the hazard or survival rates are deduced from this lifetime distribution.
	
	ASCII output of the state profile given by the smoothed probabilities  as a function of the index parameter t computed from the parameters of a hidden Markovian model for the sequence  (ViewPoint->"StateProfile").
  Returned Object
	No object returned.
  See Also
	Plot, 
	Save.
"""
