# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Alpha
    Angle defining the angle between the principal direction of the geometric model of vertex and the z axis of the global coordinate system.

    Usage
    -----
        Alpha(p, v)

    Parameters
    ----------
        p (PLANTFRAME) : plantframe containing the geometric representation of v.

    v (VTX) : vertex of the active MTG

    Returns
    -------
        REAL

    Description
    -----------
        This function returns an angle between the principal direction of the geometric model of a vertex and the z axis of the global reference system. Note that this angle might note be defined in the MTG coding file since it may result from an inference process in the PlantFrame function.

    Background
    ----------
        MTGs

    See Also
    --------
        
        MTG, 
        TopDiameter, 
        Length, 
        BottomDiamter, 
        Beta.
"""
