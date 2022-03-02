# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Array
    ARRAY constructor
Usage
	[x1,x2,...,xn]
	[i:j]
	[i:j:step]
      
Arguments
	x1, x2,..., xn(T) : values of identical type. Type T can be any type. Any xk can be Undef.
	i, j, step (INT or REAL): for incremental constructor.
Returned Object
	In the constructor form x1, x2,..., xn, assuming the type of xk is T, the value returned an array constructor is an ARRAY(T) if at least one is not Undef. If all are Undef the constructor returns Undef.
	In the incremental form of the constructor, if all the arguments i, j, step are integers, the array returned has type ARRAY(INT). If any of the argument is REAL, the array returned has type ARRAY(REAL). If any of the arguments is Undef, the result is Undef.
Description
	An ARRAY is a set-type, i.e. the type of a collection of objects. Like for SETs, all the elements of an ARRAY must have the same type. However, an ARRAY can contain Undef elements. Contrary to SETs, elements of an ARRAY are ordered by a total order relation. It is thus meaningful to speak of the ith element of an ARRAY, provided i is greater than 0 and less than the size of the array.
	An incremental constructor, [i:j], enables the user to build incremental series of values starting at a lower-bound i and finishing at a higher-bound j. The default increment value is 1 if i&pound;j and -1 if i>j. If i&pound;j for example, the resulting ARRAY is [i, i+1, i+2,..., i+m, j] where m is such that i+m<j&pound;i+m+1. To change this increment, one must specify the step of the increment by using [i:j:step].
