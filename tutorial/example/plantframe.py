from openalea.deploy.shared_data import shared_data
import vplants.tutorial

from openalea.mtg import *
from openalea.mtg import aml

data = shared_data(vplants.tutorial)/'PlantFrame'

#################################
print "MTG : monopodial_plant.mtg"
#################################

g1 = aml.MTG(data/"monopodial_plant.mtg")

################
print "Scale Option"
################
#
# Quest: Visualize the plant contained in the MTG file using the 
# following functions:
# PlantFrame, MTGRoot(), Plot
#
#----------------------------------

f=PlantFrame(MTGRoot())
Plot(f)

#----------------------------------
#
#Quest: At which scale is the plant visualized ?
#
#----------
#
# scale 1
#
#----------
#
#Quest: Visualize the same plant at scale 2, 3 and 4
#
#----------------------------------

f2=PlantFrame(MTGRoot(),Scale=2)
Plot(f2)

f3=PlantFrame(MTGRoot(),Scale=3)
Plot(f3)

f4=PlantFrame(MTGRoot(),Scale=4)
Plot(f4)

#----------------------------------
#
####################
print "Translate Option"
####################
#
#Quest: Translate the plant representation at scale 4 to point [10.0,15.0,0.0]
#
#----------------------------------

f1=PlantFrame(MTGRoot(),Scale=4, Translate=[10.0,15.0,0.0])
Plot(f1)

##########################
print "Insertion angle options"
##########################
#
#Quest: Change the default insertion angle of branches to 90 deg 
#
#----------------------------------

def angle(x): return 90

f1=PlantFrame(MTGRoot(),Alpha=angle,Scale=4)
Plot(f1)

###################
print "Diameter options"
###################
#
#Quest: Use the feature "diam" available in the MTG file to give a top 
#diameter to plant entities in the MTG representation at scale 4
#
#----------------------------------

def dia(x): return Feature(x,"diam")

# Applies a within-scale constraint to compute the
# bottom diameter of the branch 

f1=PlantFrame(MTGRoot(),Scale=4,TopDiameter=dia)
Plot(f1)

#----------------------------------
#
#Quest: At the same scale, give an explicit value to bottom diameters
# which is twice as large as the measured diameter.
#
#----------------------------------

def dia2(x):
      d = dia(x)
      if d == Undef: return d
      else: return 2*dia(x)

f1=PlantFrame(MTGRoot(),Scale=4,TopDiameter=dia, BottomDiameter=dia2)
Plot(f1)

#----------------------------------
#
# Quest: Change the above diameter function so that only the bottom diameter 
# of branches is explicitly defined (for example 1.5)
#
#----------------------------------

# Controls the bottom diameter of branches only
def dia3(x):
      if Rank(x) == 0 and Order(x) == 1: return 1.5
      else: return Undef

f1=PlantFrame(MTGRoot(),Scale=4,TopDiameter=dia, BottomDiameter=dia3)
Plot(f1)

#######################################
print "Definition of the visualized branching system"
#######################################
#
#Quest: Find the first entity at scale 3 of the first branch of the plant
# (from the bottom).
#Plot the geometric representation of the branching system 
#corresponding to this entity at scale 4.  
#
#----------------------------------

def is_branch_basis(x):
      if Order(x) == 1 and Rank(x) == 0: return True
      else: return False

bases_3 = [ x for x in VtxList(Scale=3) if is_branch_basis(x) == True]


f5 = PlantFrame(bases_3[0], Scale=4)
Plot(f5)

#----------------------------------
#
#Quest: Plot geometric representation at scale 4 of the branching
#system corresponding to the first branch of the plant
#
#----------------------------------

bases_4 = [ x for x in VtxList(Scale=4) if is_branch_basis(x) == True ]
# or
base_4 = filter(is_branch_basis, VtxList(Scale=4))

f6 = PlantFrame(bases_4[0], Scale=4)
Plot(f6)

#######################################
print "Option TrunkDist"
#######################################
#
#Quest: Create an array containing all the branches of the plant.
#Plot the geometric representations at scale 4, of all these branches in the
#same plot, as if they were independent branching systems.
#
#----------------------------------

f7 = PlantFrame(bases_4, Scale=4, TrunkDist=20)
Plot(f7)

#################################
print "MTG : length.mtg"
#################################

g1 = MTG(examples_dir + "length.mtg")

