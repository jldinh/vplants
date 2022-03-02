# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
1 The Kernel module of AML
		      
			  	
				
			  
		    
		    
			    
		    
		

1.1 List of AML functions: alphabetic order 
Abs - 
AllPos - 
Angle - 
Append - 
Arithmetic operators - 
Array - 
At - 
Boolean operators - 
 Ceil - 
Comparison operators - 
Constants - 
Cov - 
Date operators - 
Delete - 
Display - 
DisplayAllNames, DisplayAllUserNames - 
Echo - 
EchoOn / EchoOff - 
EDist - 
Filter - 
Flatten - 
Floor - 
Foreach - 
Head - 
If-Then-Else - 
InsertAt - 
Inter - 
Invert - 
List - 
Mathematical functions - 
Max - 
Mean - 
Minus - 
Mod - 
Norm - 
Plot, NewPlot - 
Plus - 
Pos - 
Prod - 
ProdSeries - 
Rand - 
RemoveAt - 
Rint - 
Save - 
Select - 
Series - 
Set - 
SetMinus - 
Size - 
Sort - 
SProd - 
SubArray - 
Sum - 
Switch - 
Tail - 
ToArray - 
ToInt - 
ToList - 
ToReal - 
ToSet - 
ToString - 
Trigonometric functions - 
Truncate - 
Union - 
Var - 
VProd

1.2 List of AML functions: by type 


  Arithmetic operators
  
   e1 + e2
   e1 - e2
   e1 * e2
   e1 / e2
   - e1
   e1 Mod e2
Rand(e1, e2) -->
   Abs(e1)
   Floor(e1)
   Ceil(e1)
   Rint(e1)
   Truncate(e1)
   ToInt(e1)
   ToReal(e1)
  
 
  Numeric functions
  
   Sqrt(e1)
   Log(e1)
   Log10(e1)
   Exp(e1)
   e1 ^ e2
   Cos(e1)
   Sin(e1)
   Tan(e1)
   Acos(e1)
   Asin(e1)
   Atan(e1)
  
 
  Constants
  
     Undef UNDEF
     Black INT
     White INT
     Green INT
     Red INT
     Blue INT
     Yellow INT
     Violet INT
     LightBlue INT
     True BOOL
     False BOOL
     CurrentPlottedObj any
     CurrentWindow window
     DefaultWindow window
     Pi real
  
  


  Boolean operators
  
    e1 And e2
    e1 Or e2
    Not e1
  
  
  Logical operators
  
    e1 == e2
    e1 != e2
  
  
  Comparison operators
  
    e1 < e2
    e1 <= e2
    e1 > e2
    e1 >= e2
  
  


  Operators on Dates
  
     Second int
     Minute int
     Hour int
     Day int
     DateUnit int
     DateFormat string
     d1 + d2
     d1 - d2
     Date(e1)
     ToTimeUnit(e1)
  
  
   Control expressions
  
     Select(e1,pred)
     If e1 Then e2 Else e3
     Switch e1 Case e2 : e3 Case e4 : e5 ... Default : e6
  
  


  Set type operators
  
    [e1,e2,...,eN]
Interval(e1, e2) -->
Interval(e1,e2,e3) -->
    [e1:e2]
    [e1:e2:e3]
    Array(e1,e2,...,eN)
    Set(e1,e2,...,eN)
    List(e1,e2,...,eN)
    e1 @ e2
    Head(e1)
    Tail(e1)
    Pos(e1, e2)
    e1+e2
    e1-e2
    Append(e1, e2)
    InsertAt(e1, e2)
    RemoveAt(e1, e2)
    Invert(e1, e2)
    ToArray(e1)
    ToSet(e1)
    ToList(e1)
    Sum(e1)
    Prod(e1)
    Max(e1)
    Mean(e1)
    Minus(e1)
    Flatten(e1)
    Size(e1)
    Sort(e1)
    e1 | e2
    e1 & e2
    SetMinus(e1,e2)
    Filter(e1,e2)
    EDist(e1, e2)
    SProd(e1, e2)
    VProd(e1, e2)
    Angle(e1, e2)
    Norm(e1)
  
  
  Iterator
  
     Foreach _c In e1 : e2
  
  
  General functions
  
     EchoOn()
     EchoOff()
     Delete(e1,e2,...,eN)
     Display()
     Display(e1)
     DisplayAll()
     Save(e1)
Print(e1) -->
     Plot(e1)
     NewPlot(e1)
"""
