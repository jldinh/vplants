# This file has been extracted from AMAPmod documentation (refermanual 18)

# AlgOrder
"""
    Algebraic value defining the relative order of one vertex with respect to another one.

    This function is similar to function `Order(v1, v2)` : it returns the number of `+'-type edges 
    between two components, at the same scale, but takes into account the order of vertices 
    `v1` and `v2`. The result is positive if `v1` is an ancestor of `v2`, 
    and negative if `v2` is an ancestor of `v1`.

    Usage
    -----
    .. python ::
        AlgOrder(v1, v2)
    
    Parameters
    ----------
        v1 (VTX) : vertex of the active MTG
        v2 (VTX) : vertex of the active MTG

    Returns
    -------
        int
        If `v1` is not an ancestor of `v2` (or vise versa), or if `v1` and `v2` are not defined 
        at the same scale, an error value None is returned.

    See Also
    --------
        `MTG`, `Rank`, `Order`, `Height`, `EdgeType`, `AlgHeight`, `AlgRank`.
"""
