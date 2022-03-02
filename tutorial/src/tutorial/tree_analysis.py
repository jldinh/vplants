# -*- coding: utf-8 -*-

"""
Analysis of the Aleppo Pine dataset at Annual Shoot (AS) scale
Quantification of branch synchronism
using hidden Markov out tree with independent children for AS labelling
and tree matching
"""

#-----------------------------------------------------------------------
#
# Definition of the default paths
#
#-----------------------------------------------------------------------

# import os
import sys

from openalea.deploy.shared_data import get_shared_data_path

import vplants.tutorial
import openalea.mtg.aml as mtg

import openalea.tree_statistic.trees as trees
import openalea.tree_statistic.hmt as hmt, numpy

import openalea.stat_tool as stat_tool
import openalea.stat_tool.plot

from openalea.mtg import turtle
import openalea.plantgl.all as pgl

from random import randint

# data
datapath = get_shared_data_path(vplants.tutorial)/"TreeAnalysis"
data_filepath = str(datapath / "aleppo_pines.mtg")
dressing_filepath = str(datapath / "aleppo_pines.drf")
model_filepath = str(datapath / "aleppo_pines.hmt")
distance_filepath = str(datapath / "aleppo_pines_distance.a")


import openalea.aml as amlPy 
from amlPy import *
amlPy.setmode(1)

openalea.stat_tool.plot.PLOTTER = openalea.stat_tool.plot.gnuplot()

#-----------------------------------------------------------------------
#
# Colour functions
#
#-----------------------------------------------------------------------

black = [0, 0, 0]
green = [0, 100, 0]
red = [100, 0, 0]
blue = [0, 0, 100]
yellow = [100, 100, 0]
pink = [100, 0, 100]
cyan = [0, 100, 100]
# grey = [150, 150, 150]#, 200, 200, 200]
# lgrey=[220, 220, 220]# 100, 100, 100]
white = [100, 100, 100,]# 255, 255, 255]
violet = [90, 0, 10]#, 200, 200, 200]
orange = [10, 90, 0]#, 200, 200, 200]
sgreen = [0,10,90]
tomato = [1, 150, 150]
yuck = [150, 150, 0]

def colour_state(s):
    """Correspondance between states and colours"""
    if (s == 0):
        return red
    elif (s == 1):
        return green
    elif (s == 2):
        return blue
    elif (s == 3):
        return pink
    elif (s == 4):
        return cyan
    elif (s == 5):
        return yellow
    elif (s == 6):
        return violet
    elif (s == 7):
        return orange
    elif (s == 8):
        return tomato
    elif (s == 9):
        return sgreen
    else:
        return yuck

#-----------------------------------------------------------------------
#
# Preprocessing and tree building
#
#-----------------------------------------------------------------------

s = 3 # AS scale

# attributes: branching order and intensity, presence of male cones, of female cones,
# polycyclism, diameter and state of the apex

# definition of the attributes

def NbBranches(g):
    """Number of branches at GU scale"""
    res = amlPy.Feature(g, "nbramif")
    if res is None:
        return 0
    else:
        return res

def BrIntensity(x):
    """Number of branches at AS scale"""
    comp = amlPy.Components(x)
    res = [NbBranches(g) for g in comp]
    # just for control
    sons = amlPy.Sons(x)
    resc = max(len(sons)-1, 0)
    # should use amlPy.Sons(g, EdgeType='+') instead
    res = sum(res)
    return resc

def GULength(x, type):
    """Length of GU of a given type
    (l_sterile, l_male or l_leave)"""
    res = amlPy.Feature(x, type)
    if res is None:
        return 0
    else:
        return int(round(res))

def Length(x):
    """Length of AS"""
    # AS is decomposed of sterile, male
    # and leaf parts (sum lengths of three parts)
    comp = amlPy.Components(x)
    sterile = [GULength(g, "l_sterile") for g in comp]
    male = [GULength(g, "l_male") for g in comp]
    leave = [GULength(g, "l_leave") for g in comp]
    length = [sterile[i] + male[i] + leave[i] for i in range(len(sterile))]
    if sum(length) == 0:
        for g in range(len(sterile)):
            if length[g] == 0:
                length[g] = amlPy.Feature(comp[g], "length")
                if length[g] is None:
                    return 0
        return sum(length)
    else:
        return sum(length)

