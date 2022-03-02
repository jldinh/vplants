# Analysis of the symphonia dataset
# This script cannot be freely distributed before the work
# on Symphonia dataset has not been published (Heuret, Durand et al.)

#-----------------------------------------------------------------------
#
# Module import
#
#-----------------------------------------------------------------------
import sys, os
import openalea.tree_statistic.trees, openalea.tree_statistic.hmt
trees=openalea.tree_statistic.trees
hmt=openalea.tree_statistic.hmt
import openalea.aml
amlPy=openalea.aml
amlPy.setmode(1)

#--------------------------------------------------------------------------------------
#
# Build Trees object
#
#--------------------------------------------------------------------------------------

# N.B. Trees described at GU scale with length, number of pairs of cataphylls,
# number of pairs of leaves and number of internodes

T=trees.Trees("symphonia.txt")

# print Attribute names
T.Attributes()

# Discard Number of Internodes variable
T2=T.SelectVariable([0, 1, 2])

# Plot Histograms: Length, Half the number of Cataphylls, Half the number of leaves
HLG = T2.ExtractHistogram("Length")
HPC = T2.ExtractHistogram("HalfNbCat")
HPL = T2.ExtractHistogram("HalfNbLeaves")
# HLG.Plot()
# HPC.Plot()
# HPL.Plot()
   
def PlotGUTree(tree_number, TGU=T2):
    """Visualisation of a given tree at GU scale"""

    v0=TGU.MTGComponentRoot(tree_number)
    print "\n Tree number", tree_number
    colourfun=lambda x: 1
    GULength=lambda vtx: amlPy.Feature(vtx, "Length")
    GUDiam=lambda vtx: 10
    DR=amlPy.DressingData("symphonia.drf")
    P=amlPy.PlantFrame(v0, Scale=2, DressingData=DR, 
                       Length=GULength, BottomDiameter=GUDiam)
    amlPy.Plot(P, Color=colourfun)
    return P

# P=PlotGUTree(26)

#-----------------------------------------------------------------------
#
# Modelling: model and state estimation
#
#-----------------------------------------------------------------------

# define initial model for the EM algorithm (difficult !)
HI=hmt.HiddenMarkovTree("symphonia7I_init.hmt")
EH=T2.Estimate("HIDDEN_MARKOV_TREE", HI, 50)
EH.Display()

# plot observation distribution of length
# EH.Plot("Observation", variable=0)

# computation of the optimal state tree
ST=T2.ComputeStateTrees(EH, "Viterbi")

#-----------------------------------------------------------------------
#
# Analysis of the states and distributions
#
#-----------------------------------------------------------------------

