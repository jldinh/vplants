# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Activate
	Activate a MTG already loaded into memory
  Usage
	Activate(mtg)
  Arguments
	mtg (MTG) : MTG to be activated
  Returned Object
	VOID
  Description
	All the functions of the MTG module use an implicit MTG argument which is defined as the "active MTG". This function activates a MTG already loaded into memory which thus becomes the implicit argument of all functions of module MTG.
  Details
	When several MTGs are loaded into memory, only one is active at a time. By default, the active MTG is the last MTG loaded using function MTG(). However, it is possible to activate an MTG already loaded using function Activate(). The current active MTG can be identified using function Active().
  Background
	MTGs, AML language
  See Also
	
	MTG, 
	Active().
"""
