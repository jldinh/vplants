# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Save
	Saving of an object of the STAT module in a file.
  Usage
	Save(obj, file_name, Format->"ASCII", Detail->2)
	
	Save(histo, file_name, ViewPoint->"Data")
	Save(vec, file_name, ViewPoint->"Data", Detail->2)
	Save(timev, file_name, ViewPoint->"Data")
	Save(seq, file_name, ViewPoint->"Data", Format->"Line",
	Detail->2)
	
	Save(dist, file_name, ViewPoint->"Survival",
	Format->"SpreadSheet")
	Save(histo, file_name, ViewPoint->"Survival",
	Format->"SpreadSheet")
	
	Save(hmc, ViewPoint->"StateProfile", Sequence->1,
	Format->"SpreadSheet")
	Save(hsmc, ViewPoint->"StateProfile", Sequence->1,
	Format->"SpreadSheet")
	
  Arguments
	obj: object of the STAT module (except objects of type vector_distance),
	file_name (string),
	
	histo (histogram, mixture_data, convolution_data, compound_data),
	vec (vectors),
	timev (time_events, renewal_data),
	seq (sequences, discrete_sequences, markov_data, semi-markov_data, tops).
	
	dist (distribution, mixture, convolution, compound),
	
	hmc (hidden_markov),
	hsmc (hidden_semi-markov).
	
  Optional Arguments 
	ViewPoint (string): point of view on the object ("Data" or "Survival" or "StateProfile"). This optional argument can be set at "Data" only if the first argument is of type vectors, sequences, discrete_sequences, markov_data, semi-markov_data or tops, can be set at "Survival" only if the first argument is of type distribution, mixture, convolution, compound, histogram, mixture_data, convolution_data or compound_data and can be set at "StateProfile" only if the first argument is of type hidden_markov or hidden_semi-markov.
	Detail (int): level of detail: 1 (default value) or 2. This optional argument can only be used if the optional argument ViewPoint is not set, or if the optional argument ViewPoint is set at "Data" and if the first mandatory argument is of type vectors, sequences, discrete_sequences, markov_data, semi-markov_data or tops.
	Format (string): file format: "ASCII" (default format), "Binary" or "SpreadSheet". These file formats cannot be specified if the optional argument ViewPoint is set at "Data". The optional argument Format can only be set at "Binary" if the optional argument ViewPoint is not set.
	Format (string): format of sequences (only relevant for multivariate sequences): "Column" (the default) or "Line". This optional argument can only be used if the optional argument ViewPoint is set at "Data", and hence, if the first mandatory argument is of type sequences, discrete_sequences, markov_data, semi-markov_data or tops.
	Sequence (int): identifier of a sequence. This optional argument can only be used if the optional argument ViewPoint is set at "StateProfile", and hence, if the first mandatory argument is of type hidden_markov or hidden_semi-markov.
	
  Description
	Saving of sets of sequences or 'tops' (ViewPoint->"Data"): the format "Column" corresponds to the ASCII file syntax for objects of type sequences or tops. For a given value of the index parameter, the different variables are successively written. With the format "Line", the univariate sequence for each variable are written on consecutive lines. In the case of univariate sequences, the two formats give the same file.
	
	Saving of a (frequency) distribution and the associate hazard or survival rates (ViewPoint->"Survival"): It is assumed that the (frequency) distribution represents lifetime and the hazard or survival rates are deduced from this lifetime distribution.
	Saving of the state profile given by the smoothed probabilities  as a function of the index parameter t computed from the parameters of a hidden Markovian model for the sequence  (ViewPoint->"StateProfile").
	
  Background
	The persistence mechanism is implemented by the Save function with the optional argument Format set at "Binary" for saving and by the function Load for restoration.
	
  Returned Object
	No object returned.
  See Also
	Display, 
	Plot, 
	Compound, 
	Convolution, 
	Distribution, 
	HiddenMarkov, 
	HiddenSemiMarkov, 
	Histogram, 
	Markov, 
	Mixture, 
	Renewal, 
	SemiMarkov, 
	Sequences, 
	TimeEvents, 
	Tops, 
	TopParameters, 
	Vectors, 
	Load.
"""
