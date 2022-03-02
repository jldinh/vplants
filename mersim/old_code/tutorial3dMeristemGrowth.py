from springTissueModel import *
from const import *
import visual

s = TissueSystem( const =   auxInhPhyll4() ) #aux smallPressureAllMeristemGrowthWallShrink() )
#s.load_pickled_WalledTissue_data( filename="stableDomeNoPhys-117step.pickle")
#s.tissue.clear_aux()
#s.tissue.mark_IC()
#s.phys["mark_cell_identities" ].apply()
#s.phys["auxin_transport_model" ].init_aux()
#s.phys["auxin_transport_model" ].pre_step()
#s.visualisation.display.autoscale = 1
#s.visualisation.display.autocenter =1
#s.tissue._tissue_properties = {}

###s.visualisation.update()
###s.visualisation.display.forward=visual.vector(1,0,0)
###s.visualisation.display.up=visual.vector(0,0,1)
###s.visualisation.rotate(grab_scene=True, angle=3.1415/2, rotation=visual.vector(0,1,0),steps=15)
s.mainloop()
# comeback
#s.visualisation.rotate(grab_scene=True, angle=-3.1415/4, rotation=visual.vector(0,1,0),steps=15)
# rotate
#s.visualisation.rotate(grab_scene=True, angle=3.1415*2, rotation=visual.vector(0,0,1),steps=60)


#s.mainloop()
#s.time=s.tissue.time
#s.clear_simulation()
#s.create_meristem_surface( tissue=s.tissue )
#s.visualisation.init_after_meristem_creation()

#s.step_until_stable( 60 )
#s.phys["auxin_transport_model" ].init_aux()
#s.phys["auxin_transport_model" ].pre_step()
#s.mainloop()

#s = TissueSystem( const = GrowthWithInternalPressureByElongatingTheWalls() )
#s = TissueSystem( Mdata.top_meristem_f_n, GrowthWithInternalPressureByElongatingTheWalls() )
#import psyco
#psyco.full()
#s.visualisation.adjust_display()
#s.load_pickled_WalledTissue_data(filename="/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump,surface,exp6,stretchDetector2/250_WalledTissue.pickle")   
#s.discover_curvature(tolerance=0.91) 
#s.visualisation.clear()
#s.create_meristem_surface( tissue=s.tissue )
#s.visualisation.init_after_meristem_creation()
#s.discover_curvature(tolerance=0.91) 
#s.mainloop()
