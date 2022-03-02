# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
DressingData
        Data and default geometric parameters used to compute the geometric interpretation of a MTG (i.e. a PLANTFRAME)

    Usage
    -----
        DressingData(dressing_file)

    Parameters
    ----------
        dressing_file : Name of the file containing the description of the dressing data.

    Returns
    -------
        DRESSING_DATA

    Description
    -----------
        The dressing data contains the default data that are used to define the geometry of an MTG vertices (i.e. of a plant entities) and to compute their geometric parameters when inference algorithms cannot be applied. These data are basically constant values and may be redefined in the dressing file. If no dressing file is defined, default (hard-coded) values are used (see Dressing files). The dressing file .drf , if it exists in the current directory, is always used as a default dressing file.
        
        Objects of type DRESSING_DATA is used by primitive Plantframe. It may also be used by primitive Plot when VIRTUAL_PATTERNs are plotted. 
  Details
        cf. example of a dressing file given in File syntax. 
        It may be noted that a given DRESSING_DATA object can be used for different PLANTFRAMEs.

    Background
    ----------
        cf. example of a dressing file given in File syntax.

    See Also
    --------
        
        PlantFrame, 
        VirtualPattern, 
        Plot.

Examples
        >>> g=MTG("an_mtg")
        >>> d=DressingData("file")
        >>> fr3=PlantFrame( 1,Scale= 3,DressingData= d)
        >>> fr4=PlantFrame( 1,Scale= 4,DressingData= d)
        >>> Plot(fr4)
"""
