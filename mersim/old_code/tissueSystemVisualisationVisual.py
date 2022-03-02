#!/usr/bin/env python

"""tissueSystemVisualisationVisual.py

Visualisation using Python Visual system.

:version: 2006-07-28 12:01:15CEST
:author: szymon stoma
"""

import visual
from tissueSystemVisualisation import *
from tissueSystemVisualisationInterface import *
from const import *
import math
import tools


class VMt( visual.arrow ):
    def __init__( self, cell = None, visualisation=None ):
        tissue_system = visualisation.tissue_system
        self.cell = cell
        shape = tissue_system.tissue.cell2wvs( cell = cell )
        s1 = shape[0]
        t1 = shape[1]
        s1pos = tissue_system.tissue.wv_pos( wv=s1 )
        t1pos = tissue_system.tissue.wv_pos( wv=t1 )
        middle_of_wall = t1pos + ( s1pos - t1pos )/2.
        center_of_cell = tissue_system.tissue.cell_center( cell = cell )
        axis = (middle_of_wall - center_of_cell).rotate( angle = tissue_system.tissue.cell_property( cell=cell, property="mtb_orientation_angle"), axis=visual.cross(s1pos-center_of_cell, t1pos-center_of_cell) ) 
        visual.arrow.__init__( self, pos = center_of_cell, axis=axis )                                                                                                                       

    def update( self, visualisation=None ):
        tissue_system = visualisation.tissue_system
        shape = tissue_system.tissue.cell2wvs( cell = self.cell )
        s1 = shape[0]
        t1 = shape[1]
        s1pos = tissue_system.tissue.wv_pos( wv=s1 )
        t1pos = tissue_system.tissue.wv_pos( wv=t1 )
        middle_of_wall = t1pos + ( s1pos - t1pos )/2.
        center_of_cell = tissue_system.tissue.cell_center( cell = self.cell )
        axis = (middle_of_wall - center_of_cell).rotate( angle = tissue_system.tissue.cell_property( cell=self.cell, property="mtb_orientation_angle"), axis=visual.cross(s1pos-center_of_cell, t1pos-center_of_cell) ) 
        arrow=visualisation._cell2vmt[ self.cell ]
        arrow.pos = center_of_cell
        arrow.axis = axis
    
    def clean_up( self, leave_visible=False ):
        if not leave_visible:
            self.visible = False


class VMassVisual(visual.sphere):
    def __init__( self, mass=None, radius=1., color=Color.normal_point, pickable=True, system=None, **keywords ):
        self.mass = mass # necessary to access the mass in the DnD loop
        visual.sphere.__init__(self, pos=mass.pos, radius=radius, color=color, pickable=pickable, **keywords)
        #self.pos = pos
        if system.const.system_display_show_force_vectors:  system.visualisation.visual_force_vectors[ self ] = visual.arrow( pos = mass.pos, axis = mass.F, visible = True )
    
    def set_fixed( self, fixed ):
        if fixed:
            self.color = Color.fixed_point
        else:
            self.color = Color.normal_point

    def update_visual_forces(self, visualisation=None, visual_force_magnifier = 1.):
        a = visualisation.visual_force_vectors[ self ]
        a.axis = self.mass.F * visual_force_magnifier
        a.pos = self.pos

    def update( self, visualisation=None, visual_force_magnifier=None ):
        self.pos = self.mass.pos
        #if system.const.system_display_show_force_vectors:  self.update_visual_forces( visualisation=visualisation, visual_force_magnifier=visual_force_magnifier)

    def clean_up( self, leave_visible=False ):
        if not leave_visible:
            self.visible = False

        
