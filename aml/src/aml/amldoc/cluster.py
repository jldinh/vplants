# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Cluster
	Clustering of values.
  Usage
	
	Cluster(histo, "Step", step)
	Cluster(histo, "Information", information_ratio)
	Cluster(histo, "Limit", limits)
	
	Cluster(vec1, "Step", step)
	Cluster(vecn, "Step", variable, step)
	Cluster(vec1, "Limit", limits)
	Cluster(vecn, "Limit", variable, limits)
	
	Cluster(seq1, "Step", step)
	Cluster(seqn, "Step", variable, step)
	Cluster(discrete_seq1, "Step", step, AddVariable->True)
	Cluster(discrete_seqn, "Step", variable, step,
	AddVariable->True)
	Cluster(seq1, "Limit", limits)
	Cluster(seqn, "Limit", variable, limits)
	Cluster(discrete_seq1, "Limit", limits, AddVariable->True)
	Cluster(discrete_seqn, "Limit", variable, limits,
	AddVariable->True)
  
  Arguments
	histo (HISTOGRAM, MIXTURE_DATA, CONVOLUTION_DATA, COMPOUND_DATA),
	
	step (INT) : step for the clustering of values
	information_ratio (REAL) : proportion of the information measure of the original sample for determining the clustering step,
	limits (ARRAY(INT)) : first values corresponding to the new classes  classes 1, ..., nb_class - 1. By convention, the first value corresponding to the first class is 0,
	
	vec1 (VECTORS): values,
	vecn (VECTORS): vectors,
	variable (INT): variable index,
	
	seq1 (SEQUENCES): univariate sequences,,
	seqn (SEQUENCES): multivariate sequences,,
	discrete_seq1 (DISCRETE_SEQUENCES, MARKOV_DATA, SEMI-MARKOV_DATA) : discrete univariate sequences,
	discrete_seqn (DISCRETE_SEQUENCES, MARKOV_DATA, SEMI-MARKOV_DATA) : discrete multivariate sequences.
	
  Optional Arguments 
	AddVariable (BOOL) : addition (instead of simple replacement) of the variable corresponding to the clustering of values (default value: False). This optional argument can only be used if the first argument is of type DISCRETE_SEQUENCES, MARKOV_DATA or SEMI-MARKOV_DATA. The addition of the clustered variable is particularly useful if one wants to evaluate a lumpability hypothesis.
  Returned Object 
    If step > 0, or if 0 <= information_ratio <= 1, 
    or if 0 < limits[0] < limits[1] < ... < limits[nb_class - 1] < (maximum possible value of histo), 
    an object of type HISTOGRAM is returned, otherwise no object is returned.
    If variable is a valid index of a variable and if step > 0, 
    or if 0 < limits[0] < limits[1] < ... < limits[nb_class - 1] < (maximum possible value taken by the selected variable of vec1 or vecn), 
    an object of type vectors is returned, otherwise no object is returned.

    If variable is a valid index of a variable of type STATE 
    and if step > 0, or if 0 < limits[0] < limits[1] < ... < limits[nb_class - 1] 
    < (maximum possible value taken by the selected variable of seq1, seqn, discrete_seq1 or discrete_seqn), 
    an object of type sequences or discrete_sequences is returned, otherwise no object is returned. 
    In the case of a first argument of type sequences, an object of type discrete_sequences is returned 
    if all the variables are of type STATE, 
    if the possible values taken by each variable are consecutive from 0 
    and if the number of possible values for each variable is < 15.
	
Description 
	In the case of the clustering of values of a frequency distribution on the basis of an information measure criterion (argument "Information"), both the information measure ratio and the selected optimal step are given in the shell window.
Background 
	The clustering mode "Step" (and its variant "Information") is naturally adapted to numeric variables while the clustering mode "Limit" applies to both symbolic (nominal) and numeric variables. In the case of a symbolic variable, the function Cluster with the mode "Limit" can be seen as a dedicated interface of the more general function Transcode.
  See Also 
	Merge, 
	Shift, 
	Transcode, 
	ValueSelect, 
	MergeVariable, 
	SelectIndividual, 
	SelectVariable, 
	AddAbsorbingRun, 
	Cumulate, 
	Difference, 
	IndexExtract, 
	LengthSelect, 
	MovingAverage, 
	RecurrenceTimeSequences, 
	Removerun, 
	Reverse, 
	SegmentationExtract,
	VariableScaling.
"""
