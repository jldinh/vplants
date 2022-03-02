# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
SDir
        Secundary direction of the geometric model of a vertex

    Usage
    -----
        SDir(p, v)

    Parameters
    ----------
        p (PLANTFRAME) : plantframe containing the geometric representation of v.
        v (VTX) : vertex of the active MTG

    Returns
    -------
        ARRAY(REAL)

    Description
    -----------
        This function returns the 3D-coordinates of the secundary direction (a direction lying in the plane perpendicular to the principal (or primary) direction) of the box containing the geometric model of a plant component in the global coordinate system. The result is an array of 3 reals. 

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
        PDir.
"""
