#!/usr/bin/env python
"""const.py

Contains different constants used in simulations.


:version: 2006-05-15 15:21:06CEST
:author: szymon stoma
"""
import visual

class Mdata:
    """Contains paths to digitized meristem data.
    """
    full_meristem_f_n = "/home/stymek/mdata/antgfp58a_proj/antgpf58a.dat"
    top_meristem_f_n = "/home/stymek/mdata/antgfp58a_proj/antgpf58a_edited.dat"
    top_meristem_f_n_hooked = "/home/stymek/mdata/antgfp58a_proj/antgpf58a_edited_hooked.dat"
    two_points =  "/home/stymek/mdata/2points.dat"
    two_cells = "/home/stymek/mdata/2cells.dat"
    honey_slice = "/home/stymek/mdata/honeySlice/honeySlice.dat"
    top_meristem_3c = "/home/stymek/mdata/antgfp58a_proj/topMeristem-3c.dat"
    honey_slice_3sides_fixed = "/home/stymek/mdata/honeySlice/honeySlice3sidesFixed.dat"
    ring_hexagon = "/home/stymek/mdata/ringHexagon.dat"
    m_07_07_05_PINwithImmunolab = "/home/stymek/mdata/07-07-05-PINwithImmunolab/c16-proj-grey.dat"

#------------------------------------------------------------------------------- Color
class Color:
    """This is class to bind the object displayed by visual with colors. Colors are stored
    in RBG format.
    """
    c = 1.5
    fixed_point =       (0.0,  0.0,   0.8)
    normal_point =      (0.4,  1.,   0.4)
    spring =           (0.0,  0.6,   0.0)
    spring_under_tension = (0.6,  0.0,   0.0)
    spring_under_compression = (0.0,  0.0,   0.6)
    background =       (0.0,  0.0,   0.0)
    high_viscosity =    (0.3,  0.3,   0.3)
    inc_auxin_point =    (0.8,  0.0,   0.0)
    dec_auxin_point =    (0.4,  0.0,   0.0)
    selected_spring =   (0.0*c,0.8*c, 0.0*c)
    added_spring =      (1, 0, 0)
    #normal_cell     = (0.,0.5,0.)
    full_auxin_cell = (0.,1.,0.)
    initialCell = (0.,0.5,0.5)
    centralZoneCell = (0.5,0.5,0.)
    peripheralZoneCell = (0.,0.,0.5)
    normalZoneCell = (0.,0.,0.)#(0.,0.7,0.)
    primordiumZoneCell=(0.,0.,0.)
    primordiumZone=(.1,0.,0.7)
#------------------------------------------------------------------------------- Const
class Const(dict):
    """This is a place to store the global setting needed for this module to work
    properly.
    """
    
    ### System initialisation
    sim_timestep = 0.1
    """#: value used by solver"""
    sim_rate = 1.0 / sim_timestep
    """#: ???"""
    sim_oversample = 1 
    """#: ???"""
    system_delta_uniform_up = 0 
    """#: Up force cooef"""
    system_spring2mass_tag = "free" 
    """#: [\"free\"|\"connected\"] If true if spring is deleted it also deletes the points atached to it (if they are unnecessary). """
    system_run = False 
    """#: If True the system is running after start."""
    system_grab_scene = False
    """#: True if scene should be saved in .pov files"""
    
    # Send to display
    name = "--define--"
    """#: Name for the system"""
    system_width = 800
    system_height = 600
    system_fov=visual.pi/3.
    system_background= (Color.background[0],Color.background[1],Color.background[2])
    system_ambient = 0.8
    #

    ## Forces
    system_forces_gravity = False
    system_forces_spring = True
    system_forces_visco = False
    system_forces_uniform_up = False
    system_forces_radial_move = False
    #should be declared in TissueConst
    #tissue_system_forces_simple_pressure = False

    # Force deps:
    gravity_const = 1
    uniform_up_const = 1
    #

    
    visualisation = True
    """#: True if simulation should be visualised"""
    system_display_show_force_vectors = False
    visual_force_magnifier  = 1
    """#: used to magnify the displayed force vectors"""

    mtb_global_direction_active = False
    """#: used to change the spring properties depanding on direction TODO move to System"""

    ## END System initialisation

    cell_node_size = 20 
    """#:Size of the cell node while generating picture using pylab graph visualisation rutines. This value is used in WalledTissue.show_cells()."""

    wv_node_size = 20 
    """#:Size of the wv node while generating picture using pylab graph visualisation rutines. This value is used in WalledTissue.show_cells()."""
    
    mass_point_size = 50
    """#:Size of the mass point used in representing mass point in visual simulation. The sphere.radius is set acording to this value."""
    
    mass_standart_mass = 1.
    """#:Standart mass used while relizing simulation system."""
    
    mass_standart_radius = 1.0
    """#:??? """


    spring_standart_radius = 0.8
    """#:Standart radius of the cylinder used to visualize spring"""

    spring_standart_k= .1 #1.
    """#:Standart spring k coefficiant"""

    spring_standart_damping = 1. #0.4
    """#:Standart spring dumping coefficiant"""

    max_up_force = 0.1
    """#:Maximal up force cooeficient which can be applied to the system. This value is used while creating control slider. This slider can have values from [0, max_up_force]."""

    max_system_viscosity = 0.1
    """#:Maximal viscosity cooeficiant which can be applied to the system. This value is used while creating control slider and setting the visco for initial system. This slider can have values from [0, max_system_viscosity]."""

    nmb_division_edge_generation = 20
    """#:This value is used to organize the new walls into 'blocks', each block can be defined identified graphically with different color in the visualisation system."""

    division_symetry_direction = visual.vector(0.,0.,0.)

    fixed_border = 125 #200 
    """#: all points which z is lower than this value will be threat as fixed"""

    dropped_border = 155 #300 
    """#: all points which z is lower than this value will be dropped from simulation"""

    simple_pressure_center = visual.vector(230,230,-100) 
    """#: point used in calculating what is IN/OUT of the meristem; this point should be put inside."""

    average_velosity_max = 15.
    """#: variable used to limit the velosity of all points --  if it is exceeded the growing factor is yield"""

    start_up_force = 0#3.
    """#: the initialized growth factor (up_force) value"""

    dividing_cell_walls_shrinking_factor = 0.8
    """#: is used while inserting the new wall (which is then divided proportionally in to two parts ), the spring has relaxing length of current_rest_length*"""

    reconstruct_3d_from_slices = True
    """#: if is true the slices are read to reconstruct meristem 3d structure"""



    spring_growth = False
    spring_growth_rate = 0.001
    """#: after each step the springs are elongating a little bit"""

    cells_divide = True
    """#: True when cells can divide."""

    force_vectors_visible = True
    force_vectors_mag = 1

    visualisation_update_frequency = 2
    """#: The update visualisation happens each *value* of TODO currently frame(time) simulation."""
    
    max_trashhold_stable_state_force = 0.01
    """#: To calculate stable state"""
    
    visualisation_system="frame"
    """#: what type of visualisation should be attached: frame|surface"""

    system_spring2mass_tag = "connected"


