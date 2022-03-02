#!/usr/bin/env python
"""One dimention up the hill model.

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
__revision__="$Id: 07-07-06-upTheHill1D.py 7875 2010-02-08 18:24:36Z cokelaer $"


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
        self.h = 100
        self.c_change = 0.002 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 500 # used to drop the loop if convergence not reached before x loops
        self.c_aux_tol=1
        self.c_D_D=0.002
        self.c_D_AT=0.06

        self.c_rho_A =0.001#1
        self.c_rho_H =0.001#1
        self.c_mu_A =0.001#1
        self.c_mu_H =0.00#1
        self.c_sigma_A=0.00#1
        self.c_sigma_H=0.001#1
        self.c_kappa_A=0.00#1
        self.c_kappa_H=0.0002
        self.c_errors=0.1
 
        self.cells={}
        for i in range( cell_number ):
            self.cells[ i ] = Cell( id=i, genes={"A": 1+0.1*random.random(), "H":1 })
            
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
        #getting
        x3, y3 = self.get_right_pin()
        x4, y4 = self.get_left_pin()
        
        # ploting concentration
        for i in range(len(self.cells)):
            x.append(i)
            y1.append(self.cells[ i ].concentrations[ "A" ] )
            y2.append(self.cells[ i ].concentrations[ "H" ] )
        pylab.plot(x, y1, "g", x,y2, "r", x3,y3,"b", x4,y4,"m")
        #pylab.axis( [0,len(self.cells)-1,0,20] )
        pylab.xlabel( "Cells" )
        pylab.ylabel( "Product  quantities" )
        pylab.title( "Initial conditions" )
        pylab.legend(("AUX concentration","PIN concentration","PIN concentration in right","PIN concentration in left" ))
        pylab.show()
                
                
    def get_right_pin( self ):
        """Returns the cordinates of the cells with the H concentration on the right wall. 
        
        <Long description of the function functionality.>
        
        :parameters:
            arg1 : `T`
                <Description of `arg1` meaning>
        :rtype: [float]*[float]
        :return: <Description of ``return_object`` meaning>
        :raise Exception: <Description of situation raising `Exception`>
        """
        x=[]
        y=[]
        for i in self.cells:
            z = 0.
            #for j in self.cell_neighbors( cell=self.cells[ i ] ):
            #    z += j.concentrations[ "A" ]
            #y.append( self.cells[ i ].concentrations[ "H" ]*self.cells[ (i+1)%len(self.cells)].concentrations[ "A" ]/z )
            for j in self.cell_neighbors( cell=self.cells[ i ] ):
                z += math.pow(3, j.concentrations[ "A" ])
            y.append( self.cells[ i ].concentrations[ "H" ]*math.pow(3, self.cells[ (i+1)%len(self.cells)].concentrations[ "A" ] )/z )
            x.append( i )
        return x,y

    def get_left_pin( self ):
        """Returns the cordinates of the cells with the H concentration on the left wall. 
        
        <Long description of the function functionality.>
        
        :parameters:
            arg1 : `T`
                <Description of `arg1` meaning>
        :rtype: [float]*[float]
        :return: <Description of ``return_object`` meaning>
        :raise Exception: <Description of situation raising `Exception`>
        """
        x=[]
        y=[]
        for i in self.cells:
            z = 0.
            #for j in self.cell_neighbors( cell=self.cells[ i ] ):
            #    z += j.concentrations[ "A" ]
            #y.append( self.cells[ i ].concentrations[ "H" ]*self.cells[ (i-1)%len(self.cells)].concentrations[ "A" ]/z )
            for j in self.cell_neighbors( cell=self.cells[ i ] ):
                z += math.pow( 3, j.concentrations[ "A" ])
            y.append( self.cells[ i ].concentrations[ "H" ]*math.pow(3, self.cells[ (i-1)%len(self.cells)].concentrations[ "A" ] )/z )
            x.append( i )
        return x,y
    
    def integrate(self):
        """Integration mechanism using SciPy.
        
        <Long description of the function functionality.> 
        """        
        stable = False
        while not stable:
            print  self.t
            (res,d)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h], rtol=self.c_errors, atol=self.c_errors, full_output=1)#, hmax=0.0001, hmin=0.0001 )
            self.t += self.h                
            stable = self.rate_change( result=res[1] )
            self.update( res[1] )
            print d
            if d["mused"]==2:
                break

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
            return self.c_D_D*(-A(j,t,x)+A(i,t,x))+self.c_D_AT*(-A(j,t,x)*P((j,i), t, x)+A(i,t,x)*P((i,j), t, x))

        def P( (i, j), t, x):
            #Smiths' P
            z = 0.
            for k in self.cell_neighbors( cell=self.cells[ i ] ):
                z += math.pow(3,A(k.id,t,x))
            return PC(i,t,x)*math.pow(3,A(j,t,x))/z

        #def P( (i, j), t, x):
        #    # johnsons' P
        #    z = 0.
        #    for k in self.cell_neighbors( cell=self.cells[ i ] ):
        #        z += A(k.id,t,x)
        #    return PC(i,t,x)*A(j,t,x)/z
        
        def PC( cid, t, x):
            return x[ self.cell2sys_H[ cid ] ]
        
        def A( cid, t, x ):
            return x[ self.cell2sys_A[ cid ] ]

        def H( cid, t, x ):
            return x[ self.cell2sys_H[ cid ] ]
                        
        x2 = numarray.zeros(len(x), typecode=numarray.Float32)
        for i in self.cells:
            x2[ self.cell2sys_A[ i ] ] = self.c_rho_A-self.c_mu_A*A( i,t,x )
            #x2[ self.cell2sys_H[ i ] ] = self.c_rho_H*(A( i,t,x )*A( i,t,x ))-self.c_mu_H*H( i,t,x )+self.c_sigma_H 
            for n in self.cell_neighbors( cell=self.cells[ i ] ):
                x2[ self.cell2sys_A[ i ] ] += J_A((n.id,i),t,x)
                # if 0 there is no feedback between the IAA presence and PIN conc.
                x2[ self.cell2sys_H[ i ] ] += self.c_rho_H - self.c_sigma_H*H(i,t,x) + self.c_kappa_H*A(i,t,x)/(1+A(i,t,x))
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
            yield self.cells[ len(self.cells)-1 ]
        elif cell.id == len(self.cells)-1:
            yield self.cells[ len(self.cells)-2 ]
            yield self.cells[ 0 ]
        elif  cell.id < len(self.cells)-1 and cell.id > 0:   
            yield self.cells[ cell.id-1]
            yield self.cells[ cell.id+1]
        else:
            raise KeyError("Cell have corrupted neighborhood..")
    
#sample usage   
s = ReactionDiffusion1DModel(cell_number=50)
#for i in range(10):
#    s.integrate()
s.visualise()
#s.step()