def GUNbFCones(g):
    """Number of female cones at GU scale"""
    res = amlPy.Feature(g, "nbcones")
    if res is None:
        return 0
    else:
        return res

def FCones(x):
    """Female cones (boolean) at AS scale"""
    comp = amlPy.Components(x)
    res = [GUNbFCones(g) for g in comp]
    if sum(res) > 0:
        return 1
    else:
        return 0

def GUNbMCones(g):
    """Number of male cones at GU scale"""
    res = amlPy.Feature(g, "l_male")
    if res is None:
        return 0
    else:
        return res

def MCones(x):
    """Male cones (boolean) at AS scale"""
    comp = amlPy.Components(x)
    res = [GUNbMCones(g) for g in comp]
    if sum(res) > 0:
        return 1
    else:
        return 0

def Polycyclism(x):
    """Number of growth cycles"""
    res = amlPy.Components(x)
    return len(res)

def Diameter(x):
    """diameter at AS scale (at middle of GUs) : max GU diameter"""
    comp = amlPy.Components(x)
    res = [10 * int(round(amlPy.Feature(g, "diam"))) for g in comp]
    if len(res) == 0:
        return 0
    else:
        return int(round(max(res)))

def StApex(x):
    """State of the apex
    0 == Alive
    1 == Dead
    2 == Broken"""
    res = amlPy.Feature(x, "state")
    if res == 'V':
        return 0
    elif res == 'M':
        return 1
    elif res == 'C':
        return 2
    else:
        return 0

def AcceptVertex(x):
    """Recursively delete partially observed vertices"""
    if ((Diameter(x) <= 0) or (StApex(x) > 0) or (Polycyclism(x) <= 0) or (Length(x) <= 0)):
        return False
    elif (x == amlPy.Root(x)):
        return True
    else:
        return AcceptVertex(amlPy.Father(x)) 

TAS = trees.Trees(data_filepath, AcceptVertex,
                  attribute_def=[Length, BrIntensity, FCones,
                                 MCones, Polycyclism, Diameter, StApex],
                  attribute_names=["Length", "Branches", "Female", "Male",
                                   "Polycyclism", "Diameter", "StApex"],
                  scale=s)

# Histogram of Lengths
# TAS.ExtractHistogram("Length").plot()

# Discard Diameter and state of apex in HMT model
T = TAS.SelectVariable(range(5))
T = T.Shift(4, -1) # polycyclism: number of cycles beyond the first one
clust = range(1,9)
clust.append(10)
T = T.Cluster("Limit", 1, clust) # delete gap in branches values

print "Extracted trees: ", T


### Same thing using newmtg
g = mtg.MTG(data_filepath)
import openalea.mtg.treestats as treestats


def MTGNbBranches(gu, graph=g):
    """Number of branches at GU scale"""
    res = graph.node(gu).nbramif
    if res is None:
        return 0
    else:
        return res

def MTGBrIntensity(x, graph=g):
    """Number of branches at AS scale"""
    comp = list(graph.components(x))
    res = sum(MTGNbBranches(gu, graph) for gu in comp)
    return res

def MTGGULength(x, type, graph=g):
    """Length of GU of a given type
    (l_sterile, l_male or l_leave)"""
    res = graph.get_vertex_property(x)
    return int(round(res.get(type,0)))
#X     if res.has_key(type):
#X         return int(round(res[type]))
#X     else:
#X         return 0

def MTGLength(x, graph=g):
    """Length of AS"""
    # AS is decomposed of sterile, male
    # and leaf parts (sum lengths of three parts)
    comp = list(graph.components(x))
    sterile = [MTGGULength(gu, "l_sterile", graph) for gu in comp]
    male = [MTGGULength(gu, "l_male", graph) for gu in comp]
    leave = [MTGGULength(gu, "l_leave", graph) for gu in comp]
    assert(len(sterile) == len(male))
    assert(len(sterile) == len(leave))
    length = [sterile[i] + male[i] + leave[i] for i in range(len(sterile))]
    if sum(length) == 0:
        for gu in range(len(sterile)):
            if length[gu] == 0:
                length[gu] = graph.node(comp[gu]).length
                if length[gu] is None:
                    return 0
        return sum(length)
    else:
        return sum(length)