class TissueConst( Const ):
    meristem_data = ""
    """#: meristem file name"""
    projection_path = "/home/stymek/mdata/antgfp58a_proj"
    """#: the z coordinates are taken from projections found in this place. More docs in Pierrs' code."""
    
    cs_surf_max_surface_before_division = 400 
    """#:Cell Division Strategy- Treshhold surface area, after exceeding the cell divides."""

    cs_peri_trashhold_perimiter_to_divide_cell=100
    """#: Cell Division Strategy- Treshhold cell perimiter, after exceeding the cell divides."""
    
    dscs_shortest_wall_with_equal_surface_nbr_of_segments_in_wall = 4
    """#: The cell wall is divided in this number of segments while trying to find equal surfaces. """
    
    dscs_shortest_wall_with_equal_surface_length_tolerance = 0.92
    """#: The cell wall from the smallest area diff is selected then it is no longer than this value times shortest wall possible(between centers of opposit walls)"""
    mtb_direction_active = False
    """#: if True the microtubules behaviour are dispatched in the system"""
    mtb_direction_initial_vector = visual.norm( visual.vector( 1, 1, 0 ) ) 
    """#: vector which is used to to initialize the microtubules"""
    mtb_direction_arrow_scale = 25
    """#: factor which scales the direction arrow displayed inside each cell"""
    mtb_max_spring_k = 3.
    mtb_min_spring_k = 0.
    """#: used while calculatiing spring effect of microtubules"""
    
    name = "SpringTissueModel v0.3"

    tissue_system_forces_cell_pressure = False
    cell_pressure = 1.
    """#: trugor cell pressure strength"""

    tissue_system_forces_simple_pressure = False
    simple_pressure_const = 1.     
    """#: simple pressure strength"""

    tissue_system_forces_simple_pressure_under_primordium=False
    simple_pressure_under_primordium_const  = 1.
    """#: simple pressure under primordium strength"""
    
    
    spring_growth = False
    """#:true iff springs should grow"""
    
    division_strategy = "dscs_shortest_wall"
    
    load_simulation = False
    """#: True if data should be taken from pickled simulation instead from calculated processes """
    save_simulation = False
    """#: True if data should be stored on disk """
    
    load_starting_meristem= False
    """#: Loads starting meristem from start.pickle"""
    

    remove_cells = False
    """#: True if cells should be dropped while simulation. TODO: add strategy here."""
    
    desired_cell_nbr = 1000
    """"#: The number of cells in the simulation. It is used to increase the presure if there is not
    enough cells."""
    
    meristem_load_scale = 1
    """#: Used to scale the meristem while loading it from .dat files. Important for tuning the simulation (to keep same
    size of the cells)."""
    
    
    auxin_spring_growth_rate = 0.1
    """#: When the cell is flooded by auxin its walls growth faster.
    """

    pickled_WalledTissue_data_folder = ""
    """#: Additional folder to store dataa from simulation"""

    folder_for_saving_data = "" 
    """#: To save the data in external folder. It B{must} exist.
    """
    
    cell_properties ={
        "IC": False,
        "PZ": False,
        "CZ": False,
        "NZ": False,
        "PrZ": 0,
        "PrC": 0,
        "border_cell": False,
        "auxin_level": 0,
        "auxin_level_1": 0,
        "identity": "normal",
        "mtb_orientation_angle": 0,
        "was_under_angular_stress":False}
    """#: Used to initialise cell properties
    """
    
    tissue_properties ={
        "primordiums": {}
    }
    """#: Used to initialise tissue properties
    """

    
    cell_edge_properties={
        "pump_active": False,
        "pump_direction": (0,0),
        "pin_level": [1,1] }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """
    
    wv_properties={}
    
    wv_edge_properties={
        "old_wall_successor": False,
        "pin_level": [1,1] }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """
    
    sphere_visualisation_sphere_size_mult = 25
    """When visualising tissue ass cells the cell is represented by sphere with radius multiplied with this value
    (radius is calculated in dynamic way depanding on cell_surface)
    """
    
    sphere_visualisation_sphere_cell_identity_size_mult = 5
    """When visualising tissue identity as  sphere with radius multiplied with this value
    (radius is calculated in dynamic way depanding on cell_surface)
    """
    
    
    tissue_system_phys_mark_cell_identities = True
    """iff True identities will be initialised
    """
    
    tissue_system_phys_aux_flow = True
    """iff True auxin transport would be dispatched
    """
    
class ShapeConst( Const ):
    mass_point_size = 10
    mass_standart_mass = 1.
    mass_standart_radius = 0.1
    max_up_force = 0.
    name = "StringModel v0.1"

class HoneySlice2DConst( TissueConst ):
    cs_surf_max_surface_before_division = 1000 
    reconstruct_3d_from_slices =False 
    max_up_force = 0 #10
    simple_pressure_const = 3.
    dividing_cell_walls_shrinking_factor = 0.9
    fixed_border = 150 #200 
    dropped_border = 200 #300
    tissue_system_forces_simple_pressure =True 




class PressureHexagonsConst( TissueConst ):
    mass_point_size = 100
    mass_standart_radius = 1
    max_up_force = 0.
    reconstruct_3d_from_slices = False 
    cells_divide = False 
    system_run = False 
    tissue_system_forces_cell_pressure =True 
    spring_growth =False 
    spring_growth_rate = 0.0001
    force_vectors_mag = 100
    spring_standart_k = 0.2
    cell_pressure_const = 40000.
    system_forces_visco =True 
    division_symetry_direction = visual.vector(1.,1.,0.)
    mtb_direction_active =True 
    mtb_direction_initial_vector = visual.norm( visual.vector( 1., 1., 0. ) ) 

class GrowthHexagonsConst( TissueConst ):
    mass_point_size = 100
    mass_standart_radius = 1
    max_up_force = 0.
    reconstruct_3d_from_slices = False 
    cells_divide = False 
    system_run = True 
    tissue_system_forces_cell_pressure =False 
    spring_growth =True 
    spring_growth_rate = 0.0005
    force_vectors_mag = 100
    spring_standart_k = 0.2
    cell_pressure = 0.0005
    cs_surf_max_surface_before_division = 3500 


class GrowthWithInternalPressureByElongatingTheWalls( TissueConst ):
    """Quite stable, growing slowly.
    """
    meristem_data = Mdata.top_meristem_f_n
    max_up_force = 0.
    system_run = True 
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 0.5#0.2
    cells_divide = True 
    spring_growth =True 
    spring_growth_rate = 0.001
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = True 
    visual_force_magnifier  = 4
    sim_timestep = 0.15
    cs_surf_max_surface_before_division = 800
    fixed_border = 70 #200 
    dropped_border = 110 #300 
    spring_standart_k = 2
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True


class GrowthWithInternalPressureByElongatingTheWalls2( TissueConst ):
    """Quite stable, growing slowly, expanding from the form
    """
    meristem_data = Mdata.honey_slice
    max_up_force = 0.
    system_run = True 
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 0.2
    cells_divide = True 
    spring_growth = False
    spring_growth_rate = 0.001
    system_forces_visco = True 
    system_display_show_force_vectors = True
    reconstruct_3d_from_slices = False 
    visual_force_magnifier  = 20
    sim_timestep = 0.3
    cs_surf_max_surface_before_division = 1200
    fixed_border = 150 #200 
    dropped_border = 200 #300 

class GrowthWithInternalPressureByElongatingTheWalls3( TissueConst ):
    """Quite stable, growing slowly, expanding from the form
    """
    meristem_data = Mdata.honey_slice
    max_up_force = 0.
    system_run = True 
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 0.2
    cells_divide = True 
    spring_growth = True 
    spring_growth_rate = 0.001
    system_forces_visco = True 
    system_display_show_force_vectors = True
    reconstruct_3d_from_slices = False 
    visual_force_magnifier  = 20
    sim_timestep = 0.3
    cs_surf_max_surface_before_division = 1200
    fixed_border = 150 #200 
    dropped_border = 200 #300 
    spring_standart_k = 2

