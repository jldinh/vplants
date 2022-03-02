#!/usr/bin/env python
"""Physiology::transport of auxin.>

<The system for transport of auxin in the tissue .>

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
__revision__="$Id: canalisation.py 7875 2010-02-08 18:24:36Z cokelaer $"


import scipy
import scipy.integrate.odepack
from openalea.mersim.tissue.algo.walled_tissue import *
import PyQt4
import numpy
import openalea.mersim.tools.integration_rk



class PhysInterface(object):
    """Interface for physiology process in the tissue.
    """
    def __init__( self, tissue_system=None):
        self.tissue_system = tissue_system
        self.hist={}
        
    def apply( self ):
        pass

class PhysAuxinTransportModel(PhysInterface):
    def __init__(self, tissue_system = None):
        PhysInterface.__init__( self,tissue_system=tissue_system )

    #def aux_con( self, cell = None, con=None, nbr=None ):
    #    if con == None and nbr==None:    
    #        return self.walled_tissue.tissue.cell_property( cell = cell, property="auxin_level") / self.walled_tissue.tissue.calculate_cell_surface( cell = cell) 
    #    else:
    #        if con == None:
    #            self.walled_tissue.tissue.cell_property( cell = cell, property="auxin_level", value= nbr )
    #        else:
    #            self.walled_tissue.tissue.cell_property( cell = cell, property="auxin_level", value= con*self.walled_tissue.tissue.calculate_cell_surface( cell = cell) )
                
    
    def aux( self, cell, value=None ):
        return auxin_level( wt=self.tissue_system.tissue, cell=cell, value=value )    
    
    def pin( self, cell_edge, value=None ):
        return pin_level( wtt=self.tissue_system.tissue, cell_edge=cell_edge, value=value )


class PhysAuxinTransportModel14(PhysAuxinTransportModel):
    """Model with correct resolution using scipy RK4 method and waiting for
    stabilisation.
    
    The parameters form nonstable 2whorled system
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 5
        self.c_change = 0.0005 #acceptable change could not be smaller to classifie as error.
        
        
        self.c_alpha = 0.0005 #creation
        self.c_beta = 0.0005 #destruction
        self.c_gamma = 0.0075#25 #active flux
        self.c_kappa = 0.05  #diffusion
        
        self.c_lambda = 0.03 # PIN production depanding on flux
        self.c_qmin = 0.005 #min production of PIN
        self.c_theta=0.005 #decay of PIN
        self.c_pin_max=1.2 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.03 #centre evacuate
        self.c_delta = 0.09 #prim evacuate


        self.aux_prim_trs_con = 0.7#0.62
        self.c_initial_aux_value=0.5

        """
        auxin_level == nbr of aux particles in a cell
        auxin_level_1 == change in number of particles of aux
        """
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            print " #: phys aux trans: loop=", i, " time=",self.t
            i+=1
            res= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=0.01, atol=0.001 )
            self.t += self.h                
            stable = self.rate_error( res[0], res[1])
            self.update( res[1] )
            y=[]
            z = 0
            # quantities
            for j in self.cell2sys:
                y.append(res[1][ self.cell2sys[ j ] ] )
                z +=  res[1][ self.cell2sys[ j ] ]
            print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
            y2=[]
            z2=0
            for j in self.wall2sys:
                y2.append(res[1][ self.wall2sys[ j ] ] )
                z2 +=  res[1][ self.wall2sys[ j ] ]
            print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)

        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        t = True
        max = -float("infinity")
        for i in range( len( self.tissue_system.tissue.cells() )):
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
            if self.c_change < abs( xn[i] - xnprim[i] ):
                t=False 
                #break
        print " #: errror =  ", max# abs( xn[i] - xnprim[i] )
        return t

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            ind += 1
        for (s,t) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (s,t) ] = ind
            ind += 1
            self.wall2sys[ (t,s) ] = ind
            ind += 1

    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return (-A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x))#act OK
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ] = self.c_alpha - A(i,t,x)*(self.c_beta+self.c_epsilon*self.i_center_evacuate( i ))#OK
            if self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] -= self.c_delta*A(i,t,x)*self.prim_distance_mod( i )
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += self.c_gamma*J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            x2[ self.wall2sys[(s1,s2)] ] = self.c_lambda*Fi(J((s1,s2),t,x))+self.c_qmin-self.c_theta*P((s1,s2),t,x)
            x2[ self.wall2sys[(s2,s1)] ] = self.c_lambda*Fi(J((s2,s1),t,x))+self.c_qmin-self.c_theta*P((s2,s1),t,x)            
        return x2
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="IC") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        PrC_pos = cell_center( t, cell_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        if x <0 or x>1:
            raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c ) > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y ),  self.aux( cell = x ) ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1


class PhysAuxinTransportModel15(PhysAuxinTransportModel):
    """Model with correct resolution using scipy RK4 method and waiting for
    stabilisation.
    
    The parameters form very stable spiral pattern "de nuvo".
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 5
        self.c_change = 0.0005 #acceptable change could not be smaller to classifie as error.
        
        
        self.c_alpha = 0.0005 #creation
        self.c_beta = 0.0005 #destruction
        self.c_gamma = 0.0075#25 #active flux
        self.c_kappa = 0.05  #diffusion
        
        self.c_lambda = 0.03 # PIN production depanding on flux
        self.c_qmin = 0.005 #min production of PIN
        self.c_theta=0.005 #decay of PIN
        self.c_pin_max=1.3 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.01 #centre evacuate
        self.c_delta = 0.09 #prim evacuate


        self.aux_prim_trs_con = 0.78#0.62
        self.c_initial_aux_value=0.5

        """
        auxin_level == nbr of aux particles in a cell
        auxin_level_1 == change in number of particles of aux
        """
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            print " #: phys aux trans: loop=", i, " time=",self.t
            i+=1
            res= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=0.001, atol=0.0001 )
            self.t += self.h                
            stable = self.rate_error( res[0], res[1])
            self.update( res[1] )
            y=[]
            z = 0
            # quantities
            for j in self.cell2sys:
                y.append(res[1][ self.cell2sys[ j ] ] )
                z +=  res[1][ self.cell2sys[ j ] ]
            print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
            y2=[]
            z2=0
            for j in self.wall2sys:
                y2.append(res[1][ self.wall2sys[ j ] ] )
                z2 +=  res[1][ self.wall2sys[ j ] ]
            print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)

        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        t = True
        max = -float("infinity")
        for i in range( len( self.tissue_system.tissue.cells() )):
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
            if self.c_change < abs( xn[i] - xnprim[i] ):
                t=False 
                #break
        print " #: errror =  ", max# abs( xn[i] - xnprim[i] )
        return t

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            ind += 1
        for (s,t) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (s,t) ] = ind
            ind += 1
            self.wall2sys[ (t,s) ] = ind
            ind += 1

    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return (-A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x))#act OK
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ] = self.c_alpha - A(i,t,x)*(self.c_beta+self.c_epsilon*self.i_center_evacuate( i ))#OK
            if self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] -= self.c_delta*A(i,t,x)*self.prim_distance_mod( i )
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += self.c_gamma*J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            x2[ self.wall2sys[(s1,s2)] ] = self.c_lambda*Fi(J((s1,s2),t,x))+self.c_qmin-self.c_theta*P((s1,s2),t,x)
            x2[ self.wall2sys[(s2,s1)] ] = self.c_lambda*Fi(J((s2,s1),t,x))+self.c_qmin-self.c_theta*P((s2,s1),t,x)            
        return x2
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="IC") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        PrC_pos = cell_center( t, cell_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        if x <0 or x>1:
            raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c ) > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y ),  self.aux( cell = x ) ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1


class PhysAuxinTransportModel16(PhysAuxinTransportModel):
    """Model with correct resolution using scipy RK4 method and waiting for
    stabilisation.
    
    The parameters form very stable spiral pattern "de nuvo".
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 100
        self.c_change = 0.01 #acceptable change could not be smaller to classifie as error.
        
        
        self.c_alpha = 0.0005 #creation
        self.c_beta = 0.0005 #destruction
        self.c_gamma = 0.0075#25 #active flux
        self.c_kappa = 0.05  #diffusion
        
        self.c_lambda = 0.03 # PIN production depanding on flux
        self.c_qmin = 0.005 #min production of PIN
        self.c_theta=0.005 #decay of PIN
        self.c_pin_max=1.3 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.01 #centre evacuate
        self.c_delta = 0.09 #prim evacuate


        self.aux_prim_trs_con = 0.8#0.62
        self.c_initial_aux_value=0.5


        self.c_pin_tol = 0.1*10
        self.c_aux_tol = 0.1*10
        """
        auxin_level == nbr of aux particles in a cell
        auxin_level_1 == change in number of particles of aux
        """
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            print " #: phys aux trans: loop=", i, " time=",self.t
            i+=1
            #res= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=0.1, atol=0.1 )
            res= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol )
            self.t += self.h                
            stable = self.rate_error( res[0], res[1])
            self.update( res[1] )
            y=[]
            z = 0
            # quantities
            for j in self.cell2sys:
                y.append(res[1][ self.cell2sys[ j ] ] )
                z +=  res[1][ self.cell2sys[ j ] ]
            print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
            y2=[]
            z2=0
            for j in self.wall2sys:
                y2.append(res[1][ self.wall2sys[ j ] ] )
                z2 +=  res[1][ self.wall2sys[ j ] ]
            print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)

        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        t = True
        max = -float("infinity")
        for i in range( len( self.tissue_system.tissue.cells() )):
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
            if self.c_change < abs( xn[i] - xnprim[i] ):
                t=False 
                #break
        print " #: errror =  ", max# abs( xn[i] - xnprim[i] )
        return t

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            ind += 1
        for (s,t) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (s,t) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (t,s) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1

    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return (-A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x))#act OK
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ] = self.c_alpha - A(i,t,x)*(self.c_beta+self.c_epsilon*self.i_center_evacuate( i ))#OK
            if self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] -= self.c_delta*A(i,t,x)*self.prim_distance_mod( i )
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += self.c_gamma*J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            x2[ self.wall2sys[(s1,s2)] ] = self.c_lambda*Fi(J((s1,s2),t,x))+self.c_qmin-self.c_theta*P((s1,s2),t,x)
            x2[ self.wall2sys[(s2,s1)] ] = self.c_lambda*Fi(J((s2,s1),t,x))+self.c_qmin-self.c_theta*P((s2,s1),t,x)            
        return x2
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="IC") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        PrC_pos = cell_center( t, cell_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        if x <0 or x>1:
            raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c ) > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y ),  self.aux( cell = x ) ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1


class PhysAuxinTransportModel17(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The more accurate calculation.
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 10
        self.c_change = 0.005 #acceptable change could not be smaller to classifie as error.
        
        
        self.c_alpha = 0.005 #creation
        self.c_beta = 0.005 #destruction
        self.c_gamma = 0.020#075#25 #active flux
        
        self.c_lambda = 200.22 # PIN production depanding on flux
        self.c_qmin = 0.001 #min production of PIN
        self.c_theta=0.001 #decay of PIN
        self.c_pin_max=1.3 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.006 #centre evacuate
        self.c_delta = 0.16 #prim evacuate


        self.aux_prim_trs_con = 0.93#0.62
        self.c_initial_aux_value=0.5


        self.c_pin_tol =0.0001
        self.c_aux_tol = 0.0001
        
        self.c_max_expected_flux = 0.6
        self.c_f_alpha = self.c_theta/self.c_max_expected_flux*self.c_max_expected_flux

    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] )
                    z +=  res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] 
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if min(y)<0 or max(y)>1.1:
                    raise Exception("Calculation problems..")
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )/self.cell2surface[c] > max:
                max=abs( xn[i] - xnprim[i] )/self.cell2surface[c]
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
    def f( self, x, t ):
        def Fi( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                print "max_flux=",x
                return self.c_max_expected_flux*self.c_max_expected_flux*self.c_f_alpha
            return x*x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            return W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta+self.c_epsilon*self.i_center_evacuate( i ) ) #OK
            if self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] -= self.c_delta*A(i,t,x)*self.prim_distance_mod( i )
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += self.c_gamma*J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            x2[ self.wall2sys[(s1,s2)] ] = self.c_lambda*Fi(J((s1,s2),t,x))+self.c_qmin-self.c_theta*P((s1,s2),t,x)
            x2[ self.wall2sys[(s2,s1)] ] = self.c_lambda*Fi(J((s2,s1),t,x))+self.c_qmin-self.c_theta*P((s2,s1),t,x)            
            #x2[ self.wall2sys[(s1,s2)] ] = 0
            #x2[ self.wall2sys[(s2,s1)] ] = 0
        return x2
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="IC") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        PrC_pos = cell_center( t, cell_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        if x <0 or x>1:
            raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c )/self.cell2surface[ c ] > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y )/self.cell2surface[ y ],  self.aux( cell = x )/self.cell2surface[ x ] ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            self.step()



class PhysAuxinTransportModel18(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The more accurate calculation.
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 10
        self.c_change = 0.005 #acceptable change could not be smaller to classifie as error.
        
        
        self.c_alpha = 0.005 #creation
        self.c_beta = 0.005 #destruction
        self.c_gamma = 0.008#075#25 #active flux
        
        self.c_lambda = 2100000 # PIN production depanding on flux
        self.c_qmin = 0.01 #min production of PIN
        self.c_theta=0.01 #decay of PIN
        self.c_pin_max=1.3 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.0001#0.03 #centre evacuate
        self.c_delta = 0.0005#0.16 #prim evacuate


        self.aux_prim_trs_con = 0.94#0.62
        self.c_initial_aux_value=0.5


        self.c_pin_tol =0.001
        self.c_aux_tol = 0.001
        
        self.c_max_expected_flux = 0.001
        self.c_f_alpha = self.c_theta/self.c_max_expected_flux*self.c_max_expected_flux

    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] )
                    z +=  res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] 
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if min(y)<0 or max(y)>1.1:
                    raise Exception("Calculation problems..")
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )/self.cell2surface[c] > max:
                max=abs( xn[i] - xnprim[i] )/self.cell2surface[c]
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            
        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
    def f( self, x, t ):
        def Fi( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                print "max_flux=",x
                return self.c_max_expected_flux*self.c_max_expected_flux*self.c_f_alpha
            return x*x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            return self.c_gamma*W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta)-self.c_epsilon*self.i_center_evacuate( i )  #OK
            if self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] -= self.c_delta*self.prim_distance_mod( i )#*A(i,t,x)
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            x2[ self.wall2sys[(s1,s2)] ] = self.c_lambda*Fi(J((s1,s2),t,x))+self.c_qmin-self.c_theta*P((s1,s2),t,x)
            x2[ self.wall2sys[(s2,s1)] ] = self.c_lambda*Fi(J((s2,s1),t,x))+self.c_qmin-self.c_theta*P((s2,s1),t,x)            
            #x2[ self.wall2sys[(s1,s2)] ] = 0
            #x2[ self.wall2sys[(s2,s1)] ] = 0
        return x2
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="IC") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        PrC_pos = cell_center( t, cell_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        if x <0 or x>1:
            raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c )/self.cell2surface[ c ] > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y )/self.cell2surface[ y ],  self.aux( cell = x )/self.cell2surface[ x ] ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            self.step()
            
            

class PhysAuxinTransportModel19(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The more accurate calculation.
    
    It forms an ALTERNATE pattern. Unfortunatelly the polarisation around primordium is not
    very big. The required params are in model 07-05-23.
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 10
        self.c_change = 0.005 #acceptable change could not be smaller to classifie as error.
        
        
        self.c_alpha = 0.005 #creation
        self.c_beta = 0.005 #destruction
        self.c_gamma = 0.0060#075#25 #active flux
        self.c_gamma_diff = 0.020
        
        self.c_lambda = 500.0 # PIN production depanding on flux
        self.c_global_lambda=50.# PIN production turnover
        self.c_qmin = 0.001 #min production of PIN
        self.c_theta=0.001 #decay of PIN
        self.c_pin_max=1.3 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.0005 #centre evacuate
        self.c_delta =  0.005 #prim evacuate


        self.aux_prim_trs_con = 0.9#0.62
        self.c_initial_aux_value=0.5


        self.c_pin_tol =0.0001
        self.c_aux_tol = 0.0001
        
        self.c_max_expected_flux = 0.006
        self.c_f_alpha = self.c_theta/self.c_max_expected_flux*self.c_max_expected_flux
        
        
        #self.c_gamma = 0.00005#075#25 #active flux
        #self.c_gamma_diff =10000000
        
        #self.c_global_lambda = 1 # PIN turnover coef
        #self.c_lambda = 500 # PIN production depanding on flux
        #self.c_qmin = 0.01 #min production of PIN
        #self.c_theta=0.01 #decay of PIN
        
        #self.c_epsilon=0.00001#0.03 #centre evacuate
        #self.c_delta = 0.0005#0.16 #prim evacuate




    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] )
                    z +=  res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] 
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if min(y)<0 or max(y)>1.1:
                    raise Exception("Calculation problems..")
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )/self.cell2surface[c] > max:
                max=abs( xn[i] - xnprim[i] )/self.cell2surface[c]
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi2( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_max_expected_flux*self.c_f_alpha
            return x*x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )

        def Fi( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_f_alpha
            return x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            #print self.c_gamma*W( (i, j) )/self.cell2overall_wall_length[ i ]*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))    
            return self.c_gamma*W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i )) + self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK W( (i, j) )*
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta)-self.c_epsilon*self.i_center_evacuate( i )  #OK
            if self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] -= self.c_delta*self.prim_distance_mod( i )#*A(i,t,x)
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            x2[ self.wall2sys[(s1,s2)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s1,s2),t,x))+self.c_qmin-self.c_theta*P((s1,s2),t,x))
            x2[ self.wall2sys[(s2,s1)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s2,s1),t,x))+self.c_qmin-self.c_theta*P((s2,s1),t,x))            
            #x2[ self.wall2sys[(s1,s2)] ] = 0
            #x2[ self.wall2sys[(s2,s1)] ] = 0
        return x2
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="IC") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        PrC_pos = cell_center( t, cell_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        if x <0 or x>1:
            raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c )/self.cell2surface[ c ] > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y )/self.cell2surface[ y ],  self.aux( cell = x )/self.cell2surface[ x ] ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            #self.step()
            
            
            


class PhysAuxinTransportModel20(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The more accurate calculation.
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 10
        self.c_change = 0.005 #acceptable change could not be smaller to classifie as error.
        
        
        self.c_alpha = 0.005 #creation
        self.c_beta = 0.005 #destruction
        self.c_gamma = 0.00001#0.0060#075#25 #active flux
        self.c_gamma_diff = 0.020
        
        self.c_lambda = 5000.0 # PIN production depanding on flux
        self.c_global_lambda=5.# PIN production turnover
        self.c_qmin = 0.001 #min production of PIN
        self.c_theta=0.001 #decay of PIN
        self.c_pin_max=1.3 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.00005 #centre evacuate
        self.c_delta =  0.005 #prim evacuate


        self.aux_prim_trs_con = 0.9#0.62
        self.c_initial_aux_value=0.5


        self.c_pin_tol =0.01
        self.c_aux_tol = 0.01
        
        self.c_max_expected_flux = 0.006
        self.c_f_alpha = self.c_theta/self.c_max_expected_flux*self.c_max_expected_flux*5
        
        
        #self.c_gamma = 0.00005#075#25 #active flux
        #self.c_gamma_diff =10000000
        
        #self.c_global_lambda = 1 # PIN turnover coef
        #self.c_lambda = 500 # PIN production depanding on flux
        #self.c_qmin = 0.01 #min production of PIN
        #self.c_theta=0.01 #decay of PIN
        
        #self.c_epsilon=0.00001#0.03 #centre evacuate
        #self.c_delta = 0.0005#0.16 #prim evacuate




    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] )
                    z +=  res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] 
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if min(y)<0 or max(y)>1.1:
                    raise Exception("Calculation problems..")
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )/self.cell2surface[c] > max:
                max=abs( xn[i] - xnprim[i] )/self.cell2surface[c]
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi2( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_max_expected_flux*self.c_f_alpha
            return x*x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )

        def Fi( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_f_alpha
            return x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            #print self.c_gamma*W( (i, j) )/self.cell2overall_wall_length[ i ]*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))    
            return self.c_gamma*W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i )) + self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK W( (i, j) )*
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta)-self.c_epsilon*self.i_center_evacuate( i )  #OK
            if self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] -= self.c_delta*self.prim_distance_mod( i )#*A(i,t,x)
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            x2[ self.wall2sys[(s1,s2)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s1,s2),t,x))+self.c_qmin-self.c_theta*P((s1,s2),t,x))
            x2[ self.wall2sys[(s2,s1)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s2,s1),t,x))+self.c_qmin-self.c_theta*P((s2,s1),t,x))            
            #x2[ self.wall2sys[(s1,s2)] ] = 0
            #x2[ self.wall2sys[(s2,s1)] ] = 0
        return x2
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        PrC_pos = cell_center( t, cell_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        if x <0 or x>1:
            raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c )/self.cell2surface[ c ] > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y )/self.cell2surface[ y ],  self.aux( cell = x )/self.cell2surface[ x ] ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            #self.step()
            
