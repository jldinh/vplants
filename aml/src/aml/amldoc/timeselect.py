# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
TimeSelect
	Selection of data item of type {time interval between two observation dates, number of events occurring between these two observation dates} according to a length of the observation period criterion.
  Usage
	TimeSelect(timev, time)
	TimeSelect(timev, min_time, max_time)	
  Arguments
	timev (time_events, renewal_data),
	time (int): time interval between two observation dates,
	min_time (int): minimum time interval between two observation dates,
	max_time (int): maximum time interval between two observation dates.
	
  Returned Object
	If either time > 0 or if 0 < min_time £ max_time and if the range of lengths of the observation period defined either by time or by min_time and max_time enables to select data items of type {time interval between two observation dates, number of events}, an object of type time_events is returned, otherwise no object is returned.
	
  See Also
	
	Merge, 
	NbEventSelect, 
	TimeScaling.
"""
