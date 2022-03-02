# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
TimeScaling
	Change of the time unit of data of type {time interval between two observation dates, number of events occurring between these two observation dates}.
  Usage
	TimeScaling(timev, scaling_factor)	
  Arguments
	timev (time_events, renewal_data),
	scaling_factor (int): scaling factor.
	
  Returned Object
	If scaling_factor > 0, an object of type time_events is returned, otherwise no object is returned.
	
  See Also
	
	Merge, 
	NbEventSelect, 
	TimeSelect.
"""