def MTGGUNbFCones(gu, graph=g):
    """Number of female cones at GU scale"""
    res = graph.node(gu).nbcones
    if res is None:
        return 0
    else:
        return res

def MTGFCones(x, graph=g):
    """Female cones (boolean) at AS scale"""
    comp = list(graph.components(x))
    res = [MTGGUNbFCones(gu, graph) for gu in comp]
    if sum(res) > 0:
        return 1
    else:
        return 0

def MTGGUNbMCones(gu, graph=g):
    """Number of male cones at GU scale"""
    res = graph.node(gu).l_male
    if res is None:
        return 0
    else:
        return res

def MTGMCones(x, graph=g):
    """Male cones (boolean) at AS scale"""
    comp = list(graph.components(x))
    res = [MTGGUNbMCones(gu, graph) for gu in comp]
    if sum(res) > 0:
        return 1
    else:
        return 0

def MTGPolycyclism(x, graph=g):
    """Number of growth cycles"""
    res = list(graph.components(x))
    return len(res)

def MTGDiameter(x, graph=g):
    """diameter at AS scale (at middle of GUs) : max GU diameter"""
    comp = list(graph.components(x))
    res = [10 * int(round(graph.node(gu).diam)) if graph.node(gu).diam else 10 for gu in comp]
    if len(res) == 0:
        return 0
    else:
        return int(round(max(res)))

def MTGStApex(x, graph=g):
    """State of the apex
    0 == Alive
    1 == Dead
    2 == Broken"""
    res = graph.node(x).state
    if res == 'V':
        return 0
    elif res == 'M':
        return 1
    elif res == 'C':
        return 2
    else:
        return 0

def filter(x, graph=g):
    """Delete partially observed vertices"""
    if ((MTGDiameter(x,graph) <= 0) or (MTGStApex(x,graph) > 0) \
        or (MTGPolycyclism(x,graph) <= 0) or (MTGLength(x,graph) <= 0)):
        return False
    elif (x == graph.root):
        return True
    else:
        return True

TAS2 = treestats.extract_trees(g, 3, filter, [MTGLength, MTGBrIntensity, MTGFCones,
                                           MTGMCones, MTGPolycyclism, MTGDiameter, MTGStApex],
                                ["Length", "Branches", "Female", "Male",
                                   "Polycyclism", "Diameter", "StApex"])

# openalea.mtg.plantframe.Plot(g)

def visitor_geom(g, v, turtle, colorfunc):
    if not filter(v,g):
        return
    length = float(MTGLength(v, g))
    diameter = float(MTGDiameter(v, g))/10.
    phyllotaxis = 83
    color = colorfunc(v)
    if g.edge_type(v) == '+':
        # First rotate depending i* phyllotaxis angle.
        # with i is the index in the ramified siblings
        children = list(g.children(g.parent(v)))
        i = children.index(v)
        turtle.rollL(phyllotaxis*i)
        turtle.down(45)
    turtle.setId(v)
    # turtle.setColor(color)
    r,g,b = color
    turtle.setColorAt(1, r, g, b)
    turtle.setColor(1)
    # see mango module
    turtle.setWidth(diameter)
    turtle.F(length)
    turtle.rollL(phyllotaxis)

rcolorfunc = lambda x: (randint(0,255), randint(0,255), randint(0,255))

def my_plot(g, index= 0, scale=3, colorfunc=lambda x:0):
    trees = list(g.component_roots_at_scale(g.root, scale=scale))
    root_id = trees[index]
    my_visitor_geom = lambda g, v, turtle: visitor_geom(g, v, turtle, colorfunc)
    scene = turtle.traverse_with_turtle(g, root_id, visitor=my_visitor_geom, gc=False)
    pgl.Viewer.display(scene)
    return scene

my_plot(g, 1, 3, rcolorfunc)
#my_plot(g, 1, 3, lambda x: (0,0,0))

#-----------------------------------------------------------------------
#
# Exploratory analysis
#
#-----------------------------------------------------------------------

# Histogram of the BrIntensity variable
HB = T.ExtractHistogram("Branches")
# HB.plot()

