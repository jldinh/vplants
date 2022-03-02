# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Histogram
	Construction of a frequency distribution from an object of type array(int) or from an ASCII file.
  Usage
	Histogram(array)
	
	Histogram(file_name)	
  Arguments
	array (array(int)),
	
	file_name (string).
	
  Returned Object
	If the construction succeeds, an object of type HISTOGRAM is returned, otherwise no object is returned.
  Description
	In the file syntax, the frequencies fi for each possible value i are given in two columns. In the case of an argument of type (array(int)), it is simply assumed that each array element represents one data item.
	
  See Also
	Save, 
	Cluster, 
	Merge, 
	Shift, 
	Transcode, 
	ValueSelect, 
	Compare (distributions), 
	Estimate (distributions).
"""