########################
print "Length option"
########################
#
#Quest: Plot the MTG at scale 3 and explain the geometric type,
#dimensions, position and orientation of the different constituents using
#information about Dressing Data in the AMAPmod reference manual.
#
#What is the default geometric model ?
#What are the default length and diameters ? 
#What is the default insertion angle ?
#
#----------------------------------
#
# Default symbol is tapered cylinder
# Default length is 10, default diameters are 1 
# Default insertion angle is 30 degrees

f1 = PlantFrame(MTGRoot(),Scale=3)
Plot(f1)

#----------------------------------
#
#Quest: Change the default length of constituents according to the
#following rules:
#- constituents from the trunk should have a length decrease 
#  as a power 3 of their rank
#- constituents from the branches should have a constant value
#different from the default one
#
#----------------------------------
#
# the default length is 10
# A polynomialy decreasing function of the rank

def len(x):
      if Order(x) == 0:return ((0.0001*Rank(x))**3)+0.3
      else: return 2.0

f1 = PlantFrame(MTGRoot(),Scale=3, Length=len)
Plot(f1)

#----------------------------------
#
#Quest: Change the default length of constituents according to the
#following rule:
#
#- the length of a constituent should be proportional to the difference
#of index with respect to its predecessor. 
#
#(This would be the case for instance when indexes are measures of the
#length to this node from the bottom of the branch)
#
#----------------------------------

def len(x):
      f = Father(x)
      if f != Undef:
            return abs(Index(f)-Index(x))
      else: return Index(x)

def color1(x):
      if (Index(Father(x))-Index(x)) < 0:
            return Green
      else: return Red

f1 = PlantFrame(MTGRoot(),Scale=3, Length=len)
Plot(f1, Color=color1)

###############################
print "origin.mtg"
###############################

g1 = MTG(examples_dir +"origin.mtg")

#----------------------------------
#
#Quest: Plot a plant representation showing vertices that have 3D
#coordinates in the MTG in red (use origine.drf).
#
#----------------------------------

dr = DressingData(examples_dir + "origin.drf")

def color_measured(x):
      if Feature(x,"XX") == Undef:return Green
      else: return Red

f1 = PlantFrame(MTGRoot(),Scale=3,DressingData=dr)

Plot(f1, Color=color_measured)

#----------------------------------
#
#Quest: Plot the same representation in which the origin of the first
#plant component has been modified to [0.0,100.0,0.0].
#
#----------------------------------

f2 = PlantFrame(MTGRoot(),Scale=3,
                Origin=[0.0,100.0,0.0],
                DressingData=dr)

Plot(f2, Color=color_measured)

###############################
print "MTG : coordinates_with_no_value.mtg"
###############################

g1 = MTG(examples_dir + "coordinates_with_no_value.mtg")

#----------------------------------
#
#Quest: Plot a plant representation of this purely topological MTG,
#with a diameter of 10 units.
#
#----------------------------------

def diam(x): return 10

f1 = PlantFrame(MTGRoot(),TopDiameter=diam, Scale=3)
Plot(f1)

###############################
print "MTG : coordinates.mtg"
###############################

g1 = MTG(examples_dir + "coordinates.mtg")

#----------------------------------
#
#Quest: Plot a plant representation of this MTG (having a topology
#identical to that of "coordinates_with_no_value.mtg" ) showing
#vertices that have 3D coordinates in the MTG in red.
#
#----------------------------------

def color_measured(x):
      if Feature(x, "XX") != Undef: return Red
      else: return Green

f1 = PlantFrame(MTGRoot(),Scale=3)
Plot(f1, Color=color_measured)

########################
print "User-defined length"
########################
#
#Quest: Change the length of vertex 46 only
#
# Overridding default behaviour using a user-defined function
# Does not work on entities whose length is interpolated (e.g. 46)
#
#----------------------------------

def len(x):
      if x == 46: return 50
      else: return Undef

def color_measured(x):
      if Feature(x, "XX") != Undef: return Red
      else: return Green

def color_measured2(x):
      if x == 51: return Black
      else: return color_measured(x) 

f1 = PlantFrame(MTGRoot(),Scale=3, Length=len)
Plot(f1, Color=color_measured2)

#----------------------------------
#
#Quest: Change the length of vertex 51 only. What can be remarked ?
#
#----------------------------------

def len(_x):
      if x == 51: return 50
      else: return Undef

f1 = PlantFrame(MTGRoot(),Scale=3, Length=len)
Plot(f1, Color=color_measured2)

# conclusion:
# the length of an entity can be changed only if the entity
# length was not implicitly defined by interpolation

