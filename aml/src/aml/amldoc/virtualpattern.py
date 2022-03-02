# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
VirtualPattern
        Object containing the specification to add (virtual) components to an existing PLANTFRAME.

    Usage
    -----
        VirtualPattern("Leaf", Symbol=symb_func, WhorlSize =ws_func)
        VirtualPattern("DigitizedLeaf", Color=color_func,
        XX=xx,YY=yy,ZZ=zz,AA=aa,BB=bb,CC=cc)
        VirtualPattern("Fruit", TopDiameter=dia_func, BottomDiameter=dia_func)
        VirtualPattern("Flower", Length=len_func,
      Alpha=alpha_func,Beta=beta_func)
        

    Parameters
    ----------
        s (STRING): String defining the type of virtual pattern used (can be one of "Leaf", "DigitizedLeaf", "Fruit", "Flower"). The difference between these options is related to the way virtual elements are oriented by default in space. Leaves have a default insertion angle with respect to their bearer of 30 degrees

    Optional Parameters
    -------------------
        PatternNumber (FUNC): AML function defining the number of virtual elements that should be added to a specific component (passed as an argument).
        WhorlSize (FUNC): AML function defining the number of virtual elements that should be located at each virtual node of a specific component (passed as an argument).
        Symbol (FUNC): AML function defining the symbols of the virtual patterns associated with each plant component. This symbol can be used to attach a particular geometric model to the virtual elements borne by a specific component (passed as an argument).
        Color (FUNC): AML function defining the color of the virtual elements borne by a specific component (passed as an argument).
        TopDiameter (FUNC): AML function defining the top diameter of the virtual elements borne by a specific component (passed as an argument).
        BottomDiameter (FUNC) : AML function defining the bottom diameter of the virtual elements borne by a specific component (passed as an argument).
        Length (FUNC): AML function defining the length of the virtual elements borne by a specific component (passed as an argument).
        Alpha (FUNC): AML function defining the insertion angle of the virtual elements borne by a specific component (passed as an argument). This angle is assumed to be defined in degrees. It is relative to the principal direction of the bearing component.
        Beta (FUNC): AML function defining the azimuth of the virtual elements borne by a specific component (passed as an argument). This angle is assumed to be defined in degrees. It is relative to the principal direction of the bearing component.
        XX (FUNC): AML function defining the x-coordinate of the virtual element borne by a specific component (should be used only when only one virtual element at most is borne by each component).
        YY (FUNC): AML function defining the y-coordinate of the virtual element borne by a specific component (should be used only when only one virtual element at most is borne by each component).
        ZZ (FUNC): AML function defining the z-coordinate of the virtual element borne by a specific component (should be used only when only one virtual element at most is borne by each component).
        AA (FUNC): AML function defining the first euler angle (azimuth)of a virtual element borne by a specific component (should be used only when only one virtual element at most is borne by each component). These angles are assumed to be defined in radians.They are absolute (expressed in a global coordinate system).
        BB (FUNC): AML function defining the second euler angle (elevation) of a virtual element borne by a specific component (should be used only when only one virtual element at most is borne by each component). These angles are assumed to be defined in radians. They are absolute (expressed in a global coordinate system). Warning, to go upwards, use negative angles.
        CC (FUNC): AML function defining the third euler angle (twist) of a virtual element borne by a specific component (should be used only when only one virtual element at most is borne by each component). These angles are assumed to be defined in radians. They are absolute (expressed in a global coordinate system).

    Returns
    -------
        If the geometric reconstruction is successfully carried out, a VIRTUAL_PATTERN object is returned. Otherwise an error is returned.

    Description
    -----------
        Virtual elements are components that are not defined in the MTG which is used to build up a particular plantframe. The user for example may want to add leaves to the plant at some specific locations, and with specific geometry whereas actually no leaves were measured in the field. It is possible to add virtual elements to the plantframe argument. The user first has to build an object of type VIRTUAL_PATTERN, and then pass on this object to the Plot command with either options VirtualLeaves (if the virtual pattern was built with argument "Leaf" of "DigitizedLeaf"), VirtualFlowers (for argument "Flower"), VirtualFruits (for argument "Fruit"). The function VirtualPattern does not create directly virtual elements. It creates an object of type VirtualPattern that just contains information defining how to compute virtual elements for a new plantframe. Virtual elements are actually computed by the Plot command if an option VirtualLeaves, VirtualFlowers or VirtualFruits is defined.
        
         Controlling the number of virtual elements per component. The total number of virtual elements that must be associated with a component (vertex) of a plantframe is defined by a function that returns an integer for any valid vertex. This function is defined using option PatternNumber. Note that this function can define 0 virtual element for a vertex, which can be used to filter virtual element based on different criteria.
        
         Controlling the number of virtual elements per virtual node of a component. If more than one virtual element is defined (see option PatternNumber) virtual elements are assumed to be arranged along their bearer by whorls at regularly distant virtual nodes between the top and the bottom of the component. A total number of  elements per virtual nodes can also be defined with option WhorlSize. Therefore, the number of virtual nodes for a component is the number of virtual element divided by the number of virtual element per virtual node. For example, a component that is associated with 12 virtual leaves which are distributed per whorls of size 3, has 4 virtual nodes.
        
         Controlling the position of virtual elements. 
        
   For Leaf, Fruit and Flower, the origin of the virtual element is determined by its position on the bearing component. As explained above, this depends on the number of virtual elements on a particular component and on the whorl size. In addition, the exact origin is translated to the periphery of the bearing component.
         For DigitizedLeaf, the position of virtual elements is defined by the coordinates of their basis. This position is defined by functions defined using options XX, YY and ZZ 
        (WARNING: this convention is different from that used for normal MTG components where XX, YY and ZZ designate the coordinates of the top of the component). These options should be used when there is at most one virtual element per component (see option PatternNumber), otherwise all the virtual elements will share the same position.
        
   Controlling the orientation of virtual elements. 
                
   For Leaf, Fruit and Flower, the orientation of a virtual element can be only partially controlled. Two angles can be used to define the principal direction of the virtual element associated with a component in spherical coordinates, using options Alpha and Beta. Alpha defines the angle of the principal direction of the virtual element with the plane normal to the principal direction of the component. For Leaf and Flowers, it corresponds to the "insertion angle" of the virtual element on its bearing component (or more precisely p/2 - i, where i the insertion angle). For flowers, the principal direction is constant, vertical and and oriented towards the soil. Beta corresponds to the relative azimuth of the principal direction of the virtual element with respect to the local reference system of its bearing component. This local reference system is defined by the secondary, ternary and principal directions of the bearing component, in this order.
         For DigitizedLeaf, the orientation of a virtual element can be defined by Euler angles. Three Euler angles can express the exact orientation of the virtual element with respect to the global reference system. These angles are automatically generated by digitizing devices like Polhemus. They should be stored in feature columns AA, BB, CC of the MTG (for example on the bearing component of each virtual leaf). They can also be defined by AML functions and passed on to the VirtualPattern function using option AA, BB, CC. 
        (WARNING: the unit of these angles is the radian. This is contrary to the convention used in other primitives of AMAPmod, that consider that angles are usually defined in degrees. This will be fixed in future releases of AMAPmod).
        
          Controlling the geometry of virtual elements. Each virtual element can be associated with a symbol that represent its geometric model. Symbols are associated with geometric models using the dressing file (see DressingData and Plot). The general geometric parameter Length, TopDiameter and BottomDiameter are used to control the dimensions of the geometric model which is associated with a given component. These parameters can be defined independently for each component by using corresponding AML functions using options Length, TopDiameter, BottomDiameter.
        
         Controlling the color of virtual elements. Virtual elements are displayed by default in Green. This default color can be changed by defining a function that returns a color code for a given vertex. All the virtual elements borne by a certain component have the same color, defined by the result of the coloring function applied to this component.

    Background
    ----------
        MTGs.

    See Also
    --------
        
        Plot, 
        DressingData, 
        PlantFrame.

Examples
        >>> g=MTG("un_mtg")
            >>> dr=DressingData("dressingfile")
            >>> fr=PlantFrame(1, Scale=3)
            >>> pn(_x)=1; nb(_x)=2
            >>> l1=VirtualPattern("Leaf",WhorlSize=nb, PatternNumber=pn)
            >>> Plot(fr, VirtualLeaves=l1, DressingData=dr)
"""
