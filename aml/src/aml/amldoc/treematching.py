# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
TreeMatching
	Comparison of rooted tree graphs (representing branching systems)
  Usage
	TreeMatching(va)
	TreeMatching(va, LocalDist-> by_topology)
	TreeMatching(va, LocalDist-> by_components)
	TreeMatching(va, LocalDist-> by_weight,
	 FuncList-> fl,VectorDistance->vec)
	TreeMatching(va, FuncList-> fl,VectorDistance->vec)
  Arguments
	va (ARRAY(VTX)) : Array of vertices at a same scale defining a set of branching system.
  Optional Arguments
	LocalDist (STRING) : type of local distance used during the matching algorithm.
		
	by_weights : weighted local distance
	by_topology : topological local distance
	by_components : algorithm preserving a minimum number of connected components during the matching algorithm.
		
	FuncList (ARRAY(FUNC)) : function array defining vertex arguments used by the weighted local distance
	VectorDistance(VECTOR_DISTANCE) : Argument used in order to define the weights, the argument type (numeric or symbolic) and the type of norm (absolute value or quadratic), used by the weighted local distance.
  Returned Object
	TREEMATCHING
  Description
	Returns a distance between two rooted tree graphs and a optimal valid matching.
	The user has first to define a local distance between elementary entities. This distance is defined using either binary symbolic or real attributes of entities. Then the comparison algorithm can be used in two different contexts: either to assess the architecture variability of a set of plants or to carry out a piece by piece comparison between two plants.
  Details
	The computational time of a comparison between two tree graphs is approximately proportional to the square of the total number of vertices in the compared branching systems.
  Background
	Method for comparing unordered rooted tree graphs [50; 14].
  See Also
	
	MTG, 
	Plot, 
	MatchingExtract.

Examples
	AML> g = MTG("un_mtg")
	AML> plants = VtxList(Scale->1)
	AML> # root extraction of plants at scale 2
	AML> AML> roots = Foreach _p In plants:Components(_p,Scale->2)
	AML> # Topological matching between plants
	AML> topo_match = TreeMatching(roots)
	AML> # Array of functions
	AML> funs = [Order,Class]
	<ARRAY(FUNCTION)>
	AML> # Vector Distance which defines 2 attributes (numeric and 
	AML> # symbolic) with same weights .5
	AML>  v = VectorDistance(.5,"NUMERIC",.5,"SYMBOLIC")
	AML> # Weighted matching between plant 1 and 2
	AML> weighted_match = TreeMatching([roots@1,roots@2],\
	AML> FuncList->funs,VectorDistance->v)
"""