class VSpringVisual( visual.cylinder ):
    """Visual representation of a spring.
    """

    def __init__( self, spring = None, radius=None, color=Color.spring, **keywords ):
        """Construct a cylinder spring.
        """
 
        #OV self.cylinder = visual.cylinder(pos=self.m0.sphere.pos, axis=self.m1.sphere.pos - self.m0.sphere.pos, 
        #    radius=radius1, color=color, **keywords)
        self.spring = spring
        visual.cylinder.__init__(self, pos=self.spring.m0.pos, axis=self.spring.m1.pos - self.spring.m0.pos, 
            radius=radius, color=color)

    def update(self):
        """Update the visual representation of the spring.
        """
        self.pos = self.spring.m0.pos
        self.axis = self.spring.m1.pos - self.spring.m0.pos
        #stress = (visual.mag( self.axis ) - self.spring.l0)/self.spring.l0
        #print "stress:" ,stress
        #if stress < 0.2:
        #    # small smaller tension
        #    if stress  < 0:
        #        print "! stress:" ,stress
        #        stress = 0
        #    self.color =tools.interpolate_color( color1=Color.spring_under_compression, color2=Color.spring, range=(0., 0.2), value=stress )
        #else:
        #    # biger tension
        #    if stress > 0.4:
        #        print "! stress:" ,stress
        #        stress = 0.4
        #    self.color = tools.interpolate_color( color1=Color.spring, color2=Color.spring_under_tension, range=(0.2, 0.4), value=stress )
            
    def clean_up( self, leave_visible=False ):
        if not leave_visible:
            self.visible = False

         

class VCellTriangleVisual( visual.faces ):
    """Used to fill the cell"""
    pass


class VCellVisual:
    """Used to display a cell from the simulation.

    Asumtions:
    * ..
    """
    def __init__( self, visualisation = None, cell = None, **keywords ):
        self.cell = cell
        self.set_color(visualisation=visualisation)

    def set_color( self, visualisation=None, color=None ):
        """Sets color for the cell representation. If None is given it takes the value calculated on cell properties.
        """
        if not color:
            ts = visualisation.tissue_system
            
            #base on identity            
            ##self.color = Color.normalZoneCell
            ##if ts.tissue.cell_property( self.cell, "CZ"):
            ##    self.color = Color.centralZoneCell
            ##if ts.tissue.cell_property( self.cell, "IC") :
            ##    self.color = Color.initialCell
            ##if ts.tissue.cell_property( self.cell, "PZ"):
            ##    self.color = Color.peripheralZoneCell
            ###if ts.tissue.cell_property( self.cell, "PrZ")>0:
            ##    #self.color = Color.primordiumZone
            ##if ts.tissue.cell_property( self.cell, "PrC")>0:
            ##    self.color = Color.primordiumZoneCell
            #    
            
            #color update
            self.color = tools.interpolate_color( color1=Color.normalZoneCell, color2=Color.full_auxin_cell, range=(0.3, 0.5), value=ts.tissue.cell_property( self.cell, "auxin_level" ) )
            #if ts.tissue.cell_property( self.cell, "PrC")>0:
            #    self.color = Color.primordiumZoneCell
            #if ts.tissue.cell_property( self.cell, "IC") :
            #    self.color = Color.initialCell
        else:
            self.color = color


    def update( self, visualisation=None ):
        """Updates the view
        """
        pass

    def clean_up( self, leave_visible=False ):
        pass

class VSphereCellVisual( VCellVisual, visual.sphere ):
    def __init__( self, visualisation = None, cell = None, **keywords ):
        ts = visualisation.tissue_system
        center = ts.tissue.cell_center( cell )
        visual.sphere.__init__( self, pos = center, radius=visualisation.system.const.sphere_visualisation_sphere_size_mult *(math.sqrt(ts.tissue.calculate_cell_surface( cell =cell)/938)))
        VCellVisual.__init__( self, visualisation=visualisation, cell=cell)
        
    def update( self, visualisation=None ):
        """Updates the view
        """
        ts = visualisation.tissue_system
        self.set_color(visualisation=visualisation)
        self.pos = ts.tissue.cell_center( self.cell )
        self.radius= visualisation.system.const.sphere_visualisation_sphere_size_mult *math.sqrt(ts.tissue.calculate_cell_surface( cell =self.cell)/938)

    def clean_up( self, leave_visible=False ):
        if not leave_visible:
            self.visible = False