class PhysAuxinTransportModel21(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The more accurate calculation.
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 10
        self.c_change = 0.005 #acceptable change could not be smaller to classifie as error.
        
        
        self.c_alpha = 0.005 #creation
        self.c_beta = 0.005 #destruction
        self.c_gamma = 0.001#0.0060#075#25 #active flux
        self.c_gamma_diff = 0.01#20
        
        self.c_lambda =2500.0 # PIN production depanding on flux
        self.c_global_lambda=5.# PIN production turnover
        self.c_qmin = 0.001 #min production of PIN
        self.c_theta=0.001 #decay of PIN
        self.c_pin_max=1.3 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.00005 #centre evacuate
        self.c_delta =  0.0005 #prim evacuate


        self.aux_prim_trs_con = 0.8#0.62
        self.c_initial_aux_value=0.5


        self.c_pin_tol =0.01
        self.c_aux_tol = 0.01
        
        self.c_max_expected_flux = 0.006
        self.c_f_alpha = self.c_theta/self.c_max_expected_flux*self.c_max_expected_flux*5
        
        
        #self.c_gamma = 0.00005#075#25 #active flux
        #self.c_gamma_diff =10000000
        
        #self.c_global_lambda = 1 # PIN turnover coef
        #self.c_lambda = 500 # PIN production depanding on flux
        #self.c_qmin = 0.01 #min production of PIN
        #self.c_theta=0.01 #decay of PIN
        
        #self.c_epsilon=0.00001#0.03 #centre evacuate
        #self.c_delta = 0.0005#0.16 #prim evacuate




    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] )
                    z +=  res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] 
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                #if min(y)<0 or max(y)>1.1:
                #    raise Exception("Calculation problems..")
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )/self.cell2surface[c] > max:
                max=abs( xn[i] - xnprim[i] )/self.cell2surface[c]
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi2( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_max_expected_flux*self.c_f_alpha
            return x*x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )

        def Fi( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_f_alpha
            return x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            #print self.c_gamma*W( (i, j) )/self.cell2overall_wall_length[ i ]*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))    
            return self.c_gamma*W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i )) + self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK W( (i, j) )*
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta)-self.c_epsilon*self.i_center_evacuate( i )  #OK
            if self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] -= self.c_delta*self.prim_distance_mod( i )#*A(i,t,x)
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            x2[ self.wall2sys[(s1,s2)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s1,s2),t,x))+self.c_qmin-self.c_theta*P((s1,s2),t,x))
            x2[ self.wall2sys[(s2,s1)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s2,s1),t,x))+self.c_qmin-self.c_theta*P((s2,s1),t,x))            
            #x2[ self.wall2sys[(s1,s2)] ] = 0
            #x2[ self.wall2sys[(s2,s1)] ] = 0
        return x2
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        PrC_pos = cell_center( t, cell_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        if x <0 or x>1:
            raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c )/self.cell2surface[ c ] > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y )/self.cell2surface[ y ],  self.aux( cell = x )/self.cell2surface[ x ] ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            #self.step()
            

class PhysAuxinTransportModel22(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The more accurate calculation. The upthe hill variant.
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 10
        self.c_change = 0.005 #acceptable change could not be smaller to classifie as error.
        
        
        self.c_alpha = 0.005 #creation
        self.c_beta = 0.005 #destruction
        self.c_gamma = 0.001#0.0060#075#25 #active flux
        self.c_gamma_diff = 0.01#20
        
        self.c_lambda =5000.0 # PIN production depanding on flux
        self.c_global_lambda=5.# PIN production turnover
        self.c_qmin = 0.001 #min production of PIN
        self.c_theta=0.001 #decay of PIN
        self.c_pin_max=1.3 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.00005 #centre evacuate
        self.c_delta =  0.0005 #prim evacuate


        self.aux_prim_trs_con = 90.9#0.62
        self.c_initial_aux_value=0.5


        self.c_pin_tol =0.01
        self.c_aux_tol = 0.01
        
        self.c_max_expected_flux = 1.
        self.c_f_alpha = self.c_theta/self.c_max_expected_flux*self.c_max_expected_flux*5
        
        
        #self.c_gamma = 0.00005#075#25 #active flux
        #self.c_gamma_diff =10000000
        
        #self.c_global_lambda = 1 # PIN turnover coef
        #self.c_lambda = 500 # PIN production depanding on flux
        #self.c_qmin = 0.01 #min production of PIN
        #self.c_theta=0.01 #decay of PIN
        
        #self.c_epsilon=0.00001#0.03 #centre evacuate
        #self.c_delta = 0.0005#0.16 #prim evacuate




    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] )
                    z +=  res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] 
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                #if min(y)<0 or max(y)>1.1:
                #    raise Exception("Calculation problems..")
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )/self.cell2surface[c] > max:
                max=abs( xn[i] - xnprim[i] )/self.cell2surface[c]
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi2( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_max_expected_flux*self.c_f_alpha
            return x*x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )

        def Fi( x ):
            #return 0
            #x = x-0.7
            if x < 0:
                return 0
            #if x>self.c_max_expected_flux:
            #    #print "max_flux=",x
            #    return 0#self.c_max_expected_flux*self.c_f_alpha
            return x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            #print self.c_gamma*W( (i, j) )/self.cell2overall_wall_length[ i ]*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))    
            return self.c_gamma*W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i )) + self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK W( (i, j) )*
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            #x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta)-self.c_epsilon*self.i_center_evacuate( i )  #OK
            #if self.i_local_evacuate( i ):
            #    x2[ self.cell2sys[ i ] ] -= self.c_delta*self.prim_distance_mod( i )#*A(i,t,x)
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            x2[ self.wall2sys[(s1,s2)] ] = self.c_global_lambda*(self.c_lambda*Fi(A(s1, t, x))+self.c_qmin-self.c_theta*P((s1,s2),t,x))
            x2[ self.wall2sys[(s2,s1)] ] = self.c_global_lambda*(self.c_lambda*Fi(A(s2, t, x))+self.c_qmin-self.c_theta*P((s2,s1),t,x))            
            #x2[ self.wall2sys[(s1,s2)] ] = 0
            #x2[ self.wall2sys[(s2,s1)] ] = 0
        return x2
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        PrC_pos = cell_center( t, cell_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        if x <0 or x>1:
            raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c )/self.cell2surface[ c ] > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y )/self.cell2surface[ y ],  self.aux( cell = x )/self.cell2surface[ x ] ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            #self.step()
            


class PhysAuxinTransportModel23(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The more accurate calculation.
    
    Forming reversed gradient!
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 10
        self.c_change = 0.01 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 40 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.00005 #creation
        self.c_beta = 0.00005 #destruction
        self.c_gamma = 0.01#0.0060#075#25 #active flux
        self.c_gamma_diff = 0.001#20
        
        self.c_lambda =500.0 # PIN production depanding on flux
        self.c_global_lambda=5.# PIN production turnover
        self.c_qmin = 0.001 #min production of PIN
        self.c_theta=0.001 #decay of PIN
        self.c_pin_max=1.3 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.05 #centre evacuate
        self.c_delta =  0.05 #prim evacuate


        self.aux_prim_trs_con = 10#0.8#0.62
        self.c_initial_aux_value=0.5


        self.c_pin_tol =0.01
        self.c_aux_tol = 0.01
        
        self.c_max_expected_flux = 0.006
        self.c_f_alpha = self.c_theta/self.c_max_expected_flux*self.c_max_expected_flux*5
        
        
        #self.c_gamma = 0.00005#075#25 #active flux
        #self.c_gamma_diff =10000000
        
        #self.c_global_lambda = 1 # PIN turnover coef
        #self.c_lambda = 500 # PIN production depanding on flux
        #self.c_qmin = 0.01 #min production of PIN
        #self.c_theta=0.01 #decay of PIN
        
        #self.c_epsilon=0.00001#0.03 #centre evacuate
        #self.c_delta = 0.0005#0.16 #prim evacuate




    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] )
                    z +=  res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] 
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                #if min(y)<0 or max(y)>1.1:
                #    raise Exception("Calculation problems..")
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )/self.cell2surface[c] > max:
                max=abs( xn[i] - xnprim[i] )/self.cell2surface[c]
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi2( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_max_expected_flux*self.c_f_alpha
            return x*x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )

        def Fi( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_f_alpha
            return x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            #print self.c_gamma*W( (i, j) )/self.cell2overall_wall_length[ i ]*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))    
            return self.c_gamma*W( (i, j) )*(-A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)/S( j )+A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)/S( i )) + self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK W( (i, j) )*
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta)-self.c_epsilon*self.i_center_evacuate( i )*A(i,t,x)  #OK
            if self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] -= A(i,t,x)*self.c_delta*self.prim_distance_mod( i )#*A(i,t,x)
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            x2[ self.wall2sys[(s1,s2)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s1,s2),t,x))+self.c_qmin-self.c_theta*P((s1,s2),t,x))
            x2[ self.wall2sys[(s2,s1)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s2,s1),t,x))+self.c_qmin-self.c_theta*P((s2,s1),t,x))            
            #x2[ self.wall2sys[(s1,s2)] ] = 0
            #x2[ self.wall2sys[(s2,s1)] ] = 0
        return x2
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        PrC_pos = cell_center( t, cell_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        if x <0 or x>1:
            raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c )/self.cell2surface[ c ] > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y )/self.cell2surface[ y ],  self.aux( cell = x )/self.cell2surface[ x ] ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            #self.step()


class PhysAuxinTransportModel24(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The more accurate calculation.
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 5
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 200 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.00005 #creation
        self.c_beta = 0.00005 #destruction
        self.c_gamma = 0.001#0.0060#075#25 #active flux
        self.c_gamma_diff = 0.0001#20
        
        self.c_lambda =5000.0 # PIN production depanding on flux
        self.c_global_lambda=5.# PIN production turnover
        self.c_qmin = 0.001 #min production of PIN
        self.c_theta=0.001 #decay of PIN
        self.c_pin_max=1.3 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.03 #centre evacuate
        self.c_delta =  0.05 #prim evacuate


        self.aux_prim_trs_con = 0.84#0.62
        self.c_initial_aux_value=0.5


        self.c_pin_tol =0.01
        self.c_aux_tol = 0.01
        
        self.c_max_expected_flux = 0.001
        self.c_f_alpha = self.c_theta/self.c_max_expected_flux*self.c_max_expected_flux*5
        
        self.c_prim_time_slowdown = 500
        self.c_center_time_slowdown = 500
        
        
        #self.c_gamma = 0.00005#075#25 #active flux
        #self.c_gamma_diff =10000000
        
        #self.c_global_lambda = 1 # PIN turnover coef
        #self.c_lambda = 500 # PIN production depanding on flux
        #self.c_qmin = 0.01 #min production of PIN
        #self.c_theta=0.01 #decay of PIN
        
        #self.c_epsilon=0.00001#0.03 #centre evacuate
        #self.c_delta = 0.0005#0.16 #prim evacuate




    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] )
                    z +=  res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] 
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                #if min(y)<0 or max(y)>1.1:
                #    raise Exception("Calculation problems..")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )/self.cell2surface[c] > max:
                max=abs( xn[i] - xnprim[i] )/self.cell2surface[c]
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi2( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_max_expected_flux*self.c_f_alpha
            return x*x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )

        def Fi( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_f_alpha
            return x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            #print self.c_gamma*W( (i, j) )/self.cell2overall_wall_length[ i ]*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))    
            return self.c_gamma*W( (i, j) )*(-A(j,t,x)/(1+A(j,t,x)/S( j ))*P((j,i),t,x)/S( j )+A(i,t,x)/(1+A(i,t,x)/S( i ))*P((i,j),t,x)/S( i )) + self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK W( (i, j) )*
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta)-self.c_epsilon*self.i_center_evacuate( i )*A(i,t,x)*self.center_time_mod()  #OK
            if self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] -= A(i,t,x)*self.c_delta*self.prim_distance_mod( i )#*A(i,t,x)
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            #if P((s1,s2),t,x) < self.c_pin_max:
            x2[ self.wall2sys[(s1,s2)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s1,s2),t,x))+self.c_qmin-self.c_theta*P((s1,s2),t,x))
            #else: x2[ self.wall2sys[(s1,s2)] ]= 0
            #if P((s2,s1),t,x) < self.c_pin_max:
            x2[ self.wall2sys[(s2,s1)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s2,s1),t,x))+self.c_qmin-self.c_theta*P((s2,s1),t,x))            
            #else: x2[ self.wall2sys[(s2,s1)] ]= 0
            #x2[ self.wall2sys[(s1,s2)] ] = 0
            #x2[ self.wall2sys[(s2,s1)] ] = 0
        return x2

    def center_time_mod( self ):
        if self.t < self.c_center_time_slowdown:
            return float(self.t)/self.c_center_time_slowdown
        else:
            return 1.
        
    def prim_time_mod( self, prz=-1 ):
        """Changes the factor of influance of the young prim.
        
        Provides smoothing effect for boundary conditions.
        
        :parameters:
            prz : `int`
                Id of cell which belongs to PrZ.
        :rtype: `float`
        :return: Value from [0,1] which depands on time of the primordium creation
        :raise Exception: <Description of situation raising `Exception`>
        """
        t = self.tissue_system.tissue.tissue_property( "prims2time" )
        if t[ prz ]+self.c_prim_time_slowdown < self.t:
            return (float( t[ prz ])+self.c_prim_time_slowdown) / self.t
        else:
            return 1.
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        for i in t.cells():
            if t.cell_property( cell=i, property="PrC")>0:
                if t.cell_property( cell=i, property="PrC")==t.cell_property( cell=cell_id, property="PrZ"):
                    prim_id = i
                    break
        PrC_pos = cell_center( t, prim_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        #if x <0 or x>1:            
            #raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        if x <0:
            return 0
        if x >1:
            return 1
    
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c )/self.cell2surface[ c ] > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y )/self.cell2surface[ y ],  self.aux( cell = x )/self.cell2surface[ x ] ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            d = t.tissue_property( property="prim2time")
            d[ c ] = self.t
            t.tissue_property( property="prim2time", value=d)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            #self.step()



class PhysReactionDiffusion1(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The more accurate calculation.
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        #self.t = 0
        #self.h = 2
        #self.c_change = 0.002 #acceptable change could not be smaller to classifie as error.
        #self.c_break_cond = 500 # used to drop the loop if convergence not reached before x loops
        #self.c_aux_tol=1
        #self.c_D_A=0.005
        #self.c_D_H=0.2
        #
        #self.c_rho_A =0.01
        #self.c_rho_H =0.02
        #self.c_mu_A =0.01
        #self.c_mu_H =0.02
        #self.c_sigma_A=0.0#1
        #self.c_sigma_H=0.
        #self.c_kappa_A=0.001
        
        self.nbr_prim=1
        self.t = 0
        self.h = 2
        self.c_change = 0.002 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 500 # used to drop the loop if convergence not reached before x loops
        self.c_aux_tol=1
        self.c_D_A=0.01
        self.c_D_H=0.4

        self.c_rho_A =0.01
        self.c_rho_H =0.02
        self.c_mu_A =0.01
        self.c_mu_H =0.02
        self.c_sigma_A=0.0#1
        self.c_sigma_H=0.0#2
        self.c_kappa_A=0.00#1
        #
        #self.c_D_A=0.00005
        #self.c_D_H=0.002
        #
        #self.c_rho_A =0.01
        #self.c_rho_H =0.02
        #self.c_mu_A =0.003
        #self.c_mu_H =0.05
        #self.c_sigma_A=0.00#1
        #self.c_sigma_H=0.00#1
        #self.c_kappa_A=0.00#1

        
    def inh( self, cell, value=None ):
        if not value:
            return self.system.tissue.cell_property( cell=cell, property="inh" )
        else:
            self.system.tissue.cell_property( cell=cell, property="inh", value=value )
            
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                y2=[]
                z2=0
                # quantitie
                for j in self.cell2sys:
                #    y.append(res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] )
                #    z +=  res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] 
                #print "  #: A qua avg: ", z/len( self.tissue_system.tissue.cells() ), "A con min:", min(y), "A con max:", max(y)
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                    y2.append(res[1][ self.cell2sysH[ j ] ] )
                    z2 +=  res[1][ self.cell2sysH[ j ] ]

                print "  #: A qua avg: ", z/len( self.tissue_system.tissue.cells() ), "A con min:", min(y), "A con max:", max(y)
                print "  #: H qua avg: ", z2/len( self.tissue_system.tissue.cells() ), "H con min:", min(y2), "H con max:", max(y2)
                print self.info
                #if min(y)<0 or max(y)>1.1:
                #    raise Exception("Calculation problems..")
            except KeyboardInterrupt:
                return
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
            self.inh( cell=i, value= x[ self.cell2sysH[ i ] ] )
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            #if abs( xn[i] - xnprim[i] )/self.cell2surface[c] > max:
            #    max=abs( xn[i] - xnprim[i] )/self.cell2surface[c]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( 2*len(t.cells()) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            x0[ self.cell2sysH[ i ] ] = self.inh( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.cell2sysH = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol =  self.c_aux_tol 
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0
            self.cell2sysH[ i ] = ind
            ind += 1

    
    def f( self, x, t ):        
        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return self.c_D_A*(-A(j,t,x)+A(i,t,x))

        def JH( (i, j), t, x):
            return self.c_D_H*(-H(j,t,x)+H(i,t,x))
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]

        def H( cid, t, x ):
            return x[ self.cell2sysH[ cid ] ]
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ] = 0 
            x2[ self.cell2sysH[ i ] ] = 0 
            x2[ self.cell2sys[ i ] ] = self.c_rho_A*((A( i,t,x )*A( i,t,x ))/((1+self.c_kappa_A*A( i,t,x )*A( i,t,x ))*H(i,t,x)))-self.c_mu_A*A( i,t,x )+self.c_sigma_A 
            x2[ self.cell2sysH[ i ] ] = self.c_rho_H*(A( i,t,x )*A( i,t,x ))-self.c_mu_H*H( i,t,x )+self.c_sigma_H 
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
                x2[ self.cell2sysH[ i ] ] += JH((n,i),t,x)
        return x2
            
