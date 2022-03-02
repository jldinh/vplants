# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
SelectVariable
	Selection of variables.
  Usage
	SelectVariable(vec, variable, Mode->"Reject")
	SelectVariable(vec, variables, Mode->"Reject")
	
	SelectVariable(seq, variable, Mode->"Reject")
	SelectVariable(seq, variables, Mode->"Reject")	
  Arguments
	vec (vectors),
	
	seq (sequences, discrete_sequences, markov_data, semi-markov_data),
	
	variable (int): variable index.
	variables (array(int)): variable indices.
	
  Optional Arguments 
	Mode (string): conservation or rejection of the selected variables: "Keep" (the default) or "Reject".
	
  Returned Object
	If either variable or variables@1, ..., variables@n are valid indices of variables, an object of type vectors (respectively sequences or discrete_sequences) is returned, otherwise no object is returned. In the case of a first argument of type sequences, the returned object is of type discrete_sequences if all the variables are of type STATE, if the possible values for each variable are consecutive from 0 and if the number of possible values for each variable is <= 15.
	
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
	SelectIndividual, 
	Shift, 
	Transcode, 
	ValueSelect,
	SegmentationExtract, 
	VariableScaling.
"""