class VIdentitySphereCellVisual( VCellVisual, visual.sphere ):
    def __init__( self, visualisation = None, cell = None, **keywords ):
        ts = visualisation.tissue_system
        center = ts.tissue.cell_center( cell ) 
        visual.sphere.__init__( self, pos = center, radius=visualisation.system.const.sphere_visualisation_sphere_cell_identity_size_mult *(math.sqrt(ts.tissue.calculate_cell_surface( cell =cell)/938)))
        VCellVisual.__init__( self, visualisation=visualisation, cell=cell)
        
    def update( self, visualisation=None ):
        """Updates the view
        """
        ts = visualisation.tissue_system
        self.set_color(visualisation=visualisation)
        self.pos = ts.tissue.cell_center( self.cell )
        self.radius= visualisation.system.const.sphere_visualisation_sphere_cell_identity_size_mult *math.sqrt(ts.tissue.calculate_cell_surface( cell =self.cell)/938)

    def clean_up( self, leave_visible=False ):
        if not leave_visible:
            self.visible = False

    def set_color( self, visualisation=None, color=None ):
        """Sets color for the cell representation. If None is given it takes the value calculated on cell properties.
        """
        if not color:
            ts = visualisation.tissue_system
            
            #base on identity            
            #self.color = tools.interpolate_color( color1=Color.normalZoneCell, color2=Color.full_auxin_cell, range=(0.1, 0.6), value=ts.tissue.cell_property( self.cell, "auxin_level" ) )#Color.normalZoneCell
            self.color = tools.interpolate_color( color1=Color.normalZoneCell, color2=Color.full_auxin_cell, range=(0.3, 0.5), value=ts.tissue.cell_property( self.cell, "auxin_level" ) )
            #print ts.tissue.cell_property( self.cell, "auxin_level" ) 
            try:
                #if ts.tissue.cell_property( self.cell, "CZ"):
                #    self.color = Color.centralZoneCell
                if ts.tissue.cell_property( self.cell, "PZ"):
                    self.color = (0,0,0)#cColor.peripheralZoneCell
                #if ts.tissue.cell_property( self.cell, "PrZ")>0:
                    #self.color = Color.primordiumZone
                if ts.tissue.cell_property( self.cell, "PrC")>0:
                    self.color = (0.8,0.,0.8)#Color.primordiumZoneCell
                #if ts.tissue.cell_property( self.cell, "IC") :
                #    self.color = Color.initialCell
            except Exception:
                print "exception on coloring cell", self.cell
                pass
        else:
            self.color = color


class VPumpVisual( VCellVisual, visual.arrow ):
    def __init__( self, visualisation = None, cell= None, **keywords ):
        ts = visualisation.tissue_system
        c=cell
        center = ts.tissue.cell_center( cell )
        nl = ts.tissue.cell_neighbors( cell=cell)
        N = nl[0]
        for n in nl:
            if ts.tissue.cell_edge_property( cell_edge  = ts.tissue.cell_edge_id( (c,n) ), property="pump_active"):
                if ts.tissue.cell_edge_property( cell_edge  = ts.tissue.cell_edge_id( (c,n) ), property="pump_direction") == (c,n):
                    N = n
        ncenter = ts.tissue.cell_center( N )
        visual.arrow.__init__( self, pos = center, axis=ncenter-center)
        VCellVisual.__init__( self, visualisation=visualisation, cell=cell)

    def set_color( self, visualisation=None, color=None ):
        """Sets color for the cell representation. If None is given it takes the value calculated on cell properties.
        """
        if not color:
            ts = visualisation.tissue_system
            self.color = Color.normalZoneCell
        else:
            self.color = color

        
    def update( self, visualisation=None ):
        """Updates the view
        """
        ts = visualisation.tissue_system
        c=self.cell
        self.set_color(visualisation=visualisation)
        self.pos = ts.tissue.cell_center( self.cell )
        nl = ts.tissue.cell_neighbors( cell=self.cell)
        N = nl[0]
        found=False
        for n in nl:
            if ts.tissue.cell_edge_property( cell_edge  = ts.tissue.cell_edge_id( (c,n) ), property="pump_active"):
                if ts.tissue.cell_edge_property( cell_edge  = ts.tissue.cell_edge_id( (c,n) ), property="pump_direction") == (c,n):
                    N = n
                    found=True
                    break
        if not found:
            self.visible=False
        ncenter = ts.tissue.cell_center( N )
        self.axis=ncenter-self.pos

    def clean_up( self, leave_visible=False ):
        if not leave_visible:
            self.visible = False