class PhysAuxinTransportModel25(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The auxin production in the boubdary.
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 5
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 200 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.00005 #creation
        self.c_beta = 0.00005 #destruction
        self.c_gamma = 0.001#0.0060#075#25 #active flux
        self.c_gamma_diff = 0.0001#20
        
        self.c_lambda =5000.0 # PIN production depanding on flux
        self.c_global_lambda=5.# PIN production turnover
        self.c_qmin = 0.001 #min production of PIN
        self.c_theta=0.001 #decay of PIN
        self.c_pin_max=1.3 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.03 #centre evacuate
        self.c_delta =  0.05 #prim evacuate


        self.aux_prim_trs_con = 0.84#0.62
        self.c_initial_aux_value=0.5


        self.c_pin_tol =0.01
        self.c_aux_tol = 0.01
        
        self.c_max_expected_flux = 0.001
        self.c_f_alpha = self.c_theta/self.c_max_expected_flux*self.c_max_expected_flux*5
        
        self.c_prim_time_slowdown = 500
        self.c_center_time_slowdown = 500
        
        
        #self.c_gamma = 0.00005#075#25 #active flux
        #self.c_gamma_diff =10000000
        
        #self.c_global_lambda = 1 # PIN turnover coef
        #self.c_lambda = 500 # PIN production depanding on flux
        #self.c_qmin = 0.01 #min production of PIN
        #self.c_theta=0.01 #decay of PIN
        
        #self.c_epsilon=0.00001#0.03 #centre evacuate
        #self.c_delta = 0.0005#0.16 #prim evacuate




    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] )
                    z +=  res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] 
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                #if min(y)<0 or max(y)>1.1:
                #    raise Exception("Calculation problems..")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )/self.cell2surface[c] > max:
                max=abs( xn[i] - xnprim[i] )/self.cell2surface[c]
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi2( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_max_expected_flux*self.c_f_alpha
            return x*x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )

        def Fi( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_f_alpha
            return x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            #print self.c_gamma*W( (i, j) )/self.cell2overall_wall_length[ i ]*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))    
            return self.c_gamma*W( (i, j) )*(-A(j,t,x)/(1+A(j,t,x)/S( j ))*P((j,i),t,x)/S( j )+A(i,t,x)/(1+A(i,t,x)/S( i ))*P((i,j),t,x)/S( i )) + self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK W( (i, j) )*
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta)-self.c_epsilon*self.i_center_evacuate( i )*A(i,t,x)*self.center_time_mod()  #OK
            if self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] -= A(i,t,x)*self.c_delta*self.prim_distance_mod( i )#*A(i,t,x)
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            #if P((s1,s2),t,x) < self.c_pin_max:
            x2[ self.wall2sys[(s1,s2)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s1,s2),t,x))+self.c_qmin-self.c_theta*P((s1,s2),t,x))
            #else: x2[ self.wall2sys[(s1,s2)] ]= 0
            #if P((s2,s1),t,x) < self.c_pin_max:
            x2[ self.wall2sys[(s2,s1)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s2,s1),t,x))+self.c_qmin-self.c_theta*P((s2,s1),t,x))            
            #else: x2[ self.wall2sys[(s2,s1)] ]= 0
            #x2[ self.wall2sys[(s1,s2)] ] = 0
            #x2[ self.wall2sys[(s2,s1)] ] = 0
        return x2

    def center_time_mod( self ):
        if self.t < self.c_center_time_slowdown:
            return float(self.t)/self.c_center_time_slowdown
        else:
            return 1.
        
    def prim_time_mod( self, prz=-1 ):
        """Changes the factor of influance of the young prim.
        
        Provides smoothing effect for boundary conditions.
        
        :parameters:
            prz : `int`
                Id of cell which belongs to PrZ.
        :rtype: `float`
        :return: Value from [0,1] which depands on time of the primordium creation
        :raise Exception: <Description of situation raising `Exception`>
        """
        t = self.tissue_system.tissue.tissue_property( "prims2time" )
        if t[ prz ]+self.c_prim_time_slowdown < self.t:
            return (float( t[ prz ])+self.c_prim_time_slowdown) / self.t
        else:
            return 1.
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        for i in t.cells():
            if t.cell_property( cell=i, property="PrC")>0:
                if t.cell_property( cell=i, property="PrC")==t.cell_property( cell=cell_id, property="PrZ"):
                    prim_id = i
                    break
        PrC_pos = cell_center( t, prim_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        #if x <0 or x>1:            
            #raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        if x <0:
            return 0
        if x >1:
            return 1
    
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c )/self.cell2surface[ c ] > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y )/self.cell2surface[ y ],  self.aux( cell = x )/self.cell2surface[ x ] ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            d = t.tissue_property( property="prim2time")
            d[ c ] = self.t
            t.tissue_property( property="prim2time", value=d)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            #self.step()



class PhysAuxinLongitudianTransportModel1(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The auxin production in the boubdary.
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 5
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 200 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.05 #creation
        self.c_beta = 0.05 #destruction
        self.c_gamma = 0.01#0.0060#075#25 #active flux
        self.c_gamma_diff = 0.001#20
        
        self.c_lambda =5000.0 # PIN production depanding on flux
        self.c_global_lambda=5.# PIN production turnover
        self.c_qmin = 0.001 #min production of PIN
        self.c_theta=0.001 #decay of PIN
        self.c_pin_max=1.3 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.03 #centre evacuate
        self.c_delta =  0.05 #prim evacuate


        self.aux_prim_trs_con = 0.84#0.62
        self.c_initial_aux_value=0.5


        self.c_pin_tol =1
        self.c_aux_tol = 1
        
        self.c_max_expected_flux = 0.0001
        self.c_f_alpha = self.c_theta/self.c_max_expected_flux*self.c_max_expected_flux*5
        
        self.c_prim_time_slowdown = 500
        self.c_center_time_slowdown = 500
        
        
        #self.c_gamma = 0.00005#075#25 #active flux
        #self.c_gamma_diff =10000000
        
        #self.c_global_lambda = 1 # PIN turnover coef
        #self.c_lambda = 500 # PIN production depanding on flux
        #self.c_qmin = 0.01 #min production of PIN
        #self.c_theta=0.01 #decay of PIN
        
        #self.c_epsilon=0.00001#0.03 #centre evacuate
        #self.c_delta = 0.0005#0.16 #prim evacuate




    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] )
                    z +=  res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] 
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                #if min(y)<0 or max(y)>1.1:
                #    raise Exception("Calculation problems..")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )/self.cell2surface[c] > max:
                max=abs( xn[i] - xnprim[i] )/self.cell2surface[c]
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi2( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_max_expected_flux*self.c_f_alpha
            return x*x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )

        def Fi( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_f_alpha
            return x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            #print self.c_gamma*W( (i, j) )/self.cell2overall_wall_length[ i ]*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))    
            return self.c_gamma*W( (i, j) )*(-A(j,t,x)/(1+A(j,t,x)/S( j ))*P((j,i),t,x)/S( j )+A(i,t,x)/(1+A(i,t,x)/S( i ))*P((i,j),t,x)/S( i )) + self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK W( (i, j) )*
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return 1
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            #x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta)-self.c_epsilon*self.i_center_evacuate( i )*A(i,t,x)*self.center_time_mod()  #OK
            #x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta)-self.c_epsilon*self.i_center_evacuate( i )*A(i,t,x)*self.center_time_mod()  #OK
            if t.cell_property( i, "CZ" ):
                x2[ self.cell2sys[ i ] ] -= 0.05*A(i,t,x)
            if self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] += S( i )*self.c_alpha-A(i,t,x)*(self.c_beta)#*A(i,t,x)
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            #if P((s1,s2),t,x) < self.c_pin_max:
            x2[ self.wall2sys[(s1,s2)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s1,s2),t,x))+self.c_qmin-self.c_theta*P((s1,s2),t,x))
            #else: x2[ self.wall2sys[(s1,s2)] ]= 0
            #if P((s2,s1),t,x) < self.c_pin_max:
            x2[ self.wall2sys[(s2,s1)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s2,s1),t,x))+self.c_qmin-self.c_theta*P((s2,s1),t,x))            
            #else: x2[ self.wall2sys[(s2,s1)] ]= 0
            #x2[ self.wall2sys[(s1,s2)] ] = 0
            #x2[ self.wall2sys[(s2,s1)] ] = 0
        return x2

    def center_time_mod( self ):
        if self.t < self.c_center_time_slowdown:
            return float(self.t)/self.c_center_time_slowdown
        else:
            return 1.
        
    def prim_time_mod( self, prz=-1 ):
        """Changes the factor of influance of the young prim.
        
        Provides smoothing effect for boundary conditions.
        
        :parameters:
            prz : `int`
                Id of cell which belongs to PrZ.
        :rtype: `float`
        :return: Value from [0,1] which depands on time of the primordium creation
        :raise Exception: <Description of situation raising `Exception`>
        """
        t = self.tissue_system.tissue.tissue_property( "prims2time" )
        if t[ prz ]+self.c_prim_time_slowdown < self.t:
            return (float( t[ prz ])+self.c_prim_time_slowdown) / self.t
        else:
            return 1.
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        for i in t.cells():
            if t.cell_property( cell=i, property="PrC")>0:
                if t.cell_property( cell=i, property="PrC")==t.cell_property( cell=cell_id, property="PrZ"):
                    prim_id = i
                    break
        PrC_pos = cell_center( t, prim_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        #if x <0 or x>1:            
            #raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        if x <0:
            return 0
        if x >1:
            return 1
    
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c )/self.cell2surface[ c ] > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y )/self.cell2surface[ y ],  self.aux( cell = x )/self.cell2surface[ x ] ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            d = t.tissue_property( property="prim2time")
            d[ c ] = self.t
            t.tissue_property( property="prim2time", value=d)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            #self.step()


class PhysAuxinTransportModel28(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The up-the-hill hypo
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 5
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 200 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.05 #creation
        self.c_beta = 0.05 #destruction
        self.c_gamma = 0.008#0.0060#075#25 #active flux
        self.c_gamma_diff = 0.001#20
        
        self.c_lambda =1.0 # PIN production depanding on flux
        self.c_global_lambda=1.# PIN production turnover
        self.c_qmin = 0.001 #min production of PIN
        self.c_theta=0.001 #decay of PIN
        self.c_pin_max=1.3 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.03 #centre evacuate
        self.c_delta =  0.05 #prim evacuate


        self.aux_prim_trs_con = 0.84#0.62
        self.c_initial_aux_value=0.5


        self.c_pin_tol =0.001
        self.c_aux_tol = 0.001
        
        self.c_max_expected_flux = 2.
        self.c_f_alpha = self.c_theta/self.c_max_expected_flux*self.c_max_expected_flux*5
        
        self.c_prim_time_slowdown = 500
        self.c_center_time_slowdown = 500
        
        
        #self.c_gamma = 0.00005#075#25 #active flux
        #self.c_gamma_diff =10000000
        
        #self.c_global_lambda = 1 # PIN turnover coef
        #self.c_lambda = 500 # PIN production depanding on flux
        #self.c_qmin = 0.01 #min production of PIN
        #self.c_theta=0.01 #decay of PIN
        
        #self.c_epsilon=0.00001#0.03 #centre evacuate
        #self.c_delta = 0.0005#0.16 #prim evacuate




    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] )
                    z +=  res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] 
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                #if min(y)<0 or max(y)>1.1:
                #    raise Exception("Calculation problems..")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)

        for wid in t.cell_edges():
            (c1,c2)=wid
            for wid in [(c1,c2),(c2,c1)]:
                (c1,c2)=wid
                z = 0.
                for u in self.system.tissue.cell_neighbors( c1 ):
                    z+= self.cell_edge2wall_length[ (c1,u) ]*(math.pow(2,self.aux(u)/self.cell2surface[ u ]))
                z= 1*self.cell_edge2wall_length[ (c1,c2) ]*(math.pow(2,self.aux(c2)/self.cell2surface[ c2 ]))/z
                self.pin( cell_edge=(c1,c2), value=z)
            

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )/self.cell2surface[c] > max:
                max=abs( xn[i] - xnprim[i] )/self.cell2surface[c]
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        #for i in t.cell_edges():
        #    (s,t)=i
        #    x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
        #    x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi2( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_max_expected_flux*self.c_f_alpha
            return x*x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )

        def Fi( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_f_alpha
            return x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )
        
        #def P( wid, t, x):
        #    (i,j)=wid
        #    z = 0.
        #    for u in self.system.tissue.cell_neighbors( i ):
        #        z+= W((i,u))*(math.pow(2,A(u,t,x)/S(u)))
        #    return 1*W(wid)*(math.pow(2,A(j,t,x)/S(j)))/z
        #    #return x[ self.wall2sys[ wid ] ] 

        def P( wid, t, x):
            (i,j)=wid
            z = 0.
            for u in self.system.tissue.cell_neighbors( i ):
                z+= C(u,t,x)
            return 1*C(j,t,x)/z
        
        def C( i, t, x):
            return A(i,t,x)/S(i)
        
        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            #print self.c_gamma*W( (i, j) )/self.cell2overall_wall_length[ i ]*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))    
            #return self.c_gamma*W( (i, j) )*(-A(j,t,x)/(1+A(j,t,x)/S( j ))*P((j,i),t,x)/S( j )+A(i,t,x)/(1+A(i,t,x)/S( i ))*P((i,j),t,x)/S( i )) + self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            return self.c_gamma*(-A(j,t,x)/(S( j )+A(j,t,x))*P((j,i),t,x)+A(i,t,x)/(S(i)+A(i,t,x))*P((i,j),t,x)) + self.c_gamma_diff*(-C(j,t,x)+C(i,t,x))#act OK
            #return self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK W( (i, j) )*
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            #x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta)#-self.c_epsilon*self.i_center_evacuate( i )*A(i,t,x)*self.center_time_mod()  #OK
            #x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta)-self.c_epsilon*self.i_center_evacuate( i )*A(i,t,x)*self.center_time_mod()  #OK
            #if t.cell_property( i, "CZ" ):
            #    x2[ self.cell2sys[ i ] ] -= 0.05*A(i,t,x)
            #if self.i_local_evacuate( i ):
            #    x2[ self.cell2sys[ i ] ] += S( i )*self.c_alpha-A(i,t,x)*(self.c_beta)#*A(i,t,x)
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        #for i in t.cell_edges():
        #    (s1,s2)=i
        #    #if P((s1,s2),t,x) < self.c_pin_max:
        #    x2[ self.wall2sys[(s1,s2)] ] = self.c_global_lambda*(self.c_lambda*Fi(A(s2,t,x)/S(s2))+self.c_qmin-self.c_theta*P((s1,s2),t,x))
        #    #else: x2[ self.wall2sys[(s1,s2)] ]= 0
        #    #if P((s2,s1),t,x) < self.c_pin_max:
        #    x2[ self.wall2sys[(s2,s1)] ] = self.c_global_lambda*(self.c_lambda*Fi(A(s1,t,x)/S(s1))+self.c_qmin-self.c_theta*P((s2,s1),t,x))            
        #    #else: x2[ self.wall2sys[(s2,s1)] ]= 0
        #    #x2[ self.wall2sys[(s1,s2)] ] = 0
        #    #x2[ self.wall2sys[(s2,s1)] ] = 0
        return x2

    def center_time_mod( self ):
        if self.t < self.c_center_time_slowdown:
            return float(self.t)/self.c_center_time_slowdown
        else:
            return 1.
        
    def prim_time_mod( self, prz=-1 ):
        """Changes the factor of influance of the young prim.
        
        Provides smoothing effect for boundary conditions.
        
        :parameters:
            prz : `int`
                Id of cell which belongs to PrZ.
        :rtype: `float`
        :return: Value from [0,1] which depands on time of the primordium creation
        :raise Exception: <Description of situation raising `Exception`>
        """
        t = self.tissue_system.tissue.tissue_property( "prims2time" )
        if t[ prz ]+self.c_prim_time_slowdown < self.t:
            return (float( t[ prz ])+self.c_prim_time_slowdown) / self.t
        else:
            return 1.
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        for i in t.cells():
            if t.cell_property( cell=i, property="PrC")>0:
                if t.cell_property( cell=i, property="PrC")==t.cell_property( cell=cell_id, property="PrZ"):
                    prim_id = i
                    break
        PrC_pos = cell_center( t, prim_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        #if x <0 or x>1:            
            #raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        if x <0:
            return 0
        if x >1:
            return 1
    
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c )/self.cell2surface[ c ] > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y )/self.cell2surface[ y ],  self.aux( cell = x )/self.cell2surface[ x ] ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            d = t.tissue_property( property="prim2time")
            d[ c ] = self.t
            t.tissue_property( property="prim2time", value=d)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            #self.step()


class PhysAuxinTransportModel29(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The more accurate calculation.
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 5
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 200 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.00005 #creation
        self.c_beta = 0.00005 #destruction
        self.c_gamma = 0.001#0.0060#075#25 #active flux
        self.c_gamma_diff = 0.0001#20
        
        self.c_lambda =5000.0 # PIN production depanding on flux
        self.c_global_lambda=5.# PIN production turnover
        self.c_qmin = 0.001 #min production of PIN
        self.c_theta=0.001 #decay of PIN
        self.c_pin_max=1.3 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.03 #centre evacuate
        self.c_delta =  0.05 #prim evacuate


        self.aux_prim_trs_con = 0.84#0.62
        self.c_initial_aux_value=0.5


        self.c_pin_tol =0.01
        self.c_aux_tol = 0.01
        
        self.c_max_expected_flux = 0.001
        self.c_f_alpha = self.c_theta/self.c_max_expected_flux*self.c_max_expected_flux*5
        
        self.c_prim_time_slowdown = 500
        self.c_center_time_slowdown = 500
        
        
        #self.c_gamma = 0.00005#075#25 #active flux
        #self.c_gamma_diff =10000000
        
        #self.c_global_lambda = 1 # PIN turnover coef
        #self.c_lambda = 500 # PIN production depanding on flux
        #self.c_qmin = 0.01 #min production of PIN
        #self.c_theta=0.01 #decay of PIN
        
        #self.c_epsilon=0.00001#0.03 #centre evacuate
        #self.c_delta = 0.0005#0.16 #prim evacuate




    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] )
                    z +=  res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] 
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                #if min(y)<0 or max(y)>1.1:
                #    raise Exception("Calculation problems..")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )/self.cell2surface[c] > max:
                max=abs( xn[i] - xnprim[i] )/self.cell2surface[c]
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi2( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_max_expected_flux*self.c_f_alpha
            return x*x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )

        def Fi( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_f_alpha
            return x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            #print self.c_gamma*W( (i, j) )/self.cell2overall_wall_length[ i ]*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))    
            return self.c_gamma*W( (i, j) )*(-A(j,t,x)/(1+A(j,t,x)/S( j ))*P((j,i),t,x)/S( j )+A(i,t,x)/(1+A(i,t,x)/S( i ))*P((i,j),t,x)/S( i )) + self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK W( (i, j) )*
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta)-self.c_epsilon*self.i_center_evacuate( i )*A(i,t,x)*self.center_time_mod()  #OK
            if self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] -= A(i,t,x)*self.c_delta*self.prim_distance_mod( i )#*A(i,t,x)
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            #if P((s1,s2),t,x) < self.c_pin_max:
            x2[ self.wall2sys[(s1,s2)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s1,s2),t,x))+self.c_qmin-self.c_theta*P((s1,s2),t,x))
            #else: x2[ self.wall2sys[(s1,s2)] ]= 0
            #if P((s2,s1),t,x) < self.c_pin_max:
            x2[ self.wall2sys[(s2,s1)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s2,s1),t,x))+self.c_qmin-self.c_theta*P((s2,s1),t,x))            
            #else: x2[ self.wall2sys[(s2,s1)] ]= 0
            #x2[ self.wall2sys[(s1,s2)] ] = 0
            #x2[ self.wall2sys[(s2,s1)] ] = 0
        return x2

    def center_time_mod( self ):
        if self.t < self.c_center_time_slowdown:
            return float(self.t)/self.c_center_time_slowdown
        else:
            return 1.
        
    def prim_time_mod( self, prz=-1 ):
        """Changes the factor of influance of the young prim.
        
        Provides smoothing effect for boundary conditions.
        
        :parameters:
            prz : `int`
                Id of cell which belongs to PrZ.
        :rtype: `float`
        :return: Value from [0,1] which depands on time of the primordium creation
        :raise Exception: <Description of situation raising `Exception`>
        """
        t = self.tissue_system.tissue.tissue_property( "prims2time" )
        if t[ prz ]+self.c_prim_time_slowdown < self.t:
            return (float( t[ prz ])+self.c_prim_time_slowdown) / self.t
        else:
            return 1.
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        for i in t.cells():
            if t.cell_property( cell=i, property="PrC")>0:
                if t.cell_property( cell=i, property="PrC")==t.cell_property( cell=cell_id, property="PrZ"):
                    prim_id = i
                    break
        PrC_pos = cell_center( t, prim_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        #if x <0 or x>1:            
            #raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        if x <0:
            return 0
        if x >1:
            return 1
    
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c )/self.cell2surface[ c ] > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y )/self.cell2surface[ y ],  self.aux( cell = x )/self.cell2surface[ x ] ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            d = t.tissue_property( property="prim2time")
            d[ c ] = self.t
            t.tissue_property( property="prim2time", value=d)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            #self.step()



