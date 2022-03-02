# This file has been extracted from AMAPmod documentation (refermanual 18)

# Descendants
"""
    Set of vertices in the branching system borne by a vertex.

    This function returns the set of descendants of its argument as an array of vertices. 
    The array thus consists of all the vertices, at the same scale as `v`, 
    that belong to the branching system starting at `v`. 
    The order of the vertices in the array is not significant. 
  
    Note : The argument always belongs to the set of its descendants.

    Usage
    -----
    .. python ::
        Descendants(v)

    Parameters
    ----------
        - v (vtx_id) : vertex of the active MTG

    Optional Parameters
    -------------------
        - RestrictedTo (str): cf. `Father`
        - ContainedIn (vtx_id): cf. `Father`
        - EdgeType (str): cf. `Father`

    Returns
    -------
        list of vtx_id.

    See Also
    --------
        `MTG`, `Ancestors`.

    Examples
    --------
    .. python ::
        >>> v 
        78
        >>> Sons(v) # set of sons of v
        [78,99,101]
        >>> Descendants(v) # set of descendants of v
        [78,99,101,121,133,135,156,171,190]

"""