class VPumpSystem:
    def __init__( self, visualisation = None, cell= None, **keywords ):
        ts = visualisation.tissue_system
        c=cell
        center = ts.tissue.cell_center( cell )
        nl = ts.tissue.cell_neighbors( cell=cell)
        self.pumps=[]
        for i in nl:
            v = ts.tissue.pin( (c,i) )
            v2 = ts.tissue.pin( (i,c) )
            if v  > 1.01:
                ncenter = ts.tissue.cell_center( i )
                self.pumps.append( visual.arrow( pos = center, axis=ncenter-center, color=tools.interpolate_color((0.4,0.517,0.04),(1,0,0),(1,1.2),v)))
                

    def set_color( self, visualisation=None, color=None ):
        """Sets color for the cell representation. If None is given it takes the value calculated on cell properties.
        """
        if not color:
            ts = visualisation.tissue_system
            self.color = Color.normalZoneCell
        else:
            self.color = color

        
    def update( self, visualisation=None ):
        """Updates the view
        """
        pass
    
    def clean_up( self, leave_visible=False ):
        if not leave_visible:
            for i in self.pumps:
                i.visible = False
            self.pumps = []





class VSurfaceCellVisual(VCellVisual):
    """Used to display a cell from the simulation.

    Asumtions:
    * ..
    """
    def __init__( self, visualisation = None, cell = None, **keywords ):
        VCellVisual.__init__( self, visualisation=visualisation, cell=cell)
        # if number is constant the shape was not changed so the 
        # update may be done just by updating triangle positions
        ts = visualisation.tissue_system
        e  = ts.tissue.cell2wvs_edges_in_real_order( self.cell )
        self.nbr_wv_edges = len( e )
        center = ts.tissue.cell_center( cell )
        self.tr = []
        #self.rev_tr = []
        for i in e:
            self.tr.append( visual.faces( pos=[center, ts.tissue.wv_pos( i[0] ), ts.tissue.wv_pos( i[1] )], color=self.color ) )
            #self.rev_tr.append( visual.faces( pos=[center, ts.tissue.wv_pos( i[1] ), ts.tissue.wv_pos( i[0] ) ] , color=self.color ) )
            #print [center, ts.tissue.wv_pos( i[0] ), ts.tissue.wv_pos( i[1] )]


    def update( self, visualisation=None ):
        """Updates the view
        """
        # if number is constant the shape was not changed so the 
        # update may be done just by updating triangle positions
        ts = visualisation.tissue_system

        self.set_color(visualisation=visualisation)
        
        e  = ts.tissue.cell2wvs_edges_in_real_order( self.cell )
        center = ts.tissue.cell_center( self.cell )
        if self.nbr_wv_edges != len( e ):
            for i in range( len(e)-self.nbr_wv_edges ):
                self.tr.append( visual.faces( pos=[visual.vector(), visual.vector(), visual.vector() ] , color=self.color) )
            self.nbr_wv_edges = len( self.tr )
        for i in range( len( e ) ):
            self.tr[ i ].pos[ 0 ] = center
            self.tr[ i ].pos[ 1 ] = ts.tissue.wv_pos( e[ i ][ 0 ] )
            self.tr[ i ].pos[ 2 ] = ts.tissue.wv_pos( e[ i ][ 1 ] )
            self.tr[ i ].color = self.color

    def clean_up( self, leave_visible=False ):
        for i in self.tr:
            if not leave_visible:
                i.visible = False



