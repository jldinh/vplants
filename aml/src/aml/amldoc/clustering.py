# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Clustering
  	Application of clustering methods (either partioning methods or hierarchical methods) to dissimilatirty matrices between partterns.
  Usage
	
      Clustering(dissimilarity_matrix, ''Partitioning'', nb_cluster,
	             Prototypes->[1, 3, 12])
	Clustering(dissimilarity_matrix, ''Partitioning'', clusters)
	Clustering(dissimilarity_matrix, ''Hierarchy'')
	
  Arguments
	dissimilarity_matrix (distance_matrix) dissimilarity matrix between patterns,
	nb_cluster (int): number of clusters,
	clusters (array(array(int))): cluster composition.
	
  Optional Arguments 
	Prototypes (array(int)): cluster prototypes.
	
  Returned Object
	If the second mandatory argument is ''Partitioning'' and if 2 < nb_cluster < (number of patterns), an object of type clusters is returned, otherwise no object is returned.
  Description
	In the case where the composition of clusters is a priori fixed, the function Clustering simply performs an evaluation of the a priori fixed partition.
	
See Also
	SelectIndividual, 
	Symmetrize, 
	Compare (vectors),
	Compare (sequences),
	Compare (Markovian models),
	ToDistanceMatrix.
"""
