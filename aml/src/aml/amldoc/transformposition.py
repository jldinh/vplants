# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
TransformPosition
	Discretization of inter-position intervals.
  Usage
	TransformPosition(seq, step)	
  Arguments
	seq (sequences),
	step (int): step of discretization.
	
  Returned Object
	If the first variable of seq is of type POSITION, and if 0 < step <= (mean of inter-position intervals), an object of type sequences or discrete_sequences is returned, otherwise no object is returned. The returned object is of type discrete_sequences if the possible values for each variable are consecutive from 0 and if the number of possible values for each variable is <= 15.
	
  See Also
	
	AddAbsorbingRun,
	Cluster, 
	Cumulate, 
	Difference, 
	SelectIndividual, 
	IndexExtract, 
	LengthSelect, 
	Merge, 
	MergeVariable, 
	MovingAverage, 
	RecurrenceTimeSequences, 
	RemoveRun, 
	Reverse, 
	SegmentationExtract.
	SelectVariable, 
	Shift, 
	Transcode, 
	ValueSelect, 
	VariableScaling.
"""