# --------------------------------------------------------------------------------------------------- VisualisationSystems

class SystemVisualisationVisual( SystemVisualisation, VisualInterface1):
    def __init__( self, system = None):
        SystemVisualisation.__init__( self, system=system )
        VisualInterface1.__init__( self, system=system ) 
        self.display = visual.display(title=self.name, width=self.width, height=self.height, fov=self.fov, background=self.background, ambient=self.ambient )
        self.display.select()
        self.drag_object = None
        self.click = None
        self.distance = None
        self.remember_fixed = None
        self.remember_color = None
        self.display.up=visual.vector(0,0.0000001,1)
        if self.system.const.mtb_global_direction_active:
            visual.arrow( axis = 40*self.direction, pos = visual.vector(10, 10, 0 ) ) 

        if self.system.forces.has_key("simple_pressure"):
            if self.show_simple_pressure_center: visual.sphere( pos=self.simple_pressure_center )

    
    def update( self ):
        if self.system.const.system_display_show_force_vectors:
            for m in self._mass2vmass.values():
                m.update_visual_forces( visualisation = self, visual_force_magnifier = self.system.const.visual_force_magnifier )
        self._update_spring_colors()

    def plane(self, t):
        """Draws a plane to help in observation of frame visualisation.
        """
        b = 100000
        s = -b
        visual.box( pos = (t, t, 0), color=(0,0,0), length = 0.0001, height=b, width=b)

    def grab_scene_to_pov( self, grab_flag = True ):
        SystemVisualisation.grab_scene_to_pov( self ) 
        import povexport
        self.display.title = str( self.system.frame_nbr )
        povexport.export(prefix_folder=self.system.const.folder_for_saving_data)


    def adjust_display( self ):
        self.display.autocenter = 1
        self.display.autoscale = 1        
        self.display.autocenter = 0
        self.display.autoscale = 0
        
    def clean( self ):
        pass
    
    def rotate( self, up=None, forward=None, rotation=visual.vector(0,0,1), grab_scene=False, steps=50, angle=2*3.1415 ):
        if up:
            self.display.up = up
        if forward:
            self.display.forward=forward
        for i in range( steps ):
            self.display.forward =  self.display.forward.rotate( angle=angle/steps, axis=rotation)
            #raw_input()
            if grab_scene:
                self.grab_scene_to_pov()
                self.system.frame_nbr += 1



class FrameSystemVisualisationVisual( SystemVisualisationVisual ):
    def __init__( self, system=None):
        SystemVisualisationVisual.__init__( self, system=system )
        self._mass2vmass = {} #: to keep link between mass and its visual repr.
        self._spring2vspring = {} #: to keep link between spring and its visual repr.        
        ##self.visual_force_vectors = {}

    def clean( self ):
        SystemVisualisationVisual.clean( self )
        for i in self._mass2vmass:
            self._mass2vmass[ i ].clean_up()
        self._mass2vmass.clear()
        for i in self._spring2vspring:
            self._spring2vspring[ i ].clean_up()
        self._spring2vspring.clear()



class TissueSystemVisualisationVisual( SystemVisualisationVisual, TissueSystemVisualisation ):
    def __init__( self, tissue_system=None ):
        SystemVisualisationVisual.__init__( self, system = tissue_system )
        TissueSystemVisualisation.__init__( self, tissue_system = tissue_system )

    def init_after_meristem_creation( self ):
        cells = self.tissue_system.tissue.cells()
        for c in cells:
            self.add_vcell( c )
        if self.system.const.mtb_direction_active:
            for c in cells:
                self.add_vmt( cell=c )
                
    def clean( self ):
        SystemVisualisationVisual.clean( self )
        TissueSystemVisualisation.clean( self )

# _______________________________________________________________________________________________________FRAME