########################
print "LengthAlgo option"
########################
#
#Quest: Use a plantframe option that enables you
#to compute automatically the length of entities
#between two measured entities as the index difference
#of these entities.
#
#----------------------------------
# Automatic length between two measurements
#
# consecutive index difference is used to compute the length of a vertex

f2 = PlantFrame(MTGRoot(),Scale=3,
                LengthAlgo="UseIndexes")
Plot(f2, Color=color_measured)

#----------------------------------
#
#Quest: Take into account that the index of entities represent
# the distance from the top of the entity to the bottom of the branch
#
#----------------------------------

f3 = PlantFrame(MTGRoot(),Scale=3,
                LengthAlgo="UseAxisIndexes")
Plot(f3)

#----------------------------------
#
#Quest: Show the difference between the two representations
#
#----------------------------------

def difference_two_pf(x):
      if abs(Length(f3,x)-Length(f2,x))>0.0001: return Red
      else: return Black

Plot(f3, Color=difference_two_pf)

###############################
print "MTG : leaf_axis.mtg"
###############################

g1 = MTG(examples_dir + "leaf_axis.mtg")

####################
print "EulerAngles option"
####################
#
#Quest: Use the following functions to plot a plant frame using Euler
#angles only for leaves (symbol F in the MTG)
#

def xx(x): return 0.0

def yy(x): return 0.0

def zz(x):
      if Class(x) != 'F': return ToReal(Rank(x))
      else: return Undef

def aa(x): return 0.0

def bb(x): return 0.0

def cc(x): return 0.0

def leaf_len(x):
      if Class(x) == 'F': return 5
      else: return Undef

def leaf_dia(x):
      if Class(x) == 'F': return 5
      else: return Undef

#
#---------------------------------

def eulerf(x):
      if Class(x) == 'F':
            return True
      else: return False

dr = DressingData(examples_dir + "leaf_axis.drf")
f1 = PlantFrame(MTGRoot(),Scale=3, 
                XX=xx, 
                YY=yy, 
                ZZ=zz, 
                Length= leaf_len, 
                TopDiameter=leaf_dia,
                BottomDiameter=leaf_dia,
                EulerAngles=eulerf,AA=aa,BB=bb,CC=cc, 
                DressingData=dr)
Plot(f1)

#---------------------------------
#
#Quest: Modify these functions to control 
#
#1. plant phyllotaxy
#2. insertion angles of leaves
#3. rolling angle of leaves
#
#---------------------------------

def aa(x):
      if Father(x) != Undef: return Rank(Father(x))*30.0
      else: return 0.0

def bb(x):
      if Father(x) != Undef: return -Rank(Father(x))*5.0
      else: return 0.0

def cc(x):
      if Father(x) != Undef: return Rank(Father(x))*10.0
      else: return 0.0

###############################
print "sympodial_plant.mtg"
###############################
      
g1 = MTG(examples_dir + "sympodial_plant.mtg")

###########################
print "Mode Option"
###########################
#
#Quest: This plant is sympodial : apparent axes (at scale 2) are
#complex components that contain several botanical axes (at scale
#3). Plot a plant representation at scale 3 that reflects the
#organisation of apparent axes.
#
#----------------------------------

f1=PlantFrame(MTGRoot(),Scale=3)
Plot(f1)

f1=PlantFrame(MTGRoot(),Scale=3,Mode="Sympodial")
Plot(f1)

###############################
print "MTG : wij10.mtg"
###############################

g = MTG(databases_dir + "wij10.mtg")

###########################
print "Dressing Data"
###########################
#
#Quest: find the plant with index 10 and visualize it at scale 4
#
#----------------------------------

plants = VtxList(Scale=1)
def plant(i):
      for v in plants:
            if Index(v)==i: return v

p10 = plant(10)
f4 = PlantFrame(p10, Scale=4)
Plot(f4)

#----------------------------------
#
#Quest: Load the dressing data contained in the dressing file wij10.drf
#(in the examples directory) and compute a new PlantFrame using this data.
#
#----------------------------------

dr1 = DressingData(examples_dir + "wij10.drf") 
f5 = PlantFrame(p10, Scale=4, DressingData=dr1)
Plot(f5)

#---------------------------------- 
#
#Quest: Change the default diameter and length default values of entities B, C, E
#
#Quest: Copy the dressing file in your current directory. Use this new
#dressing file to represent plant entities at scale 4 by different
#geometric models.
#
#---------------------------------- 
# Linux> cp examples_dir/"wij10.drf" my_wij10.drf
# or in python>
Copy(examples_dir+"wij10.drf","my_wij10.drf")

