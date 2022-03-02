# This file has been extracted from AMAPmod documentation (refermanual 18)

# Height
"""
    Number of components existing between two components in a tree graph.

    The height of a vertex (`v2`) with respect to another vertex (`v1`) 
    is the number of edges (of either type '+' or '<') that must be crossed 
    when going from `v1` to `v2` in the graph.
    This is a non-negative integer. When the function has only one argument `v1`, 
    the height of `v1` correspond to the height of `v1`with respect 
    to the root of the branching system containing `v1`.

    Usage
    -----
    .. python ::
        Height(v1)
        Height(v1, v2)

    Parameters
    ----------
        - v1 (VTX) : vertex of the active MTG
        - v2 (VTX) : vertex of the active MTG

    Returns
    -------
        int

    Note
    ----
        When the function takes two arguments, the order of the arguments is not important
        provided that one is an ancestor of the other. When the order is relevant, use
        function `AlgHeight`.

    See Also
    --------
        `MTG`, `Order`, `Rank`, `EdgeType`, `AlgHeight`, `AlgHeight`, `AlgOrder`.
"""