class PhysAuxinTransportModel30(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The up-the-hill hypo based on 1d params
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 5
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 200 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.02 #creation
        self.c_beta = 0.006 #destruction
        self.c_gamma = 0.1#0.008#0.0060#075#25 #active flux
        self.c_gamma_diff = 0.05#0.001#20
        
        self.c_lambda =1.0 # PIN production depanding on flux
        self.c_global_lambda=1.# PIN production turnover
        self.c_qmin = 0.001 #min production of PIN
        self.c_theta=0.001 #decay of PIN
        self.c_pin_max=1.3 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.03 #centre evacuate
        self.c_delta =  0.05 #prim evacuate


        self.aux_prim_trs_con = 0.84#0.62
        self.c_initial_aux_value=0.5


        self.c_pin_tol =0.001
        self.c_aux_tol = 0.001
        
        self.c_max_expected_flux = 2.
        self.c_f_alpha = self.c_theta/self.c_max_expected_flux*self.c_max_expected_flux*5
        
        self.c_prim_time_slowdown = 500
        self.c_center_time_slowdown = 500
        
        
        #self.c_gamma = 0.00005#075#25 #active flux
        #self.c_gamma_diff =10000000
        
        #self.c_global_lambda = 1 # PIN turnover coef
        #self.c_lambda = 500 # PIN production depanding on flux
        #self.c_qmin = 0.01 #min production of PIN
        #self.c_theta=0.01 #decay of PIN
        
        #self.c_epsilon=0.00001#0.03 #centre evacuate
        #self.c_delta = 0.0005#0.16 #prim evacuate

        self.c_D_D=0.02
        self.c_D_AT=0.006

        self.c_rho_A =0.001#1
        self.c_rho_H =0.001#1
        self.c_mu_A =0.001#1
        self.c_mu_H =0.00#1
        self.c_sigma_A=0.00#1
        self.c_sigma_H=0.001#1
        self.c_kappa_A=0.00#1
        self.c_kappa_H=0.0002
        self.c_errors=0.1


    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ])#/self.cell2surface[ j ] )
                    z +=  res[1][ self.cell2sys[ j ] ]#/self.cell2surface[ j ] 
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                #if min(y)<0 or max(y)>1.1:
                #    raise Exception("Calculation problems..")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)

        for wid in t.cell_edges():
            (c1,c2)=wid
            for wid in [(c1,c2),(c2,c1)]:
                (c1,c2)=wid
                z = 0.
                nl = self.system.tissue.cell_neighbors( c1 )
                for u in nl:
                    z+= (math.pow(3,self.aux(u)))
                z= (math.pow(3,self.aux(c2)))/z
                #math.sqrt(self.aux(c1))*
                self.pin( cell_edge=(c1,c2), value=math.sqrt(self.aux(c1))*z*len(nl))
                #self.pin( cell_edge=wid, value=self.f.P(wid, t, x) )

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )/self.cell2surface[c] > max:
                max=abs( xn[i] - xnprim[i] )/self.cell2surface[c]
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        #for i in t.cell_edges():
        #    (s,t)=i
        #    x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
        #    x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi2( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_max_expected_flux*self.c_f_alpha
            return x*x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )

        def Fi( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_f_alpha
            return x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )
        
        #def P( wid, t, x):
        #    (i,j)=wid
        #    z = 0.
        #    for u in self.system.tissue.cell_neighbors( i ):
        #        z+= W((i,u))*(math.pow(2,A(u,t,x)/S(u)))
        #    return 1*W(wid)*(math.pow(2,A(j,t,x)/S(j)))/z
        #    #return x[ self.wall2sys[ wid ] ] 

        def P( wid, t, x):
            (i,j)=wid
            z = 0.
            nl =  self.system.tissue.cell_neighbors( i )
            for u in nl:
                z+= math.pow(3, A(u,t,x))
            #math.sqrt(A(i,t,x))*s
            return math.sqrt(A(i,t,x))*math.pow(3, A(j,t,x))/z*len(nl)
        
        def C( i, t, x):
            return A(i,t,x)/S(i)
        
        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            #print self.c_gamma*W( (i, j) )/self.cell2overall_wall_length[ i ]*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))    
            #return self.c_gamma*W( (i, j) )*(-A(j,t,x)/(1+A(j,t,x)/S( j ))*P((j,i),t,x)/S( j )+A(i,t,x)/(1+A(i,t,x)/S( i ))*P((i,j),t,x)/S( i )) + self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return self.c_gamma*(-C(j,t,x)*P((j,i),t,x)+C(i,t,x)*P((i,j),t,x)) + self.c_gamma_diff*(-C(j,t,x)+C(i,t,x))#act OK
            #return self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK W( (i, j) )*
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
            return self.c_D_D*(-A(j,t,x)+A(i,t,x))+self.c_D_AT*(-A(j,t,x)*P((j,i), t, x)+A(i,t,x)*P((i,j), t, x))
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return 1
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]= 0 
            x2[ self.cell2sys[ i ] ]= self.c_rho_A-self.c_mu_A*A( i,t,x )
            #x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta)#-self.c_epsilon*self.i_center_evacuate( i )*A(i,t,x)*self.center_time_mod()  #OK
            #x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta)-self.c_epsilon*self.i_center_evacuate( i )*A(i,t,x)*self.center_time_mod()  #OK
            #if t.cell_property( i, "CZ" ):
            #    x2[ self.cell2sys[ i ] ] -= 0.05*A(i,t,x)
            if self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] += self.c_alpha-A(i,t,x)*(self.c_beta)
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        #for i in t.cell_edges():
        #    (s1,s2)=i
        #    #if P((s1,s2),t,x) < self.c_pin_max:
        #    x2[ self.wall2sys[(s1,s2)] ] = self.c_global_lambda*(self.c_lambda*Fi(A(s2,t,x)/S(s2))+self.c_qmin-self.c_theta*P((s1,s2),t,x))
        #    #else: x2[ self.wall2sys[(s1,s2)] ]= 0
        #    #if P((s2,s1),t,x) < self.c_pin_max:
        #    x2[ self.wall2sys[(s2,s1)] ] = self.c_global_lambda*(self.c_lambda*Fi(A(s1,t,x)/S(s1))+self.c_qmin-self.c_theta*P((s2,s1),t,x))            
        #    #else: x2[ self.wall2sys[(s2,s1)] ]= 0
        #    #x2[ self.wall2sys[(s1,s2)] ] = 0
        #    #x2[ self.wall2sys[(s2,s1)] ] = 0
        return x2

    def center_time_mod( self ):
        if self.t < self.c_center_time_slowdown:
            return float(self.t)/self.c_center_time_slowdown
        else:
            return 1.
        
    def prim_time_mod( self, prz=-1 ):
        """Changes the factor of influance of the young prim.
        
        Provides smoothing effect for boundary conditions.
        
        :parameters:
            prz : `int`
                Id of cell which belongs to PrZ.
        :rtype: `float`
        :return: Value from [0,1] which depands on time of the primordium creation
        :raise Exception: <Description of situation raising `Exception`>
        """
        t = self.tissue_system.tissue.tissue_property( "prims2time" )
        if t[ prz ]+self.c_prim_time_slowdown < self.t:
            return (float( t[ prz ])+self.c_prim_time_slowdown) / self.t
        else:
            return 1.
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        for i in t.cells():
            if t.cell_property( cell=i, property="PrC")>0:
                if t.cell_property( cell=i, property="PrC")==t.cell_property( cell=cell_id, property="PrZ"):
                    prim_id = i
                    break
        PrC_pos = cell_center( t, prim_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        #if x <0 or x>1:            
            #raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        if x <0:
            return 0
        if x >1:
            return 1
    
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c )/self.cell2surface[ c ] > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y )/self.cell2surface[ y ],  self.aux( cell = x )/self.cell2surface[ x ] ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            d = t.tissue_property( property="prim2time")
            d[ c ] = self.t
            t.tissue_property( property="prim2time", value=d)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            #self.step()





class PhysAuxinTransportModel31(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The up-the-hill hypo based on 1d params,
    USED to reproduce the pumps on static merystem.
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 5
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 200 # used to drop the loop if convergence not reached before x loops
        
        self.c_gamma = 0.1#0.008#0.0060#075#25 #active flux
        self.c_gamma_diff = 0.01#0.001#20
        
        self.c_lambda =1.0 # PIN production depanding on flux
        self.c_global_lambda=1.# PIN production turnover
        self.c_qmin = 0.001 #min production of PIN
        self.c_theta=0.001 #decay of PIN
        self.c_pin_max=1.3 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.03 #centre evacuate
        self.c_delta =  0.05 #prim evacuate


        self.aux_prim_trs_con = 0.84#0.62
        self.c_initial_aux_value=0.5


        self.c_pin_tol =0.001
        self.c_aux_tol = 0.001
        
        self.c_max_expected_flux = 2.
        self.c_f_alpha = self.c_theta/self.c_max_expected_flux*self.c_max_expected_flux*5
        
        self.c_prim_time_slowdown = 500
        self.c_center_time_slowdown = 500
        
        
        #self.c_gamma = 0.00005#075#25 #active flux
        #self.c_gamma_diff =10000000
        
        #self.c_global_lambda = 1 # PIN turnover coef
        #self.c_lambda = 500 # PIN production depanding on flux
        #self.c_qmin = 0.01 #min production of PIN
        #self.c_theta=0.01 #decay of PIN
        
        #self.c_epsilon=0.00001#0.03 #centre evacuate
        #self.c_delta = 0.0005#0.16 #prim evacuate

        self.c_D_D=0.03
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
        self.c_alpha=0.002
        self.c_beta=0.0001


    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] )
                    z +=  res[1][ self.cell2sys[ j ] ]/self.cell2surface[ j ] 
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                #if min(y)<0 or max(y)>1.1:
                #    raise Exception("Calculation problems..")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)

        for wid in t.cell_edges():
            (c1,c2)=wid
            for wid in [(c1,c2),(c2,c1)]:
                (c1,c2)=wid
                z = 0.
                for u in self.system.tissue.cell_neighbors( c1 ):
                    z+= math.pow(3, self.aux(u))
                z= math.pow(3,self.aux(c2))/z
                self.pin( cell_edge=(c1,c2), value=z)
            

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )/self.cell2surface[c] > max:
                max=abs( xn[i] - xnprim[i] )/self.cell2surface[c]
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        #for i in t.cell_edges():
        #    (s,t)=i
        #    x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
        #    x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi2( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_max_expected_flux*self.c_f_alpha
            return x*x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )

        def Fi( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_f_alpha
            return x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )
        
        #def P( wid, t, x):
        #    (i,j)=wid
        #    z = 0.
        #    for u in self.system.tissue.cell_neighbors( i ):
        #        z+= W((i,u))*(math.pow(2,A(u,t,x)/S(u)))
        #    return 1*W(wid)*(math.pow(2,A(j,t,x)/S(j)))/z
        #    #return x[ self.wall2sys[ wid ] ] 

        def P( wid, t, x):
            (i,j)=wid
            z = 0.
            for u in self.system.tissue.cell_neighbors( i ):
                z+= math.pow(3, A(u,t,x))
            return math.pow(3, A(j,t,x) )/z
        
        def C( i, t, x):
            return A(i,t,x)/S(i)
        
        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            #print self.c_gamma*W( (i, j) )/self.cell2overall_wall_length[ i ]*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))    
            #return self.c_gamma*W( (i, j) )*(-A(j,t,x)/(1+A(j,t,x)/S( j ))*P((j,i),t,x)/S( j )+A(i,t,x)/(1+A(i,t,x)/S( i ))*P((i,j),t,x)/S( i )) + self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return self.c_gamma*(-C(j,t,x)*P((j,i),t,x)+C(i,t,x)*P((i,j),t,x)) + self.c_gamma_diff*(-C(j,t,x)+C(i,t,x))#act OK
            #return self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK W( (i, j) )*
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
            return self.c_D_D*(-A(j,t,x)+A(i,t,x))+self.c_D_AT*(-A(j,t,x))/(1+A(j,t,x)*P((j,i), t, x)+A(i,t,x)/(1+-A(i,t,x)*P((i,j), t, x)))
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return 1
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]= self.c_rho_A-self.c_mu_A*A( i,t,x )
            #x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta)#-self.c_epsilon*self.i_center_evacuate( i )*A(i,t,x)*self.center_time_mod()  #OK
            #x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*(self.c_beta)-self.c_epsilon*self.i_center_evacuate( i )*A(i,t,x)*self.center_time_mod()  #OK
            #if t.cell_property( i, "CZ" ):
            #    x2[ self.cell2sys[ i ] ] -= 0.05*A(i,t,x)
            if self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ] += self.c_alpha#*A(i,t,x)
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        #for i in t.cell_edges():
        #    (s1,s2)=i
        #    #if P((s1,s2),t,x) < self.c_pin_max:
        #    x2[ self.wall2sys[(s1,s2)] ] = self.c_global_lambda*(self.c_lambda*Fi(A(s2,t,x)/S(s2))+self.c_qmin-self.c_theta*P((s1,s2),t,x))
        #    #else: x2[ self.wall2sys[(s1,s2)] ]= 0
        #    #if P((s2,s1),t,x) < self.c_pin_max:
        #    x2[ self.wall2sys[(s2,s1)] ] = self.c_global_lambda*(self.c_lambda*Fi(A(s1,t,x)/S(s1))+self.c_qmin-self.c_theta*P((s2,s1),t,x))            
        #    #else: x2[ self.wall2sys[(s2,s1)] ]= 0
        #    #x2[ self.wall2sys[(s1,s2)] ] = 0
        #    #x2[ self.wall2sys[(s2,s1)] ] = 0
        return x2

    def center_time_mod( self ):
        if self.t < self.c_center_time_slowdown:
            return float(self.t)/self.c_center_time_slowdown
        else:
            return 1.
        
    def prim_time_mod( self, prz=-1 ):
        """Changes the factor of influance of the young prim.
        
        Provides smoothing effect for boundary conditions.
        
        :parameters:
            prz : `int`
                Id of cell which belongs to PrZ.
        :rtype: `float`
        :return: Value from [0,1] which depands on time of the primordium creation
        :raise Exception: <Description of situation raising `Exception`>
        """
        t = self.tissue_system.tissue.tissue_property( "prims2time" )
        if t[ prz ]+self.c_prim_time_slowdown < self.t:
            return (float( t[ prz ])+self.c_prim_time_slowdown) / self.t
        else:
            return 1.
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        for i in t.cells():
            if t.cell_property( cell=i, property="PrC")>0:
                if t.cell_property( cell=i, property="PrC")==t.cell_property( cell=cell_id, property="PrZ"):
                    prim_id = i
                    break
        PrC_pos = cell_center( t, prim_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        #if x <0 or x>1:            
            #raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        if x <0:
            return 0
        if x >1:
            return 1
    
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c )/self.cell2surface[ c ] > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y )/self.cell2surface[ y ],  self.aux( cell = x )/self.cell2surface[ x ] ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            d = t.tissue_property( property="prim2time")
            d[ c ] = self.t
            t.tissue_property( property="prim2time", value=d)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            #self.step()




class PhysAuxinTransportModel32(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the grid. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie.
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 5
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 200 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.00005 #creation
        self.c_beta = 0.00005 #destruction
        self.c_gamma = 0.001#0.0060#075#25 #active flux
        self.c_gamma_diff = 0.01#20
        
        self.c_lambda =500.0 # PIN production depanding on flux
        self.c_global_lambda=5.# PIN production turnover
        self.c_qmin = 0.001 #min production of PIN
        self.c_theta=0.001 #decay of PIN
        self.c_pin_max=1.3 #this limits the number of pin to c_pin_max*c_qmin
        
        self.c_epsilon=0.0005 #centre evacuate
        self.c_delta =  0.000005 #prim evacuate


        self.aux_prim_trs_con = 0.84#0.62
        self.c_initial_aux_value=0.5


        self.c_pin_tol =0.01
        self.c_aux_tol = 0.01
        
        self.c_max_expected_flux = 0.001
        self.c_f_alpha = self.c_theta/self.c_max_expected_flux*self.c_max_expected_flux*5
        
        self.c_prim_time_slowdown = 500
        self.c_center_time_slowdown = 500
        
        
        #self.c_gamma = 0.00005#075#25 #active flux
        #self.c_gamma_diff =10000000
        
        #self.c_global_lambda = 1 # PIN turnover coef
        #self.c_lambda = 500 # PIN production depanding on flux
        #self.c_qmin = 0.01 #min production of PIN
        #self.c_theta=0.01 #decay of PIN
        
        #self.c_epsilon=0.00001#0.03 #centre evacuate
        #self.c_delta = 0.0005#0.16 #prim evacuate




    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                #if min(y)<0 or max(y)>1.1:
                #    raise Exception("Calculation problems..")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )/self.cell2surface[c] > max:
                max=abs( xn[i] - xnprim[i] )/self.cell2surface[c]
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi2( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_max_expected_flux*self.c_f_alpha
            return x*x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )

        def Fi( x ):
            #return 0
            if x < 0:
                return 0
            if x>self.c_max_expected_flux:
                #print "max_flux=",x
                return 0#self.c_max_expected_flux*self.c_f_alpha
            return x*self.c_f_alpha
            #return x/( 1+(1/self.c_theta)*x )
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            #print self.c_gamma*W( (i, j) )/self.cell2overall_wall_length[ i ]*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))    
            return self.c_gamma*(-A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)) + self.c_gamma_diff*(-A(j,t,x)+A(i,t,x))#act OK
            #return self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK W( (i, j) )*
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            x2[ self.cell2sys[ i ] ] = S( i )* self.c_alpha - A(i,t,x)*( self.c_beta + self.c_epsilon*self.i_center_evacuate( i ) - self.i_local_evacuate( i )*self.c_delta)
            for n in t.cell_neighbors( cell=i ):
                x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            #if P((s1,s2),t,x) < self.c_pin_max:
            x2[ self.wall2sys[(s1,s2)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s1,s2),t,x))+self.c_qmin-self.c_theta*P((s1,s2),t,x))
            #else: x2[ self.wall2sys[(s1,s2)] ]= 0
            #if P((s2,s1),t,x) < self.c_pin_max:
            x2[ self.wall2sys[(s2,s1)] ] = self.c_global_lambda*(self.c_lambda*Fi(J((s2,s1),t,x))+self.c_qmin-self.c_theta*P((s2,s1),t,x))            
            #else: x2[ self.wall2sys[(s2,s1)] ]= 0
            #x2[ self.wall2sys[(s1,s2)] ] = 0
            #x2[ self.wall2sys[(s2,s1)] ] = 0
        return x2

    def center_time_mod( self ):
        if self.t < self.c_center_time_slowdown:
            return float(self.t)/self.c_center_time_slowdown
        else:
            return 1.
        
    def prim_time_mod( self, prz=-1 ):
        """Changes the factor of influance of the young prim.
        
        Provides smoothing effect for boundary conditions.
        
        :parameters:
            prz : `int`
                Id of cell which belongs to PrZ.
        :rtype: `float`
        :return: Value from [0,1] which depands on time of the primordium creation
        :raise Exception: <Description of situation raising `Exception`>
        """
        t = self.tissue_system.tissue.tissue_property( "prims2time" )
        if t[ prz ]+self.c_prim_time_slowdown < self.t:
            return (float( t[ prz ])+self.c_prim_time_slowdown) / self.t
        else:
            return 1.
            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def prim_distance_mod(self, cell_id ):
        t = self.system.tissue
        center_pos = self.system.growth.center
        for i in t.cells():
            if t.cell_property( cell=i, property="PrC")>0:
                if t.cell_property( cell=i, property="PrC")==t.cell_property( cell=cell_id, property="PrZ"):
                    prim_id = i
                    break
        PrC_pos = cell_center( t, prim_id )
        d = ( PrC_pos-center_pos ).normalize()
        x = (self.system.cell_remover.c_remove_2d_radius - d)/self.system.cell_remover.c_remove_2d_radius
        #if x <0 or x>1:            
            #raise Exception("Wrong value for a modificator [0,1]: "+str(x))
        if x <0:
            return 0
        if x >1:
            return 1
    
        return x
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
          
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ"):
                if self.aux( cell = c )/self.cell2surface[ c ] > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y )/self.cell2surface[ y ],  self.aux( cell = x )/self.cell2surface[ x ] ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            d = t.tissue_property( property="prim2time")
            d[ c ] = self.t
            t.tissue_property( property="prim2time", value=d)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            #self.step()
            
            
