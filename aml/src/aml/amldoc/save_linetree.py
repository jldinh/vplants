# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Save (LINETREE)
	Save a LINETREE object in different formats.
  Usage
	Save(obj, filename)
	Save(obj, file, Format-> Binary)
  
  Arguments
	
		  obj (LINETREE) : the object can have any type.
		  filename (STRING) : identifies the file in which the obj is saved.
	
Optional Arguments
	Optional arguments can exist depending on the type of the first argument. Option Format can be used to select an output format. Available formats are: GEOM (ascii format for the GEOM library), AMAP (for ascendant compatibility with AMAP software and PovRay; VGStar and VRML formats will be available in the next release.	
Returned Object
	No value is returned.
Description
	Save an object to a file in different format.
  See Also
	
	Load, 
	Object constructors, 
	Display. 
  

Examples
	AML> #Saving a LineTree
	AML> pf = PlanteFrame(1, Sacle-gt; 3) # builds a PlantFrame
	AML> lt=Plot(fr) # builds a PlantFrame
	AML> Save(lt, "file1.lnt", Format-> GEOM)
	AML> # Save the LineTree to file named file1.lnt in ascii
"""
