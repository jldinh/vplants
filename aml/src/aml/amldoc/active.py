# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Active
	Returns the active MTG.
  Usage
	Active()
  Arguments
	None.
  Returned Object
	MTG
  Description
	This function returns the active MTG. If no MTG is loaded into memory, Undef is returned.
  Details
	When several MTGs are loaded into memory, only one is active at a time. By default, the active MTG is the last MTG loaded using function MTG(). However, it is possible to activate an MTG already loaded using function Activate(). The current active MTG can be identified using function Active().
  Background
	MTGs, AML language.
  See Also
	
	MTG, 
	Activate().
"""
