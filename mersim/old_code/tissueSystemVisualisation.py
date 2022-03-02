#!/usr/bin/env python

"""tissueSystemVisualisation.py

Visualisation interface for TissueSystem.

:version: 2006-08-04 13:25:12CEST
:author: szymon stoma
"""


class SystemVisualisation:
    """This is main interface for visualisation of System class.
    """

    def __init__( self, system=None ):
        """Init reads default config and sets main display properties.
        """
        self.system = system
        self.grab_scene = self.system.const.system_grab_scene
        #self.show_simple_pressure_center = self.system.const.show_simple_pressure_center
        self.name = self.system.const.name
        self.width = self.system.const.system_width 
        self.height = self.system.const.system_height 
        self.fov = self.system.const.system_fov #visual.pi/3.
        self.background = self.system.const.system_background 
        self.ambient = self.system.const.system_ambient 

        self._pov_title = 0

    def remove_vspring(self, spring=None, leave_visible=False):
        """Removes spring from the system.
        """
        #print "remove_vspring:not defined.."
        pass

    def remove_vmass(self, mass=None, leave_visible=False):
        """Removes mass from the system.
        """
        #print "remove_vmass:not defined.."
        pass

    def add_vspring(self, spring=None):
        """Adds spring from the system.
        """
        #print "add_vspring:not defined.."
        pass



    def add_vmass(self, mass=None,leave_visible=False):
        """Adds mass from the system.
        """
        #print "add_vmass:not defined.."
        pass

    def set_vspring_color( self, spring=None, color=None ):
        """Sets a color for a spring.
        """
        #print "set_vspring_color:not defined.."
        pass

    def set_vmass_color( self, mass=None, color=None ):
        """Sets a color for a mass.
        """
        #print "set_vmass_color:not defined.."
        pass


    def set_vmass_fixed( self, mass=None, fixed=False ):
        """Signal that mass is fixed 
        """
        #print "set_mass_fixed:not defined.."
        pass
    
    def adjust_display( self ):
        pass
    
    #def interpolate_color( color1=None, color2=None, range=None, value=None):
    #    """Returns the interpolated RGB value between color1 and color2.
    #    assumptions:
    #    * color?= (r,g, b)
    #    * range = (x1, x2)
    #    * x1 < x2
    #    * value is in range
    #    """
    #    try:
    #        r,b,g = color1
    #        r2,b2,g2 = color2
    #        s0, s1 = range
    #        p = value / (s1-s0) 
    #        dr = float( r2 - r )
    #        dg = float( g2 - g )
    #        db = float( b2 - b )
    #        c = (r+p*dr, b+p*db , g+p*dg)
    #    except ZeroDivisionError:
    #        return color1
    #    return c 
    #interpolate_color = staticmethod( interpolate_color )
    
    def grab_scene_to_pov( self ):
        pass
 
    def clean( self ):
        pass

    def gui_events( self ):
        self.process_input_events()

class TissueSystemVisualisation( SystemVisualisation ):
    """This is main interface for visualisation of TissueSystem.
    """

    def __init__( self, tissue_system=None ):
        SystemVisualisation.__init__( self, system=tissue_system )
        self.tissue_system = self.system
        self._cell2vcell = {}
        """#: to store cell 2 vcell information"""
        self._cell2vmt = {}
        """#: to store cell 2 vmt information"""
        self._cell2vpumps = {}
        """#: to store cell 2 vpumps information"""

    def clean( self ):
        SystemVisualisation.clean( self )
        for i in self._cell2vcell:
            self._cell2vcell[ i ].clean_up()
        self._cell2vcell.clear()
        for i in self._cell2vmt:
            self._cell2vmt[ i ].clean_up()
        self._cell2vmt.clear()
        for i in self._cell2vpumps:
            self._cell2vpumps[ i ].clean_up()
        self._cell2vpumps.clear()

    def add_vcell( self, cell = None ):
        #print "add_vcell:not defined.."
        pass

    def remove_vcell( self, cell = None, leave_visible=False ):
        #print "remove_vcell:not defined.."
        pass


    def add_vmt( self, cell = None ):
        #print "add_vmt:not defined.."
        pass

    def remove_vmt( self, cell = None,leave_visible=False ):
        #print "remove_vmt:not defined.."
        pass


    def init_after_meristem_creation( self ):
        print "init_after_meristem_creation:not defined.."
        pass
        


