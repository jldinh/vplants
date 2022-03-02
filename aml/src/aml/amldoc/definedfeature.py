# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
FirstDefinedFeature
	Date of first observation of a vertex.
  Usage
	FirstDefinedFeature(v, fname)
	FirstDefinedFeature(v, fname, MinDate-> d1, MaxDate-> d2)
  Arguments
	v (VTX) : vertex of the active MTG.
	fname (STRING) : name of the considered attribute.
  Optional Arguments
	MinDate (DATE) : minimum date of interest.
	MaxDate (DATE) : maximum date of interest.
  Returned Object
	DATE
  Description
	Returns the date d for which the attribute fname is defined for the first time on the vertex v passed as an argument. This date must be greater than the option MinDate and/or less than the maximum MaxDate when specified. Otherwise the returned date is Undef.
  Background
	Dynamic MTGs.
  See Also
	
	MTG, 
	DateSample, 
	LastDefinedFeature, 
	PreviousDate, 
	NextDate.
"""
