# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
NbEventSelect
	Selection of data item of type {time interval between two observation dates, number of events occurring between these two observation dates} according to a number of events criterion.
  Usage
	NbEventSelect(timev, min_nb_event, max_nb_event)	
  Arguments
	timev (time_events, renewal_data),
	min_nb_event (int): minimum number of events,
	max_nb_event (int): maximum number of events.
	
  Returned Object
	If 0 <= min_nb_event £ max_nb_event and if the range of number of events defined by min_nb_event and max_nb_event enables to select data items of type {time interval between two observation dates, number of events}, an object of type time_events is returned, otherwise no object is returned.
	
  See Also
	Merge, 
	TimeScaling, 
	TimeSelect.
"""