class FrameTissueSystemVisualisationVisual(  TissueSystemVisualisationVisual, FrameSystemVisualisationVisual ):
    def __init__( self, tissue_system=None ):
        TissueSystemVisualisationVisual.__init__( self, tissue_system = tissue_system )
        FrameSystemVisualisationVisual.__init__( self, system = tissue_system )
        #self.interface = VisualInterface1.__init__( self, system = tissue_system )

        self._young_springs = []
        #: to visualise them with different color

    def clean( self ):
        TissueSystemVisualisationVisual.clean( self )
        FrameSystemVisualisationVisual.clean( self )
        self._young_springs=[]

    def gui_events( self ):
        self.process_input_events()

    def _update_spring_colors( self ):
        t = []
        #TODO change to const
        ttime = 2.0
        for s in self._young_springs:
            ed = self.system.spring2id( s.spring )
            ct = self.system.tissue.wv_edge_property( wv_edge=ed, property="creation_time")
            if self.system.time - ct > ttime or self.system.tissue.wv_edge_property( wv_edge=ed, property="old_wall_successor"):
                s.color = Color.spring
            else:
                t.append( s )
                s.color = tools.interpolate_color( color1=Color.added_spring, color2=Color.spring,  range=(0., ttime), value=max(0, self.system.time - ct ))
            self._young_springs = t
  
    def init_after_meristem_creation( self ):
        TissueSystemVisualisationVisual.init_after_meristem_creation( self )

    def remove_vspring(self, spring=None, leave_visible=False):
        """Removes spring from the system.
        """
        vspring = self._spring2vspring[ spring ]
        if vspring in self._young_springs:
            self._young_springs.remove( vspring )
        if not leave_visible:
            vspring.visible = False
        del self._spring2vspring[ spring ]

    def remove_vmass(self, mass=None, leave_visible=False):
        """Removes mass from the system.
        """
        return
        vmass = self._mass2vmass[ mass ]
        if self.tissue_system.const.system_display_show_force_vectors:
            arrow = self.visual_force_vectors.pop( vmass ) 
            arrow.visible = False
            del arrow
        if not leave_visible:
            vmass.visible = False
        del self._mass2vmass[ mass ]

    def add_vmass( self, mass=None ):
        """Insert mass into visualisation
        """
        return
        vmass = VMassVisual(mass=mass, radius=mass.radius, color=mass.color, pickable=mass.pickable, system=self.system) 
        self._mass2vmass[ mass ] = vmass

    def add_vspring( self, spring=None ):
        """Insert spring into visualisation
        """
        vspring = VSpringVisual(spring=spring, axis=spring.m1.pos - spring.m0.pos, 
            radius= self.tissue_system.const.mass_standart_radius /2., color=Color.spring)
        self._spring2vspring[ spring ] = vspring
        self._young_springs.append( vspring )


    def set_vspring_color( self, spring=None, color=None):
        """Sets spring color.
        """
        self._spring2vspring[ spring ].color = color

    def set_vmass_color( self, mass=None, color=None):
        """Sets mass color.
        """
        self._mass2vmass[ mass ].color = color

    def update( self ):
        SystemVisualisationVisual.update( self )
        for i in self._spring2vspring.values():
            i.update()
        for i in self._mass2vmass.values():
            i.update()
        for i in self._cell2vmt.values():
            i.update( visualisation = self )
        for i in self._cell2vpumps.values():
            i.update( visualisation=self)
            
    def set_vmass_fixed( self, mass = None, fixed=True ):
        return
        if fixed:
            self._mass2vmass[ mass ].color = Color.fixed_point
        else:
            self._mass2vmass[ mass ].color = Color.normal_point
    
    def add_vcell( self, cell = None ):
        #self._cell2vpumps[ cell ] = VPumpVisual( visualisation=self, cell=cell)
        pass
    
    def remove_vcell( self, cell = None, leave_visible=False ):
        #self._cell2vpumps[ cell ].clean_up(leave_visible=leave_visible)
        #del self._cell2vpumps[ cell ] 
        pass
    
    def add_vmt( self, cell = None ):
        if self.tissue_system.const.mtb_direction_active:
            self._cell2vmt[ cell ] = VMt( cell = cell, visualisation=self )

    def remove_vmt( self, cell = None ):
        if self.tissue_system.const.mtb_direction_active:
            vmt = self._cell2vmt[ cell ] 
            vmt.visible=False
            del self._cell2vmt[ cell ]



