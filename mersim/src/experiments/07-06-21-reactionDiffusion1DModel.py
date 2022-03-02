#!/usr/bin/env python
"""One dimention reaction-diffusion.

<Long description of the module functionality.>

:todo:
    Nothing.

:bug:
    None known.
    
:organization:
    INRIA

"""
# Module documentation variables:
__authors__="""Szymon Stoma&Tim Hohm    
"""
__contact__=""
__license__="Cecill-C"
__date__="<Timestamp>"
__version__="0.1"
__docformat__= "restructuredtext en"
__revision__="$Id: 07-06-21-reactionDiffusion1DModel.py 7875 2010-02-08 18:24:36Z cokelaer $"


import openalea.plantgl.all as pgl
import openalea.plantgl.ext.all as pd
import math # basic math rutines
import pylab # eg. plotting figures
import scipy # all possible calculations, minimisations, etc
import scipy.integrate.odepack # solving ode by SODA
import random # random generator
import copy # to make deep copy (not references)
import numarray

class Cell(object):
    """The abstract cell implementation.
    
    Cell contains gens concentration information which could be accessed:
    c = Cell( genes=genes )
    c.concentration[ "gene1" ]            # to read
    c.concentration[ "gene1" ] = 0.1  # to set
    """

    def __init__( self , id=0, genes={}):
        """Basic constructor.
        """
        self.id=id
        self.concentrations = {}
        for i in genes.keys():
            self.concentrations[ i ] = genes[ i ]


class ReactionDiffusion1DModel(object):
    """This is the basic class to model r-d in 1d. 
    
    <Long description of the class functionality.>
    """
    def __init__( self, cell_number=10 ):
        """Basic constructor.
        """
        self.t = 0
        self.h = 10
        self.c_change = 0.002 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 500 # used to drop the loop if convergence not reached before x loops
        self.c_aux_tol=1
        self.c_D_A=0.005
        self.c_D_H=0.2

        self.c_rho_A =0.01
        self.c_rho_H =0.02
        self.c_mu_A =0.003
        self.c_mu_H =0.02
        self.c_sigma_A=0.00#1
        self.c_sigma_H=0.00#1
        self.c_kappa_A=0.00#1
 
        self.cells={}
        for i in range( cell_number ):
            self.cells[ i ] = Cell( id=i, genes={"A": 1+random.random(), "H": 1 })
            
    def step( self ):
        self.integrate()
        self.visualise()
        self.growth()
        
    def growth( self ):
        """Growht of the system.
        
        Currently a stub method.
        """
        pass
    
    def visualise( self ):
        """Visualisation of the r-d system.
        
        Pylab is required component of the visualisation.
        """
        x=[]
        y1=[]
        y2=[]
        for i in range(len(self.cells)):
            x.append(i)
            y1.append(self.cells[ i ].concentrations[ "A" ] )
            y2.append(self.cells[ i ].concentrations[ "H" ] )
        pylab.plot(x, y1, "g", x,y2, "r")
        pylab.axis( [0,len(self.cells),0,20] )
        pylab.xlabel( "Cells" )
        pylab.ylabel( "Product  quantities" )
        pylab.title( "Initial conditions" )
        pylab.show()
                
    def integrate(self):
        """Integration mechanism using SciPy.
        
        <Long description of the function functionality.> 
        """        
        stable = False
        while not stable:
            print  self.t
            (res,d)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h], rtol=0.0001, atol=0.0001, full_output=1)#, hmax=0.0001, hmin=0.0001 )
            self.t += self.h                
            stable = self.rate_change( result=res[1] )
            self.update( res[1] )
            print d

    def rate_change( self, result=None):
        """Checks if stable stare has been already reached.
        
        Currently a stub method.
        
        :parameters:
            arg1 : scipy.integrate.odepack.odeint result last vector
                Result vector got from scipy integrator.
        :rtype: `bool`
        :return: True iff stable state has been reached.
        """
        return True
    
    def prepare_x0( self ):
        """Maps datastructure to system of equations which are solved by SciPy.
        """
        self.cell2sys_A = {}
        self.cell2sys_H = {}
        k = 0
        x0 = numarray.zeros( 2*len(self.cells),typecode=numarray.Float32 )
        for i in self.cells:
            self.cell2sys_A[ i ] = k
            k+=1
            self.cell2sys_H[ i ] = k
            k+=1            
            x0[ self.cell2sys_A[ i ] ] = self.cells[ i ].concentrations[ "A" ]
            x0[ self.cell2sys_H[ i ] ] = self.cells[ i ].concentrations[ "H" ]
        return x0

    def update( self, x0):
        """Updates the  datastructure from the result SciPy integrator.
        """
        for i in self.cells:
            self.cells[ i ].concentrations[ "A" ] = x0[ self.cell2sys_A[ i ] ]
            self.cells[ i ].concentrations[ "H" ] = x0[ self.cell2sys_H[ i ] ]

    def f( self, x, t ):        
        """Integration function.
        
        We are solving a system:
        dy/dt = func(y,t0,...) where y can be a vector.
        
        :parameters:
            arg1 : vector
                The dy/dt vector.
            arg1 : vector
                The t0.
        """        
        def J_A( (i, j), t, x):
            return self.c_D_A*(-A(j,t,x)+A(i,t,x))

        def J_H( (i, j), t, x):
            return self.c_D_H*(-H(j,t,x)+H(i,t,x))
        
        def A( cid, t, x ):
            return x[ self.cell2sys_A[ cid ] ]

        def H( cid, t, x ):
            return x[ self.cell2sys_H[ cid ] ]
                        
        x2 = numarray.zeros(len(x), typecode=numarray.Float32)
        for i in self.cells:
            x2[ self.cell2sys_A[ i ] ] = self.c_rho_A*((A( i,t,x )*A( i,t,x ))/((1+self.c_kappa_A*A( i,t,x )*A( i,t,x ))*H(i,t,x)))-self.c_mu_A*A( i,t,x )+self.c_sigma_A 
            x2[ self.cell2sys_H[ i ] ] = self.c_rho_H*(A( i,t,x )*A( i,t,x ))-self.c_mu_H*H( i,t,x )+self.c_sigma_H 
            for n in self.cell_neighbors( cell=self.cells[ i ] ):
                x2[ self.cell2sys_A[ i ] ] += J_A((n.id,i),t,x)
                x2[ self.cell2sys_H[ i ] ] += J_H((n.id,i),t,x)
        return x2

    def cell_neighbors( self, cell=None ):
        """Cell neighborhood relation.
        
        <Long description of the function functionality.>
        
        :parameters:
            cell : `Cell`
                Cell which neighbors we would like to get.
        :rtype: `Cell`
        :return: Iterator on cells.
        :raise Exception: Thrown when sth. is wrong with cell neighborhood.
        """
        if cell.id == 0:
            yield self.cells[ 1] 
        elif cell.id == len(self.cells)-1:
            yield self.cells[ len(self.cells)-2 ] 
        elif  cell.id < len(self.cells)-1 and cell.id > 0:   
            yield self.cells[ cell.id-1]
            yield self.cells[ cell.id+1]
        else:
            raise KeyError("Cell have corrupted neighborhood..")
    
#sample usage   
s = ReactionDiffusion1DModel(cell_number=100)
for i in range(5):
    s.integrate()
#s.visualise()
#s.step()