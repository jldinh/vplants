# This file has been extracted from AMAPmod documentation (refermanual 18)

# NextDate
"""
    Next date at which a vertex has been observed after a specified date

    Returns the first observation date at which the vertex has been observed 
    starting at date d and proceeding forward in time. 
    None is returned if it does not exists.

    Usage
    -----
    .. python ::
        NextDate(v, d)

    Parameters
    ----------
        - v (vtx_id) : vertex of the active MTG.
        - d (date) : departure date.

    Returns
    -------
       date 

    See Also
    --------
        `MTG`, `DateSample`, `FirstDefinedFeature`, `LastDefinedFeature`, `PreviousDate`.
"""
