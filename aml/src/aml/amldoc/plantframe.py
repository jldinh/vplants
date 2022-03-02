# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
PlantFrame
        Constructs e geometric interpretation of a MTG.

    Usage
    -----
        PlantFrame(v, Scale= s, Translate= [-10,-10,0])
        PlantFrame(varray, VoxelDist= 100)
        PlantFrame(varray, TrunkDist= 1000)
        PlantFrame(v, Scale= s, DressingData=  dr1)
        PlantFrame(v, Scale= s, Mode=  "Sympodial", Origin= [12,13.4,-28])
  PlantFrame(v, Scale= s, XX= xcoord, YY= xcoord, ZZ= xcoord)
        PlantFrame(v, XX= xcoord, YY= xcoord, ZZ= xcoord, TopDia= diam,
  BottomDia= diam)
  PlantFrame(v, XX= xcoord, YY= xcoord, ZZ= xcoord, 
  EulerAngles= euler, AA= euler1, BB= euler2,CC= euler3)
  PlantFrame(v, Category= cat, Length= len, Alpha= alpha,
  Azimuth= azim)
        PlantFrame(v, Scale= s, LengthAlgo=  UseAxisIndexes)

    Parameters
    ----------
        v (VTX): vertex defining a branching system. If no optional argument Scale is given, a compound geometric model of v is computed based on the geometric of the components v (i.e. at scale Scale(v)+1). Finer components can be considered by defining an optional argument Scale with value greater than Scale(v), provided that components are defined in the MTG at this scale. If optional argument  Scale has value Scale(v), the branching system is defined as the set of all descendants of v (at the same scale as v), including v itself. This is a way to compute the geometric model of a part of a branching system only.
      varray (ARRAY(VTX)): vertex array defining a set of branching systems (in the same way as above)

    Optional Parameters
    -------------------
        Scale (INT): scale at which the plant geometric interpretation is computed. The geometric model is a compound geometric model made of the combination of geometric models of components from scale s. By default, the scale at which the compound geometric model is computed is Scale(v)+1.
        Translate (ARRAY(REAL)): defines a vector for translating a plant in the global coordinate system. Available only for a vertex argument (not for an array of vertices).
        Origin (ARRAY(REAL)):  (re)defines the origin (bottom coordinates) of the geometric model of the first component of a plant (at the basis of the trunk).
        VoxelDist (INT or REAL): distance between plants (defined as the distance between the voxels containing the plants) in case more than one plant is considered.
        TrunkDist (INT or REAL): distance between plants (defined as the distance between the trunks of the plants) in case more than one plant is considered. Lines of plants are aligned along the y axis. The maximum number of plants per line is controlled by variable NbPlantsPerLine which must be set in the DressingFile and which defaults to 10.
        DressingData (DRESSING_DATA): uses the information contained in an object of type DressingData which consists of default data that can be used to compute the geometry of a plant.
        Mode (STRING) : Sympodial, Standard : defines the way to build up axes for the geometric reconstruction. This is useful for sympodial plants where axes are actually apparent axes (as opposed to botanical axes) which correspond to stacks of botanical axes (or stacks of modules). In this case, the complexes of the components at scale s are used to group components into apparent axes. The geometric computation is then carried out on these apparent axes. Note that the complexes must of the components at scale s must have a LINEAR value in the field DECOMPOSITION  of the class description of an MTG (see File syntax).
        TopDiamter (FUNC): AML function defining the top diameter of a component.
        BottomDiameter (FUNC): AML function defining the bottom diameter of a component.
        Length (FUNC): AML function defining the length of a component.
        Category (FUNC): AML function defining the category of a component (see below).
        Alpha (FUNC): AML function defining the insertion angle of a component (in degrees) with respect to its father (by default) or to a vertical axis.
        XX (FUNC): AML function defining the x-coordinate of (the top of) a component.
        YY (FUNC): AML function defining the y-coordinate of (the top of) a component
        ZZ (FUNC): AML function defining the z-coordinate of (the top of) a component
        AA (FUNC): AML function defining the first Euler angle of a component.
        BB (FUNC): AML function defining the second Euler angle of a component.
        CC (FUNC): AML function defining the third Euler angle of a component.
        EulerAngles (FUNC): AML function defining by a boolean value the components whose general orientation must be defined by the Euler angles (and not by inference algorithms).
        LengthAlgo (STRING): UseIndexes, UseAxisIndexes choice of inference algorithms for the computation of component length (see below).

    Returns
    -------
        If the geometric reconstruction is successfully carried out, a PLANTFRAME object is returned. Otherwise an error is returned.

    Description
    -----------
        This function computes a geometric interpretation of a MTG or a part of a MTG. This computation may rely on available geometric data, stored as features of the MTG components. However, algorithms have been designed in order to compute and to tune a geometric interpretation for any MTG, containing any amount of geometric information (including none at all). If geometric information is missing, heuristic algorithms are used to infer the missing data (ex: the length of a branch will be set proportional to its number of components). In the case no heuristic can be applied, default data for different geometric characteristics are retrieved from dressing data (that are defined either as hard-coded default data or specified in a dressing file). The geometry of a branching system is computed axis per axis, starting from the trunk. Each axis geometry is entirely computed before the geometry of the borne branching systems is recursively computed. This ensures that all the geometric models of a branch are computed before starting the computation of the geometric models of the components of branches borne by this branch.
  Details
         Definition of the branching system(s) whose geometry is to be computed. This branching system is defined either by a vertex or an array of vertices. A vertex implicitly defines the branching system as explained above. An array of vertices (the vertices must have the same scale) defines a set of branching systems and a geometric interpretation is computed for the branching system defined by each vertex of the array. Each geometric interpretation is then arranged on a lattice that is controlled by optional arguments VoxelDist or TrunkDist. The space between these plants can also be set in the dressing file (see DressingData).
         
          Scale of the branching system. The geometric model of a branching system is a compound geometric model made of the combination of geometric models of components from scale s. The scale at which the geometric computation is carried out is by default the scale immediately greater than the scale of the vertex argument. For example, if the argument v is defined at scale 2, the geometric interpretation is computed at scale 3 (i.e. with finer components). This default behaviour can be changed by using optional argument Scale which must specify a scale greater than the scale of v. 
        
         Translating the origin of a plant. A translation of the origin of a plant can be made by using optional argument Translate. The value of this argument must be an array of 3 reals defining the coordinates of the translation. This can be used for instance to move the trunk of a plant at the origin of the coordinate system: if [x,y,z] defines the coordinates of the origin of the plant, the opional argument Translate=[-x,-y,-z] moves the origin of the plant at point [0,0,0]. This option usually applies in PlantFrames computed for single vertices. For PlantFrames computed for array of vertices corresponding to digitized plants, plants are by default located at the nodes of a regular grid (see options TrunkDist and VoxelDist and primitive DressingData). To change this default behaviour, you can use Translate=[0,0,0] which will make plant be located at their digitized position instead of "on a grid".
        
         Defining the origin of a plant. If coordinates are used in a MTG, they always correspond to the coordinates of the top of a component geometric model (or more precisely, of center of the top face of the box containing the geometric model). We assume that the origin of all components is determined as the top of the father component. This enables us to compute the bottom coordinates of all components in the plant except for those components that have no father. For such components, the coordinates of the origin must be set in feature column XX, YY and ZZ (or L1, L2, L3, for triangular systems) of a complex of this component. If coordinates exist in several complexes of this component, the origin is determined by the coordinates of the complex with the closest scale to the component. Otherwise default value [0,0,0] is taken for the origin (with emission of a warning message).
        
         Basic geometric models. Each MTG component at the specified scale is associated with a basic geometric model (i.e. defining its shape). In the current version of AMAPmod, the model is assumed to be controlled using 3 vectors and 3 scalar parameters: an origin in space (which consists of 3 coordinates), principal and secondary directions (defining the general orientation of the model in space), a length, a bottom diameter and a top diameter. The basic geometric model is assumed to be obtained from the geometric dilatation of a normalized model contained in a 1x1x1 box. To define the basic geometric model of a component, this normalized model is linearly scaled up or down using the three parameters: length, bottom diameter and top diameter, corresponding to changing the dimensions of the box.
        Due to the topological constraints, not all these parameters need to be specified in order to compute a basic geometric model. For instance, if the top coordinates of two consecutive segments of an axis are know, then the length and the primary direction of the second segment are known (assuming the basis of the second is connected to the top of the first). The function PlantFrame makes use of such information.
        
         Using geometric features from the MTG coding file. The function automatically detects certain geometric features if they appear in particular feature columns of the coding file. These feature columns have reserved names: Length, TopDiameter, BottomDiameter, Category, Alpha, L1, L2, L3, AA, BB, CC, XX, YY and ZZ.
      
                 Columns Length, BottomDiameter, TopDiameter enables us to define the geometric parameters of the basic geometric model associated with a component. 
                 Columns XX, YY, ZZ (or L1, L2, L3 in a triangular reference system) define the top coordinates of the component.
                     Columns AA, BB, CC define the orientation of the geometric model in space (both the primary direction and the second direction).
                     Column Alpha defines the insertion angle of a component (angle between its principal direction and the horizontal plane)
                     Column Category enables defines types of axes which enable us to tune the overall geometric form of the components of an axes using general shapes (Bezier curves), see DressingData.
        
         Coordinate systems. Two types of coordinates systems are available. The type of coordinate system is automatically detected.
            
                Cartesian coordinate system. A cartesian coordinate system is used if feature columns XX, YY, ZZ appear in the MTG coding file. The coordinates of each MTG component must be stored in the feature columns XX, YY, ZZ.
                
                    Coordinate system with triangular coordinates. A triangular system is made up of three points (A,B,C) which are defined by giving the three distances between each other. The distances are defined on one of the complexes of the vertex passed as an argument in the feature columns DAB, DAC et DBC of the coding file (respectively for the distances (A,B), (A,C) and (B,C)). Then, the coordinates (i.e. the distances to points A, B and C) of each MTG component must be stored respectively in the feature columns L1, L2, L3.
        
         Using AML functions to define or to override values of the geometric parameters. When the user wants to define new values for the geometric parameters of the components of a MTG or alternatively wants to override them, (s)he can define AML functions that take a vertex of the considered scale as an argument and pass these functions as optional argument to function PlantFrame. In this case, each time a feature is required by function PlantFrame for a vertex, it is computed by applying the corresponding user-defined function to the vertex at hand. If the user-defined function returns None, then the value is looked after in the corresponding feature column of the coding file. If it is None again, then inference algorithms (see below) are applied when possible and default values (from the dressing file) are used otherwise.
        
         Controlling the distance between plants. For a list of plants, the distance between individuals can be controlled using two optional arguments. VoxelDist enables the user to specify the distance between "virtual boxes" that contain the plants (one box is adjusted to one plant). This makes sure that no overlapping exists between the plant components in the 3D-space. TrunkDist can be used to regularly dispatch the plant trunks (like in a real field). Note that the value of TrunkDist cannot be 0 but can be as small as necessary (to supperpose exactly two trunks for instance).
        
         Controlling the orientation of the components in space. If no explicit control of the orientation of the plant components is defined, the function PlantFrame makes use of the topological connections between components and of the definition or their top coordinates to infer both the location of a component (i.e. its origin in 3D space) and its primary direction (axial orientation). The second direction is arbitrary.
        It is possible to override this default behaviour by explicitly specifying the 3D orientation of a component in space. This is done by defining the Euler angles of the component local coordinate system (the coordinate system of the box containing the basic geometric model of the component) with respect to the global reference system. The Euler angles can be specified in the coding file using the column features AA, BB and CC or by defining functions that can be passed as optional arguments (with options AA, BB and CC) to PlantFrame. In addition, if the user wants to actually use the Euler angles, (s)he must specify the MTG components for which the Euler angles must be used. This is done by defining a function that returns True for those components (and False for the others) and passing this function as an argument of PlantFrame using option EulerAngles.
        
         Inference algorithms. Inferences algorithms are used to find missing geometric data if any. For all types of geometric attributes (Length, TopDiameter, BottomDiameter, etc.), the first step consists of verifying whether the feature corresponding to a geometric attribute is explicitly defined (in a feature column of the coding file or by a corresponding AML function). If it is found and when it is a feature of type REAL, it is divided by a scale factor (which is one by default) and which may be modified in the dressing file. This factor may be used to automatically adapt the units of two different attributes, e.g. for diameters in mm and length in cm, length can be automatically converted to mm by setting the length scaling factor to 10. If it is not found, a default inference is applied for certain features (explained below). If this inference does not produce a defined value, then a default value is used (see DressingData).
        Inference algorithms are used for:
            
                Category: the category of a branch is defined by the category of its first vertex. If this value is not explicitly defined, the branching order is used (0 for the trunk, 1 for the branches, etc.). For a sympodial system (option MODE=Sympodial) the order is the apparent order of the axis. 
                Length: In some circumstances it is possible to infer the length of a component. Two types of MTGs are considered:
                            - MTGs without coordinates. There are no columns XX, YY, ZZ (or L1, L2, L3). For these MTGs, the length of a component is estimated using the number of its sub-components. If the length of the sub-components is explicitly defined (either by a valid Length value in the corresponding feature column or by an optional function) then these values are summed up to compute the component's length. If not, the length of the sub-components of each sub-component is recursively computed in the same way. If, at some level of decomposition, a component cannot be further decomposed, a default length for that type of component is used (see DressingData).
                        - MTGs with coordinates. 
                              
                                 If all the components of an axis have well defined top coordinates, the length of a component is computed as the distance between its top and the top of the preceding component. For the first component of an axis, the rule is slightly changed since its father component belongs to another axis. The inference algorithm looks for the smallest component (on the other axis but not necessarily at the same scale as the borne component) that bears this first component. If this component has well defined top coordinates, the length is defined as the distance between these topcoordinates and the first component top coordinates. Otherwise, the complex of this smallest bearing component is considered and its top coordinates are checked for definition. This process is recursively applied until a complex of the smallest bearing component is found with valid coordinates or until the scale of this complex corresponds to the scale of the borne component. In this case, the top coordinates of the bearing component are necessarily defined (since the bearing axis geometry has been computed at this scale before).
                                 There may be components of an axis that don't have valid coordinates. In this case, if no option is used, the length of a component is assumed to be homogeneous between two components with valid top coordinates. 
                                      This default behaviour can be changed by using option LengthAlgo. LengthAlgo=UseAxisIndexes may be used to compute the length of a component in a way relative to the increase of index with respect to its father. For example if the MTG contains a sequence: U3<U8<U14<U15 and U3 and U15 only have valid top coordinates (the distance between these coordinates is denoted by d). If option UseAxisIndexes is not used the length (len) of the different components is:
                                        len(U8) = (8-3)d/(15-3) = 5d/12
                                      len(U14) = (14-8)d/(15-3) = 6d/12
                                      len(U15) = (15-14)d/(15-3) = d/12
                                        
                                      Only the increment of index from one component to the next one is considered. If there is an index decrease in the sequence, like in U3<U8<U6<U14<U15, the decrease with respect with the previous component is not consider and is replaced by an increase with respect to index 0 (at the decreasing point). This would correspond to applying the previous strategy on the modified sequence U3<U8(<U0)<U6<U14<U15:
                                      len(U8) = (8-3)d/(5+6+8+1-3) = 5d/14
                                      len(U6) = (6-0)d/(5+6+8+1-3) = 6d/14
                                      len(U14) = (8-6)d/(5+6+8+1-3) = 2d/14
                                      len(U15) = (15-14)d/(5+6+8+1-3) = d/14
                                        
                                      With this option value (UseAxisIndexes), the starting index of an axis is considered to be 0. For example, for the sequence U25+U27<U30, the length of the born components are (assuming U30 has well defined coordinates):
                                      len(U27) = (27-0)d/(30-0) = 27d/30
                                      len(U30) = (30-27)d/(30-0) = 3d/30
                                        
                                      If one wants instead to use the index of the bearing element (at the same scale) as the starting index, one has to use the slightly different value LengthAlgo=UseIndexes. For the same sequence, the new computed length are:
                                        len(U27) = (27-25)d/(30-25) = 2d/5
                                      len(U30) = (30-27)d/(30-25) = 3d/5
                                
                        
                TopDiameterand BottomDiameter:  The diameter of components with undefined top or bottom diameter is linearly interpolated if the component is located between two components with defined diameters. At the beginning of a branch, a default diameter is assumed to be the one of the bearing component. At the end of a branch, if no component has a defined diameter, a default value is used (see DressingData).
        

    Background
    ----------
        [23]

    See Also
    --------
        
        Plot, 
        DressingData, 
        VirtualPattern.

Examples
        >>> g=MTG("an_mtg")
        >>> fr=PlantFrame( 1,Scale= 3)
        >>> Plot(fr)
        >>> cl(_x)=If Feature(_x,"DiamTop")!=None Then 2 Else 4
        >>> Plot(fr, Color= cl)
"""
