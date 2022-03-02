# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
RelBottomCoord
        Bottom coordinates of the geometric model of a component expressed in the global reference system translated at the origin of the plant (basis of the trunk).

    Usage
    -----
        RelBottomCoord(p, v)

    Parameters
    ----------
        p (PLANTFRAME) : plantframe containing the geometric representation of v.

    v (VTX) : vertex of the active MTG

    Returns
    -------
        ARRAY(REAL)

    Description
    -----------
        This function returns the 3D-coordinates of the bottom of the box containing the geometric model of a plant component in the translated coordinate system. The result is an array of 3 reals. 

    Background
    ----------
        MTGs

    See Also
    --------
        
        MTG, 
        PlantFrame, 
        RelTopCoord, 
        TopCoord, 
        BottomCoord, 
        PDir.
"""
