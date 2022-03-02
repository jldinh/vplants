# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
VariableScaling
	Change of the unit of a variable.
  Usage
	VariableScaling(seq1, scaling_factor)
	VariableScaling(seqn, variable, scaling_factor)	
  Arguments
	seq1 (sequences, discrete_sequences, markov_data, semi-markov_data): univariate sequences,
	seqn (sequences, discrete_sequences, markov_data, semi-markov_data): multivariate sequences.
	variable (int): variable index,
	scaling_factor (int): scaling factor.
	
  Returned Object
	If scaling_factor > 0, an object of type sequences is returned, otherwise no object is returned.	
  Background
	The function VariableScaling is mainly useful as a preprocessing when one wants to study the correlation structure of residual sequences. This function enables by an appropriate scaling to control the rounding of the residual sequences and hence to obtain exact sample correlation functions.
	
  See Also
	
	AddAbsorbingRun,
	Cluster, 
	Cumulate, 
	Difference, 
	IndexExtract, 
	LengthSelect, 
	Merge, 
	MergeVariable, 
	MovingAverage, 
	RecurrenceTimeSequences, 
	RemoveRun, 
	Reverse, 
	SegmentationExtract,
	SelectIndividual, 
	SelectVariable, 
	Shift, 
	Transcode, 
	ValueSelect.
"""
