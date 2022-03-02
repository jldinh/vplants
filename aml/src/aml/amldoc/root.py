# This file has been extracted from AMAPmod documentation (refermanual 18)

# Root
"""
    Root of the branching system containing a vertex

    This function is equivalent to Ancestors(v, EdgeType='<')[-1]. 
    It thus returns the root of the branching system containing the argument. 
    This function never returns None.

    Usage
    -----
    .. python ::
        Root(v)

    Parameters
    ----------
        - v (VTX) : vertex of the active MTG

    Optional Parameters
    -------------------
        - RestrictedTo (STRING): cf. Father
        - ContainedIn (VTX): cf. Father

    Returns
    -------
        VTX

    See Also
    --------
        `MTG`, `Extremities`.

    Examples
    --------
    .. python ::
        >>> Ancestors(v) # set of ancestors of v
        [102,78,35,33,24,12]
        >>> Root(v) # root of the branching system containing v
        12
"""
