# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
EulerAngles
	Computes the Euler angles corresponding to the local coordinate system of a vertex with respect to the global coordinate system.
  Usage
	EulerAngles(p, v)
  Arguments
	p (PLANTFRAME) : planteframe containing the geometric representation of v 
	v (VTX) : vertex of the active MTG
  Returned Object
	ARRAY(REAL)
  Description
	
		  Computes the Euler angles corresponding to the local coordinate system defined by PDir and SDir of a vertex with respect to the global coordinate system. The result is an array of 3 reals. First real is the azimuth (rotation about z-axis), the second real is the elevation (rotation about the y axis). The third real is the twist (rotation about the x axis).
		  
		  These angles are exactly those used by the Polhemus 3D digitizer.
	
  Background
	MTGs
  See Also
	
	MTG, 
	PlanteFrame, 
	RelTopCoord,
	RelBottomCoord,
	TopBottomCoord,
	BottomCoord,
	PDir,
	SDir,
"""