def MarginalDistribution(hmt, variable, hmt_data):
    """Return the marginal distribution of a variable."""
    def ToHiddenSemiMarkov(hmt):
       """Conversion from a Hidden Markov Tree 
       to a (AML) Hidden Semi-Markov Chain."""
       hmt.Save("tmp_hmt_file.hmt", overwrite=True)
       try:
           hmtf=file("tmp_hmt_file.hmt", 'r')
       except IOError:
           msg="Could not create a Hidden Semi-Markov Chain object from" + str(hmt)
           raise IOError, msg
       else:
           hsmcf=file("tmp_hmt_file.hsc", 'w+')
           # seek for keyword "HIDDEN_MARKOV_OUT_TREE"
           found=False
           while not found:
               hmt_code=hmtf.readline()
               pos=hmt_code.upper().find("HIDDEN_MARKOV_OUT_TREE")
               if pos != -1:
                   # keyword "HIDDEN_MARKOV_OUT_TREE" has been found 
                   # but can be commented out
                   if (hmt_code.find("#",0,pos)==-1):
                       found=True
               else:
                   hsmcf.write(hmt_code)
           hsmcf.write("HIDDEN_SEMI-MARKOV_CHAIN\n")
           # seek for keyword "TRANSITION_PROBABILITIES"
           found=False
           while not found:
               hmt_code=hmtf.readline()
               pos=hmt_code.upper().find("TRANSITION_PROBABILITIES")
               if pos != -1:
                   # keyword "TRANSITION_PROBABILITIES" has been found 
                   # but can be commented out
                   if (hmt_code.find("#",0,pos)==-1):
                       found=True
               else:
                   hsmcf.write(hmt_code)
           hsmcf.write("TRANSITION_PROBABILITIES\n")
           transstr="" # string for transition probabilites
           nbstates=len(hmt_data._state_marginal_distribution())
           for s in range(nbstates):
               transstr+=str(1./nbstates)+"\t"
           for s in range(nbstates):
               hsmcf.write(transstr+"\n")
           # seek for keyword "OUTPUT"
           found=False
           while not found:
               hmt_code=hmtf.readline()
               pos=hmt_code.upper().find("OUTPUT")
               if pos != -1:
                   # keyword "OUTPUT" has been found 
                   # but can be commented out
                   if (hmt_code.find("#",0,pos)==-1):
                       found=True
           hsmcf.write("\n"+hmt_code)        
           hmt_code=hmtf.read()
           hsmcf.write(hmt_code)
           hmtf.close()
           hsmcf.close()
           res=amlPy.HiddenSemiMarkov("tmp_hmt_file.hsc")
           os.remove("tmp_hmt_file.hsc")
           os.remove("tmp_hmt_file.hmt")
           return res
    def ToAMLHistogram(histo):
       """Conversion from a stat_tool.Histogram to an AML Histogram."""
       histo.Save("tmp_h_file.hst")
       try:
           f=file("tmp_h_file.hst", 'r')
       except IOError:
           msg="Could not create a AML Histogram object from" + str(histo)
           raise IOError, msg
       else:
           f.close()
           res=amlPy.Histogram("tmp_h_file.hst")
           os.remove("tmp_h_file.hst")
           return res
    hmc=ToHiddenSemiMarkov(hmt)
    obs_dist=[]
    for s in range(hmt.NbStates()):
        obs_dist.append(amlPy.ExtractDistribution(hmc,"Observation", 
                                                      variable+1, s))
    weights=hmt_data._state_marginal_distribution()
    command="amlPy.Mixture("
    for s in range(hmt.NbStates()-1):
        command+=str(weights[s])+", obs_dist["+str(s)+"], "
    s=hmt.NbStates()-1
    command+=str(weights[s])+", obs_dist["+str(s)+"])"
    mix=eval(command, globals(), locals())
    H=ToAMLHistogram(hmt_data.ExtractHistogram("Value", variable+1))
    D=amlPy.Fit(H, amlPy.ExtractDistribution(mix, "Mixture"))
    return D, mix

def SaveMarginalDistribution(hmt, variable, hmt_data):
    D, Mix=MarginalDistribution(hmt, variable, hmt_data)
    amlPy.Save(D, "fit"+str(variable)+".txt", Format="SpreadSheet")
    amlPy.Save(Mix, "mixt"+str(variable)+".txt", Format="SpreadSheet")
    return D, Mix

# Plot Mixture Distribution and Histogram for variable 0
# D, Mix=MarginalDistribution(EH, 0, ST)
# amlPy.Plot(Mix)
# amlPy.Plot(D)

#-----------------------------------------------------------------------
#
# Visualisation of the states on plants using PlantFrame
#
#-----------------------------------------------------------------------

def generic_GUcolour_fun(x, Tr):
    # tree coloration using the hidden states
    try:
        tree_vid=Tr.TreeVertex(x)
    except KeyError:
        return 0
    else:
        val=Tr.Get(tree_vid)
        if (val[0] < 7):
            return val[0]+2
        else:
            return 1

