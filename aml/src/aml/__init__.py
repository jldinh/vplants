# -#-python-#-
#  ----------------------------------------------------------------------------
#
#  amlPy package.
#
#  File author(s): Christophe Pradal, Cyril Bonnard
#
#  $Id: __init__.py 16094 2014-03-17 14:55:16Z guedon $
#
#  ----------------------------------------------------------------------------
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#  ----------------------------------------------------------------------------
#
#
#  $Id: __init__.py 16094 2014-03-17 14:55:16Z guedon $
#
#  ----------------------------------------------------------------------------
#

# Version
from amlPy_version import amlPy_version

__version__= amlPy_version

import _amlPymodule

_amlPy = _amlPymodule

# If we cannot import Numeric, it should have been detected at
# installation time and amlPy should have been compiled properly. So,
# don't complain.

try:
    import openalea.plantgl.all
except ImportError:
   try:
      import PlantGL
   except ImportError:
      pass



###########################################################################
############################# Global names ################################
###########################################################################


###########################################################################
########################### Conversion system #############################
###########################################################################

   
# Manage the global mode

def setmode(mode):
    _amlPy.set_mode(mode)

def getmode():
    return _amlPy.get_mode()

setmode(1)

class AML(object):
    """ main class """

    # called when the attribute is not found,
    # eg always except for TRUE and FALSE
    def __getattr__(self, name):
        return self.__getitem__(name)

    # return the amobj from r.__dict__ at key=name
    def __getitem__(self, name):
        #print "__getitem__", name
        obj = self.__dict__[name] = self.__dict__.get(name, _amlPy.get(name))
        return obj

    # enables the instance to be callable eg: aml("AML code")
    def __call__(self, s):
        #print "__call__", s
        return self.eval(self.parse(text=s))

# main instance
aml = AML()

# hack: usual AMAPmod functions

# Equivalent AMAPmod function in Python
import math, os

Acos = math.acos
Asin = math.asin
Atan = math.atan
Cos = math.cos
Log = math.log
Log10 = math.log10
Sin = math.sin
Sqrt = math.sqrt
Tan = math.tan
Exp = math.exp
Abs = abs
Pi = math.pi

Pwd = os.getcwd
Cd = os.chdir
Dir = os.getcwd
#Ls=os.listdir(Dir())
Rm = os.remove
Mkdir = os.mkdir

Max = max
Min = min

def Swich(x, dict, default):
    """
    Switch(x, dict, default)
    Return dict[x] or default
    """
    return dict.get( x, default )


