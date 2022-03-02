# This file has been extracted from AMAPmod documentation (refermanual 18)

# Father 
"""
    Topological father of a given vertex.
    
    Returns the topological father of a given vertex. And `None` if the father does not exist.
    If the argument is not a valid vertex, `None` is returned.

  
    Usage
    -----
    -----
    .. python ::
        Father(v)
        Father(v, EdgeType='<')
        Father(v, RestrictedTo='SameComplex')
        Father(v, ContainedIn=complex_id)
        Father(v, Scale=s)

    Parameters
    ----------
        v (VTX) : vertex of the active MTG

    Optional Parameters
    -------------------
        If no optional argument is specified,  the function returns the topological father 
        of the argument (vertex that bears or precedes to the vertex passed as an argument).
        It may be usefull in some cases to consider that the function only applies to a 
        subpart of the MTG (e.g. an axis). The following options enables us to specify 
        such restrictions:
        - `EdgeType` (str) : filter on the type of edge that connect the vertex to its father.
        Values can be '<', '+', and '*'. Values '*' means both '<' and '+'. 
        Only the vertex connected with the specified type of edge will be considered.
        - `RestrictedTo` (str) : filter defining a subpart of the MTG where the father 
        must be considered. If the father is actually outside this subpart, 
        the result is `None`. Possible subparts are defined using keywords in
        ['SameComplex', 'SameAxis', 'NoRestriction']. 
        For instance, if `RestrictedTo` is set to 'SameComplex', `Father(v)` returns a
        defined vertex only if the father `f` of `v` existsin the MTG and if `v` and `f`
        have the same complex.
        - `ContainedIn` (vtx_id) : filter defining a subpart of the MTG where the father 
        must be considered. If the father is actuallyoutside this subpart, 
        the result is `None`. In this case, the subpart of the MTG is made of the vertices 
        that composed `composite_id` (at any scale).
        - `Scale` (int) : the scale of the considered father. Returns the vertex from scale `s`
        which either bears and precedes the argument. 
        The scale `s` can be lower than the argument's (corresponding to a question such as 
        << which axis bears the internode? >>) or greater 
        (e.g. << which internodes bears this annual shoot?>>).

    Returns
    -------
        vtx_id

  
    See Also
    --------
    --------
        `MTG`, `Defined`, `Sons`, `EdgeType`, `Complex`, `Components`.

"""
