# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Length
        Length of the geometric model of a vertex

    Usage
    -----
        Length(p, v)

    Parameters
    ----------
        p (PLANTFRAME) : plantframe containing the geometric representation of v.
        v (VTX) : vertex of the active MTG

    Returns
    -------
        REAL

    Description
    -----------
        This function returns the length of the geometric model of a vertex. Note that this length might note be defined in the MTG coding file since it may result from an inference process in the PlantFrame function.

    Background
    ----------
        MTGs

    See Also
    --------
        
        MTG, 
        TopDiameter, 
        BottomDiameter, 
        Alpha, 
        Beta.
"""
