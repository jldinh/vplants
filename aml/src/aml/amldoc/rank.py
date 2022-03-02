# This file has been extracted from AMAPmod documentation (refermanual 18)

# Rank
"""
    Rank of one vertex with respect to another one.

    This function returns the number of consecutive '<'-type edges between two components, 
    at the same scale, and does not take into account the order of vertices v1 and v2. 
    The result is a non negative integer. 

    Usage
    -----
    .. python ::
        Rank(v1)
        Rank(v1, v2)

    Parameters
    ----------
        - v1 (VTX) : vertex of the active MTG
        - v2 (VTX) : vertex of the active MTG

    Returns
    -------
        `int`
        If v1 is not an ancestor of v2 (or vise versa) within the same botanical axis, 
        or if v1 and v2 are not defined at the same scale, an error value Undef id returned.

    See Also
    --------
        `MTG`, `Order`, `Height`, `EdgeType`, `AlgRank`, `AlgHeight`, `AlgOrder`.
"""