class GrowthWithInternalPressureByElongatingTheWalls4( TissueConst ):
    """Quite stable, growing slowly, expanding from the form
    """
    #meristem_data = Mdata.
    max_up_force = 0.
    system_run = True 
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 0.4
    cells_divide = True 
    spring_growth = True 
    spring_growth_rate = 0.001
    system_forces_visco = True 
    system_display_show_force_vectors = False 
    reconstruct_3d_from_slices = False 
    visual_force_magnifier  = 10
    sim_timestep = 0.3
    cs_surf_max_surface_before_division = 1200
    fixed_border = 150 #200 
    dropped_border = 200 #300 
    spring_standart_k = 2
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    
class TwoCellsConst(TissueConst):
    meristem_data = Mdata.two_cells


class smallPressureAllMeristemGrowthWallShrink( TissueConst ):
    """06-09-11-smallPressureAllMeristemGrowthWallShrink
    """
    meristem_data = Mdata.top_meristem_3c
    max_up_force = 0.
    system_run = True
    meristem_load_scale=1.2
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 0.4#.#0.2
    cells_divide = True 
    spring_growth =True
    spring_growth_rate = 0.001
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = True 
    visual_force_magnifier  = 4
    sim_timestep = 0.35
    cs_surf_max_surface_before_division =300
    fixed_border = 70*meristem_load_scale #200 
    dropped_border = 100*meristem_load_scale #300 
    spring_standart_k = 2
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True
    system_grab_scene = True
    save_simulation = False
    load_simulation = False
    #mass_point_size = 10
    spring_standart_radius = 0.2
    mass_standart_radius = 0.8
    visualisation_update_frequency = 2
    load_starting_meristem= False
    dividing_cell_walls_shrinking_factor = 0.85
    visualisation_system = "surface"


    
class ExpandingSystemWithHighPressure(TissueConst ):
    """Test for crash
    """
    meristem_data = Mdata.top_meristem_3c
    max_up_force = 0.
    system_run = True
    meristem_load_scale=1.2
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 2.#0.2
    cells_divide = True 
    spring_growth =True
    spring_growth_rate = 0.005
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = True 
    visual_force_magnifier  = 4
    sim_timestep = 0.35
    cs_surf_max_surface_before_division =300
    fixed_border = 70*meristem_load_scale #200 
    dropped_border = 100*meristem_load_scale #300 
    spring_standart_k = 2
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True
    system_grab_scene = True
    save_simulation = False
    load_simulation = True
    #mass_point_size = 10
    spring_standart_radius = 0.2
    mass_standart_radius = 0.8
    visualisation_update_frequency = 2
    load_starting_meristem= False
    dividing_cell_walls_shrinking_factor = 0.95
    visualisation_system = "surface"


class internalPressureWithMT( TissueConst ):
    """06-09-11-internalPressureWithMT
    """
    meristem_data = Mdata.honey_slice_3sides_fixed
    meristem_load_scale=0.345
    mass_point_size = 100
    mass_standart_radius = 1
    max_up_force = 0.
    reconstruct_3d_from_slices = False 
    cells_divide = False 
    system_run = True 
    tissue_system_forces_cell_pressure =True 
    spring_growth =False 
    spring_growth_rate = 0.0001
    force_vectors_mag = 100
    spring_standart_k = 0.2
    cell_pressure_const = 400.
    system_forces_visco =True 
    division_symetry_direction = visual.vector(1.,1.,0.)
    mtb_direction_active =False
    mtb_direction_initial_vector = visual.norm( visual.vector( 1., 1., 0. ) ) 
    visualisation_system = "surface"
    max_system_viscosity = 0.4


class stableMeristemFormingAStickBecauseOfFixedRemoval( TissueConst ):
    """06-09-12-stableMeristemFormingAStickBecauseOfFixedRemoval
    """
    meristem_data = Mdata.top_meristem_3c
    max_up_force = 0.
    system_run = True
    meristem_load_scale=1.2
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 1.2#.#0.2
    cells_divide = True 
    spring_growth =False
    spring_growth_rate = 0.002
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = True 
    visual_force_magnifier  = 4
    sim_timestep = 0.35
    cs_surf_max_surface_before_division =300
    fixed_border = 70*meristem_load_scale #200 
    dropped_border = 100*meristem_load_scale #300 
    spring_standart_k = 2
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True
    system_grab_scene = False
    save_simulation = False
    load_simulation = False
    #mass_point_size = 10
    spring_standart_radius = 0.2
    mass_standart_radius = 0.8
    visualisation_update_frequency = 2
    load_starting_meristem= False
    dividing_cell_walls_shrinking_factor = 0.9
    visualisation_system = "frame"

class stableMeristemGrowthWithAuxinPatch( TissueConst ):
    """06-09-12-stableMeristemGrowthWithAuxinPatch
    """
    meristem_data = Mdata.top_meristem_3c
    max_up_force = 0.
    system_run = True
    meristem_load_scale=0.8
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 0.5#8#.5
    cells_divide = True 
    spring_growth =True
    spring_growth_rate = 0.002
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = True 
    visual_force_magnifier  = 4
    sim_timestep = 0.2
    cs_surf_max_surface_before_division =200
    fixed_border = 120*meristem_load_scale #200 
    dropped_border = 140*meristem_load_scale #300 
    spring_standart_k = 1
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True
    system_grab_scene = False
    save_simulation = False
    load_simulation = False
    #mass_point_size = 10
    spring_standart_radius = 0.2
    mass_standart_radius = 0.8
    visualisation_update_frequency = 4
    load_starting_meristem= False
    dividing_cell_walls_shrinking_factor = 0.8
    visualisation_system = "frame"
    max_system_viscosity = 0.2
    max_trashhold_stable_state_force = 0.0001
    mtb_direction_active = True

class testMT( TissueConst ):
    """06-09-12-stableMeristemGrowthWithAuxinPatch
    """
    meristem_data = Mdata.honey_slice
    max_up_force = 0.
    system_run = True
    meristem_load_scale=0.8
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 0.5#8#.5
    cells_divide = True 
    spring_growth =True
    spring_growth_rate = 0.002
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = True 
    visual_force_magnifier  = 4
    sim_timestep = 0.2
    cs_surf_max_surface_before_division =200
    fixed_border = 120*meristem_load_scale #200 
    dropped_border = 140*meristem_load_scale #300 
    spring_standart_k = 1
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True
    system_grab_scene = False
    save_simulation = False
    load_simulation = False
    #mass_point_size = 10
    spring_standart_radius = 0.2
    mass_standart_radius = 0.8
    visualisation_update_frequency = 4
    load_starting_meristem= False
    dividing_cell_walls_shrinking_factor = 0.8
    visualisation_system = "frame"
    max_system_viscosity = 0.2
    max_trashhold_stable_state_force = 0.0001
    mtb_direction_active = True

class pin1exp( TissueConst ):
    """06-09-20-experiment with PIN1 mutant.
    """
    meristem_data = Mdata.top_meristem_3c
    max_up_force = 0.
    system_run = True
    meristem_load_scale=1.5
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 0.5#8#.5
    cells_divide = True 
    spring_growth =True
    spring_growth_rate = 0.002
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = True 
    visual_force_magnifier  = 4
    sim_timestep = 0.3
    cs_surf_max_surface_before_division =600 #300
    fixed_border = 100*meristem_load_scale #200 
    dropped_border = 120*meristem_load_scale #300 
    spring_standart_k = 1
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True
    system_grab_scene = False
    save_simulation = False
    load_simulation = False
    #mass_point_size = 10
    spring_standart_radius = 0.2
    mass_standart_radius = 0.8
    visualisation_update_frequency = 10
    load_starting_meristem= False
    dividing_cell_walls_shrinking_factor = 0.8
    visualisation_system = "frame"
    max_system_viscosity = 0.2
    max_trashhold_stable_state_force = 0.001
    mtb_direction_active = False
    
