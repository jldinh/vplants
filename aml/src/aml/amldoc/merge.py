# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Merge
	Merging of objects of the same 'data' type or merging of sample correlation functions.
  Usage
	Merge(histo1, histo2,...)
	
	Merge(vec1, vec2,...)
	
	Merge(timev1, timev2,...)
	
	Merge(seq1, seq2,...)
	Merge(discrete_seq1, discrete_seq2,...)
	
	Merge(top1, top2,...)
	
	Merge(correl1, correl2,...)
	
  Arguments
	histo1, histo2, ... (histogram, mixture_data, convolution_data, compound_data),
	
	vec1, vec2, ... vectors,
	
	timev1, timev2, ... (time_events, renewal_data),
	
	seq1, seq2, ... (sequences, discrete_sequences, markov_data, semi-markov_data),
	discrete_seq1, discrete_seq2, ... (discrete_sequences, markov_data, semi-markov_data),
	
	top1, top2, ... tops,
	
	correl1, correl2, ... (correlation).
	
  Returned Object
	
	 If the arguments are of type histogram, mixture_data, convolution_data, compound_data, an object of type HISTOGRAM is returned.
	 If the arguments are of type vectors and if the vectors have the same number of variables, an object of type vectors is returned, otherwise no object is returned.
	 If the arguments are of type time_events, renewal_data, an object of type time_events is returned.
	 If the arguments are of type sequences, discrete_sequences, markov_data, semi-markov_data and if the sequences have the same number of variables, an object of type sequences is returned, otherwise no object is returned.
	 If the arguments are of type discrete_sequences, markov_data, semi-markov_data and if the sequences have the same number of variables, an object of type discrete_sequences is returned, otherwise no object is returned.
	 If the arguments are of type tops, an object of type tops is returned.
	 If the arguments are of type correlation, an object of type correlation is returned.
	
  See Also
	Cluster, 
	Shift, 
	Transcode, 
	ValueSelect, 
	MergeVariable, 
	SelectIndividual, 
	SelectVariable, 
	NbEventSelect, 
	TimeScaling, 
	TimeSelect, 
	AddAbsorbingRun,
	Cumulate, 
	Difference, 
	IndexExtract, 
	LengthSelect, 
	MovingAverage, 
	RecurrenceTimeSequences, 
	RemoveRun, 
	Reverse, 
	SegmentationExtract, 
	VariableScaling, 
	RemoveApicalInternodes.
"""
