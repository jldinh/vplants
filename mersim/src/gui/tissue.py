#!/usr/bin/env python
"""<Short description of the module functionality.>

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
__revision__="$Id: tissue.py 7875 2010-02-08 18:24:36Z cokelaer $"


import  openalea.plantgl.ext.all as pd
import  openalea.plantgl.ext.color as color
import  openalea.plantgl.all as pgl
from openalea.mersim.tissue.algo.walled_tissue import cell_center, pin_level, pin_level_wv_edge, auxin_level, wv_edge2cell_edge, calculate_cell_surface
from openalea.mersim.tools.misc import segment, cast_to_0_1_segment 
#viewer.framegl.save_image()
import pylab
import math


green_cell_material = pgl.Material( (0,255,0) )


class SphericalCell(pd.AISphere):
    """<Short description of the class functionality.>
    
    <Long description of the class functionality.>
    """
    def __init__( self, cell=None, wt=None, c_sphere_radius_factor=1, material_f=None, material_range=(0,1), **keys ):
        """Basic constructor.
        """
        pos = cell_center( wt, cell=cell )
        radius = c_sphere_radius_factor*math.sqrt( calculate_cell_surface( wt, cell=cell ) )
        material =  material_f(wt, material_range=material_range, cell=cell )
        pd.AISphere.__init__( self, pos=pos, radius=radius, material=material, **keys )

class PolygonalCell(pd.AICenterPolygon):
    
    def __init__( self,  **keys ):
        """<Short description of the function functionality.>
        
        <Long description of the function functionality.>
        
        :parameters:
            arg1 : `T`
                <Description of `arg1` meaning>
        :rtype: `T`
        :return: <Description of ``return_object`` meaning>
        :raise Exception: <Description of situation raising `Exception`>
        """
        self._common_init(**keys)
        pd.AICenterPolygon.__init__( self, points=self.l, **keys )

            
    def _common_init( self, cell=None, wt=None, abs_border_size=0., **keys ):
        self.cell_center = cell_center( wt=wt, cell=cell )
        self.l = []
        self.abs_border_size = abs_border_size
        for i in wt.cell2wvs( cell=cell ):
            v=wt.wv_pos( wv=i )-self.cell_center
            v2=pgl.Vector3(v)
            v2.normalize()
            self.l.append( self.cell_center+v-v2*abs_border_size )
        
class WalledPolygonalCell(PolygonalCell):

    def __init__( self,  cell=None, wt=None, concentration=False, auxin_range=None, pin_range=(1., 1.3), **keys ):
        """<Short description of the function functionality.>
        
        <Long description of the function functionality.>
        
        :parameters:
            arg1 : `T`
                <Description of `arg1` meaning>
        :rtype: `T`
        :return: <Description of ``return_object`` meaning>
        :raise Exception: <Description of situation raising `Exception`>
        """
        PolygonalCell.__init__( self, cell=cell, wt=wt, pos=pgl.Vector3(0,0,-0.0001), **keys )
        #self._points[ 0 ].z = -1
        self.walls = {}
        if not concentration:
            aux = cast_to_0_1_segment( (0.1,1.5), auxin_level( wt, cell=cell ) )
        else:
            #print auxin_level( wt, cell=cell )/calculate_cell_surface( wt, cell=cell )
            aux = cast_to_0_1_segment( (auxin_range[ 0 ], auxin_range[ 1 ]), auxin_level( wt, cell=cell ))#/calculate_cell_surface( wt, cell=cell ) )
        if wt.cell_property(cell=cell, property="PZ"):
            pd.AISphere(pos=self.cell_center, radius=0.009)
        if wt.cell_property(cell=cell, property="PrC")>0:
            pd.AISphere(pos=self.cell_center, radius=0.01, material=pgl.Material((250,250,0)))
    
        for i in wt.cell2wvs_edges_in_real_order( cell=cell ):
            (wv1, wv2) = i
            v11=wt.wv_pos( wv=wv1 )-self.cell_center
            v12=pgl.Vector3(v11)
            v12.normalize()
            v21=wt.wv_pos( wv=wv2 )-self.cell_center
            v22=pgl.Vector3(v21)
            v22.normalize()
            
            # searching for pin concentration in the wall
            try:
                ce = wv_edge2cell_edge( wt, wt.wv_edge_id( i ) )
                if ce[ 0 ] == cell:
                    pl = pin_level( wt, cell_edge=ce )
                else:
                    pl = pin_level( wt, cell_edge=(ce[ 1 ], ce[ 0 ] ) )                
                pl = (pl - 0.99)*14 #/70
            except TypeError:
                pl=0.
            
            pin_con = 0.003+pl/100.
            
            self.walls[ i ] = pd.AITriangle( points=[self.cell_center, self.cell_center+v11-v12*pin_con, self.cell_center+v21-v22*pin_con], material=pgl.Material(pgl.Color3(0,int(aux*255),0)) )


class WalledPolygonalCell1(PolygonalCell):

    def __init__( self,  cell=None, wt=None, concentration=False, auxin_range=None, pin_range=(1., 1.3), **keys ):
        """The pin property is required for this cell.
        
        <Long description of the function functionality.>
        
        :parameters:
            arg1 : `T`
                <Description of `arg1` meaning>
        :rtype: `T`
        :return: <Description of ``return_object`` meaning>
        :raise Exception: <Description of situation raising `Exception`>
        """
        PolygonalCell.__init__( self, cell=cell, wt=wt, pos=pgl.Vector3(0,0,-0.0001), **keys )
        if wt.cell_property(cell=cell, property="PZ"):
            pd.AISphere(pos=self.cell_center, radius=0.009)
        if wt.cell_property(cell=cell, property="PrC")>0:
            pd.AISphere(pos=self.cell_center, radius=0.01, material=pgl.Material((250,250,0)))
        self.walls = {}
        for i in wt.cell2wvs_edges_in_real_order( cell=cell ):
            (wv1, wv2) = i
            v11=wt.wv_pos( wv=wv1 )-self.cell_center
            v12=pgl.Vector3(v11)
            v12.normalize()
            v21=wt.wv_pos( wv=wv2 )-self.cell_center
            v22=pgl.Vector3(v21)
            v22.normalize()
            
            # searching for pin concentration in the wall
            try:
                ce = wv_edge2cell_edge( wt, wt.wv_edge_id( i ) )
                if ce[ 0 ] == cell:
                    pl = pin_level( wt, cell_edge=ce )
                else:
                    pl = pin_level( wt, cell_edge=(ce[ 1 ], ce[ 0 ] ) )                
                pl = (pl - 0.99)*14 #/70
            except TypeError:
                pl=0.
            
            pin_con = 0.003+pl/100.
            
            self.walls[ i ] = pd.AITriangle( points=[self.cell_center, self.cell_center+v11-v12*pin_con, self.cell_center+v21-v22*pin_con], material=pgl.Material(pgl.Color3(0,255,0)) )



class WalledPolygonalCellScale(PolygonalCell):

    def __init__( self,  cell=None, wt=None, auxin_range=(0.1,1.5), pin_range=(1., 1.3), **keys ):
        """<Short description of the function functionality.>
        
        <Long description of the function functionality.>
        
        :parameters:
            arg1 : `T`
                <Description of `arg1` meaning>
        :rtype: `T`
        :return: <Description of ``return_object`` meaning>
        :raise Exception: <Description of situation raising `Exception`>
        """
        PolygonalCell.__init__( self, cell=cell, wt=wt, pos=pgl.Vector3(0,0,-0.0001), **keys )

        self.walls = {}
        aux = cast_to_0_1_segment( (auxin_range[ 0 ], auxin_range[ 1 ]), auxin_level( wt, cell=cell ))#/calculate_cell_surface( wt, cell=cell ) )
        
        #if wt.cell_property(cell=cell, property="PZ"):
        #    pd.AISphere(pos=self.cell_center, radius=0.009)
        #if wt.cell_property(cell=cell, property="PrC")>0:
        #    pd.AISphere(pos=self.cell_center, radius=0.01, material=pgl.Material((250,250,0)))
    
        for i in wt.cell2wvs_edges_in_real_order( cell=cell ):
            (wv1, wv2) = i
            v11=wt.wv_pos( wv=wv1 )-self.cell_center
            v12=pgl.Vector3(v11)
            v12.normalize()
            v21=wt.wv_pos( wv=wv2 )-self.cell_center
            v22=pgl.Vector3(v21)
            v22.normalize()
            # searching for pin concentration in the wall
            try:
                ce = wv_edge2cell_edge( wt, wt.wv_edge_id( i ) )
                if ce[ 0 ] == cell:
                    pl = cast_to_0_1_segment( base_segment=pin_range, value=pin_level( wt, cell_edge=ce ))
                else:
                    pl = cast_to_0_1_segment( base_segment=pin_range, value=pin_level( wt, cell_edge=(ce[ 1 ], ce[ 0 ] ) ) )
            except TypeError:
                pl=0.
            k = 0.97*(1-0.25*pl)
            #self.walls[ i ] = pd.AITriangle( points=[self.cell_center, self.cell_center+v11-v12*0.02*(0.98-0.6*pl), self.cell_center+v21-v22*0.02*(0.98-0.6*pl)], material=pgl.Material(pgl.Color3(0,int(aux*255),0)) )
            self.walls[ i ] = pd.AITriangle( points=[self.cell_center, self.cell_center+v11*k, self.cell_center+v21*k], material=pgl.Material(0, pgl.Color3(int(aux*255),0)) )


class WalledPolygonalCellRD1(PolygonalCell):

    def __init__( self,  cell=None, wt=None, concentration=False, auxin_range=None, concentration_rangeH=None, **keys ):
        """<Short description of the function functionality.>
        
        <Long description of the function functionality.>
        
        :parameters:
            arg1 : `T`
                <Description of `arg1` meaning>
        :rtype: `T`
        :return: <Description of ``return_object`` meaning>
        :raise Exception: <Description of situation raising `Exception`>
        """
        PolygonalCell.__init__( self, cell=cell, wt=wt, pos=pgl.Vector3(0,0,-0.0001), **keys )
        #self._points[ 0 ].z = -1
        self.walls = {}
        if not concentration:
            aux = cast_to_0_1_segment( (0,1), auxin_level( wt, cell=cell ) )
        else:
            #print auxin_level( wt, cell=cell )/calculate_cell_surface( wt, cell=cell )
            #/calculate_cell_surface( wt, cell=cell )
            aux = cast_to_0_1_segment( (auxin_range[ 0 ], auxin_range[ 1 ]), auxin_level( wt, cell=cell ) )
        
        #/calculate_cell_surface( wt, cell=cell )
        inh = cast_to_0_1_segment( (concentration_rangeH[ 0 ], concentration_rangeH[ 1 ]), wt.cell_property( cell=cell, property="inh" ) )
        pd.AISphere(pos=self.cell_center, radius=0.04, material=pgl.Material(pgl.Color3(int(inh*255),0,0)))
        
        for i in wt.cell2wvs_edges_in_real_order( cell=cell ):
            (wv1, wv2) = i
            v11=wt.wv_pos( wv=wv1 )-self.cell_center
            v12=pgl.Vector3(v11)
            v12.normalize()
            v21=wt.wv_pos( wv=wv2 )-self.cell_center
            v22=pgl.Vector3(v21)
            v22.normalize()
            
            # searching for pin concentration in the wall
            try:
                ce = wv_edge2cell_edge( wt, wt.wv_edge_id( i ) )
                if ce[ 0 ] == cell:
                    pl = pin_level( wt, cell_edge=ce )
                else:
                    pl = pin_level( wt, cell_edge=(ce[ 1 ], ce[ 0 ] ) )                
                pl = (pl - 0.99)*14 #/70
            except TypeError:
                pl=0.
            
            pin_con = 0.003+pl/100.
            
            self.walls[ i ] = pd.AITriangle( points=[self.cell_center, self.cell_center+v11-v12*pin_con, self.cell_center+v21-v22*pin_con], material=pgl.Material(pgl.Color3(0,int(aux*255),0)) )


class WalledPolygonalCellTODO(PolygonalCell):

    def __init__( self,  cell=None, wt=None, thickness_range=(0., 1.), max_wall_absolute_thickness=1., wall_thickness_f=None, material_range=None, material_f=green_cell_material, **keys ):
        """<Short description of the function functionality.>
        
        This cell has a standard cell color and a standard cell wall color. It requires the wall
        property which would be used to determine wall fickness. Also a range of the possible
        fickness should be given as well as *absolute* max wall thickness. The function specifying
        the wall thickness should be also specified.
        
        :parameters:
            arg1 : `T`
                <Description of `arg1` meaning>
        :rtype: `T`
        :return: <Description of ``return_object`` meaning>
        :raise Exception: <Description of situation raising `Exception`>
        """
        PolygonalCell.__init__( self, cell=cell, wt=wt, pos=pgl.Vector3(0,0,-0.01), **keys )

        self.walls = {}
            
        for i in wt.cell2wvs_edges_in_real_order( cell=cell ):
            (wv1, wv2) = i
            # searching for pin concentration in the wall
            try:
                ce = wv_edge2cell_edge( wt, wt.wv_edge_id( i ) )
                if ce[ 0 ] == cell:
                    pl = cast_to_0_1_segment( base_segment=thickness_range, value=wall_thickness_f( wt, cell_edge=ce ))
                else:
                    pl = cast_to_0_1_segment( base_segment=thickness_range, value=wall_thickness_f( wt, cell_edge=(ce[ 1 ], ce[ 0 ] ) ) )
            except TypeError:
                pl=0.
            pl = pl*max_wall_absolute_thickness
            
            l = []
            v1 = wt.wv_pos( wv=wv1 )
            v2 = wt.wv_pos( wv=wv2 )
            c = self.cell_center
            for i in [(v1, v2), (v2, v1)]:
                norm_h = pl*pgl.norm(c - i[0])*pgl.norm(i[1]-i[0])/pgl.norm( pgl.cross(c-i[0], i[1]-i[0]) )
                #print v1, v2, i[0],  pgl.norm( (c - i[0]) ), norm_h
                x = (c - i[0])
                x.normalize()
                h = i[0] + x*norm_h
                l.append( h )
            if material_f == green_cell_material:
                self.walls[ wt.wv_edge_id( i ) ] = pd.AITriangle( points=[self.cell_center, l[0], l[1]], material= pgl.Material(pgl.Color3())) 
            else:
                self.walls[ wt.wv_edge_id( i ) ] = pd.AITriangle( points=[self.cell_center, l[0], l[1]], material= material_f( wt, material_range, cell ) )


class WalledPolygonalCellWithArrowWalls(PolygonalCell):

    def __init__( self,  cell=None, wt=None, thickness_range=(0., 1.), max_wall_absolute_thickness=1., wall_thickness_f=None, material_range=None, material_f=green_cell_material, **keys ):
        """<Short description of the function functionality.>
        
        This cell has a standard cell color and a standard cell wall color. It requires the wall
        property which would be used to determine wall fickness. Also a range of the possible
        fickness should be given as well as *absolute* max wall thickness. The function specifying
        the wall thickness should be also specified.
        
        :parameters:
            arg1 : `T`
                <Description of `arg1` meaning>
        :rtype: `T`
        :return: <Description of ``return_object`` meaning>
        :raise Exception: <Description of situation raising `Exception`>
        """
        PolygonalCell.__init__( self, cell=cell, wt=wt, pos=pgl.Vector3(0,0,-0.01), **keys )

        self.walls = {}
        wiro = wt.cell2wvs_edges_in_real_order( cell=cell )
        count = 0
        for i in wiro:
            (wv1, wv2) = i
            # searching for pin concentration in the wall
            ex = False
            try:
                ce = wv_edge2cell_edge( wt, wt.wv_edge_id( i ) )
            except TypeError:
                #print "err", thickness_range, wall_thickness_f( wt, cell_edge=ce ), wall_thickness_f( wt, cell_edge=(ce[ 1 ], ce[ 0 ] ) )
                pl=0.
                #s.print "err", i
                ex=True
            if not ex:
                if ce[ 0 ] == cell:
                    pl = cast_to_0_1_segment( base_segment=thickness_range, value=wall_thickness_f( wt, cell_edge=ce ))
                    #print "#1", thickness_range, wall_thickness_f( wt, cell_edge=ce )
                else:
                    pl = cast_to_0_1_segment( base_segment=thickness_range, value=wall_thickness_f( wt, cell_edge=(ce[ 1 ], ce[ 0 ] ) ) )
                    #print "#2", thickness_range, wall_thickness_f( wt, cell_edge=(ce[ 1 ], ce[ 0 ] ) ) 
                pl = pl*max_wall_absolute_thickness
            #print i, pl
            l = []
            c = self.cell_center
            nv1 = wt.wv_pos( wv=wv1 )-c
            nv2 = wt.wv_pos( wv=wv2 )-c
            nv1.normalize()
            nv2.normalize()
            v1 = wt.wv_pos( wv=wv1 ) - nv1*self.abs_border_size 
            v2 = wt.wv_pos( wv=wv2 ) - nv2*self.abs_border_size
            for i in [(v1, v2), (v2, v1)]:
                norm_h = pl*pgl.norm(c - i[0])*pgl.norm(i[1]-i[0])/pgl.norm( pgl.cross(c-i[0], i[1]-i[0]) )
                #print v1, v2, i[0],  pgl.norm( (c - i[0]) ), norm_h
                x = (c - i[0])
                x.normalize()
                h = i[0] + x*norm_h
                l.append( h )
            if material_f == green_cell_material:
                material = pgl.Material(pgl.Color3())
            else:
                material = material_f( wt, material_range, cell )    
            self.walls[ wt.wv_edge_id( i ) ] = pd.AITriangle( points=[self.cell_center, l[0], l[1]], material= material)
            
            #plotting the arrow marks
            vs = (v1,v2)
            ns = (wt.wv_pos( wiro[ (count - 1)%len(wiro) ][ 0 ]), wt.wv_pos( wiro[ (count + 1)%len(wiro) ][ 1 ]) )
            for i in range(2):
                zz1 = ns[i]-vs[i]
                nor = zz1.normalize()
                points = [vs[i],vs[i]+zz1*min(nor*0.5, norm_h*1.5),l[i]]
                if points[0] != points[1] and points[0] != points[2] and points[1] != points[2]:
                    pd.AITriangle( points=points, material= pd.red, pos=pgl.Vector3(0,0,0.01) ) 
            count += 1

def auxin2material1( wt=None, auxin_range=(0,1), cell=None ):
    aux = cast_to_0_1_segment( (auxin_range[ 0 ], auxin_range[ 1 ]), auxin_level( wt, cell=cell ))#/calculate_cell_surface( wt, cell=cell ) )
    #print aux
    #int(aux*255))
    return pgl.Material(pgl.Color3(0, int(aux*255),0))


jet_color_range = color.JetMap(outside_values=True)
def auxin2material2( wt=None, auxin_range=(0,1), cell=None ):
    jet_color_range.set_value_range( auxin_range )
    #aux = cast_to_0_1_segment( (auxin_range[ 0 ], auxin_range[ 1 ]), auxin_level( wt, cell=cell ))#/calculate_cell_surface( wt, cell=cell ) )
    #return pgl.Material(pgl.Color3(0, int(aux*255),0))
    return pgl.Material( jet_color_range.get_color( auxin_level( wt, cell=cell ) ).i3tuple() ) 

jet_color_range2 = color.JetMap(outside_values=True)
def auxin2material3( wt=None, auxin_range=(0,1), cell=None ):
    jet_color_range2.set_value_range( auxin_range )
    #aux = cast_to_0_1_segment( (auxin_range[ 0 ], auxin_range[ 1 ]), auxin_level( wt, cell=cell ))#/calculate_cell_surface( wt, cell=cell ) )
    #return pgl.Material(pgl.Color3(0, int(aux*255),0))
    return pgl.Material( jet_color_range2.get_color( auxin_level( wt, cell=cell ) ).i3tuple() ) 


terrain_color_range = color.TerrainMap(outside_values=True)
def auxin2material4( wt=None, auxin_range=(0,1), cell=None ):
    terrain_color_range.set_value_range( auxin_range )
    #aux = cast_to_0_1_segment( (auxin_range[ 0 ], auxin_range[ 1 ]), auxin_level( wt, cell=cell ))#/calculate_cell_surface( wt, cell=cell ) )
    #return pgl.Material(pgl.Color3(0, int(aux*255),0))
    return pgl.Material( terrain_color_range.get_color( auxin_level( wt, cell=cell ) ).i3tuple() )

jet_without_red_color_range = color.JetMapWithoutRed(outside_values=True)
def auxin2material5( wt=None, auxin_range=(0,1), cell=None ):
    jet_without_red_color_range.set_value_range( auxin_range )
    return pgl.Material( jet_without_red_color_range.get_color( auxin_level( wt, cell=cell ) ).i3tuple() )

green_range = color.GreenMap(outside_values=True)
def auxin2material6( wt=None, auxin_range=(0,1), cell=None ):
    green_range.set_value_range( auxin_range )
    return pgl.Material( green_range.get_color( auxin_level( wt, cell=cell ) ).i3tuple() )


def auxin2material7( wt=None, auxin_range=(0,1), cell=None ):
    if auxin_level( wt, cell=cell ) > 4.6: return pgl.Material( (0,255,0) )
    return pgl.Material((0,0,0))

flux2material_green_range = color.GreenMap(outside_values=True)
flux2material_green_range._position_list=[0.,0.5,1.]
def flux2material( wt=None, auxin_range=(0,1), cell=None ):
    flux2material_green_range.set_value_range(auxin_range)
    if wt.cell_property(cell, "PrZ"): return pgl.Material((0,255,0))
    return pgl.Material( flux2material_green_range.get_color( wt.cell2flux[cell] ).i3tuple() )

fluxAndAuxin2material_green_range = color.GreenMap(outside_values=True)
fluxAndAuxin2material_green_range._position_list=[0.,0.5,1.]
def fluxAndAuxin2material( wt=None, auxin_range=(0,1), cell=None ):
    fluxAndAuxin2material_green_range.set_value_range(auxin_range)
    #if wt.cell_property(cell, "PrZ"): return pgl.Material((0,255,0))
    print min(wt.c_flux_factor*wt.cell2flux[cell], auxin_level(wt, cell))== wt.c_flux_factor*wt.cell2flux[cell],min(wt.c_flux_factor*wt.cell2flux[cell], auxin_level(wt, cell)), wt.c_flux_factor*wt.cell2flux[cell], auxin_level(wt, cell)
    return pgl.Material( fluxAndAuxin2material_green_range.get_color( min(wt.c_flux_factor*wt.cell2flux[cell],auxin_level(wt, cell)) ).i3tuple() )


fluxAndAuxin2material2_green_range = color.GreenMap(outside_values=True)
fluxAndAuxin2material2_green_range._position_list=[0.,0.5,1.]
def fluxAndAuxin2material2( wt=None, auxin_range=(0,1), cell=None ):
    fluxAndAuxin2material2_green_range.set_value_range(auxin_range)
    #if wt.cell_property(cell, "PrZ"): return pgl.Material((0,255,0))
    #print wt.c_flux_factor*wt.cell2flux[cell], auxin_level(wt, cell)
    #if wt.cell_property(cell, "PrZ"):
    #    return pgl.Material(pgl.Color3(0,255,0))
    return pgl.Material( fluxAndAuxin2material2_green_range.get_color( wt.c_flux_factor*wt.cell2flux[cell]+wt.c_concentration_factor*auxin_level(wt, cell) ).i3tuple() )


def f_property2material( property=None, property_material=pgl.Material((0,255,0)), normal_material=pgl.Material((0,0,0)) ):
    def f( wt=None, cell=None, **keys):
        if wt._cell2properties[cell].has_key(property):
            if wt.cell_property( cell, property):
                return property_material
            else: return normal_material
        else: return normal_material
    return f

weighted_property2material_green_range = color.GreenMap(outside_values=True)
weighted_property2material_green_range._position_list=[0.,0.1,1.]
def f_weighted_property2material( property=None, range=[0,1], property_material=pgl.Material((0,255,0)), normal_material=pgl.Material((0,0,0)) ):
    weighted_property2material_green_range.set_value_range(range)
    def f( wt=None, cell=None, **keys):
        if wt._cell2properties[cell].has_key(property):
            return pgl.Material( weighted_property2material_green_range.get_color( wt.cell_property(cell, property) ).i3tuple() )
        else: return normal_material
    return f


def visualisation1( wt, concentration_range=None):
    pd.set_instant_update_visualisation_policy( policy = False )
    l=[]
    for i in wt.cells():
        #l.append( WalledPolygonalCell(cell=i, wt=wt, abs_border_size=0.007, material=pd.red) )
        l.append( WalledPolygonalCell(cell=i, wt=wt, abs_border_size=0., material=pd.red, concentration=True, auxin_range=concentration_range) )
    pd.set_instant_update_visualisation_policy( policy = True )
    #pd.instant_update_viewer( )

def visualisation2( wt, concentration_range=None, concentration_rangeH=None):
    pd.set_instant_update_visualisation_policy( policy = False )
    l=[]
    for i in wt.cells():
        #l.append( WalledPolygonalCell(cell=i, wt=wt, abs_border_size=0.007, material=pd.red) )
        l.append( WalledPolygonalCellRD1(cell=i, wt=wt, abs_border_size=0., material=pd.red, concentration=True, auxin_range=concentration_range, concentration_rangeH=concentration_rangeH ) )
    pd.set_instant_update_visualisation_policy( policy = True )
    #pd.instant_update_viewer( )

def visualisation3( wt, concentration_range=None, pin_range=None):
    pd.set_instant_update_visualisation_policy( policy = False )
    l=[]
    for i in wt.cells():
        #l.append( WalledPolygonalCell(cell=i, wt=wt, abs_border_size=0.007, material=pd.red) )
        l.append( WalledPolygonalCellScale(cell=i, wt=wt, abs_border_size=0., material=pd.red, auxin_range=concentration_range, pin_range=pin_range ) )
    pd.set_instant_update_visualisation_policy( policy = True )
    #pd.instant_update_viewer( )

def cont_prims_visualisation1( wt ):
    pd.set_instant_update_visualisation_policy( policy = False )
    l=[]
    for (n,p) in wt.cont_prims.prims.iteritems():
        l.append( pd.AISphere(pos=p.pos, radius=p.radius, material=pgl.Material((0,60,0))) )
    pd.set_instant_update_visualisation_policy( policy = True )
    #pd.instant_update_viewer( )

def visualisation_of_flux_zones_1( wt, cells=None, tol=1.2, group_material=pgl.Material((250,0,200)), rest_material=pgl.Material((255,255,255)),
    group_center_material=pgl.Material((250,0,100)), pin_range=None ):
    pd.set_instant_update_visualisation_policy( policy = False )
    cell=cells[ 0 ]
    l={}
    for i in wt.cells():
        #l.append( WalledPolygonalCell(cell=i, wt=wt, abs_border_size=0.007, material=pd.red) )
        #l[i]= WalledPolygonalCellScale(cell=i, wt=wt, abs_border_size=0., material=pd.red, concentration=True, auxin_range=(0,2), pin_range=pin_range) 
        l[i]=WalledPolygonalCellTODO(cell=i, wt=wt, abs_border_size=0., material=pd.red,  thickness_range=pin_range,
                                          wall_thickness_f=pin_level, max_wall_absolute_thickness=0.05 ) 

    for i in wt.cells():
        for j in l[ i ].walls: 
            l[ i ].walls[ j ].material = rest_material

    # coloring the desired group
    for i in cells:
        for j in l[ i ].walls: 
            l[ i ].walls[ j ].material = group_material

    # finding influance zone        
    z=cells
    rem = []
    changed = []
    while z:
        c = z.pop()
        if c in rem: continue
        rem.append( c )
        for i in wt.cell_neighbors( c ):
            if pin_level( wt, cell_edge=(i, c) ) > tol:
                for j in l[ i ].walls: 
                    l[ i ].walls[ j ].material = group_material
                z.append( i )
                changed.append( i )
        
    # filing the gaps
    for i in wt.cells():
        nei = wt.cell_neighbors( i )
        k = 0
        for n in nei:
            if n in changed:
                k+=1
            else:
                continue
            if k > len(nei)-2:
                changed.append( i )
                for j in l[ i ].walls: 
                    l[ i ].walls[ j ].material = group_material        
                break
    
    # filing center
    for j in l[ cell ].walls: 
        l[ cell ].walls[ j ].material = group_center_material
                
    pd.set_instant_update_visualisation_policy( policy = True )
    
    
def create_meristem_stem( points=None, central_zone=None, distance=None, profile_f=None ):
    """Creates and displays a surface of revolution around given set of points.
    
    Given set of points should be a list of openalea.plantgl.Vector2 describing a X and Y
    of the surface. The surface is turned around Z axis.
    
    :parameters:
        points : [`openalea.plantgl.Vector2`]
            list of points createing a SOR 
    """
    if not points:
        if not profile_f:
            profile_f = lambda x: -x*x + central_zone*central_zone
        x = segment(x1=central_zone, x2=central_zone+distance, step=0.01)
        y = map( profile_f , x )
        xy= map( lambda x: pgl.Vector2(x), zip(x, y))
    pl = pgl.Polyline2D( xy )
    r = pgl.Revolution(pl, 36)
    sh = pgl.Shape(r, pd.green)
    pd.SCENES[ 0 ] += sh
    c=pd.AICylinder( pos=(0,0,-0.001), axis=(0,0,0.0005), radius=central_zone+0.01, material=pd.green)
    c.geometry.slices=50
    #pd.instant_update_viewer( )



def visualisationTODO( wt, concentration_range=None, pin_range=None):
    pd.set_instant_update_visualisation_policy( policy = False )
    l=[]
    for i in wt.cells():
        #l.append( WalledPolygonalCell(cell=i, wt=wt, abs_border_size=0.007, material=pd.red) )
        l.append( WalledPolygonalCellTODO(cell=i, wt=wt, abs_border_size=0., material=pd.red, auxin_range=concentration_range, thickness_range=pin_range,
                                          wall_thickness_f=pin_level, max_wall_absolute_thickness=0.05, material_f=auxin2material1, material_range=concentration_range) )
    pd.set_instant_update_visualisation_policy( policy = True )
    #pd.instant_update_viewer( )
    

def visualisationTODO2( wt, concentration_range=None, pin_range=None):
    pd.set_instant_update_visualisation_policy( policy = False )
    l=[]
    for i in wt.cells():
        #l.append( WalledPolygonalCell(cell=i, wt=wt, abs_border_size=0.007, material=pd.red) )
        l.append( WalledPolygonalCellTODO(cell=i, wt=wt, abs_border_size=0., material=pd.red, auxin_range=concentration_range, thickness_range=pin_range,
            wall_thickness_f=pin_level, max_wall_absolute_thickness=0.005, material_f=auxin2material1, material_range=concentration_range) )
        if wt.cell_property( i, "CZ") > 0:
            l.append( pd.AISphere(pos=cell_center( wt, i ), radius=0.01 ) )
        if wt.cell_property( i, "PrZ") > 0:
            l.append( pd.AISphere(pos=cell_center( wt, i ), radius=0.01, material=pd.blue ) )
    pd.set_instant_update_visualisation_policy( policy = True )
    #pd.instant_update_viewer( )


def visualisation_pgl_2D_linear_tissue_aux_pin( wt, concentration_range=None, pin_range=None, max_wall_absolute_thickness=0.15, cell_marker_size=0.03, abs_intercellular_space=0., material_f=auxin2material2):
    pd.set_instant_update_visualisation_policy( policy = False )
    l=[]
    for i in wt.cells():
        #l.append( WalledPolygonalCellTODO(cell=i, wt=wt, abs_border_size=0., material=pd.red, auxin_range=concentration_range, thickness_range=pin_range,
        #    wall_thickness_f=pin_level, max_wall_absolute_thickness=max_wall_absolute_thickness, material_f=auxin2material1, material_range=concentration_range) )
        l.append( WalledPolygonalCellWithArrowWalls(cell=i, wt=wt, abs_border_size=abs_intercellular_space, material=pd.red, auxin_range=concentration_range, thickness_range=pin_range,
            wall_thickness_f=pin_level, max_wall_absolute_thickness=max_wall_absolute_thickness, material_f=material_f, material_range=concentration_range) )
        if wt.cell_property( i, "CZ") > 0:
            l.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size ) )
        if wt.cell_property( i, "PrZ") > 0:
            l.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size , material=pd.blue ) )
        if wt.cell_property( i, "PZ") > 0:
            l.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size , material=pd.black ) )
    pd.set_instant_update_visualisation_policy( policy = True )
    #pd.instant_update_viewer( )

def visualisation_pgl_2D_plain( wt, concentration_range=None, pin_range=None, max_wall_absolute_thickness=0.15, cell_marker_size=0.03, abs_intercellular_space=0., material_f=auxin2material2):
    pd.set_instant_update_visualisation_policy( policy = False )
    l=[]
    for i in wt.cells():
        l.append( WalledPolygonalCellWithArrowWalls(cell=i, wt=wt, abs_border_size=abs_intercellular_space, material=pd.red, auxin_range=concentration_range, thickness_range=pin_range,
            wall_thickness_f=pin_level, max_wall_absolute_thickness=max_wall_absolute_thickness, material_f=material_f, material_range=concentration_range) )
    pd.set_instant_update_visualisation_policy( policy = True )


def mark_regions1( wt, cell, list, cell_marker_size ):
    """Surface
    """
    l2=list
    i=cell
    if wt.cell_property( i, "CZ") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size, material=pd.white ) )
    if wt.cell_property( i, "PrZ") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size , material=pd.blue ) )
    if wt.cell_property( i, "PZ") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size , material=pd.black ) )
    return l2


def visualisation_pgl_2D_linear_tissue_aux_pin2( wt, concentration_range=None, pin_range=None, max_wall_absolute_thickness=0.15,
                                                cell_marker_size=0.03, abs_intercellular_space=0., material_f=auxin2material2,
                                                revers=True,  wall_color=pgl.Color4(0,0,0,0), pump_color=pgl.Color4(255,0,0,0),
                                                prim_cells_with_pin=None, stride=100, f_mark_regions=mark_regions1):
    
    pd.set_instant_update_visualisation_policy( policy = False )
    from openalea.mersim.gui.draw_cell import draw_cell
    def ff(x,j):
        if x[0]==j: return x
        else: return (x[1],x[0])

    l=[]
    l2=[]
    for i in wt.cells():
        #print i
        cell_corners=[wt.wv_pos(j) for j in wt.cell2wvs(i)]
        # wv edges to get cell edges to dig into pin 
        c=[]
        for j in wt.cell2wvs_edges(i):
            try:
                c.append( ff(wv_edge2cell_edge( wt, j), i) )
            except Exception:
                c.append(None)
        wall_relative_thickness=[]
        for j in c:
            if j: wall_relative_thickness.append(pin_level(wt,j))
            else: wall_relative_thickness.append(0.)
        # PZ are glowing
        #if wt.cell_property(i, "PrZ") and prim_cells_with_pin:
        #    for j in range(len(wall_relative_thickness)):
        #        wall_relative_thickness[j] = prim_cells_with_pin
        if wt.cell_property(i, "PrZ") and prim_cells_with_pin:
            for j in range(len(c)):
                try:
                    if wt.cell_property(c[j][1], "PrC"): 
                        wall_relative_thickness[j] = prim_cells_with_pin
                except TypeError:
                    wall_relative_thickness[j] = 0 
        if wt.cell_property(i, "PrC") and prim_cells_with_pin:
            for j in range(len(wall_relative_thickness)):
                wall_relative_thickness[j] = prim_cells_with_pin

        
        wall_relative_thickness=[cast_to_0_1_segment( base_segment=pin_range, value=j) for j in wall_relative_thickness]
        thickness_min=abs_intercellular_space#0.1*max_wall_absolute_thickness
        thickness_max=max_wall_absolute_thickness
        cell_color=material_f(wt=wt,auxin_range=concentration_range, cell=i)
        cell_color=pgl.Color4(cell_color.ambient.red,cell_color.ambient.green,cell_color.ambient.blue,0)
        #wall_color=pgl.Color4(0,0,0,0)
        #pump_color=pgl.Color4(255,0,0,0)
        if revers:
            cell_corners.reverse()
            wall_relative_thickness=[wall_relative_thickness[(j-1)%len(wall_relative_thickness)] for j in range(len(wall_relative_thickness))]
            wall_relative_thickness.reverse()
        l.append( draw_cell (cell_corners, wall_relative_thickness, thickness_min, thickness_max, cell_color, wall_color, pump_color, stride=stride, nb_ctrl_pts=3, sc=None))
        l2=f_mark_regions(wt, i, l2, cell_marker_size)
    for i in l: pd.get_scene().add(pgl.Shape(i,pgl.Material( (0,0,0) )))


def visualisation_pgl_2D_linear_tissue_aux_pin3( wt, concentration_range=None, pin_range=None, max_wall_absolute_thickness=0.15,
                                                cell_marker_size=0.03, abs_intercellular_space=0., material_f=auxin2material2,
                                                revers=True,  wall_color=pgl.Color4(0,0,0,0), pump_color=pgl.Color4(255,0,0,0), prim_cells_with_pin=None):
    
    pd.set_instant_update_visualisation_policy( policy = False )
    from openalea.mersim.gui.draw_cell import draw_cell
    def ff(x,j):
        if x[0]==j: return x
        else: return (x[1],x[0])

    l=[]
    l2=[]
    for i in wt.cells():
        cell_corners=[wt.wv_pos(j) for j in wt.cell2wvs(i)]
        # wv edges to get cell edges to dig into pin 
        c=[]
        for j in wt.cell2wvs_edges(i):
            try:
                c.append( ff(wv_edge2cell_edge( wt, j), i) )
            except Exception:
                c.append(None)
        wall_relative_thickness=[]
        for j in c:
            if j: wall_relative_thickness.append(pin_level(wt,j))
            else: wall_relative_thickness.append(0.)
        #if wt.cell_property(i, "PrZ") and prim_cells_with_pin:
        #    for j in range(len(wall_relative_thickness)):
        #        wall_relative_thickness[j] = prim_cells_with_pin
        wall_relative_thickness=[cast_to_0_1_segment( base_segment=pin_range, value=j) for j in wall_relative_thickness]
        thickness_min=abs_intercellular_space#0.1*max_wall_absolute_thickness
        thickness_max=max_wall_absolute_thickness
        cell_color=material_f(wt=wt,auxin_range=concentration_range, cell=i)
        cell_color=pgl.Color4(cell_color.ambient.red,cell_color.ambient.green,cell_color.ambient.blue,0)
        #wall_color=pgl.Color4(0,0,0,0)
        #pump_color=pgl.Color4(255,0,0,0)
        if revers:
            cell_corners.reverse()
            wall_relative_thickness=[wall_relative_thickness[(j-1)%len(wall_relative_thickness)] for j in range(len(wall_relative_thickness))]
            wall_relative_thickness.reverse()
        l.append( draw_cell (cell_corners, wall_relative_thickness, thickness_min, thickness_max, cell_color, wall_color, pump_color, stride=100, nb_ctrl_pts=3, sc=None))
        l2=mark_regions2(wt, i, l2, cell_marker_size)
    for i in l: pd.get_scene().add(pgl.Shape(i,pgl.Material( (0,0,0) )))

    
    


def mark_regions3( wt, cell, list, cell_marker_size ):
    """1D linear system
    """
    l2=list
    i=cell
    if wt.cell_property( i, "CZ") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size, material=pd.white ) )
    if wt.cell_property( i, "PrZ") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size , material=pd.blue ) )
    if wt.cell_property( i, "PZ") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size , material=pd.black ) )
    return l2

def mark_regions2( wt, cell, list, cell_marker_size ):
    """Transversal
    """
    l2=list
    i=cell
    if wt.cell_property( i, "Sink") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size, material=pd.white ) )
    if wt.cell_property( i, "Source") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size , material=pd.blue ) )
    if wt.cell_property( i, "L1") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size , material=pd.black ) )
    return l2

def mark_regions2_a( wt, cell, list, cell_marker_size ):
    """Transversal
    """
    l2=list
    i=cell
    if wt.cell_property( i, "Sink") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size, material=pd.blue  ) )
    if wt.cell_property( i, "Source") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size , material=pd.white) )
    if wt.cell_property( i, "L1") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size , material=pd.black ) )
    return l2


def mark_regions4( wt, cell, list, cell_marker_size ):
    """Surface
    """
    l2=list
    i=cell
    if wt.cell_property( i, "CZ") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size, material=pd.white ) )
    if wt.cell_property( i, "PrZ") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size , material=pd.blue ) )
    if wt.cell_property( i, "PZ") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size , material=pd.black ) )
    if wt.cell_property( i, "PrC_stub") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size , material=pd.yellow ) )
    return l2

def mark_regions5( wt, cell, list, cell_marker_size ):
    """Surface for maps
    """
    l2=list
    i=cell
    if wt.cell_property( i, "CZ") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size, material=pd.white ) )
    if wt.cell_property( i, "PrZ") > 0:
        l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size , material=pd.blue ) )
    #if wt.cell_property( i, "PZ") > 0:
    #    l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size , material=pd.black ) )
    #if wt.cell_property( i, "PrC_stub") > 0:
    #    l2.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size , material=pd.yellow ) )
    return l2

def visualisation_pgl_2D_spherical_aux( wt, concentration_range=None, c_sphere_radius_factor=1, cell_marker_size=1, marker_displacement=pgl.Vector3(0,0,5) ):
    pd.set_instant_update_visualisation_policy( policy = False )
    l=[]
    for i in wt.cells():
        l.append( SphericalCell(cell=i, wt=wt, material_f=auxin2material3, material_range=concentration_range, c_sphere_radius_factor=c_sphere_radius_factor) )
        if wt.cell_property( i, "CZ") > 0:
            l.append( pd.AISphere(pos=cell_center( wt, i )+marker_displacement, radius=cell_marker_size ) )
        if wt.cell_property( i, "PrZ") > 0:
            l.append( pd.AISphere(pos=cell_center( wt, i )+marker_displacement, radius=cell_marker_size , material=pd.blue ) )
        if wt.cell_property( i, "PZ") > 0:
            l.append( pd.AISphere(pos=cell_center( wt, i )+marker_displacement, radius=cell_marker_size , material=pd.black ) )
    pd.set_instant_update_visualisation_policy( policy = True )


def visualisation_pgl_1D_linear_tissue_aux_pin( wt, concentration_range=None, pin_range=None, max_wall_absolute_thickness=0.15, cell_marker_size=0.03):
    pd.set_instant_update_visualisation_policy( policy = False )
    l=[]
    for i in wt.cells():
        #l.append( WalledPolygonalCellTODO(cell=i, wt=wt, abs_border_size=0., material=pd.red, auxin_range=concentration_range, thickness_range=pin_range,
        #    wall_thickness_f=pin_level, max_wall_absolute_thickness=max_wall_absolute_thickness, material_f=auxin2material1, material_range=concentration_range) )
        l.append( WalledPolygonalCellWithArrowWalls(cell=i, wt=wt, abs_border_size=0., material=pd.red, auxin_range=concentration_range, thickness_range=pin_range,
            wall_thickness_f=pin_level, max_wall_absolute_thickness=max_wall_absolute_thickness, material_f=auxin2material1, material_range=concentration_range) )
        if wt.cell_property( i, "CZ") > 0:
            l.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size ) )
        if wt.cell_property( i, "PrZ") > 0:
            l.append( pd.AISphere(pos=cell_center( wt, i ), radius=cell_marker_size , material=pd.blue ) )
    pd.set_instant_update_visualisation_policy( policy = True )
    #pd.instant_update_viewer( )

def visualisation_mpl_1D_linear_tissue_aux_pin( wt, **keys ):
    """Visualisation of 1D linear system showing aux and pin using the mathplot lib.
    
    <Long description of the function functionality.>
    
    :parameters:
        arg1 : `WalledTissue`
            Walled tissue to be displayed
    """
    x=[]
    y=[]
    y0=[]
    y1=[]
    y2=[]
    y1d={}
    y2d={}
    
    for i in wt.cell_edges():
        (c1, c2) = i
        if ((c1,c2)!=(0,len(wt.cells())-1)) and ((c1,c2)!=(len(wt.cells())-1,0)):
            for (k,l) in [(c1,c2), (c2,c1)]:
                if k>l:
                    y1d[ k ] = pin_level( wtt=wt, cell_edge=(k,l) )
                else:
                    y2d[ k ] = pin_level( wtt=wt, cell_edge=(k,l) )
    
    lw = len(wt.cells())
    y1d[ 0 ] = pin_level( wtt=wt, cell_edge=(0,lw-1) ) 
    y2d[ lw-1 ] = pin_level( wtt=wt, cell_edge=( lw-1,0) )
    # ploting concentration
    print y1d, y2d
    for i in range(len(wt.cells())):
        x.append(i) 
        y.append(wt.cell_property( cell=i, property="auxin_level" ) )
        y0.append( 1. )
        y1.append( y1d[ i ] )
        y2.append( y2d[ i ] )
        
    pylab.plot(x, y, "g", x, y0, "r", x, y1,"b", x, y2,"m")
    pylab.xlabel( "Cells" )
    pylab.ylabel( "Product  quantities" )
    pylab.legend(("A","P","P in right wall","P in left wall" ))
    pylab.show()
                
def visualisation_mpl_1D_linear_tissue_aux_pin( wt, **keys ):
    """Visualisation of 1D linear system showing aux and pin using the mathplot lib.
    
    <Long description of the function functionality.>
    
    :parameters:
        arg1 : `WalledTissue`
            Walled tissue to be displayed
    """
    x=[]
    y=[]
    y0=[]
    y1=[]
    y2=[]
    y1d={}
    y2d={}
    
    for i in wt.cell_edges():
        (c1, c2) = i
        if ((c1,c2)!=(0,len(wt.cells())-1)) and ((c1,c2)!=(len(wt.cells())-1,0)):
            for (k,l) in [(c1,c2), (c2,c1)]:
                if k>l:
                    y1d[ k ] = pin_level( wtt=wt, cell_edge=(k,l) )
                else:
                    y2d[ k ] = pin_level( wtt=wt, cell_edge=(k,l) )
    
    lw = len(wt.cells())
    y1d[ 0 ] = pin_level( wtt=wt, cell_edge=(0,lw-1) ) 
    y2d[ lw-1 ] = pin_level( wtt=wt, cell_edge=( lw-1,0) )
    # ploting concentration
    
    #for i in range( len( wt.cells() ) ):
    #    y0[ i ] = y1d[ i ] + y2d
    
    for i in range(len(wt.cells())):
        x.append(i) 
        y.append(wt.cell_property( cell=i, property="auxin_level" ) )
        y0.append( y1d[ i ]+y2d[ i ] )
        y1.append( y1d[ i ] )
        y2.append( y2d[ i ] )
    
    if keys.has_key("phys"): plots = 3
    else: plots = 2
    
    pylab.subplot(plots,1,1)    
    pylab.plot(x, y, "g" )
    pylab.xlabel( "Cells" )
    pylab.ylabel( "IAA quantitie" )
    if keys.has_key( "auxin_range" ):
        pylab.axis( [0, len( wt.cells() ), keys["auxin_range"][ 0 ], keys["auxin_range"][ 1 ] ] )
    pylab.subplot(plots,1,2)
    pylab.plot( x, y0, "r", x, y1,"b", x, y2,"m")
    pylab.xlabel( "Cells" )
    pylab.ylabel( "PIN  quantities" )
    #pylab.legend(("P","P in right wall","P in left wall" ))
    if keys.has_key( "pin_range" ):
        pylab.axis( [0, len( wt.cells() ), keys["pin_range"][ 0 ], keys["pin_range"][ 1 ] ] )
    if keys.has_key("phys"):
        phys=keys["phys"]
        pylab.subplot(plots,1,3)
        y=[]
        x=phys.hist.keys()
        x.sort()
        for i in x:
            y.append(phys.hist[ i ]["max_aux_diff"])
        pylab.plot( x, y)
        pylab.xlabel( "Time" )
        pylab.ylabel( "Max IAA change" )
        #pylab.show()
        
    
def visualisation_mpl_1D_linear_tissue_aux( wt, **keys ):
    """Visualisation of 1D linear system showing aux  using the mathplot lib.
    
    <Long description of the function functionality.>
    
    :parameters:
        arg1 : `WalledTissue`
            Walled tissue to be displayed
    """
    x=[]
    y=[]
    y0=[]
    y1=[]
    y2=[]
    y1d={}
    y2d={}
    
    for i in range(len(wt.cells())):
        x.append(i) 
        y.append(wt.cell_property( cell=i, property="auxin_level" ) )
        y0.append( 1. )
        
    pylab.plot(x, y, "g" )
    pylab.xlabel( "Cells" )
    pylab.ylabel( "Product  quantities" )
    pylab.legend(("A" ))
    pylab.show()
    

def f_green_material( wt=None, cell=None ):
    """Returns green material for every cell.
    
    <Long description of the function functionality.>
    
    :parameters:
        arg1 : `T`
            <Description of `arg1` meaning>
    :rtype: `T`
    :return: <Description of ``return_object`` meaning>
    :raise Exception: <Description of situation raising `Exception`>
    """
    return pgl.Material((0,255,0))    
    
def visualisation_pgl_2D_plain( wt, max_wall_absolute_thickness=0.15,
                                    abs_intercellular_space=0., material_f=f_green_material,
                                    revers=True,  wall_color=pgl.Color4(0,0,0,0),
                                    pump_color=pgl.Color4(255,0,0,0),
                                    stride=100,
                                    **keys):
    
    from openalea.mersim.gui.draw_cell import draw_cell
    l=[]
    for i in wt.cells():
        cell_corners=[wt.wv_pos(j) for j in wt.cell2wvs(i)]
        wall_relative_thickness= [0 for i in wt.cell2wvs_edges(i)]
        cell_color=material_f(wt=wt, cell=i)
        cell_color=pgl.Color4(cell_color.ambient.red,cell_color.ambient.green,cell_color.ambient.blue,0)
        if revers:
            cell_corners.reverse()
        l.append( draw_cell (cell_corners, wall_relative_thickness, abs_intercellular_space, abs_intercellular_space, cell_color, wall_color, pump_color, stride=stride, nb_ctrl_pts=3, sc=None))
    for i in l: pd.get_scene().add(pgl.Shape(i,pgl.Material( (0,0,0) )))
    return 0



    