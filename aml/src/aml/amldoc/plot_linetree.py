# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Plot (LINETREE)
	Plots a LINETREE.
  Usage
	Plot(lt, Geometry-> geomfunc)
	Plot(lt, Appearance-> appfunc)
	Plot(lt, Quotient-> quotientfunc)
  Arguments
	p (LINETREE) : plantframe
  Optional Arguments
	Geometry (FUNC) : Function defining a geometry for a vertex as a GEOM object. The function returns a string referring to an object previously loaded using the dressing file keyword "Geometry" in the dressong file.
	Appearance (FUNC) : Function defining an appearance for a vertex as an APPEARANCE object. The function returns a string referring to an object previously loaded using the dressing file keyword "Appearance" in the dressong file. 
	Quotient (FUNC) : Predicate on vertex that defines a set of vertices which should be considered as root vertices of new macro-constituents (not necessarily defined in the original MTG).  Then the Geometric models are associated with these new macroscopic vertex by using between-scale constraints. More information on this possibility will be available in a future release.
	

Returned Object
	On a PLANTEFRAME Plot returns a LINETREE object.
Background
	MTGs
  See Also
	
	MTG, 
	Array, 
	Scale, 
	Class, 
	Index.

Examples
	AML> cl(_x)=If Feature(_x,"DiamTop")!=Undef Then RED2 Else GREEN3
	AML> lt=Plot(fr)
	AML> Plot(lt, Appearance-> cl)
"""