# _______________________________________________________________________________________________________SURF

class SurfaceTissueSystemVisualisationVisual( FrameTissueSystemVisualisationVisual):

    def __init__( self, tissue_system=None ):
        FrameTissueSystemVisualisationVisual.__init__( self, tissue_system = tissue_system )
        self._cell2vcellId = {}
        self._pump_systems=[]
        
    def init_after_meristem_creation( self ):
        FrameTissueSystemVisualisationVisual.init_after_meristem_creation( self )
        #pumps
        for i in self.tissue_system.tissue.cells():
            self._pump_systems.append(VPumpSystem(visualisation=self, cell=i))
            
    def update( self ):
        FrameTissueSystemVisualisationVisual.update( self )
        for i in self._cell2vcell.values():
            i.update( visualisation=self )
        for i in self._cell2vcellId.values():
            i.update( visualisation=self )
        
        #ugly pump update    
        for i in self._pump_systems:
            i.clean_up( leave_visible=False )
        self._pump_systems=[]          
        for i in self.tissue_system.tissue.cells():
            self._pump_systems.append(VPumpSystem(visualisation=self, cell=i))

    
    def add_vcell( self, cell = None ):
        self._cell2vcell[ cell ] = VSurfaceCellVisual( visualisation = self, cell = cell )
        self._cell2vcellId[ cell ] = VIdentitySphereCellVisual( visualisation=self, cell = cell )
        #self._cell2vpumps[ cell ] = VPumpVisual( visualisation=self, cell=cell)

    def remove_vcell( self, cell = None, leave_visible=False ):
        self._cell2vcell[ cell ].clean_up(leave_visible=leave_visible)
        del self._cell2vcell[ cell ]
        self._cell2vcellId[ cell ].clean_up(leave_visible=leave_visible)
        del self._cell2vcellId[ cell ] 
        #self._cell2vpumps[ cell ].clean_up(leave_visible=leave_visible)
        #del self._cell2vpumps[ cell ] 

    def clean( self ):
        FrameTissueSystemVisualisationVisual.clean( self )
        for i in self._cell2vcellId:
            self._cell2vcellId[ i ].clean_up(leave_visible=False)
        self._cell2vcellId = {}
        
        #pumps
        for i in self._pump_systems:
            i.clean_up(leave_visible=False)
        self._pump_systems=[]
        
# _______________________________________________________________________________________________________SPHERE

class SphereTissueSystemVisualisationVisual( TissueSystemVisualisationVisual):
    def __init__( self, tissue_system=None ):
        TissueSystemVisualisationVisual.__init__( self, tissue_system = tissue_system )

    def add_vcell( self, cell=None ):
        self._cell2vcell[ cell ] = VSphereCellVisual( visualisation=self, cell = cell )
        #self._cell2vpumps[ cell ] = VPumpVisual( visualisation=self, cell=cell)
    
    def remove_vcell( self, cell = None, leave_visible=False):
        self._cell2vcell[ cell ].clean_up(leave_visible=leave_visible)
        del self._cell2vcell[ cell ] 
        #self._cell2vpumps[ cell ].clean_up(leave_visible=leave_visible)
        #del self._cell2vpumps[ cell ] 

    def update( self ):
        for i in self._cell2vcell.values():
            i.update( visualisation=self )
        #for i in self._cell2vpumps.values():
            #i.update( visualisation=self)
            
    #def process_input_events(self):
    #    """Process the drag and drop interaction from the mouse.
    #    TODO drop it
    #    """
    #    if self.display.mouse.clicked : 
    #        click = self.display.mouse.getclick()
    #        if click.pick.__class__ == VSphereCellVisual:
    #            o = click.pick
    #            self.system.tissue.investigate_cell( o.cell )

