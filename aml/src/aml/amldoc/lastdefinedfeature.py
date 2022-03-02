# LastDefinedFeature

"""
    Date of last observation of a given attribute of a vertex.

    Returns the date `d` for which the attribute `fname` is defined for the last time 
    on the vertex `v` passed as an argument. This date must be greater than 
    the option `MinDate` and/or less than the maximum `MaxData` when specified.
    Otherwise the returned date is None.

    Usage
    -----
    .. python ::
        FirstDefinedFeature(v, fname)
        FirstDefinedFeature(v, fname, MinDate=d1, MaxDate=d2)

    Properties
    ----------
        - v (vtx_id) : vertex of the active MTG
        - fname (str) : name of the considered property

    Optional Properties
    -------------------
        - MinDate (date) : minimum date of interest.
        - MaxData (date) : maximum date of interest.

    Returns
    -------
        date

    See Also
    --------
        `MTG`, `DateSample`, `FirstDefinedFeature`, `PreviousDate`, `NextDate`.
"""