__var= """
AMAPMOD_DIR
Black
Blue 
LightBlue
CurrentMTG
CurrentPlottedObj
CurrentWindow 
CWD
DateFormat
DateUnit
Day
DefaultWindow
Green
HOME
Hour
Minute
Red
ROOTDIR
Second
Undef
Violet
White
Yellow
"""
__function = """
Activate
Active
AlgHeight
AlgOrder
AlgRank
AllPos 
Alpha  
Ancestors
Angle    
Append   
Array
Axis          
Azimuth       
Beta          
BottomCoord   
BottomDiameter
Ceil          
Class         
ClassScale    
Complex       
ComponentRoots
Components    
Coord         
Copy          
Cov
Date          
DateSample    
Defined       
Delete        
Descendants   
Display       
DressingData  
EDist         
Echo          
EchoOff       
EchoOn        
EdgeType      
ElectricalModel
EulerAngles   
Exists        
ExpSequence   
Extract       
Extremities   
Father        
Feature       
FileHelp      
Filter        
FirstDefinedFeature
Flatten       
Floor         
GeomScene     
Head          
Height        
Identity      
IfThenElse    
Index         
InsertAt      
Inter         
Interval      
Invert        
LastDefinedFeature
Length        
List          
Location
Ls
MSVoxel       
MTG
MTGRoot       
MatchingExtract
Mean          
Minus         
Mod
NewPlot       
NextDate      
Norm          
Octree        
Order         
PDir          
Path          
PlantFrame    
Plot
Plus
Pos
Predecessor   
PreviousDate  
Print         
Prod          
ProdSeries    
Rank          
RelBottomCoord
RelTopCoord   
Rand          
Remove        
RemoveAt      
Rename        
Rint          
Root
SDir          
SProd         
Save          
SaveMTG       
Scale         
Select        
Series        
Set
SetAmapmodDir 
SetMinus      
SetViewer     
Size          
Sons          
Sort          
StartViewer   
StopViewer    
SubArray      
Successor     
Sum
Switch        
Tail          
Times         
ToArray       
ToInt         
ToList        
ToReal        
ToSet         
ToString      
ToTimeUnit    
TopCoord      
TopDiameter   
TreeMatching  
TreeMatchingLoad
Truncate      
Trunk         
Union         
VProd         
Var
ViewerHelp    
ViewerIsRunning
ViewerSelection
VirtualPattern
VtxList       
WaitViewer    

AddAbsorbingRun
BuildAuxiliaryVariable
Cluster
Clustering
Compare
ComparisonTest
Compound
ComputeAutoCorrelation
ComputeCorrelation
ComputeInitialRun
ComputePartialAutoCorrelation
ComputeRankCorrelation
ComputeSelfTransition
ComputeStateSequences
ComputeWhiteNoiseCorrelation
ConsecutiveValues
ContingencyTable
Convolution
Cross
Cumulate
Difference
DiscreteMixture
Distribution
Estimate
ExplicitIndexParameter
ExtractData
ExtractDistribution
ExtractFrequencyDistribution
ExtractHistogram
ExtractVectors
Fit
FrequencyDistribution
HiddenSemiMarkov
HiddenVariableOrderMarkov
Histogram
IndexParameterExtract
IndexParameterSelect
LengthSelect
LumpabilityTest
Merge
MergeVariable
Mixture
MovingAverage
NbEventSelect
NonhomogeneousMarkov
PointwiseAverage
RecurrenceTimeSequences
Regression
RemoveApicalInternodes
RemoveIndexParameter
RemoveRun
Renewal
RenewalData
Reverse
Round
Segmentation
SegmentationExtract
SelectIndividual
SelectStep
SelectVariable
SemiMarkov
SequenceNormalization
Sequences
Shift
ShiftVariable
Simulate
SojournTimeSequences
Symmetrize
Thresholding
TimeEvents
TimeScaling
TimeSelect
ToDistanceMatrix
ToDistribution
ToFrequencyDistribution
ToHistogram
TopParameters
Tops
Transcode
TransformPosition
TransitionCount
TruncateDistribution
Unnormalize
ValueSelect
VariableOrderMarkov
VariableScaling
VarianceAnalysis
VectorDistance
Vectors
WordCount
"""

__function= __function.split()
__var= __var.split()
__liste = __function + __var
__dictionnary = globals()


def doc_wrapper(func, name):
   """ Wrap aml instance in a function """

   # Get Documentation
   try:
      baseimp = "openalea.aml.amldoc." + name.lower()
      docmodule = __import__(baseimp, globals(), locals(), ['__doc__'])
      docstr = docmodule.__doc__
   
   except Exception, e:
      docstr = "AML Function : Documentation unavailable"

   def wrapped(*args, **kwds):
      """ dummy documentation (changed later) """
      # call function
      return func(*args, **kwds)

   # Add doc
   wrapped.__doc__ = docstr
   wrapped.__name__ = name

   return wrapped


# Update globals() with aml functions
for fct in __function:
   try:
      __dictionnary[fct] = doc_wrapper(aml.__getattr__(fct), fct)
   except Exception:
      pass


for fct in __var:
   try:
      __dictionnary[fct] = aml.__getattr__(fct)
   except Exception:
      pass


_DEBUG = False
if _DEBUG:
    # Test
    cpt = 0

    for fct in __function:
        baseimp = "amldoc." + fct.lower()
        try:
            docmodule = __import__(baseimp, globals(), locals(), ['__doc__'])
        except:
            print fct, "NO DOC"
            cpt += 1

    if(cpt > 0): 
        print cpt
    del cpt
   
del _DEBUG

import datetime
def ToPyDate(d):
  s = str(d)
  sv = s.split(':')[1]
  d,m,y = sv.split('/')
  return datetime.date(int(y),int(m),int(d))