Details
	
    	 In version 1.x of AMAPmod there is no way of saving or loading binary representations of arrays
	
    	 An array can be saved in ASCII format, using primitive Save:
	AML> Save(array1,"filename")
	For exporting data to other programs, an option Format is provided that save an array in the selected format. Current values of Format option can be ASCII (default option) or SpreadSheet. The SpreadSheet value enables the user to save a possibly multidimentional array in a format that can be loaded later on with a spreadsheet program:
	AML> array1=[[1,2,3],[4,5,6],[7,8,9]]
	AML> Save(array1,"filename",Format_SpreadSheet)
	
	This command saves array1 in file "filename" as follows:
	#2
	1 2 3
	4 5 6
	7 8 9
	
    	 An array that has been saved with the previous command in ASCII format can be loaded in ASCII format using its explicit constructor Array:
    	AML> Array("filename")
	
    	A file which consists of objects of type INT, REAL, STRING, having the same type, separated by white space characters can be loaded as a multidimentional array as follows:
    	AML> Array("filename",[n1,n2,...,nm-1])
	where filename is the name of a file containing homogeneous ASCII data (of only one type). The data in the file can be any of the simple types: INT, CHAR, REAL, BOOL, DATE, STRING. If a multidimentional array with m dimensions is expected, then the number of elements of each dimension, except the last one nm, must be indicated as an argument, in increasing order of dimensions. The number of element of the last dimension derives from the numbers other dimensions and from the size of the file. For example, assume we have an ASCII file of 21 integers and we want to load this file into a 2-dimensional array whose first dimension has 7 elements and whose second dimension has 3 elements. Then, we must load the file as follows:
	AML> Array("filename",[7])
	<ARRAY(ARRAY(int))> [[46,58,4,10,11,-23,0],[5,16,
	-7,15,17,-29,1],[36,26,5,12,11,-13,1]]
	
    	The same file considered as a monodimensional array would be loaded as follows:
    	AML> Array("filename",[])
	<ARRAY(INT)> [46,58,4,10,11,-23,0,5,16,-7,15,17,
	-29,1,36,26,5,12,11,-13,1]
	
    	 For certain types of arrays, a graphical display of an array can be obtained with the command Plot. These arrays are either 1- 2- or 3- dimensional arrays of INTs, REALs or DATEs. These arrays can be Plotted as follows:
	Plot of 1-dimensional arrays:
	AML> y1 = [2,4,22,40,49,53,55,45,33,27,19,13,10,12,7]
	AML> Plot(y1)#fig
	
	This simple command assumes that the elements of array y1 are y-coordinates of points whose x-coordinate can be implicitly defined by the rank of the element in the array y1. The output of the Plot() command thus looks as follows:
	In this graphic points are linked to each other by a line. Other styles of plot can be usedby specifying the optional parameter Style. Style can be one of the following: lines, points, linespoints, dots, impulses, steps, boxes (linespoints is the default).
	AML> Plot(y1,Style->"boxes")
	
	The default values of the implicit x-coordinates can be changed with optional parameters XOutSet, XStep, XMax, XMin. Similarly, the bounds of the y axis that are graphically displayed is estimated from the values of array y1. These bounds can be changed with options YMin and YMax.
	AML> Plot(y1,XOutset->-10,XStep->2,XMax->50,YMax->100) # fig
	
    	Titles can be given to coordinate axes and to the plot with options XTitle, YTitle, Title which must take STRING values.
	AML> year=1997
	AML> Plot(y1,Title->"Observationsin"+ToString(year),\ 
	AML> Xtitle->"Branchorde",YTitle->"amount of Apples") # fig
	
	If both x and y coordinates of every points are explicitly defined, it is possible to plot the points in two different ways. First, we may give an array of points defined by their (x, y) coordinates:
	AML> p1=[[10,2],[15,4],[22,22],[24,40],[30,49],[45,53],\
	AML> [58,45],[61,33],[67,27],[80,19],[87,13],[90,10],\
	AML> [95,12],[100,7]]
	
    	We thus have a set of points whose x- and y-coordinates are respectively in the arrays x1 and y1. To plot the corresponding points, we have to specify with option XAxis which of them corresponds to the x coordinates:
	AML> Plot(p1,XAxis->1) # fig
	
	In this expression XAxis has value 1, which means that the first element of each array defining the coordinates of points of p1 must be interpreted as the x-coordinate of the point.
	This method can be extended for plotting several curves on the same graphic. If we assume that for each x-coordinate, two y-coordinates are defined, cooresponding respectively to two different curves. We can make up 3uples (x, y1, y2) containing one x-coordinate and the two corresponding y-coordinates for the two curves, i.e. respectively y1 and y2. Thus defining the two curves comes down to giving a set of 3-uples like:
	AML> p2=[[10,2,-1],[15,4,-6],[22,22,-12],[24,40,-5],\
	AML> [30,49,-1],[45,53,-6],[55,55,-10],[58,45,-6],\
	AML> [61,33,-2],[67,27,-5],[80,19,-13],[87,13,-7],\
	AML> [90,10,-1],[95,12,-5],[100,7,-15]]
	AML> Plot(p2,XAxis->1)#fig
	
	This method can be extended to any number of curves n. In this case an array pn of n-uples has to be built. The command Plot(pn) plots n curves with implicit x-coordinates. If the ith value of the n-uples designates the x-coordinates, this can be indicated by option XAxis:
	AML> Plot(pn,XAxis->i)
	which plots n-1curves.
	There exists another way to plot several curves in the same window. One has to create an array representing each series of y values (one series for each curve and represented as an array like y1). For instance, to plot the two curves corresponding to array y1 and to array x1 (defined below), we just have to specify that the arrays y1 and x1 corresponds to groups of data associated with our curves. This is done with option Groups which specifies how should be interpreted the elements (which are arrays of integers y1 and x1) of the array passed as an argument to plot:
	AML> x1=[10,15,22,24,30,45,55,58,61,67,80,87,90,95,100]
	AML> Plot([y1,x1],Groups->"curves").
	
	In this case, the x-coordinates of curve points are defined implicitly: elements of y1 corresponds to a first group of y-coordinates (defining the first curve) and elements of x1 corresponds to a second group of y-coordinates (defining a second curve). The x-coordinates can be explicitly defined by specifying a group of values associated with them. In our example, we can for instance specify with option XAxis that the second array, x1, actually corresponds to the x-coordinates of the curve points whose y-coordinates are given in the first array y1:
	AML> Plot([y1,x1],Groups->"curves",XAxis->2).
	
Note
	Two arrays are equal whenever their ith element are equal, for all possible i. This notably entails that two identical arrays must have the same size.
See Also
	
	Size, 
	At, 
	Sum, 
	Series, 
	Pos, 
	AllPos, 
	Invert, 
	Set, 
	List, 
	ToArray, 
	ToSet, 
	ToList.
	

Examples
	AML>a=[".aml",".mtg",".amlog",".hmm"]
	<ARRAY(STRING)> [.aml,.mtg,.amlog,.hmm]
	AML> a=[[1,2],[3,4,5],Undef,[7],[8,9,10]]
	<ARRAY(ARRAY(INT))>[[1,2],[3,4,5],Undef,[7],[8,9,10]]
	AML> a=[1:9]
	<ARRAY(INT)>[1,2,3,4,5,6,7,8,9]
	AML> a=[1:9:2]
	<ARRAY(INT)>[1,3,5,7,9]
	AML> a=[9:1:-2]
	<ARRAY(INT)>[9,7,5,3,1]
	AML> a=[9:1]
	<ARRAY(INT)>[9,8,7,6,5,4,3,2,1]
	AML> a=[1.1:9:2.7]
	<ARRAY(REAL)>[1.1,3.8,6.5]
	AML> a=[Date("01/01/97"),Date("11/01/97"),Date("24/01/97"),\
	AML> Date("03/02/97")]
	<ARRAY(DATE)> [01/01/97, 11/01/97, 24/01/97, 03/02/97]
"""