def GeomTreeGU(tree_number, STG=ST):
    """Display the states for a tree identified by given argument."""
    v0=STG.MTGComponentRoot(tree_number)
    print "\n Tree number", tree_number
    # tree colouration using the hidden states
    colourfun=lambda x: generic_GUcolour_fun(x, STG.Tree(tree_number))
    GULength=lambda vtx: amlPy.Feature(vtx, "Length")
    GUDiam=lambda vtx: 10
    DR=amlPy.DressingData("symphonia.drf")
    P=amlPy.PlantFrame(v0, Scale=2, DressingData=DR, Length=GULength,
                       BottomDiameter=GUDiam)
    amlPy.Plot(P, Color=colourfun)
    return P

# P=GeomTreeGU(26, ST)

#-----------------------------------------------------------------------
#
# Synchronism analysis and tree matching
#
#-----------------------------------------------------------------------

def InitMatching(STG=ST):
   STG.Save("symphonia_augmentes.txt", overwrite=True)
   h=amlPy.MTG("symphonia_augmentes.txt")
   OptimalState = lambda vtx : amlPy.Feature(vtx,"OptimalState")
   return OptimalState

OptimalState=InitMatching(ST)

def GeomTreeA(tree_number):
    """Display the states for a tree identified by given argument."""
    plants = amlPy.VtxList(Scale=1)
    v0=plants[tree_number]
    colourfun=lambda vtx : amlPy.Feature(vtx,"OptimalState")+2
    lengthfun=lambda vtx : amlPy.Feature(vtx,"Length")
    diamfun=lambda vtx : 5
    DR=amlPy.DressingData("symphonia.drf")
    P=amlPy.PlantFrame(v0, Scale=2, DressingData=DR, Length=lengthfun, BottomDiameter=diamfun)
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
   branches_root=[]
   for v in trunk :
      l = amlPy.Sons(v)
      for w in l :
         if w not in trunk:
            branches_root+=[w]
   funs=[OptimalState]
   v=amlPy.VectorDistance("ORDINAL", Distance="QUADRATIC")
   # v=amlPy.VectorDistance("align1s7.a")
   m=amlPy.TreeMatching(branches_root, MatchingType="Edition",\
                        FuncList=funs, VectorDistance=v)
   return plant, m

def ComputeTrMatching(plant_number):
   """Compute alignment of all branches with the trunk of a given plant"""
   # root of each plant
   plants = amlPy.VtxList(Scale=1)
   # root of the plant of interest
   plant = plants[plant_number]
   # vertices of the trunk
   trunk = amlPy.Trunk(plant, Scale=2)
   # branches rooted along the trunk
   branches_root=[]
   for v in trunk :
      l = amlPy.Sons(v)
      if len(l) > 1:
         for w in l :
            branches_root+=[w]
   funs=[OptimalState]
   # v=amlPy.VectorDistance("align1s7.a")
   v=amlPy.VectorDistance("ORDINAL", Distance="QUADRATIC")
   m=amlPy.TreeMatching(branches_root, MatchingType="Edition",\
                        FuncList=funs, VectorDistance=v)
   return plant, m

def DisplayMatching(cm, ref_br, input_br):
   """Plot the matched vertices of 2 branching systems using the state color"""
   plant, m = cm
   list=amlPy.MatchingExtract(m, ViewPoint="List", InputTree=input_br, ReferenceTree=ref_br)
   # Vertices of the input plant that have an image by TreeMatching
   input_vtx=list[0]
   # Vertices of the reference plant that have an image by TreeMatching
   ref_vtx=list[1]
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
   lengthfun=lambda vtx : amlPy.Feature(vtx,"Length")
   diamfun=lambda vtx : 5
   DR=amlPy.DressingData("symphonia.drf")
   p=amlPy.PlantFrame(plant, Scale=2, DressingData=DR, Length=lengthfun, BottomDiameter=diamfun)
   amlPy.Plot(p, Color=fc)
   return list

# Mutual alignment of branches

# P=GeomTreeA(26)

# r=ComputeBrMatching(26)

# N.B. You should display 2 GeomViewers:
# the first one with the original tree P=GeomTreeA
# the other one with the mapping

# DisplayMatching(r, 6, 5)