class PhysAuxinTransportModel33(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 1d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie.
    
    The parameters are fixed for the (2) equation.
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.1
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.00001 
        self.c_beta = 0.005#001625 
        self.c_gamma = 0.05 
        
        self.c_sigma = 0 # 50 #!! in the paper they put 50
        self.c_F = 15 #!! in the paper they put 15

        self.c_transport_saturation = 300

        self.c_initial_aux_value = 0.
        self.c_initial_pin_value = 0.325

        self.c_pin_max = 4.
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_product_source = 217
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x)
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_F*self.i_local_evacuate( i ) + self.c_sigma*self.i_production_on_a_grid( i )
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            if p1 <= self.c_pin_max: x2[ self.wall2sys[(s1,s2)] ] = self.c_alpha*Fi(J((s1,s2),t,x))+self.c_beta-self.c_gamma*p1
            else: x2[ self.wall2sys[(s1,s2)] ] = - p1 + self.c_pin_max
            
            p2 = P((s2,s1),t,x)
            if p2 <= self.c_pin_max: x2[ self.wall2sys[(s2,s1)] ] = self.c_alpha*Fi(J((s2,s1),t,x))+self.c_beta-self.c_gamma*p2
            else: x2[ self.wall2sys[(s2,s1)] ] = - p2 + self.c_pin_max
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
        
    def init_aux4quadrat_grid( self, grid_size=15 ):
        for i in range(grid_size):
            for j in range( grid_size ):
                #self.aux(cell= i*15+j, value= self.c_F*i/self.c_initial_pin_value ) #+random.random() )
                self.aux(cell= i*15+j, value= 1. ) #+random.random() )
        #self.aux(cell= self.c_product_source, value= self.aux(cell= self.c_product_source) + self.c_F ) #+random.random() )

    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
            
class PhysAuxinLongitudianTransportModel2(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 1d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie.
    
    The parameters are fixed for the (2) equation.
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.1
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.00001 
        self.c_beta = 0.005#001625 
        self.c_gamma = 0.05 
        
        self.c_sigma = 0 # 50 #!! in the paper they put 50
        self.c_F = 1 #!! in the paper they put 15

        self.c_transport_saturation = 300

        self.c_initial_aux_value = 10.
        self.c_initial_pin_value = 0.325

        self.c_pin_max = 4.
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_product_source = 176
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x)
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_F*self.i_local_evacuate( i ) + self.c_sigma*self.i_production_on_a_grid( i )
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            if p1 <= self.c_pin_max: x2[ self.wall2sys[(s1,s2)] ] = self.c_alpha*Fi(J((s1,s2),t,x))+self.c_beta-self.c_gamma*p1
            else: x2[ self.wall2sys[(s1,s2)] ] = - p1 + self.c_pin_max
            
            p2 = P((s2,s1),t,x)
            if p2 <= self.c_pin_max: x2[ self.wall2sys[(s2,s1)] ] = self.c_alpha*Fi(J((s2,s1),t,x))+self.c_beta-self.c_gamma*p2
            else: x2[ self.wall2sys[(s2,s1)] ] = - p2 + self.c_pin_max
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
        
    def init_aux4quadrat_grid( self, grid_size=15 ):
        for i in range(grid_size):
            for j in range( grid_size ):
                #self.aux(cell= i*15+j, value= self.c_F*i/self.c_initial_pin_value ) #+random.random() )
                self.aux(cell= i*15+j, value= 1. ) #+random.random() )
        #self.aux(cell= self.c_product_source, value= self.aux(cell= self.c_product_source) + self.c_F ) #+random.random() )

    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
            
            
            
class PhysDiffWithSinkModel1(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Diffusion, creation, decay and differenciated cell. Prepared for 100cell linear system.
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 30
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.0001 
        self.c_beta = 0.0001
        self.c_delta = 0.001
        self.c_diff_c = 0.01
        
        self.c_aux_min = 0.
        self.c_aux_tol = 1
        self.c_pin_tol = 1
        self.c_pin_max =1
        self.c_initial_aux_value = 1.0
        self.c_initial_pin_value = 0.325

        self.c_product_source = 50
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return self.c_diff_c*(-A(j,t,x)+A(i,t,x))
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
                x2[ self.cell2sys[ i ] ] = self.c_alpha-(self.c_beta+self.c_delta*self.i_center_evacuate( i ))*A( i, t, x) 
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            x2[ self.wall2sys[(s1,s2)] ] = 0
            x2[ self.wall2sys[(s2,s1)] ] = 0
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
        
    def init_aux4quadrat_grid( self, grid_size=15 ):
        for i in range(grid_size):
            for j in range( grid_size ):
                #self.aux(cell= i*15+j, value= self.c_F*i/self.c_initial_pin_value ) #+random.random() )
                self.aux(cell= i*15+j, value= 1. ) #+random.random() )
        #self.aux(cell= self.c_product_source, value= self.aux(cell= self.c_product_source) + self.c_F ) #+random.random() )

    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
            
class PhysAuxinInternalModel1(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 1d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie.
    
    The parameters are fixed for the (2) equation.
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.1
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.001 
        self.c_beta = 0.0005#001625 
        self.c_gamma = 0.005 
        
        self.c_omega = 1
        self.c_teta = 0.01
        self.c_sigma = 0 # 50 #!! in the paper they put 50
        self.c_F = 1 #!! in the paper they put 15

        self.c_transport_saturation = 300

        self.c_initial_aux_value = 10.
        self.c_initial_pin_value = 0.1#0.325

        self.c_pin_max = 1.
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_product_source = 176
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x#*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return -(A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x))
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if  not self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_omega - A(i,t,x)*self.c_teta#self.c_F*self.i_local_evacuate( i ) + self.c_sigma*self.i_production_on_a_grid( i )
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            if p1 <= self.c_pin_max: x2[ self.wall2sys[(s1,s2)] ] = self.c_alpha*Fi(J((s1,s2),t,x))+self.c_beta-self.c_gamma*p1
            else: x2[ self.wall2sys[(s1,s2)] ] = - p1 + self.c_pin_max
            
            p2 = P((s2,s1),t,x)
            if p2 <= self.c_pin_max: x2[ self.wall2sys[(s2,s1)] ] = self.c_alpha*Fi(J((s2,s1),t,x))+self.c_beta-self.c_gamma*p2
            else: x2[ self.wall2sys[(s2,s1)] ] = - p2 + self.c_pin_max
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
            if self.i_local_evacuate( c ):
                self.aux( cell=c, value=self.c_aux_min )
        
    def init_aux4quadrat_grid( self, grid_size=15 ):
        for i in range(grid_size):
            for j in range( grid_size ):
                #self.aux(cell= i*15+j, value= self.c_F*i/self.c_initial_pin_value ) #+random.random() )
                self.aux(cell= i*15+j, value= 1. ) #+random.random() )
        #self.aux(cell= self.c_product_source, value= self.aux(cell= self.c_product_source) + self.c_F ) #+random.random() )

    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
            
class Phys2DGrid_RL_acropetal(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 2d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie.
    
    The parameters are fixed for the (2) equation. Except the additional production factor is added
    to guarantee the acropetal vein formation.
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.1
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.00001 
        self.c_beta = 0.005#001625 
        self.c_gamma = 0.05 
        
        self.c_sigma = 0 # 50 #!! in the paper they put 50
        self.c_omega =10
        self.c_F = 0 #!! in the paper they put 15

        self.c_transport_saturation = 300

        self.c_initial_aux_value = 200.
        self.c_initial_pin_value = 0.325

        self.c_pin_max = 4.
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_product_source = 217
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x)
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_omega+self.c_F*self.i_local_evacuate( i ) + self.c_sigma*self.i_production_on_a_grid( i )
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            if p1 <= self.c_pin_max: x2[ self.wall2sys[(s1,s2)] ] = self.c_alpha*Fi(J((s1,s2),t,x))+self.c_beta-self.c_gamma*p1
            else: x2[ self.wall2sys[(s1,s2)] ] = - p1 + self.c_pin_max
            
            p2 = P((s2,s1),t,x)
            if p2 <= self.c_pin_max: x2[ self.wall2sys[(s2,s1)] ] = self.c_alpha*Fi(J((s2,s1),t,x))+self.c_beta-self.c_gamma*p2
            else: x2[ self.wall2sys[(s2,s1)] ] = - p2 + self.c_pin_max
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        
    def init_aux4quadrat_grid( self, grid_size=15 ):
        for i in range(grid_size):
            for j in range( grid_size ):
                #self.aux(cell= i*15+j, value= self.c_F*i/self.c_initial_pin_value ) #+random.random() )
                self.aux(cell= i*15+j, value= 200. ) #+random.random() )
        #self.aux(cell= self.c_product_source, value= self.aux(cell= self.c_product_source) + self.c_F ) #+random.random() )

    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
            
            
class Phys1Dcanalisation1(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 1d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie. Based on 2 eq. the target would be
    to limit the pumps to certain distance
    
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.2
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.00001 
        self.c_beta = 0.005#001625 
        self.c_gamma = 0.05 
        
        self.c_sigma = 0 # 50 #!! in the paper they put 50
        self.c_omega = 0.1*320
        self.c_omega_d =0.1
        self.c_F = 0 #!! in the paper they put 15

        self.c_transport_saturation = 300

        self.c_initial_aux_value = 320.
        self.c_initial_pin_value = 0.325

        self.c_pin_max = 4.
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_product_source = 24
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x)
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_omega-self.c_omega_d*A(i,t,x)+self.c_F*self.i_local_evacuate( i ) + self.c_sigma*self.i_production_on_a_grid( i )
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            if p1 <= self.c_pin_max: x2[ self.wall2sys[(s1,s2)] ] = self.c_alpha*Fi(J((s1,s2),t,x))+self.c_beta-self.c_gamma*p1
            else: x2[ self.wall2sys[(s1,s2)] ] = - p1 + self.c_pin_max
            
            p2 = P((s2,s1),t,x)
            if p2 <= self.c_pin_max: x2[ self.wall2sys[(s2,s1)] ] = self.c_alpha*Fi(J((s2,s1),t,x))+self.c_beta-self.c_gamma*p2
            else: x2[ self.wall2sys[(s2,s1)] ] = - p2 + self.c_pin_max
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        
    def init_aux4quadrat_grid( self, grid_size=15 ):
        for i in range(grid_size):
            for j in range( grid_size ):
                #self.aux(cell= i*15+j, value= self.c_F*i/self.c_initial_pin_value ) #+random.random() )
                self.aux(cell= i*15+j, value= 200. ) #+random.random() )
        #self.aux(cell= self.c_product_source, value= self.aux(cell= self.c_product_source) + self.c_F ) #+random.random() )

    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
            
            
class Phys2DGrid_RL_acropetal2(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 2d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie.
    
    The parameters are fixed for the (2) equation (check!).
    
    The target would be to have acropetal vein formations
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.1
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.00001 
        self.c_beta = 0.005#001625 
        self.c_gamma = 0.05 
        
        self.c_sigma = 0 # 50 #!! in the paper they put 50
        self.c_omega =0
        self.c_F = 50 #!! in the paper they put 15

        self.c_transport_saturation = 300

        self.c_initial_aux_value = 200.
        self.c_initial_pin_value = 0.325

        self.c_pin_max = 4.
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_product_source = 217
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x)
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_omega+self.c_F*self.i_local_evacuate( i ) + self.c_sigma*self.i_production_on_a_grid( i )
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            if p1 <= self.c_pin_max: x2[ self.wall2sys[(s1,s2)] ] = self.c_alpha*Fi(J((s1,s2),t,x))+self.c_beta-self.c_gamma*p1
            else: x2[ self.wall2sys[(s1,s2)] ] = - p1 + self.c_pin_max
            
            p2 = P((s2,s1),t,x)
            if p2 <= self.c_pin_max: x2[ self.wall2sys[(s2,s1)] ] = self.c_alpha*Fi(J((s2,s1),t,x))+self.c_beta-self.c_gamma*p2
            else: x2[ self.wall2sys[(s2,s1)] ] = - p2 + self.c_pin_max
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        
    def init_aux4quadrat_grid( self, grid_size=15 ):
        t = self.system.tissue
        for i in range(grid_size):
            for j in range( grid_size ):
                self.aux(cell= i*15+j, value= self.c_F*i/self.c_initial_pin_value ) #+random.random() )
                #self.aux(cell= i*15+j, value= 200. ) #+random.random() )
        #self.aux(cell= self.c_product_source, value= self.aux(cell= self.c_product_source) + self.c_F ) #+random.random() )
        for c in t.cells():
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        

    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
class Phys1Dcanalisation2(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 1d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie. Based on 2 eq. to present source to sink
    canalisation process
    
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.05#0.2
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.00001 
        self.c_beta = 0.005#001625 
        self.c_gamma = 0.05 
        
        self.c_sigma = 0 # 50 #!! in the paper they put 50
        self.c_omega = 0#0.1*320
        self.c_omega_d =0#0.1
        self.c_F = 130 #!! in the paper they put 15

        self.c_transport_saturation = 300

        self.c_initial_aux_value = 0.1
        self.c_initial_pin_value = 0.1

        self.c_pin_max = 4.
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_product_source = 24
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x)
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_F*self.i_local_evacuate( i ) 
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            if p1 <= self.c_pin_max: x2[ self.wall2sys[(s1,s2)] ] = self.c_alpha*Fi(J((s1,s2),t,x))+self.c_beta-self.c_gamma*p1
            else: x2[ self.wall2sys[(s1,s2)] ] = - p1 + self.c_pin_max
            
            p2 = P((s2,s1),t,x)
            if p2 <= self.c_pin_max: x2[ self.wall2sys[(s2,s1)] ] = self.c_alpha*Fi(J((s2,s1),t,x))+self.c_beta-self.c_gamma*p2
            else: x2[ self.wall2sys[(s2,s1)] ] = - p2 + self.c_pin_max
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= (50-c)*self.c_initial_aux_value ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        
    def init_aux4quadrat_grid( self, grid_size=15 ):
        for i in range(grid_size):
            for j in range( grid_size ):
                #self.aux(cell= i*15+j, value= self.c_F*i/self.c_initial_pin_value ) #+random.random() )
                self.aux(cell= i*15+j, value= 200. ) #+random.random() )
        #self.aux(cell= self.c_product_source, value= self.aux(cell= self.c_product_source) + self.c_F ) #+random.random() )

    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
            
class Phys1Dcanalisation3(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 1d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie. Based on 2 eq. to present source to sink
    canalisation process
    
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.00001#0.2
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.00001 
        self.c_beta = 0.005#001625 
        self.c_gamma = 0.05 
        
        self.c_sigma = 0 # 50 #!! in the paper they put 50
        self.c_omega = 0#0.1*320
        self.c_omega_d =0#0.1
        self.c_F = 130 #!! in the paper they put 15

        self.c_transport_saturation = 300

        self.c_initial_aux_value = 10
        self.c_initial_pin_value = 0.1

        self.c_pin_max = 4.
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_product_source = 24
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x)
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_F*self.i_local_evacuate( i ) 
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            if p1 <= self.c_pin_max: x2[ self.wall2sys[(s1,s2)] ] = self.c_alpha*Fi(J((s1,s2),t,x))+self.c_beta-self.c_gamma*p1
            else: x2[ self.wall2sys[(s1,s2)] ] = - p1 + self.c_pin_max
            
            p2 = P((s2,s1),t,x)
            if p2 <= self.c_pin_max: x2[ self.wall2sys[(s2,s1)] ] = self.c_alpha*Fi(J((s2,s1),t,x))+self.c_beta-self.c_gamma*p2
            else: x2[ self.wall2sys[(s2,s1)] ] = - p2 + self.c_pin_max
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value=400000+ (50-c)*self.c_initial_aux_value ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        
    def init_aux4quadrat_grid( self, grid_size=15 ):
        for i in range(grid_size):
            for j in range( grid_size ):
                #self.aux(cell= i*15+j, value= self.c_F*i/self.c_initial_pin_value ) #+random.random() )
                self.aux(cell= i*15+j, value= 200. ) #+random.random() )
        #self.aux(cell= self.c_product_source, value= self.aux(cell= self.c_product_source) + self.c_F ) #+random.random() )

    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
            


class Phys1Dcanalisation4(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 1d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie. Based on 2 eq. to test if the full pumping and
    a gradient is possible with creation everywhere.
    
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.5#0.2
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.00001 
        self.c_beta = 0.005#001625 
        self.c_gamma = 0.05 
        
        self.c_sigma = 0 # 50 #!! in the paper they put 50
        self.c_omega = 0#0.1*320
        self.c_omega_d =0#0.1
        self.c_F = 0#130 #!! in the paper they put 15

        self.c_prod = 15
        self.c_dest = 0#0.001

        self.c_transport_saturation = 300

        self.c_initial_aux_value = 100
        self.c_initial_pin_value = 0.1

        self.c_pin_max = 0.3
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_product_source = 24
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x)
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_F*self.i_local_evacuate( i ) + self.c_prod - self.c_dest*A(i,t,x) 
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            if p1 <= self.c_pin_max: x2[ self.wall2sys[(s1,s2)] ] = self.c_alpha*Fi(J((s1,s2),t,x))+self.c_beta-self.c_gamma*p1
            else: x2[ self.wall2sys[(s1,s2)] ] = - p1 + self.c_pin_max
            
            p2 = P((s2,s1),t,x)
            if p2 <= self.c_pin_max: x2[ self.wall2sys[(s2,s1)] ] = self.c_alpha*Fi(J((s2,s1),t,x))+self.c_beta-self.c_gamma*p2
            else: x2[ self.wall2sys[(s2,s1)] ] = - p2 + self.c_pin_max
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value=self.c_initial_aux_value ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        
    def init_aux4quadrat_grid( self, grid_size=15 ):
        for i in range(grid_size):
            for j in range( grid_size ):
                #self.aux(cell= i*15+j, value= self.c_F*i/self.c_initial_pin_value ) #+random.random() )
                self.aux(cell= i*15+j, value= 200. ) #+random.random() )
        #self.aux(cell= self.c_product_source, value= self.aux(cell= self.c_product_source) + self.c_F ) #+random.random() )

    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
            


class Phys1Dcanalisation5(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 1d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie. Based on 2 eq. 
    
    Used for general test on the parameter space
    
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.5#0.2
        self.c_change = 0.01 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_kappa = 0.001#0.00001 
        self.c_sigma_p = 0.005#001625 
        self.c_theta_p = 0.05 
        
        self.c_sigma_a = 0
        self.c_sigma_a_prim = 0
        self.c_theta_a = 0
        self.c_omega = 0

        self.c_gamma = 1.


        self.c_initial_aux_value = 100
        self.c_initial_pin_value = 0.1

        self.c_pin_max = 0.3
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                self.hist[ self.t ] = {}
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if stable:
                    raise Exception("Time to stop iterations")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        #d = self.hist[ self.t ]
        #d[ "max_aux_diff" ] = max
        self.hist[ self.t ][ "max_aux_diff" ] = max
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #return self.c_gamma*( -A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x) )
            return self.c_gamma*( -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x) )
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a*self.i_local_evacuate( i ) + self.c_sigma_a_prim - self.c_theta_a*A(i,t,x) 
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            if p1 <= self.c_pin_max: x2[ self.wall2sys[(s1,s2)] ] = self.c_kappa*Fi(J((s1,s2),t,x))+self.c_sigma_p-self.c_theta_p*p1
            else: x2[ self.wall2sys[(s1,s2)] ] = - p1 + self.c_pin_max
            
            p2 = P((s2,s1),t,x)
            if p2 <= self.c_pin_max: x2[ self.wall2sys[(s2,s1)] ] = self.c_kappa*Fi(J((s2,s1),t,x))+self.c_sigma_p-self.c_theta_p*p2
            else: x2[ self.wall2sys[(s2,s1)] ] = - p2 + self.c_pin_max
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value=self.c_initial_aux_value ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        
    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
            



class PhysAuxinTransportModel35(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The target is to get best possible PIN map fit with canalisation eq.
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.5
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 200 # used to drop the loop if convergence not reached before x loops
        
        self.c_kappa = 0.001#0.00001 
        self.c_sigma_p = 0.005#001625 
        self.c_theta_p = 0.05 
        
        self.c_sigma_a = 0
        self.c_sigma_a_prim = 5
        self.c_theta_a = 0

        self.c_gamma = 1.

        self.c_pin_max=0.2 #this limits the number of pin to c_pin_max*c_qmin

        self.c_initial_aux_value = 10
        self.c_initial_pin_value = 0.1

        self.c_pin_tol =  100000000000
        self.c_aux_tol = 100000000000
                
        self.error_tol = 10000000000


    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1, mxstep=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ] 
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                #if min(y)<0 or max(y)>1.1:
                #    raise Exception("Calculation problems..")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(0, min( t1,self.c_pin_max))
            t2 = max(0, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )> max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi2( x ):
            return x*x
        
        def Fi( x ):
            return x
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return self.c_gamma*(-A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x)) 
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            #print self.c_gamma*W( (i, j) )/self.cell2overall_wall_length[ i ]*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))    
            #return self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK W( (i, j) )*
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            if not ( self.i_local_evacuate( i ) or self.i_center_evacuate( i ) ):
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a_prim
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
                for i in t.cell_edges():
                    (s1,s2)=i
                    if P((s1,s2),t,x) < self.c_pin_max:
                        x2[ self.wall2sys[(s1,s2)] ] = self.c_kappa*Fi(J((s1,s2),t,x))+self.c_sigma_p - self.c_theta_p*min(self.c_pin_max, P((s1,s2),t,x)) 
                    else: x2[ self.wall2sys[(s1,s2)] ]= self.c_sigma_p - self.c_theta_p*min(self.c_pin_max, P((s1,s2),t,x)) 
                    if P((s2,s1),t,x) < self.c_pin_max:
                        x2[ self.wall2sys[(s2,s1)] ] = self.c_kappa*Fi(J((s2,s1),t,x))+self.c_sigma_p - self.c_theta_p*min( self.c_pin_max, P((s2,s1),t,x)) 
                    else: x2[ self.wall2sys[(s2,s1)] ]= self.c_sigma_p - self.c_theta_p*min( self.c_pin_max, P((s2,s1),t,x))             
        return x2

            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
            if self.i_center_evacuate( c ) or self.i_local_evacuate( c ):
                self.aux(cell= c, value= 0. ) #+random.random() )

    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )


