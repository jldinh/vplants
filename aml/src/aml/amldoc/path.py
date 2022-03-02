# This file has been extracted from AMAPmod documentation (refermanual 18)

# Path
"""
    List of vertices defining the path between two vertices

    This function returns the list of vertices defining the path 
    between two vertices that are in an ancestor relationship. 
    The vertex `v1` must be an ancestor of vertex `v2`. 
    Otherwise, if both vertices are valid, then the empty array is returned 
    and if at least one vertex is undefined, None is returned.


    Note : `v1` can be equal to `v2`.

    Usage
    -----
    .. python ::
        Path(v1, v2)

    Parameters
    ----------
        - `v1` (VTX) : vertex of the active MTG
        - `v2` (VTX) : vertex of the active MTG

    Returns
    -------
        list of vtx_id

    See Also
    --------
        `MTG`, `Axis`, `Ancestors`.

    Examples
    --------
    .. python ::
        >>> v # print the value of v
        78
        >>> Ancestors(v)
        [78,45,32,10,4]
        >>> Path(10,v)
        [10,32,45,78]
        >>> Path(9,v) # 9 is not an ancestor of 78
        []
"""
