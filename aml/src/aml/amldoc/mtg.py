# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
2 The MTG module
		      
				
				
			  
		    
		    
			    
		    
		

2.1 List of AML functions from MTG: alphabetic order 

Activate - 
Active - 
AlgHeight - 
AlgOrder - 
AlgRank - 
Alpha - 
Ancestors - 
Axis - 
Beta - 
BottomCoord - 
BottomDiameter - 
Class - 
ClassScale - 
Complex - 
ComponentRoots - 
Components - 
Coord - 
DateSample - 
Defined - 
Descendants - 
DressingData - 
EdgeType - 
EulerAngles - 
Extremities - 
Father - 
Feature - 
FirstDefinedFeature - 
Height - 
Index - 
LastDefinedFeature - 
Length - 
Location - 
MatchingExtract - 
MTG - 
MTGRoot - 
NextDate - 
Order - 
Path - 
PDir - 
PlantFrame - 
Plot - 
Plot (LINETREE) - 
Predecessor - 
PreviousDate - 
Rank - 
RelBottomCoord - 
RelTopCoord - 
Root - 
Save (LINETREE) - 
Scale - 
SDir - 
Sons - 
Successor - 
TopCoord - 
TopDiameter - 
TreeMatching - 
Trunk - 
VirtualPattern - 
VtxList - 

2.2 List of AML functions from MTG: by type 


  Construction
  
   MTG(e1)
   Activate(e1)
   Active()
   Entry points in the MTG
   MTGroot()
   VtxList()
ARRAY(vtx)-->
  
  
  Feature functions
  
   Class(e1)
   Index(e1)
   Scale(e1)
   Feature(e1, e2)
   Feature(e1, e2, e3)
   ClassScale(e1)
   EdgeType(e1, e2)
   Defined(e1)
   Order(e1)
   Rank(e1)
   Height(e1)
   Order(e1, e2)
   Rank(e1, e2)
   Dist(e1, e2) -->
   AlgOrder(e1, e2)
   AlgRank(e1, e2)
   AlgHeight(e1, e2)
   AlgDist(e1, e2) -->
  
  
  
   Date functions
  
   DateSample(e1)
   FirstDefinedFeature(e1, e2)
   LastDefinedFeature(e1, e2)
   NextDate(e1)
   PreviousDate(e1)
  
  




  Functions for moving in MTGs
  
   Father(e1)
   Successor(e1)
   Predecessor(e1)
   Root(e1)
   Complex(e1)
   Location(e1)
   Sons(e1)
   Ancestors(e1)
   Descendants(e1)
   Extremities(e1)
   Components(e1)
   Componentroots(e1)
   Path(e1, e2)
   Axis(e1)
   Trunk(e1)

  
  
  Geometric interpretation
  
   PlantFrame(e1)
   TopCoord(e1, e2)
   RelTopCoord(e1, e2)
   BottomCoord(e1, e2)
   RelBottomCoord(e1, e2)
   Coord(e1, e2)
   DressingData(e1)
   Plot(e1)
   BottomDiameter(e1,e2)
   TopDiameter(e1,e2)
   Alpha(e1,e2)
   Beta(e1,e2)
   Length(e1,e2)
   VirtualPattern(e1)
   PDir(e1,e2)
   SDir(e1,e2)

  
  
  Comparison Functions
  
   TreeMatching(e1)
   MatchingExtract(e1)
  
  


  Options (cf. Father())
  
   EdgeType(+, <, *)
   RestrictedTo(NoRestriction, SameComplex, SameAxis)
   ContainedIn(i)
   Scale(i)
   Format(ASCII, GNUPLOT)
   ErrorNb(i)
"""