class pin1exp2( TissueConst ):
    """06-09-21-pin one
    auxin injected in round 100 in 6th row
    """
    meristem_data = Mdata.top_meristem_3c
    max_up_force = 0.
    system_run = True
    meristem_load_scale=1.5
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 0.5#8#.5
    cells_divide = True 
    spring_growth =True
    spring_growth_rate = 0.002
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = True 
    visual_force_magnifier  = 4
    sim_timestep = 0.3
    cs_surf_max_surface_before_division =300
    fixed_border = 100*meristem_load_scale #200 
    dropped_border = 120*meristem_load_scale #300 
    spring_standart_k = 1
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True
    system_grab_scene = True
    save_simulation = False
    load_simulation = False
    #mass_point_size = 10
    spring_standart_radius = 0.2
    mass_standart_radius = 0.8
    visualisation_update_frequency = 2
    load_starting_meristem= False
    dividing_cell_walls_shrinking_factor = 0.8
    visualisation_system = "surface"
    max_system_viscosity = 0.2
    max_trashhold_stable_state_force = 0.001
    mtb_direction_active = False

class pin1exp3( TissueConst ):
    """06-09-23-pin one
    auxin injected in round 100 in 6th row
    try to lower pressure
    test of wall growth alg.
    it was because of error -- springs grow with different factor under the bump.
    """
    meristem_data = Mdata.top_meristem_3c
    max_up_force = 0.
    system_run = True
    meristem_load_scale=1.5
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 0.3#8#.5
    simple_pressure_under_primordium_const = 0.1
    cells_divide = True 
    spring_growth =True
    spring_growth_rate = 0.01
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = True 
    visual_force_magnifier  = 4
    sim_timestep = 0.3
    cs_surf_max_surface_before_division =300
    fixed_border = 140 #200 
    dropped_border = 160 #300 
    spring_standart_k = 1
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True
    system_grab_scene = False
    save_simulation = False
    load_simulation = False
    #mass_point_size = 10
    spring_standart_radius = 0.2
    mass_standart_radius = 0.8
    visualisation_update_frequency = 2
    load_starting_meristem= False
    dividing_cell_walls_shrinking_factor = 0.8
    visualisation_system = "frame"
    max_system_viscosity = 0.2
    max_trashhold_stable_state_force = 0.001
    mtb_direction_active = False
    folder_for_saving_data = "/media/sdf1/meristem/06-09-23-pin1exp,formingBump/"

class pin1exp4( TissueConst ):
    """06-09-23-pin one
    auxin injected in round 100 in 6th row
    try to lower pressure
    test of wall growth alg.
    too low pressure to pop the bump and let it decomrepss
    """
    meristem_data = Mdata.top_meristem_3c
    max_up_force = 0.
    system_run = True
    meristem_load_scale=1.5
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 0.2#8#.5
    simple_pressure_under_primordium_const = 0.1
    cells_divide = True 
    spring_growth =True
    spring_growth_rate = 0.01
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = True 
    visual_force_magnifier  = 4
    sim_timestep = 0.3
    cs_surf_max_surface_before_division =300
    fixed_border = 140 #200 
    dropped_border = 160 #300 
    spring_standart_k = 1
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True
    system_grab_scene = True
    save_simulation = False
    load_simulation = False
    #mass_point_size = 10
    spring_standart_radius = 0.2
    mass_standart_radius = 0.8
    visualisation_update_frequency = 2
    load_starting_meristem= False
    dividing_cell_walls_shrinking_factor = 0.8
    visualisation_system = "frame"
    max_system_viscosity = 0.2
    max_trashhold_stable_state_force = 0.001
    mtb_direction_active = False
    folder_for_saving_data = "/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump/"


class pin1exp5( TissueConst ):
    """06-09-23-pin one
    auxin injected in round 100 in 6th row
    try to lower pressure
    test of wall growth alg.
    too low pressure to pop the bump and let it decomrepss
    """
    meristem_data = Mdata.top_meristem_3c
    max_up_force = 0.
    system_run = True
    meristem_load_scale=1.5
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 0.2#8#.5
    simple_pressure_under_primordium_const = 0.1
    cells_divide = True 
    spring_growth =True
    spring_growth_rate = 0.01
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = True 
    visual_force_magnifier  = 4
    sim_timestep = 0.3
    cs_surf_max_surface_before_division =300
    fixed_border = 140 #200 
    dropped_border = 160 #300 
    spring_standart_k = 1
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True
    system_grab_scene = True
    save_simulation = True
    load_simulation = False
    #mass_point_size = 10
    spring_standart_radius = 0.2
    mass_standart_radius = 0.8
    visualisation_update_frequency = 2
    load_starting_meristem= False
    dividing_cell_walls_shrinking_factor = 0.8
    visualisation_system = "surface"
    max_system_viscosity = 0.2
    max_trashhold_stable_state_force = 0.001
    mtb_direction_active = False
    folder_for_saving_data = "/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump,surface/"
    pickled_WalledTissue_data_folder = "/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump,surface/"

class pin1exp6( TissueConst ):
    """06-09-23-pin1exp,formingBump,surface,exp6
    auxin injected in round 100 in 6th row
    """
    meristem_data = Mdata.top_meristem_3c
    max_up_force = 0.
    system_run = True
    meristem_load_scale=1.5
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 0.2#8#.5
    simple_pressure_under_primordium_const = 0.2
    cells_divide = True 
    spring_growth =True
    spring_growth_rate = 0.01
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = True 
    visual_force_magnifier  = 4
    sim_timestep = 0.3
    cs_surf_max_surface_before_division =300
    fixed_border = 140 #200 
    dropped_border = 160 #300 
    spring_standart_k = 1
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True
    system_grab_scene = True
    save_simulation = False
    load_simulation = True
    #mass_point_size = 10
    spring_standart_radius = 0.2
    mass_standart_radius = 0.8
    visualisation_update_frequency = 2
    load_starting_meristem= False
    dividing_cell_walls_shrinking_factor = 0.8
    visualisation_system = "surface"
    max_system_viscosity = 0.2
    max_trashhold_stable_state_force = 0.001
    mtb_direction_active = False
    folder_for_saving_data = "/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump,surface,exp6/"
    pickled_WalledTissue_data_folder = "/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump,surface,exp6/"

class pin1exp8( TissueConst ):
    """06-09-23-pin1exp,formingBump,surface,exp6,stretchDetector2
    auxin injected in round 100 in 6th row
    curv detector at 180
    """
    meristem_data = Mdata.top_meristem_3c
    max_up_force = 0.
    system_run = True
    meristem_load_scale=1.5
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 0.2#8#.5
    simple_pressure_under_primordium_const = 0.2
    cells_divide = True 
    spring_growth =True
    spring_growth_rate = 0.01
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = True 
    visual_force_magnifier  = 4
    sim_timestep = 0.3
    cs_surf_max_surface_before_division =300
    fixed_border = 140 #200 
    dropped_border = 160 #300 
    spring_standart_k = 1
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True
    system_grab_scene = False
    save_simulation = False 
    load_simulation = False
    #mass_point_size = 10
    spring_standart_radius = 0.2
    mass_standart_radius = 0.8
    visualisation_update_frequency = 2 
    load_starting_meristem= False
    dividing_cell_walls_shrinking_factor = 0.8
    visualisation_system = "surface"
    max_system_viscosity = 0.2
    max_trashhold_stable_state_force = 0.001
    mtb_direction_active = False
    folder_for_saving_data = "/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump,surface,exp6,stretchDetector2/"
    pickled_WalledTissue_data_folder = "/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump,surface,exp6,stretchDetector2/"