def PlotAttribute(tree_number, Attribute, T=T):
    """Display given attribute."""
    v0 = T.MTGComponentRoot(tree_number)
    t0 = T.MTGVertexId(tree_number,0)
    if (t0!=v0):
        raise Warning, "MTGComponentRoot and MTGVertexId do not match!"
    print "\n Tree number", tree_number
    diamfun = lambda x: max(Diameter(x), 1)
    lengthfun = lambda x: max(Length(x) / 2, 1)
    DR = amlPy.DressingData(dressing_filepath)
    P = amlPy.PlantFrame(v0, Scale=3, DressingData=DR, Length=lengthfun,
                       BottomDiameter=diamfun)
    amlPy.Plot(P, Color=Attribute)
    return P

# P = PlotAttribute(2, MCones)

# P = PlotAttribute(2, FCones)

# P = PlotAttribute(2, Polycyclism)

# P = PlotAttribute(2, BrIntensity)


#-----------------------------------------------------------------------
#
# Statistical modelling: Hidden Markov out-trees with conditionally
# independent children states (HMT)
#
#-----------------------------------------------------------------------
# initialisation file for estimation
HI = hmt.HiddenMarkovIndOutTree(model_filepath)
# HMT estimation
EH = T.Estimate("HIDDEN_MARKOV_TREE", HI, 200)
EH.Display()
# EH.Plot("Observation", variable=0)

# computation of the optimal state tree
ST = T.ComputeStateTrees(EH, "Viterbi")

print "Marginal distribution of the states: "
print map(lambda x: 100 * x, ST._state_marginal_distribution())

# add states to MTG g
def HMTStateFunction(vid, tree, StateVariable=None, ST=ST):
    """Return pair MTGvid, state associated
    with a given tree vid"""
    if StateVariable is None:
        attributes = ST.Attributes()
        state_variables = [i for i in range(ST.NbVariables()) if "state" in attributes[i].lower()]
        StateVariable = state_variables[0]
    mtg_vid = ST.MTGVertexId(tree, vid)
    val = ST.Tree(tree).Get(vid)
    return mtg_vid, val[StateVariable]

statep = []
for t in range(ST.NbTrees()):
    statep += [HMTStateFunction(vid, t, 0, ST) for vid in ST.Tree(t).MTGVertex().keys()]

g.add_property("OptimalState")
g.properties()["OptimalState"] = dict(statep)

state_func = lambda x,graph=g : colour_state(graph.node(x).OptimalState)
my_plot(g, 1, 3, state_func)

#-----------------------------------------------------------------------
#
# Visualisation of the states on plants using PlantFrame
#
#-----------------------------------------------------------------------

def generic_color_fun(x, Tr):
    # tree coloration using the hidden states
    try:
        tree_vid = Tr.TreeVertex(x)
    except KeyError:
        return 0
    else:
        val = Tr.Get(tree_vid)
        if (val[0] < 7):
            return val[0]+2
        else:
            return 1

def GeomTree(tree_number, ST=ST):
    """Display the states for a tree identified by given argument."""
    v0 = ST.MTGComponentRoot(tree_number)
    t0 = ST.MTGVertexId(tree_number,0)
    if (t0 != v0):
        raise Warning, "MTGComponentRoot and MTGVertexId do not match!"
    print "\n Tree number", tree_number
    # ST.Tree(tree_number).Display(mtg_vids=True)
    # tree coloration using the hidden states
    colorfun = lambda x: generic_color_fun(x, ST.Tree(tree_number))
    diamfun = lambda x: max(Diameter(x), 1)
    lengthfun = lambda x: max(Length(x) / 2, 1)
    DR = amlPy.DressingData(dressing_filepath)
    P = amlPy.PlantFrame(v0, Scale=3, DressingData=DR, Length=lengthfun,
                         BottomDiameter=diamfun)
    amlPy.Plot(P, Color=colorfun)
    return P

# P = GeomTree(2, ST)


#-----------------------------------------------------------------------
#
# Synchronism analysis and tree matching
#
#-----------------------------------------------------------------------

def InitMatching(T=TAS, ST=ST):
    """ """
    filepath = "augmented_aleppo_pines.txt"
    try:
        f = file(filepath)
    except IOError:
        ST2 = ST.MergeVariable([TAS.SelectVariable([5])])
        ST2.Save(filepath, overwrite=True)
    h = amlPy.MTG(filepath)
    TCtrl = trees.Trees(filepath)
    OptimalState = lambda vtx : amlPy.Feature(vtx,"OptimalState")
    return OptimalState