class PhysAuxinLongitudianTransportModel3(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 1d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie.
    
    The parameters are fixed for the (2) equation.
    
    The idea of L1 layer event after the inner layer event.
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.1
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.00001 
        self.c_beta = 0.005#001625 
        self.c_gamma = 0.05 
        
        self.c_sigma = 50 # 50 #!! in the paper they put 50
        self.c_F = 10 #!! in the paper they put 15

        self.c_initial_aux_value = 1.
        self.c_initial_pin_value = 0.1

        self.c_pin_max = 4.
        self.c_aux_min = 0.
        self.c_aux_max = 100

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_layer_mod = 0.001
        
        self.c_product_source = -1
        self.c_error_tol = 1000000000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1, mxstep=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x)
            #return -min(A(j,t,x), self.c_aux_max)*P((j,i),t,x)+min(A(i,t,x),self.c_aux_max)*P((i,j),t,x)
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_F*self.i_local_evacuate( i ) + self.c_sigma*self.i_production_on_a_grid( i )
                if self.i_local_evacuate( i ) and not self.i_production_on_a_grid( i ):
                    for n in t.cell_neighbors( cell=i ):
                        if self.i_local_evacuate( n ):
                            x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
                        else:
                            x2[ self.cell2sys[ i ] ] += self.c_layer_mod * J((n,i),t,x)
                elif self.i_production_on_a_grid( i ):
                    for n in t.cell_neighbors( cell=i ):
                        x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
                else: # inner cell
                    for n in t.cell_neighbors( cell=i ):
                        if self.i_local_evacuate( n ) and not self.i_production_on_a_grid( n ):
                            x2[ self.cell2sys[ i ] ] += self.c_layer_mod * J((n,i),t,x)
                        else:
                            x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
                        
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            if p1 <= self.c_pin_max: x2[ self.wall2sys[(s1,s2)] ] = self.c_alpha*Fi(J((s1,s2),t,x))+self.c_beta-self.c_gamma*p1
            else: x2[ self.wall2sys[(s1,s2)] ] = - p1 + self.c_pin_max
            
            p2 = P((s2,s1),t,x)
            if p2 <= self.c_pin_max: x2[ self.wall2sys[(s2,s1)] ] = self.c_alpha*Fi(J((s2,s1),t,x))+self.c_beta-self.c_gamma*p2
            else: x2[ self.wall2sys[(s2,s1)] ] = - p2 + self.c_pin_max
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
        
    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            

class Phys1Dcanalisation6(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 1d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie. Based on 2 eq. 
    
    The purpose would be to check if the marginalisation of active transport could
    be reached as a function of high auxin concentration.
    
    The added assumption are:
    PIN_max
    PIN_efficiency
    
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.5#0.2
        self.c_change = 0.01 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_kappa = 0.001#0.00001 
        self.c_sigma_p = 0.005#001625 
        self.c_theta_p = 0.05 
        
        self.c_sigma_a = 0
        self.c_sigma_a_prim = 10#20
        self.c_theta_a = self.c_sigma_a_prim/1000
        self.c_omega = 0

        self.c_gamma = 1.


        self.c_initial_aux_value = 100
        self.c_initial_pin_value = 0.1

        self.c_pin_max = 0.2
        self.c_aux_min = 0.
        self.c_aux_max = 100

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                self.hist[ self.t ] = {}
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if stable:
                    raise Exception("Time to stop iterations")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        #d = self.hist[ self.t ]
        #d[ "max_aux_diff" ] = max
        self.hist[ self.t ][ "max_aux_diff" ] = max
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #return self.c_gamma*( -A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x) )
            return self.c_gamma*( -min(A(j,t,x), self.c_aux_max)*P((j,i),t,x)+min(A(i,t,x),self.c_aux_max)*P((i,j),t,x) ) +0.1*(-A(j,t,x)+A(i,t,x))
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)
            #return 0.1*(-A(j,t,x)+A(i,t,x))
        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a*self.i_local_evacuate( i ) + self.c_sigma_a_prim - self.c_theta_a*A(i,t,x) 
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            if p1 <= self.c_pin_max: x2[ self.wall2sys[(s1,s2)] ] = self.c_kappa*Fi(J((s1,s2),t,x))+self.c_sigma_p-self.c_theta_p*p1
            else: x2[ self.wall2sys[(s1,s2)] ] = - p1 + self.c_pin_max
            
            p2 = P((s2,s1),t,x)
            if p2 <= self.c_pin_max: x2[ self.wall2sys[(s2,s1)] ] = self.c_kappa*Fi(J((s2,s1),t,x))+self.c_sigma_p-self.c_theta_p*p2
            else: x2[ self.wall2sys[(s2,s1)] ] = - p2 + self.c_pin_max
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value=self.c_initial_aux_value+c ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        
    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
            