class stressDetectorOnSprings( TissueConst ):
    """06-10-05-stressDetectorOnSprings
    auxin injected in round 100 in 6th row
    """
    meristem_data = Mdata.top_meristem_3c
    max_up_force = 0.
    system_run = True
    meristem_load_scale=1.5
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 0.2#8#.5
    simple_pressure_under_primordium_const = 0.2
    cells_divide = True 
    spring_growth =True
    spring_growth_rate = 0.01
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = True 
    visual_force_magnifier  = 4
    sim_timestep = 0.3
    cs_surf_max_surface_before_division =300
    fixed_border = 140 #200 
    dropped_border = 160 #300 
    spring_standart_k = 1
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True
    system_grab_scene = False
    save_simulation = False 
    load_simulation = False
    #mass_point_size = 10
    spring_standart_radius = 0.2
    mass_standart_radius = 0.8
    visualisation_update_frequency = 2 
    load_starting_meristem= False
    dividing_cell_walls_shrinking_factor = 0.8
    visualisation_system = "frame"
    max_system_viscosity = 0.2
    max_trashhold_stable_state_force = 0.001
    mtb_direction_active = False
    folder_for_saving_data = "/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump,surface,exp6,stretchDetector2/"
    pickled_WalledTissue_data_folder = "/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump,surface,exp6,stretchDetector2/"


class nicePicture( TissueConst ):
    """06-10-08-nicePicture
    """
    meristem_data = Mdata.full_meristem_f_n
    max_up_force = 0.
    system_run = True
    meristem_load_scale=1.5
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 0.2#8#.5
    simple_pressure_under_primordium_const = 0.2
    cells_divide = True 
    spring_growth =True
    spring_growth_rate = 0.01
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = True 
    visual_force_magnifier  = 4
    sim_timestep = 0.3
    cs_surf_max_surface_before_division =300
    fixed_border = 140 #200 
    dropped_border = 160 #300 
    spring_standart_k = 1
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True
    system_grab_scene = False
    save_simulation = False 
    load_simulation = False
    #mass_point_size = 10
    spring_standart_radius = 0.2
    mass_standart_radius = 0.8
    visualisation_update_frequency = 2 
    load_starting_meristem= False
    dividing_cell_walls_shrinking_factor = 0.8
    visualisation_system = "surface"
    max_system_viscosity = 0.2 
    max_trashhold_stable_state_force = 0.001
    mtb_direction_active = True
    folder_for_saving_data = "/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump,surface,exp6,stretchDetector2/"
    pickled_WalledTissue_data_folder = "/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump,surface,exp6,stretchDetector2/"


class ballTest( nicePicture ):
    """06-10-08-nicePicture
    """
    visualisation_system = "sphereCells"



class presentationKatowice1( TissueConst ):
    """06-10-11-presentationKatowice1
    regular growth from regular 2d structure to 3d structure,
    no cell divisions, 
    """
    meristem_data = Mdata.honey_slice
    max_up_force = 0.
    system_run = True
    meristem_load_scale=1.5
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = True 
    simple_pressure_const = 5.2#8#.5
    simple_pressure_under_primordium_const = 0
    cells_divide = False 
    spring_growth =False
    spring_growth_rate = 0.
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = False
    visual_force_magnifier  = 4
    sim_timestep = 0.3
    cs_surf_max_surface_before_division = 0
    fixed_border = 1000#140 #200 
    dropped_border = 1000#160 #300 
    spring_standart_k = 1
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True
    system_grab_scene = True
    save_simulation = False 
    load_simulation = False
    #mass_point_size = 10
    spring_standart_radius = 0.2
    mass_standart_radius = 4.0
    visualisation_update_frequency = 2 
    load_starting_meristem= False
    dividing_cell_walls_shrinking_factor = 0.9
    visualisation_system = "surface"
    max_system_viscosity = 0.8
    max_trashhold_stable_state_force = 0.001
    mtb_direction_active = False
    #folder_for_saving_data = "/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump,surface,exp6,stretchDetector2/"
    #pickled_WalledTissue_data_folder = "/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump,surface,exp6,stretchDetector2/"

class presentationKatowice2a( presentationKatowice1 ):
    """06-10-11-presentationKatowice2
    regular growth from regular 2d structure
    cell divisions, turgor pressure,
    NO cell wall grows,
    up tp 350 evertything ok
    """
    meristem_data = Mdata.two_cells
    max_up_force = 0.
    system_run = True
    meristem_load_scale=1.5
    tissue_system_forces_cell_pressure =True 
    tissue_system_forces_simple_pressure = False 
    simple_pressure_const = 0#8#.5
    simple_pressure_under_primordium_const = 0
    cells_divide = True 
    spring_growth =False
    spring_growth_rate = 0.
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = False
    visual_force_magnifier  = 4
    sim_timestep = 0.03
    cs_surf_max_surface_before_division = 2000
    fixed_border = 140 #200 
    dropped_border = 160 #300 
    spring_standart_k = 1
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True
    system_grab_scene = True
    save_simulation = False 
    load_simulation = False
    #mass_point_size = 10
    spring_standart_radius = 0.2
    mass_standart_radius = 4.0
    visualisation_update_frequency = 2 
    load_starting_meristem= False
    dividing_cell_walls_shrinking_factor = 0.4
    visualisation_system = "surface"
    max_system_viscosity = 0.1
    max_trashhold_stable_state_force = 0.001
    mtb_direction_active = False
    #folder_for_saving_data = "/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump,surface,exp6,stretchDetector2/"
    #pickled_WalledTissue_data_folder = "/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump,surface,exp6,stretchDetector2/"
    cell_pressure_const = 30000

class presentationKatowice2b( presentationKatowice2a ):
    """06-10-11-presentationKatowice2b
    regular growth from regular 2d structure
    cell divisions, turgor pressure,
    cell wall grows, 
    cell wall grows,
    up tp 300 ok, leter colaps of middle
    """
    spring_growth =True
    spring_growth_rate = 0.1


class presentationKatowice3a( presentationKatowice1 ):
    """06-10-11-presentationKatowice2c
    algoritm showing divisions. get the artificial shape,
    find some approx. heightmap fill with small cells.
    """
    meristem_data = Mdata.honey_slice
    max_up_force = 0.
    system_run = True
    meristem_load_scale=1.5
    tissue_system_forces_cell_pressure =False 
    tissue_system_forces_simple_pressure = False 
    simple_pressure_const = 0#8#.5
    simple_pressure_under_primordium_const = 0
    cells_divide = True 
    spring_growth =False
    spring_growth_rate = 0.
    system_forces_visco = True 
    system_display_show_force_vectors =False
    reconstruct_3d_from_slices = True
    visual_force_magnifier  = 4
    sim_timestep = 0.15
    cs_surf_max_surface_before_division = 2000
    fixed_border = 1400 #200 
    dropped_border = 1600 #300 
    spring_standart_k = 1
    division_strategy = "dscs_shortest_wall_with_equal_surface"
    remove_cells = True
    system_grab_scene = True
    save_simulation = False 
    load_simulation = False
    #mass_point_size = 10
    spring_standart_radius = 0.2
    mass_standart_radius = 4.0
    visualisation_update_frequency = 1 
    load_starting_meristem= False
    dividing_cell_walls_shrinking_factor = 0.8 ###!!
    visualisation_system = "surface"
    max_system_viscosity = 0.8
    max_trashhold_stable_state_force = 0.001
    mtb_direction_active = False
    #folder_for_saving_data = "/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump,surface,exp6,stretchDetector2/"
    #pickled_WalledTissue_data_folder = "/media/FHD-2PRO/meristem/06-09-23-pin1exp,formingBump,surface,exp6,stretchDetector2/"
    cell_pressure_const = 500

