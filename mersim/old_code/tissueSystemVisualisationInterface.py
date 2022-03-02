#!/usr/bin/env python

"""tissueSystemVisualInterface.py

Class containing the interfaces for visual. 

:version: 2006-08-10 18:13:47CEST
:author: szymon stoma
"""

from visual.controls import *
import tissueSystemVisualisation
import tissueSystemVisualisationVisual

class VisualInterface1:
    def __init__(self, system=None):
        """TODO drop it and move to interface..
        """
        self.controls = controls( title="TissueControls", width=300, height=700) # Create controls window
        # Create a button in the controls window:
        posy = [ 90, 70, 50, 30, 10, -10, -30, -50, -70, -90]
        posx = [  0,  0,  0,  0, 0,   0,   0,   0,    0,    0,    0]
        size_x = 60
        size_y = 25
        self.system = system
        self.fix_btn_status = False
        self.inc_aux_btn_status = False
        self.dec_aux_btn_status = False
        self.start_btn = button( pos=(posx[0], posy[0]), width=size_x, height=size_y, 
            text='Run simulation', action=lambda: self._start_btn_act())
        self.fix_btn = button( pos=(posx[1], posy[1]), width=size_x, height=size_y, 
            text='Fix point', action=lambda: self._fix_btn_act())
        self.inc_aux_btn = button( pos=(posx[2], posy[2]), width=size_x, height=size_y, 
            text=' Inc. auxine in point', action=lambda: self._inc_aux_btn_act())
        self.dec_aux_btn = button( pos=(posx[3], posy[3]), width=size_x, height=size_y, 
            text='Dec. auxine in point', action=lambda: self._dec_aux_btn_act())
        self.divide_btn = button( pos=(posx[4], posy[4]), width=size_x, height=size_y, 
            text='Divide', action=lambda: self._divide_btn_act())
        
        if self.system.const.system_forces_visco:
            self.visco_sld = slider( pos=(posx[5]-size_x/2, posy[5] ), min = 0, max = 0.99, 
                axis = (size_x,0,0), action=lambda: self._visco_sld_act() )
            self.visco_sld.setvalue( self.system.const.max_system_viscosity )
        
        #self.force_sld = slider( pos=(posx[6]-size_x/2, posy[6] ), min = 0.0000, max = self.const.const.max_up_force, #0.01, 
        #    axis = (size_x,0,0), action=lambda: self._force_sld_act() )
        #self.force_sld.setvalue( 0 )
        
        self.turn_on_tgl = toggle( pos=(posx[7], posy[7] ),width=size_x, height=size_y/2, text0=' Console ON ', text1=' Console OFF ',
            action=lambda: self._turn_on_tgl_act())    
        # TODO add reset
    
    def _start_btn_act( self ):
        if self.run:
            self.run = False
            self.start_btn.text = "Run simulation"
        else:
            self.run = True
            self.start_btn.text = "Stop simulation"

    def _fix_btn_act( self ):
        mem = self.fix_btn_status
        self._reset_buttons()
        if not mem:
            self.fix_btn_status = True
            self.fix_btn.text = "!! NOW select the point !!"

    def _inc_aux_btn_act( self ):
        mem = self.inc_aux_btn_status 
        self._reset_buttons()
        if not mem: 
            self.inc_aux_btn_status = True
            self.inc_aux_btn.text = "!! NOW select the point !!"

    def _dec_aux_btn_act( self ):
        mem = self.dec_aux_btn_status 
        self._reset_buttons()
        if not mem: 
            self.dec_aux_btn_status = True
            self.dec_aux_btn.text = "!! NOW select the point !!"

    def _turn_on_tgl_act( self ):
        if self.turn_on:
            self.turn_on = False
        else:
            self.turn_on = True

    def _visco_sld_act( self ):
        self.system.forces["visco_force"].visco = self.visco_sld.value
        #self.display.background = (Color.background[0]*self.visco_sld.value,  Color.background[1]*self.visco_sld.value, Color.background[2]*self.visco_sld.value)

    def _force_sld_act( self ):
        self.delta_uniform_up = self.force_sld.value
        #print self.force_sld.value
        #self.display.background = (Color.background[0]*self.visco_sld.value,  Color.background[1]*self.visco_sld.value, Color.background[2]*self.visco_sld.value)

    def _reset_buttons( self ):
          self.dec_aux_btn_status = False
          self.dec_aux_btn.text = "Dec. auxine in point" 
          self.inc_aux_btn_status = False
          self.inc_aux_btn.text = "Inc. auxine in point" 
          self.fix_btn_status = False
          self.fix_btn.text = "Fix point" 

    def process_input_events(self):
        """Process the drag and drop interaction from the mouse.
        TODO drop it
        """
        if self.display.kb.keys:
            key = self.display.kb.getkey()
            if key == "i":
                if self.display.mouse.clicked : 
                    click = self.display.mouse.getclick()
                    if click.pick.__class__ == tissueSystemVisualisationVisual.VSphereCellVisual:
                        o = click.pick
                        self.system.tissue.investigate_cell( o.cell )                
            if key == "q":
                #print key
                self.system.turn_on = False
            if key == "p":
                if self.display.mouse.clicked : 
                    click = self.display.mouse.getclick()
                    if click.pick.__class__ == tissueSystemVisualisationVisual.VSphereCellVisual:
                        o = click.pick
                    self.system.tissue.investigate_cell( o.cell )
                    t = self.system.tissue
                    if click.pick.__class__ == tissueSystemVisualisationVisual.VSphereCellVisual:
                        o = click.pick
                        c=o.cell
                        t.cell_property( cell=c, property="PrC", value=self.system.phys["auxin_transport_model" ].nbr_prim)
                        t.cell_property( cell=c, property="PrZ", value=self.system.phys["auxin_transport_model" ].nbr_prim)
                        for n in t.cell_neighbors( c ):
                            t.cell_property( cell=n, property="PrZ", value=self.system.phys["auxin_transport_model" ].nbr_prim)
                        self.system.phys["auxin_transport_model" ].nbr_prim+=1
            
            # ------------------------------------------------------------------------------------------ fixed
        #    if self.fix_btn_status and  click.pick and click.pick.__class__ == svv.VMassVisual:
        #        o = click.pick
        #        if o.mass.fixed:
        #            o.mass.fixed = 0 
        #            #V o.color = Color.normal_point
        #        else:    
        #            o.mass.fixed = 1 
        #            #V o.color = Color.fixed_point
        #    # ------------------------------------------------------------------------------------------ auxin
        #    elif self.inc_aux_btn_status and  click.pick and click.pick.__class__ == svv.VMassVisual:
        #        o = click.pick
        #        o.mass.auxin += 1 
        #        if o.mass.auxin == 0: o.color = Color.normal_point
        #        else: 
        #            if o.mass.auxin < 0: o.color = Color.dec_auxin_point
        #            else: o.color = Color.inc_auxin_point
        #        l = self.find_springs_conected_with_mass( o.mass )
        #        for s in l: s.multiply_l( 1.2 )
        #    elif self.dec_aux_btn_status and  click.pick and click.pick.__class__ == svv.VMassVisual:
        #        o = click.pick
        #        o.mass.auxin -= 1 
        #        if o.mass.auxin == 0: o.color = Color.normal_point
        #        else: 
        #            if o.mass.auxin < 0: o.color = Color.dec_auxin_point
        #            else: o.color = Color.inc_auxin_point
        #        l = self.find_springs_conected_with_mass( o.mass )
        #        for s in l: s.multiply_l( 1/1.2 )
        #
        #    # ------------------------------------------------------------------------------------------ picking/dropping mass
        #    # this is used to process the mass dragging WITHOUT modificator
        #    elif self.drag_object: # drop the selected object
        #        # restore original attributes
        #        self.drag_object.mass.fixed = self.remember_fixed
        #        self.drag_object.color = self.remember_color
        #        # no initial velocity after dragging
        #        self.drag_object.mass.v = visual.vector(0., 0., 0.)
        #        self.drag_object = None
        #    elif click and click.pick and click.pick.__class__ == svv.VMassVisual and click.pick.mass.pickable: 
        #        # pick up the object (but only masses
        #        self.drag_object = click.pick
        #        print self.drag_object.pos, self.drag_object.mass.v, self.drag_object.mass.F
        #        self.selected_mass_id = self._mass2id[ self.drag_object.mass ]
        #        self.distance = visual.dot(self.display.forward, self.drag_object.pos)
        #        # save original attributes and overwrite them
        #        self.remember_fixed = self.drag_object.mass.fixed
        #        self.drag_object.mass.fixed = 1
        #        self.remember_color = self.drag_object.color
        #        self.drag_object.color = (self.remember_color[0] * 1.5,
        #                                 self.remember_color[1] * 1.5,
        #                                 self.remember_color[2] * 1.5)
        #    # ------------------------------------------------------------------------------------------ picking div. walls
        #    elif click and click.pick and click.pick.__class__ == vss.VSpringVisual:
        #        # TODO double click in the same edge
        #        if self.dividing_walls[ 1 ] == click.pick or self.dividing_walls[ 0 ] == click.pick: return
        #        click.pick.color = Color.selected_spring
        #        if self.dividing_walls[ 1 ] != None:
        #            self.dividing_walls[ 1 ].color = Color.spring
        #        self.dividing_walls[ 1 ] = self.dividing_walls[ 0 ]
        #        self.dividing_walls[ 0 ] = click.pick
        #        print click.pick.spring.k
        #
        #  # ------------------------------------------------------------------------------------------ dragging
        #if self.drag_object:
        #    self.drag_object.pos = self.display.mouse.project(normal=self.display.forward, d=self.distance)