class Phys1Dcanalisation7(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 1d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie. Based on 2 eq. 
    
    Added pin efficacity
    
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.5#0.2
        self.c_change = 0.01 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_kappa = 0.001#0.00001 
        self.c_sigma_p = 0.005#001625 
        self.c_theta_p = 0.05 
        
        self.c_sigma_a = 0
        self.c_sigma_a_prim = 0
        self.c_theta_a = 0
        self.c_omega = 0

        self.c_gamma = 1.


        self.c_initial_aux_value = 1000
        self.c_initial_pin_value = 0.1

        self.c_pin_max = 0.3
        self.c_aux_max = 1100
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                self.hist[ self.t ] = {}
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if stable:
                    raise Exception("Time to stop iterations")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        #d = self.hist[ self.t ]
        #d[ "max_aux_diff" ] = max
        self.hist[ self.t ][ "max_aux_diff" ] = max
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #return self.c_gamma*( -A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x) )
            return self.c_gamma*( -min(self.c_aux_max,A(j,t,x))*P((j,i),t,x)+min(self.c_aux_max,A(i,t,x))*P((i,j),t,x) )
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a*self.i_local_evacuate( i ) + self.c_sigma_a_prim - self.c_theta_a*A(i,t,x) 
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            if p1 <= self.c_pin_max: x2[ self.wall2sys[(s1,s2)] ] = self.c_kappa*Fi(J((s1,s2),t,x))+self.c_sigma_p-self.c_theta_p*p1
            else: x2[ self.wall2sys[(s1,s2)] ] = - p1 + self.c_pin_max
            
            p2 = P((s2,s1),t,x)
            if p2 <= self.c_pin_max: x2[ self.wall2sys[(s2,s1)] ] = self.c_kappa*Fi(J((s2,s1),t,x))+self.c_sigma_p-self.c_theta_p*p2
            else: x2[ self.wall2sys[(s2,s1)] ] = - p2 + self.c_pin_max
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        import random
        for c in t.cells():
            self.aux(cell= c, value=self.c_initial_aux_value+random.random()*200 ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        
    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
            

class Phys1Dcanalisation8(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 1d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie. Based on 2 eq. 
    
    Added pin efficacity(?), used to test the concept of two sources.
    
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.5#0.2
        self.c_change = 0.01 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_kappa = 0.001#0.00001 
        self.c_sigma_p = 0.05#001625 
        self.c_theta_p = 0.5 
        
        self.c_sigma_a = 0
        self.c_sigma_a_prim = 10
        self.c_theta_a = 0
        self.c_omega = 0

        self.c_gamma = 1.


        self.c_initial_aux_value = 100
        self.c_initial_pin_value = 0.1

        self.c_pin_max = 0.2
        self.c_aux_max = 100000
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                self.hist[ self.t ] = {}
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if stable:
                    raise Exception("Time to stop iterations")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        #d = self.hist[ self.t ]
        #d[ "max_aux_diff" ] = max
        self.hist[ self.t ][ "max_aux_diff" ] = max
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            #return self.c_gamma*( -A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x) )
            return self.c_gamma*( -min(self.c_aux_max,A(j,t,x))*P((j,i),t,x)+min(self.c_aux_max,A(i,t,x))*P((i,j),t,x) )
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a*self.i_local_evacuate( i ) + self.c_sigma_a_prim - self.c_theta_a*A(i,t,x) 
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            if p1 <= self.c_pin_max: x2[ self.wall2sys[(s1,s2)] ] = self.c_kappa*Fi(J((s1,s2),t,x))+self.c_sigma_p-self.c_theta_p*p1
            else: x2[ self.wall2sys[(s1,s2)] ] = - p1 + self.c_pin_max
            
            p2 = P((s2,s1),t,x)
            if p2 <= self.c_pin_max: x2[ self.wall2sys[(s2,s1)] ] = self.c_kappa*Fi(J((s2,s1),t,x))+self.c_sigma_p-self.c_theta_p*p2
            else: x2[ self.wall2sys[(s2,s1)] ] = - p2 + self.c_pin_max
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        import random
        for c in t.cells():
            self.aux(cell= c, value=self.c_initial_aux_value+random.random()*200 ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        
    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
            



class PhysAuxinTransportModel36(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The target is to get reversed gradient and to check how is it modified after
    inserting a primordium.
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system



        self.nbr_prim=1
        self.t = 0
        self.h = 0.1
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 200 # used to drop the loop if convergence not reached before x loops
        
        self.c_kappa = 0.001#0.00001 
        self.c_sigma_p = 0.005#001625 
        self.c_theta_p = 0.05 
        
        self.c_sigma_a = 0
        self.c_sigma_a_prim = 5
        self.c_sigma_a_border = 5
        self.c_theta_a = 0

        self.c_gamma = 1.

        self.c_pin_max=0.4 #this limits the number of pin to c_pin_max*c_qmin
        self.c_pin_min=0.1
        self.c_initial_aux_value = 50
        self.c_initial_pin_value = 0.1

        self.c_pin_tol =  100000000000
        self.c_aux_tol = 100000000000
                
        self.error_tol = 10000000000
        
        # only for static case..
        self.h_border_cells={}
        self.h_centre_cells={}
        self.h_prim_cells={}
        for i in self.system.tissue.cells():
            self.h_border_cells[ i ] = self.system.tissue.cell_property( i, "BC" )
            self.h_centre_cells[ i ] = self.system.tissue.cell_property( i, "CZ" )
            self.h_prim_cells[ i ] = self.system.tissue.cell_property( i, "PrZ" )

    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ] 
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                #if min(y)<0 or max(y)>1.1:
                #    raise Exception("Calculation problems..")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(self.c_pin_min, min( t1,self.c_pin_max))
            t2 = max(self.c_pin_min, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )> max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
        
    def f( self, x, t ):
        def Fi2( x ):
            if x > 0:
                return x*x
            else:
                return 0
        
        def Fi( x ):
            if x > 0:
                return x
            else:
                return 0
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return self.c_gamma*(-A(j,t,x)*P((j,i),t,x)/ len(self.tissue_system.tissue.cell2wvs( j ) )+A(i,t,x)*P((i,j),t,x)/ len(self.tissue_system.tissue.cell2wvs( i )) ) 
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            #print self.c_gamma*W( (i, j) )/self.cell2overall_wall_length[ i ]*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))    
            #return self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK W( (i, j) )*
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
        
        def A( cid, t, x ):
            return x[ self.cell2sys[ cid ] ]
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            if not ( self.i_local_evacuate( i ) or self.i_center_evacuate( i ) ):
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a_prim + self.c_sigma_a_border*self.i_border_cell( i )
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            if P((s1,s2),t,x) <= self.c_pin_max:
                x2[ self.wall2sys[(s1,s2)] ] = self.c_kappa*Fi(J((s1,s2),t,x))+self.c_sigma_p - self.c_theta_p*min(self.c_pin_max, P((s1,s2),t,x)) 
            else: x2[ self.wall2sys[(s1,s2)] ]= - self.c_theta_p*min(self.c_pin_max, P((s1,s2),t,x)) 
            if P((s2,s1),t,x) <= self.c_pin_max:
                x2[ self.wall2sys[(s2,s1)] ] = self.c_kappa*Fi(J((s2,s1),t,x))+self.c_sigma_p - self.c_theta_p*min( self.c_pin_max, P((s2,s1),t,x)) 
            else: x2[ self.wall2sys[(s2,s1)] ]= - self.c_theta_p*min( self.c_pin_max, P((s2,s1),t,x))             
        return x2

            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        #if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
        if self.h_prim_cells[ cell ]:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        #if t.cell_property( cell=cell, property="CZ") > 0:
        if self.h_centre_cells[ cell ]:
            return 1
        else:
            return 0

    def i_border_cell( self, cell ):
        #t = self.system.tissue
        #if t.cell_property( cell=cell, property="BC") > 0:
        if self.h_border_cells[ cell ]:
            return 1
        else:
            return 0

        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
            if self.i_center_evacuate( c ) or self.i_local_evacuate( c ):
                self.aux(cell= c, value= 0. ) #+random.random() )

    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )


class SpeedTest(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 1d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie. Based on 2 eq. to present source to sink
    canalisation process
    
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.1#0.2

        self.c_gamma=0.1
        self.c_aux_min = 0
    
        self.c_initial_aux_value = 1
        self.c_initial_pin_value = 0.1
        self.c_error_tol = 1000000000
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()

        for i in range(nbr_step):
            self.sub_step()
            
    def sub_step( self ):    
        (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.c_error_tol, atol=self.c_error_tol, full_output=1)
        self.t += self.h                
        self.update( res[1] )
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
    

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return -A(j,t,x)+A(i,t,x)
            
        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value=self.c_initial_aux_value ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        
class PhysAuxinTransportModel37(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The target is to get reversed gradient and to check how is it modified after
    inserting a primordium.
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system



        self.nbr_prim=1
        self.t = 0
        self.h = 0.1
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 200 # used to drop the loop if convergence not reached before x loops
        
        self.c_kappa = 0.001#0.00001 
        self.c_sigma_p = 0.005#001625 
        self.c_theta_p = 0.05 
        
        self.c_sigma_a = 0
        self.c_sigma_a_prim = 10
        self.c_sigma_a_border = 5
        self.c_theta_a = 0

        self.c_gamma = 1.

        self.c_pin_max=0.4 #this limits the number of pin to c_pin_max*c_qmin
        self.c_pin_min=0.1
        self.c_initial_aux_value = 500
        self.c_initial_pin_value = 0.1
        self.c_aux_max = 1000

        self.c_pin_tol =  100000000000
        self.c_aux_tol = 100000000000
                
        self.error_tol = 10000000000
        
        # only for static case..
        self.h_border_cells={}
        self.h_centre_cells={}
        self.h_prim_cells={}
        self.update_identity_dics()
        
    def update_identity_dics( self ):
        for i in self.system.tissue.cells():
            self.h_border_cells[ i ] = self.system.tissue.cell_property( i, "BC" )
            self.h_centre_cells[ i ] = self.system.tissue.cell_property( i, "CZ" )
            self.h_prim_cells[ i ] = self.system.tissue.cell_property( i, "PrZ" )

    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        i=0
        for i in range( nbr_step ):
            print " #: phys aux trans: loop=", i, " time=",self.t
            i+=1
            (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
            self.t += self.h                
            self.rate_error( res[0], res[1])
            self.update( res[1] )
            y=[]
            z = 0
            # quantitie
            for j in self.cell2sys:
                y.append(res[1][ self.cell2sys[ j ] ] )
                z +=  res[1][ self.cell2sys[ j ] ] 
            print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
            y2=[]
            z2=0
            for j in self.wall2sys:
                y2.append(res[1][ self.wall2sys[ j ] ] )
                z2 +=  res[1][ self.wall2sys[ j ] ]
            print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
            print self.info
    
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = min(self.c_aux_max, max(0,t0) )
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(self.c_pin_min, min( t1,self.c_pin_max))
            t2 = max(self.c_pin_min, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )> max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
        
    def f( self, x, t ):
        def Fi2( x ):
            if x > 0:
                return x*x
            else:
                return 0
        
        def Fi( x ):
            if x > 0:
                return x
            else:
                return 0
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return self.c_gamma*( -A(j,t,x)*P((j,i),t,x) +A(i,t,x)*P((i,j),t,x) ) 
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            #print self.c_gamma*W( (i, j) )/self.cell2overall_wall_length[ i ]*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))    
            #return self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK W( (i, j) )*
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
        
        def A( cid, t, x ):
            return min(self.c_aux_max, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            if not ( self.i_local_evacuate( i ) or self.i_center_evacuate( i ) ):
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a_prim + self.c_sigma_a_border*self.i_border_cell( i )
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            if P((s1,s2),t,x) <= self.c_pin_max:
                x2[ self.wall2sys[(s1,s2)] ] = self.c_kappa*Fi(J((s1,s2),t,x))+self.c_sigma_p - self.c_theta_p*min(self.c_pin_max, P((s1,s2),t,x)) 
            else: x2[ self.wall2sys[(s1,s2)] ]= - self.c_theta_p*min(self.c_pin_max, P((s1,s2),t,x)) 
            if P((s2,s1),t,x) <= self.c_pin_max:
                x2[ self.wall2sys[(s2,s1)] ] = self.c_kappa*Fi(J((s2,s1),t,x))+self.c_sigma_p - self.c_theta_p*min( self.c_pin_max, P((s2,s1),t,x)) 
            else: x2[ self.wall2sys[(s2,s1)] ]= - self.c_theta_p*min( self.c_pin_max, P((s2,s1),t,x))             
        return x2

            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        #if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
        if self.h_prim_cells[ cell ]:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        #if t.cell_property( cell=cell, property="CZ") > 0:
        if self.h_centre_cells[ cell ]:
            return 1
        else:
            return 0

    def i_border_cell( self, cell ):
        #t = self.system.tissue
        #if t.cell_property( cell=cell, property="BC") > 0:
        if self.h_border_cells[ cell ]:
            return 1
        else:
            return 0

        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
            if self.i_center_evacuate( c ) or self.i_local_evacuate( c ):
                self.aux(cell= c, value= 0. ) #+random.random() )

    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )




class PhysAuxinTransportModel38(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The target is to check pin realocation model and its influance on the overal behaviour.
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system



        self.nbr_prim=1
        self.t = 0
        self.h = 0.1
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 200 # used to drop the loop if convergence not reached before x loops
        
        self.c_kappa = 0.001#0.00001 
        self.c_sigma_p = 0.005#001625 
        self.c_theta_p = 0.05 
        
        self.c_sigma_a = 0
        self.c_sigma_a_prim = 10
        self.c_sigma_a_border = 50
        self.c_theta_a = 0

        self.c_gamma = 1.

        self.c_pin_max=0.4 #this limits the number of pin to c_pin_max*c_qmin
        self.c_pin_min=0.1
        self.c_initial_aux_value = 500
        self.c_initial_pin_value = 0.1
        self.c_aux_max = 1000

        self.c_pin_tol =  100000000000
        self.c_aux_tol = 100000000000
                
        self.error_tol = 10000000000
        
        # only for static case..
        self.h_border_cells={}
        self.h_centre_cells={}
        self.h_prim_cells={}
        self.update_identity_dics()
        
    def update_identity_dics( self ):
        for i in self.system.tissue.cells():
            self.h_border_cells[ i ] = self.system.tissue.cell_property( i, "BC" )
            self.h_centre_cells[ i ] = self.system.tissue.cell_property( i, "CZ" )
            self.h_prim_cells[ i ] = self.system.tissue.cell_property( i, "PrZ" )

    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        i=0
        for i in range( nbr_step ):
            print " #: phys aux trans: loop=", i, " time=",self.t
            i+=1
            (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.error_tol, full_output=1)
            self.t += self.h                
            self.rate_error( res[0], res[1])
            self.update( res[1] )
            y=[]
            z = 0
            # quantitie
            for j in self.cell2sys:
                y.append(res[1][ self.cell2sys[ j ] ] )
                z +=  res[1][ self.cell2sys[ j ] ] 
            print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux con min:", min(y), "aux con max:", max(y)
            y2=[]
            z2=0
            for j in self.wall2sys:
                y2.append(res[1][ self.wall2sys[ j ] ] )
                z2 +=  res[1][ self.wall2sys[ j ] ]
            print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
            print self.info
    
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = min(self.c_aux_max, max(0,t0) )
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            t1=x[ self.wall2sys[ (c1,c2) ] ]
            t2=x[ self.wall2sys[ (c2,c1) ] ]
            t1 = max(self.c_pin_min, min( t1,self.c_pin_max))
            t2 = max(self.c_pin_min, min( t2,self.c_pin_max))
            self.pin( cell_edge=(c1,c2), value=t1 )
            self.pin( cell_edge=(c2,c1), value=t2 )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] )> max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
        
    def f( self, x, t ):
        def Fi2( x ):
            if x > 0:
                return x*x
            else:
                return 0
        
        def Fi( x ):
            if x > 0:
                return x
            else:
                return 0
        
        def P( wid, t, x):
            return x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return self.c_gamma*( -A(j,t,x)*P((j,i),t,x) +A(i,t,x)*P((i,j),t,x) ) 
            #print W( (i, j) )*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))
            #print self.c_gamma*W( (i, j) )/self.cell2overall_wall_length[ i ]*(-A(j,t,x)*P((j,i),t,x)/S( j )+A(i,t,x)*P((i,j),t,x)/S( i ))    
            #return self.c_gamma_diff*W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK W( (i, j) )*
            #return W( (i, j) )*(-A(j,t,x)/S( j )+A(i,t,x)/S( i ))#act OK
            #return W( (i, j) )*(-A(j,t,x)+A(i,t,x))#act OK
            #return (-A(j,t,x)+A(i,t,x))#act OK
        
        def A( cid, t, x ):
            return min(self.c_aux_max, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            x2[ self.cell2sys[ i ] ]=0
            if not ( self.i_local_evacuate( i ) or self.i_center_evacuate( i ) ):
                # *max(0, 1-(A(i,t,x)/200))
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a_prim + self.c_sigma_a_border*self.i_border_cell( i )
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
        for i in t.cell_edges():
            (s1,s2)=i
            if P((s1,s2),t,x) <= self.c_pin_max:
                x2[ self.wall2sys[(s1,s2)] ] = self.c_kappa*Fi(J((s1,s2),t,x))+self.c_sigma_p - self.c_theta_p*min(self.c_pin_max, P((s1,s2),t,x)) 
            else: x2[ self.wall2sys[(s1,s2)] ]= - self.c_theta_p*min(self.c_pin_max, P((s1,s2),t,x)) 
            if P((s2,s1),t,x) <= self.c_pin_max:
                x2[ self.wall2sys[(s2,s1)] ] = self.c_kappa*Fi(J((s2,s1),t,x))+self.c_sigma_p - self.c_theta_p*min( self.c_pin_max, P((s2,s1),t,x)) 
            else: x2[ self.wall2sys[(s2,s1)] ]= - self.c_theta_p*min( self.c_pin_max, P((s2,s1),t,x))             
        return x2

            
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        #if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
        if self.h_prim_cells[ cell ]:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        #if t.cell_property( cell=cell, property="CZ") > 0:
        if self.h_centre_cells[ cell ]:
            return 1
        else:
            return 0

    def i_border_cell( self, cell ):
        #t = self.system.tissue
        #if t.cell_property( cell=cell, property="BC") > 0:
        if self.h_border_cells[ cell ]:
            return 1
        else:
            return 0

        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
            if self.i_center_evacuate( c ) or self.i_local_evacuate( c ):
                self.aux(cell= c, value= 0. ) #+random.random() )

    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
            
class Phys1Dcanalisation9(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 1d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie. Based on 2 eq. 
    
    test of realocation model from fougiers' paper.
    
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.5#0.2
        self.c_change = 0.01 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_kappa = 0.001#0.00001 
        self.c_sigma_p = 0.05#001625 
        self.c_theta_p = 0.5 
        
        self.c_sigma_a = 0
        self.c_sigma_a_prim = 10
        self.c_theta_a = 0
        self.c_omega = 0

        self.c_gamma = 1.


        self.c_initial_aux_value = 100
        self.c_initial_pin_value = 0.1

        self.c_pin_max = 0.2
        self.c_aux_max = 100000
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                self.hist[ self.t ] = {}
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if stable:
                    raise Exception("Time to stop iterations")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        #d = self.hist[ self.t ]
        #d[ "max_aux_diff" ] = max
        self.hist[ self.t ][ "max_aux_diff" ] = max
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return self.c_gamma*( -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x) )
            return self.c_gamma*( -min(self.c_aux_max,A(j,t,x))*P((j,i),t,x)+min(self.c_aux_max,A(i,t,x))*P((i,j),t,x) )
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a*self.i_local_evacuate( i ) + self.c_sigma_a_prim*max(0,1-(A(i,t,x)/200)) - self.c_theta_a*A(i,t,x) 
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            if p1 <= self.c_pin_max: x2[ self.wall2sys[(s1,s2)] ] = self.c_kappa*Fi(J((s1,s2),t,x))+self.c_sigma_p-self.c_theta_p*p1
            else: x2[ self.wall2sys[(s1,s2)] ] = - p1 + self.c_pin_max
            
            p2 = P((s2,s1),t,x)
            if p2 <= self.c_pin_max: x2[ self.wall2sys[(s2,s1)] ] = self.c_kappa*Fi(J((s2,s1),t,x))+self.c_sigma_p-self.c_theta_p*p2
            else: x2[ self.wall2sys[(s2,s1)] ] = - p2 + self.c_pin_max
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        import random
        for c in t.cells():
            self.aux(cell= c, value=self.c_initial_aux_value+random.random()*200 ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        
    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
            

class PhysCanalisation1(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 1d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie. Based on 2 eq. 
    
    test of realocation model invented on the basis of ff..
    
    
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.5#0.2
        self.c_change = 0.01 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        
        self.c_sigma_a = 0
        self.c_sigma_a_prim = 10
        self.c_theta_a = 0
        self.c_omega = 0

        self.c_gamma = 1.


        self.c_initial_aux_value = 100
        self.c_initial_pin_value = 0.1

        self.c_pin_Max = 0.4*6
        self.c_pin_min = 0.1
        self.c_aux_max = 100000
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                self.hist[ self.t ] = {}
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if stable:
                    raise Exception("Time to stop iterations")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        z = self.pin_in_walls( )
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=z[ (c1,c2) ] )
            self.pin( cell_edge=(c2,c1), value=z[ (c2,c1) ] )        
    
    def pin_in_walls( self ):
        z = {}
        sq_fi = {}
        wall2pin = {}
        t = self.system.tissue
        for i in t.cells():
            sq_fi[ i ] = self.f_sum_of_sq_fi( i )
            z[ i ] = max( 6*self.c_pin_min, min( self.c_pin_Max, self.f_psi( sq_fi[ i ] ) ) )
                                                

        for i in t.cell_edges():
            (c1,c2)=i
            wall2pin[ (c1,c2) ] = self.c_pin_min + pow(self.f_J( (c1,c2) ), 2)/sq_fi[ c1 ]*(z[ c1 ]-6*self.c_pin_min )
            wall2pin[ (c2,c1) ] = self.c_pin_min + pow(self.f_J( (c2,c1) ), 2)/sq_fi[ c2 ]*(z[ c2 ]-6*self.c_pin_min )
            
        return wall2pin

    def f_psi( self, x):
        return x
    
    def f_sum_of_sq_fi( self, cid ):
        z= 0.
        for i in s.tissue.cell_neighbors( cid ):
            z += pow(self.f_fi( self.f_J( (cid, i ) ) ), 2 )
        return z
    
    def f_J( self, (i,j) ):
        return 1#self.
            
    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        #d = self.hist[ self.t ]
        #d[ "max_aux_diff" ] = max
        self.hist[ self.t ][ "max_aux_diff" ] = max
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return self.c_gamma*( -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x) )
            return self.c_gamma*( -min(self.c_aux_max,A(j,t,x))*P((j,i),t,x)+min(self.c_aux_max,A(i,t,x))*P((i,j),t,x) )
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a*self.i_local_evacuate( i ) + self.c_sigma_a_prim*max(0,1-(A(i,t,x)/200)) - self.c_theta_a*A(i,t,x) 
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            if p1 <= self.c_pin_max: x2[ self.wall2sys[(s1,s2)] ] = self.c_kappa*Fi(J((s1,s2),t,x))+self.c_sigma_p-self.c_theta_p*p1
            else: x2[ self.wall2sys[(s1,s2)] ] = - p1 + self.c_pin_max
            
            p2 = P((s2,s1),t,x)
            if p2 <= self.c_pin_max: x2[ self.wall2sys[(s2,s1)] ] = self.c_kappa*Fi(J((s2,s1),t,x))+self.c_sigma_p-self.c_theta_p*p2
            else: x2[ self.wall2sys[(s2,s1)] ] = - p2 + self.c_pin_max
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        import random
        for c in t.cells():
            self.aux(cell= c, value=self.c_initial_aux_value+random.random()*200 ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        
    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
            
            
class Phys1Dcanalisation10(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Basic model
    
    
    """
    

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 1#0.2
        self.c_change = 0.00000001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_kappa = 0.0
        self.c_sigma_p = 0.0
        self.c_theta_p = 0.0
        
        self.c_sigma_a = 0.0
        self.c_sigma_a_prim = 0.0
        self.c_theta_a = 0.0
        self.c_omega = 0.0

        self.c_gamma = 0.0
        self.c_ksi = 0.0


        self.c_initial_aux_value = 0.0
        self.c_initial_pin_value = 0.0

        self.c_pin_max = 0
        self.c_aux_max = 0
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_error_tol = 100000000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                self.hist[ self.t ] = {}
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if stable:
                    raise Exception("Time to stop iterations")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        #d = self.hist[ self.t ]
        #d[ "max_aux_diff" ] = max
        self.hist[ self.t ][ "max_aux_diff" ] = max
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x
        
        def P( wid, t, x):
            return  x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return self.c_gamma*( -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x) )
            #return self.c_gamma*( -min(self.c_aux_max,A(j,t,x))*P((j,i),t,x)+min(self.c_aux_max,A(i,t,x))*P((i,j),t,x) )
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a_prim - self.c_theta_a*A(i,t,x)
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            x2[ self.wall2sys[(s1,s2)] ] = Fi(J((s1,s2),t,x))+self.c_sigma_p-self.c_theta_p*p1
            
            
            p2 = P((s2,s1),t,x)
            x2[ self.wall2sys[(s2,s1)] ] = Fi(J((s2,s1),t,x))+self.c_sigma_p-self.c_theta_p*p2
            
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        import random
        for c in t.cells():
            self.aux(cell= c, value=self.c_initial_aux_value ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        
    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            


class Phys2DcanalisationWithExtBoundary1(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Analitical canalisation solution. the value of pin should be 0.9 max next to the sink.
    
    
    """
    

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 1#0.2
        self.c_change = 0.00000001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_kappa = 0.00#0.00001
        self.c_pin2aux_diff= 0.01
        self.c_sigma_p = 0.001*self.c_pin2aux_diff#001625 
        self.c_theta_p = 0.002 
        
        self.c_sigma_a = 0
        self.c_sigma_a_prim = 0.001
        self.c_theta_a = 0.002*self.c_pin2aux_diff
        self.c_omega = 0

        self.c_gamma = 0.1
        self.c_ksi = 0.001


        self.c_initial_aux_value = self.c_sigma_a_prim / self.c_theta_a
        self.c_initial_pin_value = self.c_sigma_p / self.c_theta_p

        self.c_pin_max = 2000000
        self.c_aux_max = 1
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                self.hist[ self.t ] = {}
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if stable:
                    raise Exception("Time to stop iterations")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        #d = self.hist[ self.t ]
        #d[ "max_aux_diff" ] = max
        self.hist[ self.t ][ "max_aux_diff" ] = max
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return self.c_ksi*x
        
        def P( wid, t, x):
            return  x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return self.c_gamma*( -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x) )
            #return self.c_gamma*( -min(self.c_aux_max,A(j,t,x))*P((j,i),t,x)+min(self.c_aux_max,A(i,t,x))*P((i,j),t,x) )
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ) and not self.system.tissue.cell_property( i , "BC"):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a_prim - self.c_theta_a*A(i,t,x)
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            x2[ self.wall2sys[(s1,s2)] ] = Fi(J((s1,s2),t,x))+self.c_sigma_p-self.c_theta_p*p1
            
            
            p2 = P((s2,s1),t,x)
            x2[ self.wall2sys[(s2,s1)] ] = Fi(J((s2,s1),t,x))+self.c_sigma_p-self.c_theta_p*p2
            
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        import random
        for c in t.cells():
            self.aux(cell= c, value=self.c_initial_aux_value ) #+random.random() )
            if t.cell_property( c, "CZ") > 0 or t.cell_property( c , "BC"):
                self.aux( c,  0. )
        
    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            


class Phys2DcanalisationForDynamicTopView1(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Analitical canalisation solution. the value of pin should be 0.9 max next to the sink.
    
    
    """
    

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 100#0.2
        self.c_change = 1. #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_kappa = 0.00#0.00001
        self.c_pin2aux_diff = 0.0001
        self.c_pin_stability = 0.01
        self.c_sigma_p = 0.1*self.c_pin2aux_diff*self.c_pin_stability#001625 
        self.c_theta_p = 0.2*self.c_pin_stability
        
        self.c_sigma_a = 0
        self.c_sigma_a_prim = 0.1
        self.c_theta_a = 0.2*self.c_pin2aux_diff
        self.c_theta_a_CZ= self.c_theta_a
        self.c_omega = 0

        self.c_gamma = 1
        self.c_ksi = 0.0#4e-7


        self.c_initial_aux_value = self.c_sigma_a_prim / self.c_theta_a
        self.c_initial_pin_value = self.c_sigma_p / self.c_theta_p
        
        self.c_initial_aux_value_CZ = self.c_sigma_a_prim / (self.c_theta_a+self.c_theta_a_CZ )

        self.c_pin_max = 2000000
        self.c_aux_max = 1
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_error_tol = 100000
        
        self.aux_prim_trs_con=2800
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            if i > self.c_break_cond:
                print " !breaking the loop.."
                break
            print " #: phys aux trans: loop=", i, " time=",self.t
            i+=1
            self.info="No info" #(f, x, t,delta_t)
            x0 = self.prepare_x0()
            res = openalea.mersim.tools.integration_rk.rk4( self.f, x0, self.t, self.h )
            #(res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
            res = (x0,res)
            self.t += self.h                
            self.hist[ self.t ] = {}
            stable = self.rate_error( res[0], res[1])
            print stable
            self.update( res[1] )
            y=[]
            z = 0
            # quantitie
            for j in self.cell2sys:
                y.append(res[1][ self.cell2sys[ j ] ] )
                z +=  res[1][ self.cell2sys[ j ] ]
            print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
            y2=[]
            z2=0
            for j in self.wall2sys:
                y2.append(res[1][ self.wall2sys[ j ] ] )
                z2 +=  res[1][ self.wall2sys[ j ] ]
            print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
            print self.info
            if stable:
                self.create_primordiums(self.search_for_primodium())
                    
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        #d = self.hist[ self.t ]
        #d[ "max_aux_diff" ] = max
        self.hist[ self.t ][ "max_aux_diff" ] = max
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return numpy.array(x0)

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return self.c_ksi*x
        
        def P( wid, t, x):
            return  x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return self.c_gamma*( -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x) )
            #return self.c_gamma*( -min(self.c_aux_max,A(j,t,x))*P((j,i),t,x)+min(self.c_aux_max,A(i,t,x))*P((i,j),t,x) )
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ) and not self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a_prim - (self.c_theta_a)*A(i,t,x) #+self.c_theta_a_CZ*self.i_center_evacuate(i)
                s = 0.
                for n in t.cell_neighbors( cell=i ):
                    s+=J((n,i),t,x)*W((i,n))
                x2[ self.cell2sys[ i ] ] += s/S(i)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            x2[ self.wall2sys[(s1,s2)] ] = Fi(J((s1,s2),t,x))+self.c_sigma_p-self.c_theta_p*p1
            
            
            p2 = P((s2,s1),t,x)
            x2[ self.wall2sys[(s2,s1)] ] = Fi(J((s2,s1),t,x))+self.c_sigma_p-self.c_theta_p*p2
            
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        import random
        for c in t.cells():
            self.aux(cell= c, value=self.c_initial_aux_value ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  self.c_initial_aux_value_CZ )
        
    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ") and not t.cell_property( cell=c, property="PrZ"):
                if self.aux( cell = c ) > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y ),  self.aux( cell = x ) ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            #d = t.tissue_property( property="prim2time")
            #d[ c ] = self.t
            #t.tissue_property( property="prim2time", value=d)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            #self.step()


class Phys2DcanalisationForDynamicTopView2(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The center is not doing anything
    
    
    """
    

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 100#0.2
        self.c_change = 1. #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_kappa = 0.00#0.00001
        self.c_pin2aux_diff = 0.0001
        self.c_pin_stability = 0.01
        self.c_sigma_p = 0.1*self.c_pin2aux_diff*self.c_pin_stability#001625 
        self.c_theta_p = 0.2*self.c_pin_stability
        
        self.c_sigma_a = 0
        self.c_sigma_a_prim = 0.1
        self.c_theta_a = 0.2*self.c_pin2aux_diff
        self.c_theta_a_CZ= self.c_theta_a
        self.c_omega = 0

        self.c_gamma = 1
        self.c_ksi = 0.0#4e-7


        self.c_initial_aux_value = self.c_sigma_a_prim / self.c_theta_a
        self.c_initial_pin_value = self.c_sigma_p / self.c_theta_p
        
        self.c_initial_aux_value_CZ = self.c_sigma_a_prim / (self.c_theta_a+self.c_theta_a_CZ )

        self.c_pin_max = 2000000
        self.c_aux_max = 1
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_error_tol = 100000
        
        self.aux_prim_trs_con=self.c_sigma_a_prim / self.c_theta_a - 1300
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            if i > self.c_break_cond:
                print " !breaking the loop.."
                break
            print " #: phys aux trans: loop=", i, " time=",self.t
            i+=1
            self.info="No info" #(f, x, t,delta_t)
            x0 = self.prepare_x0()
            res = openalea.mersim.tools.integration_rk.rk4( self.f, x0, self.t, self.h )
            #(res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
            res = (x0,res)
            self.t += self.h                
            self.hist[ self.t ] = {}
            stable = self.rate_error( res[0], res[1])
            print stable
            self.update( res[1] )
            y=[]
            z = 0
            # quantitie
            for j in self.cell2sys:
                y.append(res[1][ self.cell2sys[ j ] ] )
                z +=  res[1][ self.cell2sys[ j ] ]
            print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
            y2=[]
            z2=0
            for j in self.wall2sys:
                y2.append(res[1][ self.wall2sys[ j ] ] )
                z2 +=  res[1][ self.wall2sys[ j ] ]
            print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
            print self.info
            if stable:
                self.create_primordiums(self.search_for_primodium())
                    
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        #d = self.hist[ self.t ]
        #d[ "max_aux_diff" ] = max
        self.hist[ self.t ][ "max_aux_diff" ] = max
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return numpy.array(x0)

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return self.c_ksi*x
        
        def P( wid, t, x):
            return  x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return self.c_gamma*( -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x) )
            #return self.c_gamma*( -min(self.c_aux_max,A(j,t,x))*P((j,i),t,x)+min(self.c_aux_max,A(i,t,x))*P((i,j),t,x) )
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            #not self.i_center_evacuate( i ) and
            if  not self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a_prim - (self.c_theta_a)*A(i,t,x)#+self.c_theta_a_CZ*self.i_center_evacuate(i))*A(i,t,x) 
                s = 0.
                for n in t.cell_neighbors( cell=i ):
                    s+=J((n,i),t,x)*W((i,n))
                x2[ self.cell2sys[ i ] ] += s/S(i)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            x2[ self.wall2sys[(s1,s2)] ] = Fi(J((s1,s2),t,x))+self.c_sigma_p-self.c_theta_p*p1
            
            
            p2 = P((s2,s1),t,x)
            x2[ self.wall2sys[(s2,s1)] ] = Fi(J((s2,s1),t,x))+self.c_sigma_p-self.c_theta_p*p2
            
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        import random
        for c in t.cells():
            self.aux(cell= c, value=self.c_initial_aux_value ) #+random.random() )
            #if t.cell_property( c, "CZ") > 0:
            #    self.aux( c,  self.c_initial_aux_value_CZ )
        
    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ") and not t.cell_property( cell=c, property="PrZ"):
                if self.aux( cell = c ) > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y ),  self.aux( cell = x ) ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            #d = t.tissue_property( property="prim2time")
            #d[ c ] = self.t
            #t.tissue_property( property="prim2time", value=d)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            #self.step()


class Phys2DcanalisationForDynamicTopView3(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    The center is destroying IAA (removal and not FIXED conc.)
    
    for 2whorled
    self.c_theta_a_CZ= self.c_theta_a*0.2
    self.aux_prim_trs_con=self.c_sigma_a_prim / self.c_theta_a - 1300
    
    for 3whorled
        self.c_theta_a_CZ= self.c_theta_a*0.9
        self.aux_prim_trs_con=self.c_sigma_a_prim / self.c_theta_a - 1500
    
    """
    

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 500#0.2
        self.c_change = 1. #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 300 # used to drop the loop if convergence not reached before x loops
        
        self.c_kappa = 0.00#0.00001
        self.c_pin2aux_diff = 0.0001
        self.c_pin_stability = 0.01
        self.c_sigma_p = 0.1*self.c_pin2aux_diff*self.c_pin_stability#001625 
        self.c_theta_p = 0.2*self.c_pin_stability
        
        self.c_sigma_a = 0
        self.c_sigma_a_prim = 0.1
        self.c_theta_a = 0.2*self.c_pin2aux_diff
        self.c_theta_a_CZ= self.c_theta_a
        self.c_omega = 0

        self.c_gamma = 1
        self.c_ksi = 0.7e-7


        self.c_initial_aux_value = self.c_sigma_a_prim / self.c_theta_a
        self.c_initial_pin_value = self.c_sigma_p / self.c_theta_p
        
        self.c_initial_aux_value_CZ = self.c_sigma_a_prim / (self.c_theta_a+self.c_theta_a_CZ )

        self.c_pin_max = 2000000
        self.c_aux_max = 1
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_error_tol = 100000
        
        self.aux_prim_trs_con=self.c_sigma_a_prim / self.c_theta_a -900
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            if i > self.c_break_cond:
                print " !breaking the loop.."
                break
            print " #: phys aux trans: loop=", i, " time=",self.t
            i+=1
            self.info="No info" #(f, x, t,delta_t)
            x0 = self.prepare_x0()
            res = openalea.mersim.tools.integration_rk.rk4( self.f, x0, self.t, self.h )
            #(res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
            res = (x0,res)
            self.t += self.h                
            self.hist[ self.t ] = {}
            stable = self.rate_error( res[0], res[1])
            print stable
            self.update( res[1] )
            y=[]
            z = 0
            # quantitie
            for j in self.cell2sys:
                y.append(res[1][ self.cell2sys[ j ] ] )
                z +=  res[1][ self.cell2sys[ j ] ]
            print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
            y2=[]
            z2=0
            for j in self.wall2sys:
                y2.append(res[1][ self.wall2sys[ j ] ] )
                z2 +=  res[1][ self.wall2sys[ j ] ]
            print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
            print self.info
            if stable:
                self.create_primordiums(self.search_for_primodium())
                    
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        #d = self.hist[ self.t ]
        #d[ "max_aux_diff" ] = max
        self.hist[ self.t ][ "max_aux_diff" ] = max
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return numpy.array(x0)

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return self.c_ksi*x
        
        def P( wid, t, x):
            return  x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return self.c_gamma*( -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x) )
            #return self.c_gamma*( -min(self.c_aux_max,A(j,t,x))*P((j,i),t,x)+min(self.c_aux_max,A(i,t,x))*P((i,j),t,x) )
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            #not self.i_center_evacuate( i ) and
            if  not self.i_local_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a_prim - (self.c_theta_a)*A(i,t,x) - self.c_theta_a_CZ*self.i_center_evacuate(i) *A(i,t,x)
                s = 0.
                for n in t.cell_neighbors( cell=i ):
                    s+=J((n,i),t,x)*W((i,n))
                x2[ self.cell2sys[ i ] ] += s/S(i)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            x2[ self.wall2sys[(s1,s2)] ] = Fi(J((s1,s2),t,x))+self.c_sigma_p-self.c_theta_p*p1
            
            
            p2 = P((s2,s1),t,x)
            x2[ self.wall2sys[(s2,s1)] ] = Fi(J((s2,s1),t,x))+self.c_sigma_p-self.c_theta_p*p2
            
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        import random
        for c in t.cells():
            self.aux(cell= c, value=self.c_initial_aux_value ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  self.c_initial_aux_value_CZ )
        
    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            
    def search_for_primodium( self ):
        t = self.system.tissue
        pc = []
        for c in t.cells():
            if t.cell_property( cell=c, property="PZ") and not t.cell_property( cell=c, property="PrZ"):
                if self.aux( cell = c ) > self.aux_prim_trs_con:
                    pc.append( c )
        return pc
        
    def create_primordiums( self, primordium_cand=None):
        t = self.system.tissue
        if len(primordium_cand)>0:
            primordium_cand.sort( lambda x, y: cmp( self.aux( cell = y ),  self.aux( cell = x ) ))
            c = primordium_cand[ 0 ]
            t.cell_property( cell=c, property="PrC", value=self.nbr_prim)
            t.cell_property( cell=c, property="PrZ", value=self.nbr_prim)
            #d = t.tissue_property( property="prim2time")
            #d[ c ] = self.t
            #t.tissue_property( property="prim2time", value=d)
            for n in t.cell_neighbors( c ):
                t.cell_property( cell=n, property="PrZ", value=self.nbr_prim)
            self.nbr_prim+=1
            #self.step()



class Phys2DGrid_RL_cactus(PhysAuxinTransportModel):
    """Model with correct resolution using scipy.
    
    Parametrs tuned to reflect canalisation on the 2d system. Inspired by
    Rolland-Lagan&Prusinkiewicz articlie.
    
    The parameters are fixed for the (2) equation (check!).
    
    The target would be to have acropetal vein formations
    """

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 0.1
        self.c_change = 0.0001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        
        self.c_alpha = 0.00001 
        self.c_beta = 0.005#001625 
        self.c_gamma = 0.05 
        
        self.c_sigma = 0 # 50 #!! in the paper they put 50
        self.c_omega =0
        self.c_F = 50 #!! in the paper they put 15

        self.c_transport_saturation = 300

        self.c_initial_aux_value = 200.
        self.c_initial_pin_value = 0.325

        self.c_pin_max = 4.
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_product_source = [217]
        self.c_error_tol = 100000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        self.create_primordiums(self.search_for_primodium())
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return x*x
        
        def P( wid, t, x):
            return min(self.c_pin_max, x[ self.wall2sys[ wid ] ] )

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return -A(j,t,x)*P((j,i),t,x)+A(i,t,x)*P((i,j),t,x)
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_omega+self.c_F*self.i_local_evacuate( i ) + self.c_sigma*self.i_production_on_a_grid( i )
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            if p1 <= self.c_pin_max: x2[ self.wall2sys[(s1,s2)] ] = self.c_alpha*Fi(J((s1,s2),t,x))+self.c_beta-self.c_gamma*p1
            else: x2[ self.wall2sys[(s1,s2)] ] = - p1 + self.c_pin_max
            
            p2 = P((s2,s1),t,x)
            if p2 <= self.c_pin_max: x2[ self.wall2sys[(s2,s1)] ] = self.c_alpha*Fi(J((s2,s1),t,x))+self.c_beta-self.c_gamma*p2
            else: x2[ self.wall2sys[(s2,s1)] ] = - p2 + self.c_pin_max
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell in self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        for c in t.cells():
            self.aux(cell= c, value= self.c_initial_aux_value ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        
    def init_aux4quadrat_grid( self, grid_size=15 ):
        t = self.system.tissue
        for i in range(grid_size):
            for j in range( grid_size ):
                self.aux(cell= i*15+j, value= self.c_F*i/self.c_initial_pin_value ) #+random.random() )
                #self.aux(cell= i*15+j, value= 200. ) #+random.random() )
        #self.aux(cell= self.c_product_source, value= self.aux(cell= self.c_product_source) + self.c_F ) #+random.random() )
        for c in t.cells():
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        

    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )




class Phys1DcanalisationAUX(PhysAuxinTransportModel):
    """The PIN and AUX model.
    
    Basic model
    
    
    """
    

    def __init__(self, tissue_system = None):
        PhysAuxinTransportModel.__init__( self, tissue_system=tissue_system)
        self.system = tissue_system
        self.nbr_prim=1
        self.t = 0
        self.h = 1#0.2
        self.c_change = 0.00000001 #acceptable change could not be smaller to classifie as error.
        self.c_break_cond = 100 # used to drop the loop if convergence not reached before x loops
        self.c_fi_deg = 0.
        
        self.c_kappa = 0.0
        self.c_sigma_p = 0.0
        self.c_theta_p = 0.0
        
        self.c_sigma_a = 0.0
        self.c_sigma_a_prim = 0.0
        self.c_theta_a = 0.0
        self.c_omega = 0.0

        self.c_gamma = 0.0
        self.c_gamma_diff = 0.0
        self.c_ksi = 1.0
        self.c_fi_aux =0.0


        self.c_initial_aux_value = 0.0
        self.c_initial_pin_value = 0.0

        self.c_pin_max = 0
        self.c_aux_max = 0
        self.c_aux_min = 0.

        self.c_pin_tol = 0.01
        self.c_aux_tol = 0.01
        
        self.c_error_tol = 100000000
        
    def apply( self ):
        self.step( )
         
    def step( self, nbr_step=1, precision=1 ):
        t = self.tissue_system.tissue
        self.prepare_sys_map()
        stable=False
        i=0
        while not stable:
            try:
                if i > self.c_break_cond:
                    print " !breaking the loop.."
                    break
                print " #: phys aux trans: loop=", i, " time=",self.t
                i+=1
                (res,self.info)= scipy.integrate.odepack.odeint( self.f, self.prepare_x0(), [self.t, self.t+self.h],rtol=self.error_tol, atol=self.c_error_tol, full_output=1)
                self.t += self.h                
                self.hist[ self.t ] = {}
                stable = self.rate_error( res[0], res[1])
                self.update( res[1] )
                y=[]
                z = 0
                # quantitie
                for j in self.cell2sys:
                    y.append(res[1][ self.cell2sys[ j ] ] )
                    z +=  res[1][ self.cell2sys[ j ] ]
                print "  #: aux qua avg: ", z/len( self.tissue_system.tissue.cells() ), "aux qua min:", min(y), "aux qua max:", max(y)
                y2=[]
                z2=0
                for j in self.wall2sys:
                    y2.append(res[1][ self.wall2sys[ j ] ] )
                    z2 +=  res[1][ self.wall2sys[ j ] ]
                print "  #: pin qua avg: ", z2/len( y2 ), "pin qua min:", min(y2), "pin qua max:", max(y2)
                print self.info
                if stable:
                    raise Exception("Time to stop iterations")
                if precision == 0:
                    return
            except KeyboardInterrupt:
                return
        
    def update( self, x ):
        t = self.system.tissue
        for i in t.cells():
            t0 = x[ self.cell2sys[ i ] ]
            t0 = max(0,t0)
            self.aux( cell=i, value= t0)
        for i in t.cell_edges():
            (c1,c2)=i
            self.pin( cell_edge=(c1,c2), value=min(self.c_pin_max, x[ self.wall2sys[ (c1,c2) ] ] ) )
            self.pin( cell_edge=(c2,c1), value=min(self.c_pin_max, x[ self.wall2sys[ (c2,c1) ] ] ) )        
    

    def rate_error( self, xn, xnprim ):
        max = -float("infinity")
        for c in self.tissue_system.tissue.cells():
            i = self.cell2sys[ c ]
            if abs( xn[i] - xnprim[i] ) > max:
                max=abs( xn[i] - xnprim[i] )
        print " #: max con diff between last steps =  ", max# abs( xn[i] - xnprim[i] )
        #d = self.hist[ self.t ]
        #d[ "max_aux_diff" ] = max
        self.hist[ self.t ][ "max_aux_diff" ] = max
        return self.c_change > max

    def prepare_x0( self ):
        x0 = []
        t = self.system.tissue
        for x in range( len(t.cells()) + len( 2*t.cell_edges() ) ):
            x0.append(0)
        for i in t.cells():
            x0[ self.cell2sys[ i ] ] = self.aux( i )
            self.cell2surface[  i  ] = calculate_cell_surface( t, cell=i )
        for i in t.cell_edges():
            (s,t)=i
            x0[ self.wall2sys[ (s,t) ] ] = self.pin( cell_edge=(s,t) )
            x0[ self.wall2sys[ (t,s) ] ] = self.pin( cell_edge=(t,s) )
        return x0

    def prepare_sys_map( self ):
        self.cell2sys = {}
        self.wall2sys = {}
        self.error_tol = []
        self.cell2surface = {}
        self.cell_edge2wall_length = {}
        self.cell2overall_wall_length = {}
        t = self.system.tissue
        ind = 0
        for i in t.cells():
            self.cell2sys[ i ] = ind
            self.error_tol.append( self.c_aux_tol )
            self.cell2surface[ i ] = calculate_cell_surface( t, cell=i )
            ind += 1
            self.cell2overall_wall_length[ i ] = 0

        for (x,y) in t.cell_edges():
            #(s,t) = i
            self.wall2sys[ (x,y) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            self.wall2sys[ (y,x) ] = ind
            self.error_tol.append( self.c_pin_tol )
            ind += 1
            wl = calculate_wall_length( t, wv_edge= cell_edge2wv_edge( t, (x,y) ) )
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell_edge2wall_length[ (x,y) ] =  wl
            self.cell_edge2wall_length[ (y,x) ] =  wl
            self.cell2overall_wall_length[ x ] +=  wl
            self.cell2overall_wall_length[ y ] +=  wl
    
    def f( self, x, t ):
        def Fi( x ):
            if x < 0:
                return 0
            return self.c_ksi*x
        
        def  Fi_aux( x ):
            #Fi_aux : R+ -> [0,1]
            if x < 0:
                return 1
            return 1./(x+1)
        
        def P( wid, t, x):
            return  x[ self.wall2sys[ wid ] ] 

        def D( (i, j), t, x):
            return (A(i,t,x)-A(j,t,x))
        
        def J( (i, j), t, x):
            return self.c_gamma*( -A(j,t,x)*(P((j,i),t,x)-self.c_fi_aux*Fi_aux(A(j,t,x)))+A(i,t,x)*(P((i,j),t,x)-self.c_fi_aux*Fi_aux(A(i,t,x))))
            #return self.c_gamma*( -min(self.c_aux_max,A(j,t,x))*P((j,i),t,x)+min(self.c_aux_max,A(i,t,x))*P((i,j),t,x) )
            #return -self.c_transport_saturation*A(j,t,x)/(1+A(j,t,x))*P((j,i),t,x)+self.c_transport_saturation*A(i,t,x)/(1+A(i,t,x))*P((i,j),t,x)

        def A( cid, t, x ):
            return max( self.c_aux_min, x[ self.cell2sys[ cid ] ] )
        
        def S( i ):
            return self.cell2surface[ i ]
        
        def W( (i,j) ):
            return self.cell_edge2wall_length[ (i,j) ]
        
        t = self.tissue_system.tissue
        x2 = copy.copy( x )
        for i in t.cells():
            if not self.i_center_evacuate( i ):
                x2[ self.cell2sys[ i ] ]=0
                x2[ self.cell2sys[ i ] ] = self.c_sigma_a_prim - self.c_theta_a*(1+self.c_fi_deg*Fi_aux(A(i,t,x)))*A(i,t,x)
                for n in t.cell_neighbors( cell=i ):
                    x2[ self.cell2sys[ i ] ] += J((n,i),t,x) + self.c_gamma_diff*D((n,i), t, x)
            else:
                x2[ self.cell2sys[ i ] ]=0
        for i in t.cell_edges():
            (s1,s2)=i
            
            p1 = P((s1,s2),t,x)
            x2[ self.wall2sys[(s1,s2)] ] = Fi(J((s1,s2),t,x))+self.c_sigma_p-self.c_theta_p*p1
            
            
            p2 = P((s2,s1),t,x)
            x2[ self.wall2sys[(s2,s1)] ] = Fi(J((s2,s1),t,x))+self.c_sigma_p-self.c_theta_p*p2
            
        return x2

    def i_production_on_a_grid( self, cell ):
        if cell == self.c_product_source:
            return 1
        else: return 0
        
    def i_local_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="PrC") or t.cell_property( cell=cell, property="PrZ") > 0:
            return 1
        else:
            return 0
        
    def i_center_evacuate( self, cell ):
        t = self.system.tissue
        if t.cell_property( cell=cell, property="CZ") > 0:
            return 1
        else:
            return 0
        
    def init_aux(self):
        t = self.system.tissue
        import random
        for c in t.cells():
            self.aux(cell= c, value=self.c_initial_aux_value ) #+random.random() )
            if t.cell_property( c, "CZ") > 0:
                self.aux( c,  0. )
        
    def init_pin( self ):
        t = self.system.tissue
        for (i,j) in t.cell_edges():
            self.pin( (i,j), self.c_initial_pin_value )
            self.pin( (j,i), self.c_initial_pin_value )
            