# In this new dressing file
#
# SMBModel node = nentn103
# or
# SMBModel node = pommecyl
#
#(try several geometric models) then
#
#back to python> :

dr2 = DressingData("my_wij10.drf") 
f5 = PlantFrame(p10, Scale=4, DressingData=dr2)
Plot(f5)

#---------------------------------- 
#
#Quest: To distinguish entities that correspond to fruits at scale 4 it
#is necessary to test their complex and to check whether they are
#fruiting growth units (Class I). Define a function h(x) that
#associates entities from scale 4 that correspond to fruits with a new
#Class W.
#
#----------------------------------

def h(x):
      if Class(Complex(x)) == 'I': return 'W'
      else: return Undef

#----------------------------------
#
#Quest: Check what type of basic geometric model is used to represent
#entities of type W in the dressing file. Plot a geometric
#representation of the PlantFrame that makes use of this new geometric
#model
#
#----------------------------------

f5 = PlantFrame(p10, Scale=4, DressingData=dr1)
Plot(f5, Class=h)

#----------------------------------
#
#Quest: Resize each fruit in the plant representation by scaling their
#bounding box up to 50x50x50
#
#----------------------------------

def diam(x):
      if h(x) == 'W': return 50
      else: return Undef

f5 = PlantFrame(p10, Scale=4, DressingData=dr1, TopDiameter=diam, BottomDiameter=diam, Length=diam)
Plot(f5, Class=h)

#----------------------------------
#
#Quest: Change function the way the diameter of fruit is computed so as
# to suppress the effect of interpolation on the basis of fruits 
#
#----------------------------------

def diam(x):
      if h(x) == 'W': return 50
      elif h(Successor(x)) == 'W': return 10
      else: return Undef
      
f6 = PlantFrame(p10, Scale=4, DressingData=dr1, TopDiameter=diam, BottomDiameter=diam, Length=diam)
Plot(f6, Class=h)

######################################################################
print "Coloring plant representation to explore architecture"
######################################################################
#
#Quest: Use colors to distinguish entities with different orders at
# scale 4.
#
#----------------------------------

dict_color = {
      0 : Green ,
      1 : Red,
      2 : Blue,
      3 : Yellow,
      4 : Violet }

def color_order(v):
      return dict_color.get(Order(v),White)

Plot(f6, Color = color_order, Class=h)

#----------------------------------
#
#Quest: Use colors to distinguish entities with different types
#(Classes) at scale 4
#
#----------------------------------

def color_class(x):
      if Class(Complex(x, Scale=3)) == 'I': return Violet
      else:
            dict_class_color = {
                  'B' : Green,
                  'C' : Red,
                  'E' : Black }
            return dict_class_color.get(Class(x),Yellow)

Plot(f6, Color = color_class, Class = h )

#----------------------------------
#
#Quest: Show all entities that are not part of the trunk
#
#----------------------------------

def select_order(x):
      if (Order(x) == 0): return False
      else: return True

Plot(f6, Show=select_order, Class=h)

#----------------------------------
#
#Quest: Show only entities belonging to a 90 annual shoot. (The annual
#shoot year is represented by the index of entities at scale 2)
#
#----------------------------------

def select_order(x):
      if (Index(Complex(x, Scale=2)) == 90): return True
      else: return False

Plot(f6, Show=select_order, Class=h)

#----------------------------------
#
#Quest: Plot a colored map of the distances
# (in number of internodes from the basis of the plant leading to a given entity) 
#
#-------------------

def interpol_fun(x): return Height(x)

Plot(f6, Interpol=interpol_fun)

###################################################
#
##  Extracting informations from digitized trees
#
print "A digitized Apple Tree"
print "Database credits: E. Costes and H. Sinoquet"
#
###################################################

examples_dir = AMAPMOD_DIR + "/examples/MTG/PlantFrame/"
databases_dir = AMAPMOD_DIR + "/databases/MTGFiles/AppleTree/"

###############################
print "MTG : agraf.mtg"
###############################

g  = MTG(databases_dir + "agraf.mtg")

#-------------------
#   
#Quest: Look at the definition of this digitized tree,
#load it and visualize the digitized tree at scale 3 using
#the following dressing file:
#

dr1 = DressingData(examples_dir + "agraf.drf")

#
#-------------------

