# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
TimeEvents
	Construction of data of type {time interval between two observation dates, number of events occurring between these two observation dates} from time sequences, from an object of type HISTOGRAM or from an ASCII file.
  Usage
	TimeEvents(seq1, begin_date, end_date, PreviousDate->3,
	NextDate->8)   
	TimeEvents(seqn, variable, begin_date, end_date,
	PreviousDate->3, NextDate->8)   
	
	TimeEvents(histo, time)
	
	TimeEvents(file_name)	
  Arguments
	seq1 (sequences): univariate time sequences (with an explicit index parameter of type TIME),
	seqn (sequences): multivariate time sequences (with an explicit index parameter of type TIME),
	variable (int): variable index,
	begin_date (int): initial observation date,
	end_date (int): final observation date,
	
	histo (histogram, mixture_data, convolution_data, compound_data): number of events frequency distribution,
	time (int): time interval between two observation dates (length of the observation period),
	
	file_name (string).
	
  Optional Arguments 
	PreviousDate (int): date preceding the initial observation date to check the increasing character of the number of events. This optional argument can only be used if the first mandatory argument is of type sequences.
	NextDate (int): date following the final observation date to check the increasing character of the number of events. This optional argument can only be used if the first mandatory argument is of type sequences.
	
  Returned Object
	If the construction succeeds, an object of type time_events is returned, otherwise no object is returned.
	
  See Also
	Save, 
	ExtractHistogram, 
	Merge, 
	NbEventSelect, 
	TimeScaling, 
	TimeSelect.
"""
