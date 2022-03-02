#!/usr/bin/env python
import visual
import scipy as s
import scipy.optimize as so
import math

def change_basis_to_baricentre( list_of_vectors ):
    """Changes the basis of the points to the baricenter.
    Desired effect should be:
    input: [ v(100,100,100), v(102,102,102) ]
    output: [ v(-1,-1,-1), v(1, 1, 1) ]
    """
    
    baricenter = visual.vector()
    for i in list_of_vectors:
        baricenter += i
    baricenter = baricenter/len( list_of_vectors )
    
    result = []
    for i in list_of_vectors:
        result.append( baricenter-i )
    
    return result


class Pair_difference:
    """Should be used to evaluate the difference between old and new  values.
    """
    def __init__( self, old_values, new_values ):
        """Used to set old values.
        """
        self.old_values = old_values
        self.new_values = new_values
        for i in [self.old_values, self.new_values]:
            for z in range( len ( i ) ):
                i[ z ] = s.matrix( i[ z ] ).transpose()
                
        
        
    def evaluate( self, transformation):
        """Used to evaluate the difference between the values.
        
        :returns: a list L in which for i in L old_value[ i ] - new_value[ i ]
        TODO -- exchange sqrt with 3.
        """
        #print new_values
        #print self.old_values
        #result=[]
        #for i in range( len( self.old_values) ):
        #    for j in range( len( self.old_values[ i ] ) ):
        #        print i, "#", self.old_values[ i ],  new_values[ i ]
        #        r = math.pow( self.old_values[ i ][ j ] - new_values[ i ][ j ], len( new_values[ i ] ) ) 
        #    result.append(  math.sqrt( s ) )
        #return result
    
        error = []
        t = transformation
        for i in range( len ( self.old_values ) ):
            k = transformation.reshape(3,3) * self.old_values[ i ]  -  self.new_values[ i ]
            ##k = transformation.reshape(2,2) * self.old_values[ i ]  -  self.new_values[ i ]

            error.append(  s.dot( k.transpose(), k ).tolist()[0][0] )   
        #print "e=", error
        return error

def vector_to_list( vector_list ):
    result = []
    for i in vector_list:
        result.append( [i.x, i.y, i.z]  )
    return result

def calculate_main_axis( old_shape, new_shape ):
    """Algorithm calculating main axis of deformation of the polygon.
    """
    #for i in old_shape2new_shape.keys():
    #    old_shape.append( i )
    #    new_shape.append( old_shape2new_shape[ i ] )
        
    old_shape  = change_basis_to_baricentre( old_shape )
    new_shape = change_basis_to_baricentre( new_shape )
    
    old_shape = vector_to_list( old_shape )
    new_shape = vector_to_list( new_shape )

    f = Pair_difference( old_values=old_shape, new_values=new_shape )
    return so.leastsq( func = f.evaluate, x0=s.array(  [ 1,0,0, 0,1,0, 0,0,1 ]  ) )
    ##return so.leastsq( func = f.evaluate, x0=s.array(  [ 1,0, 0,1 ]  ), full_output=1 )
old_points3d = [
    [  1.,  1., 0.],
    [ -1., -1., 0.],
    [ -1.,  1., 0.],
    [  1., -1., 0.],
    [  0., 0., 0.],
    [  0., 0., 0.],
    [  0., 0., 0.],
    [  0., 0., 0.],
    [  0., 0., 0.],
    ]
new_points3d = [
    [  2.,  2.,  0. ],
    [ -2., -2.,  0. ],
    [ -2.,  2.,  0. ],
    [  2, -2,  0.],
    [  0., 0., 0.],
    [  0., 0., 0.],
    [  0., 0., 0.],
    [  0., 0., 0.],
    [  0., 0., 0.],

    ]

old_points2d = [
    [  1,  1],
    [ -1, -1],
    [ -1,  1],
    [  1, -1 ]
    ]
new_points2d = [
    [  2,  2 ],
    [ -2, -2 ],
    [ -2,  2 ],
    [  2, -2]
    ]

z = calculate_main_axis(  old_points3d, new_points3d  )
##z = calculate_main_axis(  old_points2d, new_points2d  )
print z
z0 = z[0]
print "z0=",z0 
#f = math.sin
#print so.leastsq( func= f,  x0 = s.identity( 1 ) )
for i in old_points3d:
    #print "i=",i
    #print m
    print z0.reshape(3,3)*i
    
