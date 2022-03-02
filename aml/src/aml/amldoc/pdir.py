# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
PDir
        Principal (or primary) direction of the geometric model of a vertex

    Usage
    -----
        PDir(p, v)

    Parameters
    ----------
        p (PLANTFRAME) : plantframe containing the geometric representation of v.
        v (VTX) : vertex of the active MTG

    Returns
    -------
        ARRAY(REAL)

    Description
    -----------
        This function returns the 3D-coordinates of the axial direction (principal or primary direction) of the box containing the geometric model of a plant component in the global coordinate system. The result is an array of 3 reals. 

    Background
    ----------
        MTGs

    See Also
    --------
        
        MTG, 
        PlantFrame, 
        RelTopCoord, 
        RelBottomCoord, 
        TopCoord, 
        BottomCoord,
        SDir.
"""