OptimalState = InitMatching(ST)

def GeomTreeA(tree_number):
    """Display the states for a tree identified by given argument."""
    filepath = "augmented_aleppo_pines.txt"
    h = amlPy.MTG(filepath)
    plants = amlPy.VtxList(Scale=1)
    v0 = plants[tree_number]
    colourfun = lambda vtx : amlPy.Feature(vtx,"OptimalState")+2
    lengthfun = lambda vtx : max(amlPy.Feature(vtx,"Length"), 1)
    diamfun = lambda vtx : max(amlPy.Feature(vtx,"Diameter"), 1)
    DR = amlPy.DressingData(dressing_filepath)
    P = amlPy.PlantFrame(v0, Scale=2, DressingData=DR, Length=lengthfun,\
                         BottomDiameter=diamfun)
    amlPy.Plot(P, Color=colourfun)
    return P

def ComputeBrMatching(plant_number):
   """Compute alignment of all branches of a given plant"""
   # root of each plant
   plants = amlPy.VtxList(Scale=1)
   # root of the plant of interest
   plant = plants[plant_number]
   # vertices of the trunk
   trunk = amlPy.Trunk(plant, Scale=2)
   # branches rooted along the trunk
   branches_root = []
   for v in trunk :
      l = amlPy.Sons(v)
      for w in l :
         if w not in trunk:
            branches_root += [w]
   funs = [OptimalState]
   v = amlPy.VectorDistance(distance_filepath)
   m = amlPy.TreeMatching(branches_root, MatchingType="by_weights",\
                          FuncList=funs, VectorDistance=v)
   return plant, m

def DisplayMatching(cm, ref_br, input_br):
   """Plot the matched vertices of 2 branching systems using the state color"""
   plant, m = cm
   list = amlPy.MatchingExtract(m, ViewPoint="List", InputTree=input_br, ReferenceTree=ref_br)
   # Vertices of the input plant that have an image by TreeMatching
   input_vtx = list[0]
   # Vertices of the reference plant that have an image by TreeMatching
   ref_vtx = list[1]
   def M(v, input=input_vtx, ref=ref_vtx):
      """Return the image of a vertex in the other branching system, if any
      (-1 in other cases)"""
      if v in input_vtx :
         return ref_vtx[amlPy.Pos(input_vtx,v)-1]
      elif v in ref_vtx :
         return input_vtx[amlPy.Pos(ref_vtx,v)-1]
      else :
         return  -1
   def I(v):
      """Return argument vertex if it belongs to the input plant,
      and its image (if any) if it belongs to the reference plant"""
      if v in input_vtx :
         return v
      else :
         return M(v)
   def fc(v):
      """Colour function using the aligned vertices"""
      if (M(amlPy.Complex(v, Scale=2)) != -1):
         return OptimalState(I(amlPy.Complex(v, Scale=2))) + 2
      else:
         return amlPy.Black
   lengthfun = lambda vtx : max(amlPy.Feature(vtx,"Length"), 1)
   diamfun = lambda vtx : max(amlPy.Feature(vtx,"Diameter"), 1)
   DR = amlPy.DressingData(dressing_filepath)
   p = amlPy.PlantFrame(plant, Scale=2, DressingData=DR, Length=lengthfun, BottomDiameter=diamfun)
   amlPy.Plot(p, Color=fc)
   return list


# Mutual alignment of branches

# P = GeomTreeA(1)

# r = ComputeBrMatching(1)

# DisplayMatching(r, 4, 5)

# r=ComputeBrMatching(2)
# amlPy.MatchingExtract(r[1], ViewPoint="Text")
# M=amlPy.MatchingExtract(r[1], ViewPoint="DistanceMatrix")
# amlPy.Display(M)
# DisplayMatching(r, 3, 2)
# DisplayMatching(r, 4, 1)
# DisplayMatching(r, 6, 5) # not so much convincing !
# DisplayMatching(r, 6, 2)
# DisplayMatching(r, 6, 3)
# DisplayMatching(r, 7, 8)
# DisplayMatching(r, 9, 8)
# DisplayMatching(r, 9, 7)
# DisplayMatching(r, 15, 18)
# DisplayMatching(r, 17, 18)
# DisplayMatching(r, 15, 18)