class presentationKatowice3b( presentationKatowice1 ):
    """06-10-11-presentationKatowice3d
    role of params in alg. div
    """
    dividing_cell_walls_shrinking_factor = 0.2 ###!!


class presentationKatowice4( presentationKatowice1 ):
    """06-10-11-presentationKatowice3
    regular growth from regular 2d structure to 3d structure,
    cell divisions, cell wall grows, seems to be stable and grows
    long.
    """
    cells_divide = True 
    spring_growth =True
    spring_growth_rate = 0.01
    cs_surf_max_surface_before_division = 3000
    fixed_border = 180 #200 
    dropped_border = 200 #300 
    division_strategy = "dscs_shortest_wall_with_equal_surface"

    system_run = True
    remove_cells = True
    system_grab_scene = True
    save_simulation = False 
    load_simulation = False
    spring_standart_radius = 0.2
    mass_standart_radius = 2.0
    visualisation_update_frequency = 2 
    load_starting_meristem= False
    visualisation_system = "surface"

class auxTests1( presentationKatowice4 ):
    """06-10-11-auxTests
    Stable growth with folding for >5000steps.
    """
    visualisation_system = "sphereCells"
    system_grab_scene = False
    cs_surf_max_surface_before_division = 1500
    sphere_visualisation_sphere_size_mult = 26
    simple_pressure_const = 2.0#5.2

class auxTests( presentationKatowice4 ):
    """06-10-11-auxTests
    Fast visualisation for aux simul test.
    """
    visualisation_system = "sphereCells"
    system_grab_scene = True
    cs_surf_max_surface_before_division = 1500
    sphere_visualisation_sphere_size_mult = 26#5
    simple_pressure_const = 4.0#5.2
    
class auxTests1(presentationKatowice4):
    """06-10-11-auxTests1
    Very stable, cylinder.
    < 1000s => ~300
    1000-1900s => 260-240
    1900-2310s => 249-230
    2310-3320   => 240-220
    3320-5110   => 230-210
    looks stable after
    """
    system_grab_scene = True
    visualisation_system = "surface"
    cs_surf_max_surface_before_division = 3000
    meristem_load_scale = 4
    meristem_data = Mdata.ring_hexagon
    system_run = True
    mass_point_size = 20
    mass_standart_radius = 2.0
    visualisation_update_frequency = 2
    simple_pressure_under_primordium_const = 1

class debuggingPressure(presentationKatowice4):
    """06-10-16-debugingPressure

    """
    system_grab_scene = False
    visualisation_system = "sphereCells"
    cs_surf_max_surface_before_division = 5000
    meristem_load_scale = 4
    meristem_data = Mdata.ring_hexagon
    system_run = True
    mass_point_size = 20
    mass_standart_radius = 2.0
    visualisation_update_frequency = 1
    simple_pressure_under_primordium_const = 1
    simple_pressure_const = 1.


class auxTestsStabilityCheck(presentationKatowice4):
    """06-10-11-auxTests1
    Very stable, cylinder.
    < 1000s => ~300
    1000-1900s => 260-240
    1900-2310s => 249-230
    2310-3320   => 240-220
    3320-5110   => 230-210
    looks stable after
    """
    system_grab_scene = False
    visualisation_system = "sphereCells"
    cs_surf_max_surface_before_division = 3000
    meristem_load_scale = 4
    meristem_data = Mdata.ring_hexagon
    system_run = True
    mass_point_size = 20
    mass_standart_radius = 2.0
    visualisation_update_frequency = 2
    simple_pressure_under_primordium_const = 1
    simple_pressure_const = 5.8#5.6
    visualisation_update_frequency = 2
    sphere_visualisation_sphere_size_mult=5
    
    
class auxTestsPeaksTest(presentationKatowice4):
    """06-10-11-pixTest
    stable big tissue. no growth. only active transport.
    """
    system_grab_scene = False
    visualisation_system = "sphereCells"
    cs_surf_max_surface_before_division = 700
    meristem_load_scale = 4
    meristem_data = Mdata.ring_hexagon
    system_run = True
    mass_point_size = 20
    mass_standart_radius = 2.0
    visualisation_update_frequency = 2
    simple_pressure_under_primordium_const = 1
    simple_pressure_const = 5.8#5.6
    visualisation_update_frequency = 2
    sphere_visualisation_sphere_size_mult=5
    tissue_system_forces_simple_pressure = False
    simple_pressure_const = 1.     
    tissue_system_forces_simple_pressure_under_primordium=False
    spring_growth = False

class auxTestsMinGrad(presentationKatowice4):

    system_grab_scene = False
    visualisation_system = "sphereCells"
    visualisation_system = "surface"
    cs_surf_max_surface_before_division = 3000
    meristem_load_scale = 4
    meristem_data = Mdata.ring_hexagon
    system_run = True
    mass_point_size = 20
    mass_standart_radius = 2.0
    simple_pressure_under_primordium_const = 1
    simple_pressure_const = 5.9#5.6
    visualisation_update_frequency = 2
    sphere_visualisation_sphere_size_mult=5

class auxMechPumps1(presentationKatowice4):
    """Used to make 2 movies for J&C presentation in Lyon.
    """
    system_grab_scene =True
    visualisation_system = "sphereCells"
    #visualisation_system = "surface"
    cs_surf_max_surface_before_division = 3000
    meristem_load_scale = 4
    meristem_data = Mdata.ring_hexagon
    system_run = True
    mass_point_size = 20
    mass_standart_radius = 2.0
    simple_pressure_under_primordium_const = 1
    simple_pressure_const = 5.9#5.6
    visualisation_update_frequency = 5
    sphere_visualisation_sphere_size_mult=30#5    
    simple_pressure_under_primordium_const = 1
    tissue_system_forces_simple_pressure_under_primordium=True
    sphere_visualisation_sphere_cell_identity_size_mult=2
    
    auxin_spring_growth_rate=0.5
    system_ambient =0.7
    
class auxInhPhyll1(presentationKatowice4):
    """Used to 06-12-19-inhibitoryFieldOnDynamicCBMeristem-3unWhorledPhyl-dueToSimArt
    with inh rad=        self.min_distance_between_prim=400

    """
    system_grab_scene =True
    visualisation_system = "sphereCells"
    #visualisation_system = "surface"
    cs_surf_max_surface_before_division = 3000
    meristem_load_scale = 4
    meristem_data = Mdata.ring_hexagon
    system_run = True
    mass_point_size = 20
    mass_standart_radius = 2.0
    simple_pressure_under_primordium_const = 1
    simple_pressure_const = 5.9#5.6
    visualisation_update_frequency = 5
    sphere_visualisation_sphere_size_mult=30#5    
    simple_pressure_under_primordium_const = 1
    tissue_system_forces_simple_pressure_under_primordium=True
    sphere_visualisation_sphere_cell_identity_size_mult=2    
    auxin_spring_growth_rate=0.5
    system_ambient =0.7
    
