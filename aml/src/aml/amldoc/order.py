# This file has been extracted from AMAPmod documentation (refermanual 18)

# Order
"""
    Order of a vertex in a graph.

    The order of a vertex (v2) with respect to another vertex (v1) 
    is the number of edges of either type '+' that must be crossed 
    when going from v1 to v2 in the graph. This is thus a non negative integer 
    which corresponds to the "botanical order". 
    When the function only has one argument v1, the order of v1 correspond 
    to the order of v1 with respect to the root of the branching system containing  v1.

    Usage
    -----
    .. python ::
        Order(v1)
        Order(v1, v2)

    Parameters
    ----------
        v1 (VTX) : vertex of the active MTG
        v2 (VTX) : vertex of the active MTG

    Returns
    -------
        int
    
    Note
    ----
        When the function takes two arguments, the order of the arguments is not important 
        provided that one is an ancestor of the other. 
        When the order is relevant, use function AlgOrder().

        Warning: the value returned by function Order is 0 for trunks, 1 for branches etc. 
        This might be different with some botanical conventions where 1 is the order of the 
        trunk, 2 the order of branches, etc.
    
    See Also
    --------
        `MTG`, `Rank`, `Height`, `EdgeType`, `AlgOrder`, `AlgRank`, `AlgHeight`.
"""
