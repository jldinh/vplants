# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
MovingAverage
	Extraction of trends or residuals using a symmetric smoothing filter.
  Usage
	MovingAverage(seq, filter, Variable->1, BeginEnd->True,
	Output->"Residual",
	FileName->"filtered_sequences")
	MovingAverage(seq, frequencies, Variable->1, BeginEnd->True,
	Output->"Residual",
	FileName->"filtered_sequences")
	MovingAverage(seq, dist, Variable->1, BeginEnd->True,
	Output->"Residual",
	FileName->"filtered_sequences")
	
  Arguments
	seq (sequences, discrete_sequences, markov_data, semi-markov_data)
	filter (array(real)): filter values on the half width i.e. from one extremity to the central value (with the constraintfilter@i + filter@m = 1),
	frequencies (array(int)): frequencies defining the filter,
	dist (distribution, mixture, convolution, compound): symmetric distribution, whose size of the support is even, defining the filter (for instance Distribution("BINOMIAL", 0, 4, 0.5)),
	
  Optional Arguments 
	Variable (int): variable index,
	BeginEnd (bool): begin and end of sequences filtered or suppresses (default value: False),
	Output (string): "Trend" (the default), "Residual" or "DivisionResidual",
	FileName (string): name of file of non-rounded filtered sequences.
	
  Background
	Consider a symmetric smoothing filter of half width q applied to a sequence of length t. Whenever a symmetric smoothing filter is chosen, there is likely to be an end-effect problem for t<q or t>t - q - 1. We chose to apply the following solution to the first and the last q terms of the sequences: we define Xt:=X0 for t<0 and Xt:=Xt-1 for t>t-1.
	
  Returned Object
	An object of type sequences or discrete_sequences is returned. An object of type discrete_sequences is returned if all the variables are of type STATE, if the possible values for each variable are consecutive from 0 and if the number of possible values for each variable is <= 15.
	
  See Also
	
	AddAbsorbingRun,
	Cluster, 
	Cumulate, 
	Difference, 
	IndexExtract, 
	IndexSelect, 
	Merge, 
	MergeVariable, 
	RecurrenceTimeSequences, 
	RemoveRun, 
	Reverse, 
	SegmentationExtract, 
	SelectIndividual, 
	SelectVariable, 
	Shift, 
	Transcode, 
	ValueSelect,
	VariableScaling.
"""