class auxInhPhyll2(presentationKatowice4):
    """Used to 06-12-19-inhibitoryFieldOnDynamicCBMeristem-3unWhorledPhyl-dueToSimArt
    with inh rad=        self.min_distance_between_prim=600

    """
    system_grab_scene =True
    visualisation_system = "sphereCells"
    #visualisation_system = "surface"
    cs_surf_max_surface_before_division = 3000
    meristem_load_scale = 4
    meristem_data = Mdata.ring_hexagon
    system_run = True
    mass_point_size = 20
    mass_standart_radius = 2.0
    simple_pressure_under_primordium_const = 1
    simple_pressure_const = 5.9#5.6
    visualisation_update_frequency = 5
    sphere_visualisation_sphere_size_mult=30#5    
    simple_pressure_under_primordium_const = 1
    tissue_system_forces_simple_pressure_under_primordium=True
    sphere_visualisation_sphere_cell_identity_size_mult=2
    auxin_spring_growth_rate=0.5
    system_ambient =0.7
    
class auxInhPhyll3(presentationKatowice4):
    """Used to 06-12-19-inhibitoryFieldOnDynamicCBMeristem-4-1spiralPhyl-dueToSimArt
    with inh rad=        self.min_distance_between_prim=270

    """
    system_grab_scene =True
    visualisation_system = "sphereCells"
    #visualisation_system = "surface"
    cs_surf_max_surface_before_division = 3000
    meristem_load_scale = 4
    meristem_data = Mdata.ring_hexagon
    system_run = True
    mass_point_size = 20
    mass_standart_radius = 2.0
    simple_pressure_under_primordium_const = 1
    simple_pressure_const = 5.9#5.6
    visualisation_update_frequency = 5
    sphere_visualisation_sphere_size_mult=30#5    
    simple_pressure_under_primordium_const = 1
    tissue_system_forces_simple_pressure_under_primordium=True
    sphere_visualisation_sphere_cell_identity_size_mult=2
    auxin_spring_growth_rate=0.5
    system_ambient =0.7

    
class auxInhPhyll4(presentationKatowice4):
    """Used to 06-12-19-inhibitoryFieldOnDynamicCBMeristem-4-1spiralPhyl-dueToSimArt
    with inh rad=        self.min_distance_between_prim=350

    """
    system_grab_scene =False
    visualisation_system = "sphereCells"
    #visualisation_system = "surface"
    cs_surf_max_surface_before_division = 3000
    meristem_load_scale = 4
    meristem_data = Mdata.ring_hexagon
    system_run = True
    mass_point_size = 20
    mass_standart_radius = 2.0
    simple_pressure_under_primordium_const = 1
    simple_pressure_const = 5.9#5.6
    visualisation_update_frequency = 5
    sphere_visualisation_sphere_size_mult=30#5    
    simple_pressure_under_primordium_const = 1
    tissue_system_forces_simple_pressure_under_primordium=True
    sphere_visualisation_sphere_cell_identity_size_mult=2
    auxin_spring_growth_rate=0.5
    system_ambient =0.7

 
class RadialGrowth(TissueConst):
    system_forces_gravity = False
    system_forces_spring = True
    system_forces_visco = False
    system_forces_uniform_up = False
    system_forces_radial_move = True
    tissue_system_forces_simple_pressure = False
    cs_surf_max_surface_before_division =2000#3000
    meristem_load_scale = 1
    meristem_data = Mdata.ring_hexagon
    visualisation_system = "sphereCells"
    reconstruct_3d_from_slices=False
    system_run = True
    division_strategy = "dscs_shortest_wall_with_geometric_shrinking"
    remove_cells=True
    tissue_system_phys_aux_flow=True
    sphere_visualisation_sphere_cell_identity_size_mult = 2
    
class SphericalGrowth(TissueConst):
    system_forces_gravity = False
    system_forces_spring = True
    system_forces_visco = False
    system_forces_uniform_up = False
    system_forces_radial_move = True
    system_forces_spherical_move = True
    tissue_system_forces_simple_pressure = False
    cs_surf_max_surface_before_division = 100
    meristem_load_scale = 1
    meristem_data = Mdata.ring_hexagon
    visualisation_system = "surface"
    reconstruct_3d_from_slices=False
    system_run = True
    division_strategy = "dscs_shortest_wall_with_geometric_shrinking"
    remove_cells=True
    tissue_system_phys_aux_flow=False
    
class RadialGrowthCanalisationHypo(TissueConst):
    system_forces_gravity = False
    system_forces_spring = True
    system_forces_visco = False
    system_forces_uniform_up = False
    system_forces_radial_move = True
    tissue_system_forces_simple_pressure = False
    cs_surf_max_surface_before_division =5000
    meristem_load_scale = 1
    meristem_data = Mdata.ring_hexagon
    visualisation_system = "surface"
    #visualisation_system ="sphereCells"
    reconstruct_3d_from_slices=False
    system_run = True
    division_strategy = "dscs_shortest_wall_with_geometric_shrinking"
    remove_cells=True
    tissue_system_phys_aux_flow=True
    sphere_visualisation_sphere_cell_identity_size_mult = 2
    save_simulation=True
    system_grab_scene =True
    visualisation_update_frequency = 1
    pickled_WalledTissue_data_folder = "/media/IOMEGA_HDD/mersim-output/07-03-20-canalisation2D/"
    sphere_visualisation_sphere_cell_identity_size_mult = 3
    system_ambient =0.7
    #spring_standart_radius = 1.2
    mass_standart_radius = 2


class PlantGLTissueTest(TissueConst):
    system_forces_gravity = False
    system_forces_spring = True
    system_forces_visco = False
    system_forces_uniform_up = False
    system_forces_radial_move = True
    tissue_system_forces_simple_pressure = False
    cs_surf_max_surface_before_division =5000
    meristem_load_scale = 1
    meristem_data = Mdata.full_meristem_f_n
    visualisation_system = "empty"
    reconstruct_3d_from_slices=True
    system_run = False
    division_strategy = "dscs_shortest_wall_with_geometric_shrinking"
    remove_cells=True
    tissue_system_phys_aux_flow=True
    sphere_visualisation_sphere_cell_identity_size_mult = 2
    tissue_system_phys_mark_cell_identities=False
    tissue_system_phys_aux_flow=False


class WalledTissueTest( TissueConst ):
    #meristem_data =  Mdata.two_cells #
    meristem_data =  Mdata.full_meristem_f_n


class WalledTissueGrowthAndDivisionTest( TissueConst ):
    #meristem_data =  Mdata.two_cells #
    meristem_data =  Mdata.full_meristem_f_n
    cs_surf_max_surface_before_division=0.08

class WalledTissueCanalisationExp1( TissueConst ):
    #meristem_data =  Mdata.two_cells #
    #meristem_data =  Mdata.full_meristem_f_n
    cs_surf_max_surface_before_division=0.1#0.05
    
    PZ_absolute_dist=0.7
    
    cell_properties ={
        "IC": False,
        "PZ": False,
        "CZ": False,
        "NZ": False,
        "PrZ": 0,
        "PrC": 0,
        "auxin_level": 0,
        "PrC_stub": 0,
        "PrZ_stub": 0
    }
    """#: Used to initialise cell properties
    """
    
    tissue_properties ={
        "primordiums": {},
        "primordium_removal_history": {}
    }
    """#: Used to initialise tissue properties
    """

    
    cell_edge_properties={ }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """
    
    wv_properties={ }
    
    wv_edge_properties={
        "pin_level": [1,1] }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """

class WalledTissueReactionDiffusion1( TissueConst ):
    #meristem_data =  Mdata.two_cells #
    #meristem_data =  Mdata.full_meristem_f_n
    cs_surf_max_surface_before_division=0.05#0.1
    
    PZ_absolute_dist=0.7
    
    cell_properties ={
        "IC": False,
        "PZ": False,
        "CZ": False,
        "NZ": False,
        "PrZ": 0,
        "PrC": 0,
        "auxin_level": 0,
        "inh": 0
    }
    """#: Used to initialise cell properties
    """
    
    tissue_properties ={
        "primordiums": {},
        "prim2time": {}
    }
    """#: Used to initialise tissue properties
    """

    
    cell_edge_properties={ }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """
    
    wv_properties={ }
    
    wv_edge_properties={
        "pin_level": [1,1] }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """


class WalledTissueLongitudinalCutExp1( TissueConst ):
    #meristem_data =  Mdata.two_cells #
    #meristem_data =  Mdata.full_meristem_f_n
    cs_surf_max_surface_before_division=0.05#0.1
    
    PZ_absolute_dist=0.7
    
    cell_properties ={
        "IC": False,
        "PZ": False,
        "CZ": False,
        "NZ": False,
        "PrZ": 0,
        "PrC": 0,
        "auxin_level": 0,
        "inh": 0,
        "innerSink": False
    }
    """#: Used to initialise cell properties
    """
    
    tissue_properties ={
        "primordiums": {},
        "prim2time": {}
    }
    """#: Used to initialise tissue properties
    """

    
    cell_edge_properties={ }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """
    
    wv_properties={ }
    
    wv_edge_properties={
        "pin_level": [1,1] }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """

class WalledTissuePinMapsExp1( TissueConst ):
    #meristem_data =  Mdata.two_cells #
    #meristem_data =  Mdata.full_meristem_f_n
    cs_surf_max_surface_before_division=0.05#0.1
    
    PZ_absolute_dist=0.7
    
    cell_properties ={
        "IC": False,
        "PZ": False,
        "CZ": False,
        "NZ": False,
        "PrZ": 0,
        "PrC": 0,
        "auxin_level": 0,
        "inh": 0,
        "innerSink": False
    }
    """#: Used to initialise cell properties
    """
    
    tissue_properties ={
        "primordiums": {},
        "prim2time": {}
    }
    """#: Used to initialise tissue properties
    """

    
    cell_edge_properties={ }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """
    
    wv_properties={ }
    
    wv_edge_properties={
        "pin_level": [1,1] }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """

    meristem_data = Mdata.top_meristem_3c

class WalledTissuePinMapsExp2( TissueConst ):
    #meristem_data =  Mdata.two_cells #
    #meristem_data =  Mdata.full_meristem_f_n
    cs_surf_max_surface_before_division=0.05#0.1
    
    PZ_absolute_dist=0.7
    
    cell_properties ={
        "IC": False,
        "PZ": False,
        "CZ": False,
        "NZ": False,
        "PrZ": 0,
        "PrC": 0,
        "auxin_level": 0,
        "inh": 0,
        "innerSink": False
    }
    """#: Used to initialise cell properties
    """
    
    tissue_properties ={
        "primordiums": {},
        "prim2time": {}
    }
    """#: Used to initialise tissue properties
    """

    
    cell_edge_properties={ }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """
    
    wv_properties={ }
    
    wv_edge_properties={
        "pin_level": [1,1] }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """

    meristem_data = Mdata.m_07_07_05_PINwithImmunolab
    
    

class WalledTissueVisuTest( TissueConst ):
    #meristem_data =  Mdata.two_cells #
    #meristem_data =  Mdata.full_meristem_f_n
    cs_surf_max_surface_before_division=0.05#0.1
    
    PZ_absolute_dist=0.7
    
    cell_properties ={
        "IC": False,
        "PZ": False,
        "CZ": False,
        "NZ": False,
        "PrZ": 0,
        "PrC": 0,
        "auxin_level": 0,
        "inh": 0,
        "innerSink": False
    }
    """#: Used to initialise cell properties
    """
    
    tissue_properties ={
        "primordiums": {},
        "prim2time": {}
    }
    """#: Used to initialise tissue properties
    """

    
    cell_edge_properties={ }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """
    
    wv_properties={ }
    
    wv_edge_properties={
        "pin_level": [1,1] }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """

    meristem_data = Mdata.two_cells

class WalledTissuePinMapsExp3( TissueConst ):
    #meristem_data =  Mdata.two_cells #
    #meristem_data =  Mdata.full_meristem_f_n
    cs_surf_max_surface_before_division=0.05#0.1
    
    PZ_absolute_dist=0.7
    
    cell_properties ={
        "IC": False,
        "PZ": False,
        "CZ": False,
        "NZ": False,
        "PrZ": 0,
        "PrC": 0,
        "auxin_level": 0,
        "inh": 0,
        "innerSink": False,
        "BC": 0
    }
    """#: Used to initialise cell properties
    """
    
    tissue_properties ={
        "primordiums": {},
        "prim2time": {}
    }
    """#: Used to initialise tissue properties
    """

    
    cell_edge_properties={ }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """
    
    wv_properties={ }
    
    wv_edge_properties={
        "pin_level": [1,1] }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """

    meristem_data = Mdata.m_07_07_05_PINwithImmunolab
    
class WalledTissueDynamicCanalisation( TissueConst ):
    #meristem_data =  Mdata.two_cells #
    #meristem_data =  Mdata.full_meristem_f_n
    cs_surf_max_surface_before_division=0.045#0.1
    
    PZ_absolute_dist=0.7
    
    cell_properties ={
        "IC": False,
        "PZ": False,
        "CZ": False,
        "NZ": False,
        "PrZ": 0,
        "PrC": 0,
        "auxin_level": 0,
        "inh": 0,
        "innerSink": False
    }
    """#: Used to initialise cell properties
    """
    
    tissue_properties ={
        "primordiums": {},
        "prim2time": {}
    }
    """#: Used to initialise tissue properties
    """

    
    cell_edge_properties={ }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """
    
    wv_properties={ }
    
    wv_edge_properties={
        "pin_level": [5e-05,5e-05] }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """

    meristem_data = Mdata.top_meristem_3c


class WalledTissueDynamicCanalisation2( TissueConst ):
    """08-02-14-can2d,dynamic
    """
    #meristem_data =  Mdata.two_cells #
    #meristem_data =  Mdata.full_meristem_f_n
    cs_surf_max_surface_before_division=0.030#0.1
    
    PZ_absolute_dist=0.6
    
    cell_properties ={
        "IC": False,
        "PZ": False,
        "CZ": False,
        "NZ": False,
        "PrZ": 0,
        "PrC": 0,
        "auxin_level": 0,
        "inh": 0,
        "innerSink": False,
        "PrC_stub": 0,
        "PrZ_stub": 0
    }
    """#: Used to initialise cell properties
    """
    
    tissue_properties ={
        "primordiums": {},
        "prim2time": {},
        "prim2removal_time": {}
    }
    """#: Used to initialise tissue properties
    """

    
    cell_edge_properties={ }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """
    
    wv_properties={ }
    
    wv_edge_properties={
        "pin_level": [0.1,0.1] }
    """#: The pin_level codes the pin quantity in cell wall. The [0] value codes the quantity in the
    direction *coherent* with valid cell_edge_id.
    """

    meristem_data = Mdata.top_meristem_3c
