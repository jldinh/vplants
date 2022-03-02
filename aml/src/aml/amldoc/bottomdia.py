# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
BottomDiameter
	Bottom diameter of the geometric model of a vertex
  Usage
	BottomDiameter(p, v)
  Arguments
	p (PLANTFRAME) : plantframe containing the geometric representation of v.

    v (VTX) : vertex of the active MTG
  Returned Object
	REAL
  Description
	This function returns the bottom diameter of the geometric model of a vertex. Note that this diameter might note be defined in the MTG coding file since it may result from an inference process in the PlantFrame function.
  Background
	MTGs
  See Also
	
	MTG, 
	TopDiameter, 
	Length, 
	Alpha, 
	Beta.
"""
