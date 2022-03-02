#!/usr/bin/env python
"""Test of matplot lib resolution.


<Long description of the module functionality.>

:todo:
    Nothing.

:bug:
    None known.
    
:organization:
    INRIA

"""
# Module documentation variables:
__authors__="""Szymon Stoma    
"""
__contact__=""
__license__="Cecill-C"
__date__="<Timestamp>"
__version__="0.1"
__docformat__= "restructuredtext en"
__revision__="$Id: 08-04-30-testPylabPlot.py 7875 2010-02-08 18:24:36Z cokelaer $"


import  pylab
import numpy
import math
x=numpy.arange(0., 2*numpy.pi, 0.5)
pylab.rcParams["font.size"]=20

pylab.plot( x, [math.sin(i) for i in x])
pylab.plot( x, [math.cos(i) for i in x], linestyle="", marker="d")
pylab.legend( ("sin", "cos") )

pylab.title("Test of fonts")
pylab.xlabel("X label")
pylab.ylabel("Y label")
pylab.show()
pylab.savefig("300.png",dpi=300, format="png")
pylab.savefig("100.png",dpi=100, format="png")