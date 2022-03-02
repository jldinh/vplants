# -*- python -*-
#
#       HydroRoot
#
#       Copyright 2012 INRIA - CIRAD - INRA  
#
#       File author(s): Mathilde Balduzzi
#                       Christophe Pradal <christophe.pradal.at.cirad.fr>
#                       Christophe Godin  <christophe.pradal.at.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################

"""

"""
from math import pi

from openalea.mtg import traversal
from openalea.plantgl.math import *
from openalea.mtg.plantframe import *


class Meca(object):
    """ Compute the mecanical bending on tree branches defined by a MTG.

    """
    gravity = Vector3(0.0,0.0,-10) # in Newtons

    def __init__(self, density, elasticity, relax, eps):
        """ Flux computes water potential and fluxes at each vertex of the MTG `g`.

        :Parameters:
            - `g` (MTG) - the root architecture

        :Example:

            meca = Meca(g, ...)
        """
        self.density = density
        self.elasticity = elasticity
        self.relax = relax
        self.eps = eps
        self.dresser = dresser

    def rigidity(self,section_type, a, b=0):
        # moment_surf are computed with respect to a horizontal axis in their plane (bending)
        if section_type == "Disc":
            # a should be the radius
            moment_surf = pi*a**4/2
        elif section_type == "Square": 
            moment_surf = a**4/12
        elif section_type == "Rectangle":
            # b = height (bending axis transversal to height)
            moment_surf = a*b**3/12
        elif section_type == "Ring":
            # a = inner radius, b = outer radius
            moment_surf = pi*(b**4-a**4)/32
        return self.elasticity * moment_surf
        
    def run(self, ginit, PLOTFRAMES = True):
        """ Compute the torque, mass and deflexion angles due to gravity of each segments

        :Algorithm:
            The algorithm has two passes:
                - First, on each segment, quantities are accumulated from the leaves of the tree to the root. For this a post-order is used.
                - Second, the bending of the branches is computed from the root to the leaves. For this a pre order (parent then children).
        """
        g = ginit.copy()  # argument should be read only

        # in this first call to plantframe, g is a clone of ginit
        # therefore plantframe will compute the elastic line from the coordinates XX, YY, ZZ of the plant
        topdia = lambda x: g.property('TopDia').get(x)
        pf = plantframe.PlantFrame(g, TopDiameter=topdia, DressingData=self.dresser)
        pf.run()
        density = self.density;
        relax = self.relax; eps = self.eps; gravityvec = self.gravity

        # The idea is to create a MTG g that is a clone of ginit and then to remove its properties 
        # (most of them are not useful for the mecanics)
        # then this structure will be used to iterate the mecanical model by modifying the 
        # vectors representing the segments (segmentvec) that are then used by the plantframe
        # to build the elastic line

        # g.clear_properties() # this will be the datastructure on which we are going to iterate the mecanic module
        g.properties()['segmentvec']= pf.compute_segmentvec()
        g.properties()['topdiam']= pf.compute_diameter()
    
        # Select the base of the root
        v_base = g.component_roots_at_scale_iter(g.root, scale=g.max_scale()).next()
              
        # pf = PlantFrame(g, TopDiameter=topdia)  # Devrait s'appeler MTGgeometry ou equivalent

        error = 0.
        count = 0
        segmentvec = g.property('segmentvec')

        while True:
            cummass = {}
            cumtorque = {}    
            # Backward computation step 
            for v in traversal.post_order2(g, v_base):
                 vmass = density * pf.compute_volume(v)
                 # note: hereafter we don't need to specify the case of leaves as in will follow from the fact that they have no child
                 cummass[v] = vmass + sum(cummass[cid] for cid in g.children(v)) 
                 cumtorque[v] = Vector3(0.,0.,0.)
                 for cid in g.children(v):
                     segvec = segmentvec[cid]
                     weightvec = gravityvec * cummass[cid]
                     cumtorque[v] += cumtorque[cid] + (segvec ^ weightvec)
    
            # Forward computation step 
            for v in traversal.pre_order2(g, v_base):
                parent = g.parent(v)
                if parent is None:
                    parent_dir = Vector3(0.,0.,1.)
                else:
                    parent_dir = segmentvec[parent]; 
                
                seg_dir = segmentvec[v]
                seg_diam = pf.compute_diameter(v)
                seg_length = pf.compute_length(v)
                curvature = cumtorque[v] * (1/(self.rigidity("Disc",seg_diam))) * seg_length
                # plane bending hypothesis !!!! 
                # Only works if seg_dir is not parallel to gravity
                rotation_axis = gravityvec ^ seg_dir 
                if norm(rotation_axis) <= 1.e-8: # seg_dir is in the direction of gravity
                    rot = Matrix3.IDENTITY # then there is no bending (no buckling)
                else:
                    # CPL: rot = Matrix3.axisRotation(rotation_axis,curvature) 
                    rot = Matrix3.axisRotation(rotation_axis,norm(curvature)) 
                new_dir = rot * parent_dir  
                diff = new_dir - seg_dir
                error += norm(diff)
                new_seg_dir = seg_dir + diff * relax
                
                # computes the new value of segmentvec, 
                # as modified by mechanics of the current segment
                # and updates it directly in the segmentvec dict stored in the MTG g
                
                segmentvec[v] = (new_seg_dir/norm(new_seg_dir))*seg_length 
                
                # Note: here diameters don't change (this may change due to growth)

            if PLOTFRAMES:
                # Plots the intermediate result of the machanical computationetry ou equivalent
                #def visitor(g,v,turtle):
                #    turtle.setId(v)
                #    turtle.lineRel(node.segmentvec, node.topdiam)
                #axes = plantframe.compute_axes(g, g.max_scale(), pf.points, pf.origin)
                #diameters = pf.algo_diameter()
                
                #scene = plantframe.build_scene(pf.g, pf.origin, axes, pf.points, diameters, 10000, option='cylinder')
                pf.plot()
                
            if count < 10:
                print "ERROR ", error
                count += 1
            else:
                break
            if error <= eps: break

def apply_meca(ginit, wood_density=1000., young_modulus=1e+9, relax=0.8, epsilon=0.1, dresser=None):
    """ Computes mecanical bending due to gravity of a branching structure defined in the MTG `g`.

        :Parameters:
            - `filename` (MTG) - filename of the MTG
            - wood_density (kg/dm3)
            - young_modulus (MPa)
            - `relax` - 
            - `epsilon` - 


        :Optional Parameters:
            - 
            - 
        :Returned value:
            - MTG modified with meca values and new geometry

        :Example::

            my_modified_mtg = meca(g)
    """    
    

    meca = Meca(wood_density, young_modulus, relax, epsilon)
    
    meca.dresser = dresser
    gbend  = meca.run(ginit, True) # ginit is assumed to be read-only, the second argument indicates whether 
    
    return gbend



