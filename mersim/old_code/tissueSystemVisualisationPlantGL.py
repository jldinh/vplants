#!/usr/bin/env python
"""filename.py

Desc.

:version: 2006-05-15 15:21:06CEST
:author:  szymon stoma
"""
import PlantGL as pgl

class SystemVisualisationVisual( SystemVisualisation, VisualInterface1):
    def __init__( self, system = None):
        SystemVisualisation.__init__( self, system=system )
        VisualInterface1.__init__( self, system=system ) 
        self.display = pgl.Viewer

    
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