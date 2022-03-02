# This file has been extracted from AMAPmod documentation (refermanual 18)

# Feature
"""
    Extracts the attributes of a vertex.

    Returns the value of the attribute `fname` of a vertex in a `MTG`. 
    If the value of an attribute is not defined in the coding file, the value None is returned.

    Usage
    -----
    .. python ::
        Feature(vid, fname)
        Feature(vid, fname, date)

    Properties
    ----------
        vid (vtx_id) : vertex of the active MTG.
        fname (str) : name of the attribute (as specified in the coding file).
        date (date) : (for a dynamic `MTG`) date at which the attribute of the vertex is considered.

    Returns
    -------
        int, str, date or float

    Details
    -------
        If for a given attribute, several values are available(corresponding to different dates), 
        the date of interest must be specified as a third attribute. 
        This date must be a valid date appearing in the coding file for a considered vertex.
        Otherwise `None` is returned.

    Background
    ----------
        MTGs and Dynamic MTGs.

    See Also
    --------	
        `MTG`, `Class`, `Index`, `Scale`.
"""
