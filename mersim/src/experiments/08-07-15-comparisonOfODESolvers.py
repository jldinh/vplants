#!/usr/bin/env python
"""Comparision of ODE solvers

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
__revision__="$Id: 08-07-15-comparisonOfODESolvers.py 7875 2010-02-08 18:24:36Z cokelaer $"


import pylab
#from openalea.mersim.tools.integration_rk import rk4

class IntegrationResult(dict):
    """Class containing the results of integration.
    
    <Long description of the class functionality.>
    """
    def __init__( self ):
        """Basic constructor.
        """
        self[ "x" ] = {}
        self.label_x_axis = ""
        self.label_y_axis = ""

def rk4(f, x, t, delta_t):
        # compute the k1's
        k1 = delta_t*f(x,t)
        # compute the k2's
        tmpx = x + k1/2
        k2 = delta_t*f( tmpx, t+delta_t/2)
        # compute the k3's
        tmpx = x + k2/2 
        k3 = delta_t*f( tmpx, t+delta_t/2)
        # compute the k4's
        tmpx = x + k3
        k4 = delta_t*f( tmpx, t+delta_t)
        # compute the new variables
        newx = x + ( k1+2*k2+2*k3+k4 )/6
        return newx


def solve_euler( f_dot=None, x0=None, t=0., h=0.1, t_fin=10. ):
    """<Short description of the function functionality.>
    
    <Long description of the function functionality.>
    
    :parameters:
        arg1 : `T`
            <Description of `arg1` meaning>
    :rtype: `T`
    :return: <Description of ``return_object`` meaning>
    :raise Exception: <Description of situation raising `Exception`>
    """
    res=IntegrationResult()
    res["x"][ t ] = x0
    i=0
    while t<t_fin:
        t_new = t+h
        res[ "x" ][ t_new ] = res[ "x" ][ t ]+f_dot(res[ "x" ][ t ],t)*h
        t = t_new
    return res

def solve_real( f=None, x0=None, t=0., h=0.1, t_fin=10. ):
    """<Short description of the function functionality.>
    
    <Long description of the function functionality.>
    
    :parameters:
        arg1 : `T`
            <Description of `arg1` meaning>
    :rtype: `T`
    :return: <Description of ``return_object`` meaning>
    :raise Exception: <Description of situation raising `Exception`>
    """
    res=IntegrationResult()
    res["x"][ t ] = x0
    while t<t_fin:
        t_new = t+h
        res[ "x" ][ t_new ] = f(res[ "x" ][ t ], t_new)
        t = t_new
    return res

def solve_rk4( f_dot=None, x0=None, t=0., h=0.1, t_fin=10. ):
    """<Short description of the function functionality.>
    
    <Long description of the function functionality.>
    
    :parameters:
        arg1 : `T`
            <Description of `arg1` meaning>
    :rtype: `T`
    :return: <Description of ``return_object`` meaning>
    :raise Exception: <Description of situation raising `Exception`>
    """
    res=IntegrationResult()
    res["x"][ t ] = x0
    i=0
    while t<t_fin:
        t_new = t+h
        res[ "x" ][ t_new ] = rk4(f_dot, res[ "x" ][ t ], t, h )
        # (f, x, t,delta_t)
        #(  f_dot(res[ "x" ][ t ], t)+f_dot(res[ "x" ][ t ],t)*h
        t = t_new
    return res

def solve_pylab_lsode( f_dot=None, x0=None, t=0., h=0.1, t_fin=10., atol=1e-8,  rtol=1e-8 ):
    """<Short description of the function functionality.>
    
    <Long description of the function functionality.>
    
    :parameters:
        arg1 : `T`
            <Description of `arg1` meaning>
    :rtype: `T`
    :return: <Description of ``return_object`` meaning>
    :raise Exception: <Description of situation raising `Exception`>
    """
    import scipy.integrate.odepack
    res=IntegrationResult()
    res["x"][ t ] = x0
    j=0
    xs=pylab.arange(t,t_fin, h)
    ys=scipy.integrate.odepack.odeint( f_dot, res[ "x" ][ t ], xs,  atol=atol, rtol=rtol )
    for i in xs:
        res[ "x" ][ i ] = ys[j]
        j+=1
    return res

def plot_results( results={} ):
    """<Short description of the function functionality.>
    
    <Long description of the function functionality.>
    
    :parameters:
        arg1 : `T`
            <Description of `arg1` meaning>
    :rtype: `T`
    :return: <Description of ``return_object`` meaning>
    :raise Exception: <Description of situation raising `Exception`>
    """
    ""
    
    line=["b","g", "c", "r", "y", "k"]
    line_type=["-","--"]
    point_type=["v"]#["p","v","o","s","^","D",">", "h"]
    i_line=0
    labels=[]
    sorted_keys=results.keys()
    sorted_keys.sort()
    for i in sorted_keys:
        x=[]
        y=[]
        items = results[ i ][ "x" ].items()
        items.sort()
        for j in items:
            x.append(j[0])
            y.append(j[1])
        labels.append( i )
        pylab.plot(x,y,line[i_line%len(line)]+line_type[i_line%len(line_type)]+point_type[i_line%len(point_type)])
        i_line+=1
    pylab.legend(labels)
    pylab.xlabel("t")
    pylab.ylabel("f(y)")
    #pylab.axis([0,1,0,1])
    pylab.show()    

def plot_results_error( f, results={} ):
    """<Short description of the function functionality.>
    
    <Long description of the function functionality.>
    
    :parameters:
        arg1 : `T`
            <Description of `arg1` meaning>
    :rtype: `T`
    :return: <Description of ``return_object`` meaning>
    :raise Exception: <Description of situation raising `Exception`>
    """
    ""
    
    line=["b","g", "c", "r", "y", "k"]
    line_type=["-","--"]
    point_type=["v"]#["p","v","o","s","^","D",">", "h"]
    i_line=0
    labels=[]
    sorted_keys=results.keys()
    sorted_keys.sort()
    
    for i in sorted_keys:
        x=[]
        y=[]
        items = results[ i ][ "x" ].items()
        items.sort()
        for j in items:
            x.append(j[0])
            y.append(abs(j[1] - f(0,j[0])))
        labels.append( i )
        pylab.plot(x,y,line[i_line%len(line)]+line_type[i_line%len(line_type)]+point_type[i_line%len(point_type)])
        i_line+=1
    pylab.legend(labels)
    pylab.xlabel("t")
    pylab.ylabel("error")
    #pylab.axis([0,1,0,1])
    pylab.show()    

def plot_integration_times( results={} ):
    """<Short description of the function functionality.>
    
    <Long description of the function functionality.>
    
    :parameters:
        arg1 : `T`
            <Description of `arg1` meaning>
    :rtype: `T`
    :return: <Description of ``return_object`` meaning>
    :raise Exception: <Description of situation raising `Exception`>
    """
    ""
    
    line=["b","g", "c", "r", "y", "k"]
    line_type=["-","--"]
    point_type=["v"]#["p","v","o","s","^","D",">", "h"]
    i_line=0
    labels=[]
    sorted_keys=results.keys()
    sorted_keys.sort()
    #print sorted_keys
    for i in sorted_keys:
        x=[]
        y=[]
        items = results[ i ][ "x" ].items()
        items.sort()
        for j in items:
            x.append(j[0])
            y.append(j[1])
        labels.append( i )
        pylab.plot(x,y,line[i_line%len(line)]+line_type[i_line%len(line_type)]+point_type[i_line%len(point_type)])
        i_line+=1
    pylab.legend(labels)
    pylab.xlabel("t")
    pylab.ylabel("time")
    #pylab.axis([0,1,0,1])
    pylab.show()    



def order_dict( self, adict={} ):
    """<Short description of the function functionality.>
    
    <Long description of the function functionality.>
    
    :parameters:
        arg1 : `T`
            <Description of `arg1` meaning>

    :rtype: `T`
    :return: <Description of ``return_object`` meaning>
    :raise Exception: <Description of situation raising `Exception`>
    """
    items = adict.items()
    items.sort()
    return [value for key, value in items]


def f1_dot( x, t ):
    """Expotential
    
    <Long description of the function functionality.>
    
    :parameters:
        arg1 : `T`
            <Description of `arg1` meaning>
    :rtype: `T`
    :return: <Description of ``return_object`` meaning>
    :raise Exception: <Description of situation raising `Exception`>
    """
    #k = -1.01
    k=-2
    return k*x

def f1( x, t ):
    """Solution of f1_dot
    
    <Long description of the function functionality.>
    
    :parameters:
        arg1 : `T`
            <Description of `arg1` meaning>
    :rtype: `T`
    :return: <Description of ``return_object`` meaning>
    :raise Exception: <Description of situation raising `Exception`>
    """
    import math
    #k= -1.01
    k=-2
    return math.pow(math.e, k*t )



def time_test(t_final=[5.], trials=50):
    import time
    print "final time: ", t_final
    res=  {}
    res[ "euler-0.5" ] = IntegrationResult()
    res[ "rk4-1." ] = IntegrationResult()
    res[ "rk4-0.5" ] = IntegrationResult()
    res[ "lsode4-1.-prec-1e-1" ]  = IntegrationResult()
    res[ "lsode4-0.5-prec-1e-1" ] =  IntegrationResult()

    results=IntegrationResult()
    
    #initial run
    for i in t_final:
        print "current time: ", i
        t=time.time()    
        results["euler-0.5"] = solve_euler( f_dot=f1_dot, x0=x0, t=0., h=0.5, t_fin=i )
        t1=time.time()
        results["rk4-1."] = solve_rk4( f_dot=f1_dot, x0=x0, t=0., h=1., t_fin=i )
        t2=time.time()
        results["rk4-0.5"] = solve_rk4( f_dot=f1_dot, x0=x0, t=0., h=0.5, t_fin=i )
        t3=time.time()
        results["lsode4-1.-prec-1e-1"] = solve_pylab_lsode( f_dot=f1_dot, x0=x0, t=0., h=1., t_fin=i, atol=1e-1, rtol=1e-1 )
        t4=time.time()
        results["lsode4-0.5-prec-1e-1"] = solve_pylab_lsode( f_dot=f1_dot, x0=x0, t=0., h=0.5, t_fin=i, atol=1e-1, rtol=1e-1 )
        t5=time.time()
        
        #print  "euler-0.5",  t1-t
        #print  "rk4-1.", t2-t1
        #print  "rk4-0.5", t3-t2
        #print  "lsode4-1.-prec-1e-1", t4-t3
        #print  "lsode4-0.5-prec-1e-1", t5-t4
        #
        res[ "euler-0.5" ]["x"][ i ] = t1-t
        res[ "rk4-1." ]["x"][ i ] = t2-t1
        res[ "rk4-0.5" ]["x"][ i ] = t3-t2
        res[ "lsode4-1.-prec-1e-1" ]["x"][ i ] = t4-t3 
        res[ "lsode4-0.5-prec-1e-1" ]["x"][ i ] = t5-t4

        # repeats
        for j in range(trials):
            t=time.time()    
            results["euler-0.5"] = solve_euler( f_dot=f1_dot, x0=x0, t=0., h=0.5, t_fin=i )
            t1=time.time()
            results["rk4-1."] = solve_rk4( f_dot=f1_dot, x0=x0, t=0., h=1., t_fin=i )
            t2=time.time()
            results["rk4-0.5"] = solve_rk4( f_dot=f1_dot, x0=x0, t=0., h=0.5, t_fin=i )
            t3=time.time()
            results["lsode4-1.-prec-1e-1"] = solve_pylab_lsode( f_dot=f1_dot, x0=x0, t=0., h=1., t_fin=i, atol=1e-1, rtol=1e-1 )
            t4=time.time()
            results["lsode4-0.5-prec-1e-1"] = solve_pylab_lsode( f_dot=f1_dot, x0=x0, t=0., h=0.5, t_fin=i, atol=1e-1, rtol=1e-1 )
            t5=time.time()

            res[ "euler-0.5" ]["x"][ i ] += t1-t
            res[ "rk4-1." ]["x"][ i ] += t2-t1
            res[ "rk4-0.5" ]["x"][ i ] += t3-t2
            res[ "lsode4-1.-prec-1e-1" ]["x"][ i ] += t4-t3 
            res[ "lsode4-0.5-prec-1e-1" ]["x"][ i ] += t5-t4

    res[ "euler-0.5" ]["x"][ i ] += res[ "euler-0.5" ]["x"][ i ] / float(trials+1)
    res[ "rk4-1." ]["x"][ i ] += res[ "rk4-1." ]["x"][ i ] / float(trials+1)
    res[ "rk4-0.5" ]["x"][ i ] += res[ "rk4-0.5" ]["x"][ i ] / float(trials+1)
    res[ "lsode4-1.-prec-1e-1" ]["x"][ i ] += res[ "lsode4-1.-prec-1e-1" ]["x"][ i ] / float(trials+1)
    res[ "lsode4-0.5-prec-1e-1" ]["x"][ i ] += res[ "lsode4-0.5-prec-1e-1" ]["x"][ i ] / float(trials+1)
            
    return res

results={}
x0=1.
t=0.
t_fin=5.
h=1.

# tests for precision
results["real"] = solve_real( f=f1, x0=x0, t=t, h=0.1, t_fin=t_fin )
results["euler-0.5"] = solve_euler( f_dot=f1_dot, x0=x0, t=t, h=0.5, t_fin=t_fin )
results["rk4-1."] = solve_rk4( f_dot=f1_dot, x0=x0, t=t, h=1., t_fin=t_fin )
results["rk4-0.5"] = solve_rk4( f_dot=f1_dot, x0=x0, t=t, h=0.5, t_fin=t_fin )
results["lsode4-1.-prec-1e-1"] = solve_pylab_lsode( f_dot=f1_dot, x0=x0, t=t, h=1., t_fin=t_fin, atol=1e-1, rtol=1e-1 )
results["lsode4-0.5-prec-1e-1"] = solve_pylab_lsode( f_dot=f1_dot, x0=x0, t=t, h=0.5, t_fin=t_fin, atol=1e-1, rtol=1e-1 )
plot_results(results)
pylab.axis([0,1,0,1])

# tests for errors
plot_results_error(f1, results )

## tests for execution times
#r=time_test([10, 110, 210, 310, 410, 510, 610, 710, 810, 910])
#plot_integration_times(r)