f1 = PlantFrame(MTGRoot(), Scale=3, DressingData=dr1)
Plot(f1)

#-------------------
#
#Quest: Color in red entities whose top-point were digitized.
#
#-------------------

def color_measured(x):
      if Feature(x,"XX") != Undef: return Red
      else: return Blue

Plot(f1, Color=color_measured)

#-------------------
#
#Quest: Find the range of diameters observed on all plant entities and
#divide it into 5 classes. Color each entity according to its diameter
#class.
#
#-------------------

def diam(x): return ToInt(TopDiameter(f1, x))

diameters = [ diam(v) for v in VtxList(Scale=3)]

max(diameters)
min(diameters)

dict_diam_col = {
      0: Red,
      1: Green,
      2: Violet,
      3: LightBlue,
      4: Blue }

def color_diam(x):
   return dict_diam_col.get(diam(x)/10,Black)

Plot(f1, Color=color_diam)

#-------------------
#
#Quest: compute the wood volume of the plant (volume of a cone frustum
#with base diam b, top diam t and height h:
#
#hint: vol = Pi*h*(b^2+tb+t^2)/12
#
#-------------------

def height(x): return Length(f1,x)

def topd(x): return TopDiameter(f1,x)

def botd(x): return BottomDiameter(f1,x)

def cone_frust_vol(x):
      if(height(x)==Undef or topd(x)==Undef or botd(x)==Undef): return 0
      else: return Pi*height(x)*(topd(x)**2+topd(x)*botd(x)+botd(x)**2)/12

# Computing the volume of the tree
# (in mm3)

volume = 0
for x in Components(1, Scale=3): volume += cone_frust_vol(x)

print "Volume = " + ToString(volume)

#-------------------
#
#Quest: compute the distribution of azimuth of the first node of the axes
#borne by the trunk
#
#-------------------

axes = [ x for x in VtxList(Scale=3) if Order(x)==1 and Rank(x) == 0 ]

setmode(1)
azimuth_array = [ EulerAngles(f1,v)[0] for v in axes ]

def toDeg(x): return (180/Pi) * x 

azimuth_dist = [ ToInt(toDeg(Pi+r)/10) for r in azimuth_array ]

###################################
#
print "Digitized Walnut Tree (20 years)"
print "Database credits: H. Sinoquet"
#
###################################

###############################
print "MTG : boutdenoylum2.mtg"
###############################

# g2 = MTG(amapmod_dir + "databases/MTGFiles/WalnutTree/noylum2.mtg")
g2 = MTG(AMAPMOD_DIR + "/databases/MTGFiles/WalnutTree/boutdenoylum2.mtg")

#-------------------
#
#Quest: Look at the definition of this digitized tree,
#load it and visualize the digitized tree at scale 3 using
#the following function for the bottom diameters of entities 
#and dressing file:
#

def bot_dia(x):
      if Rank(x) == 0: return Feature(Complex(x), "TopDia")
      else: return Undef

dr1 = DressingData(examples_dir + "walnut.drf")

#
#-------------------

f2 = PlantFrame(MTGRoot(),Scale=3, BottomDiameter=bot_dia, DressingData=dr1)
Plot(f2)

#-------------------
#
#Quest: plot the histogram of entity length.
#
#-------------------

scale3_entities = VtxList(Scale=3)

length_set = [ Length(f2,v) for v in scale3_entities ]
length_set_int = [  ToInt(e) for e in length_set ]

Plot(Histogram(length_set_int))

#-------------------
#
#Quest: find all entities whose length is greater than 3cm
#
#-------------------

length_set_30 = [ x for x in length_set if x > 30 ]

#-------------------
#
#Quest: Plot in Green the set of entities whose top-point in the box
#defined by its diagonal points: [-100.0,-100.0,200.0], [0.0,0.0,400.0]
#
#-------------------

boxpt1 = [-100.0,-100.0,200.0]
boxpt2 = [0.0,0.0,400.0]

def xx(v): return Coord(f2, v)[0]

def yy(v): return Coord(f2, v)[1]

def zz(v): return Coord(f2, v)[2]

def test_inbox(x,y,z):
      if ((x >= boxpt1[0] and x <= boxpt2[0]) and
      (y >= boxpt1[1] and y <= boxpt2[1]) and
      (z >= boxpt1[2] and z <= boxpt2[2])) : return True
      else: return False

def color_box(v):
      if test_inbox(xx(v),yy(v),zz(v)): return Green
      else: return Black

Plot(f2, Color=color_box)

#-------------------

