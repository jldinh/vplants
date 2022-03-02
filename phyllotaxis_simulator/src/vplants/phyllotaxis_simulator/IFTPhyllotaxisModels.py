#from numpy import empty, inf, array, sin, cos, exp, trunc, pi, sum, abs, radians, sort, where, zeros, column_stack, arange, meshgrid
import numpy as np
import matplotlib.pylab as plt
from pickle import dump
from scipy.spatial import distance
from openalea.container.graph import Graph
from openalea.plantgl.all import *
from time import time
from openalea.plantgl.math import norm
from numpy.random import normal

class IFTPhyllotaxisModel(object):
  """
  IFTPhyllotaxisModel (Inhibitory Field Theory Phyllotaxis Model) is the base class for phyllotaxis models
  """
  def __init__(self, CZRadius, R, PInitRadius, V_0, initAngle, ringSize, maxDistance, primordiaNb, initDt, timePrec, addDelay, addGaussianNoise, dr, parastichiesDistThreshold, initialDivAngle, initialDivAngleNumber, equipotentialSpaceResolution, drawEquipotential):
    # Phyllotaxis parameters
    self.CZRadius = CZRadius                     # Radius of the central zone of meristem
    self.R = R                                   # Ratio of the central zone radius to primordium initial radius
    self.PInitRadius = CZRadius / R              # Initial radius of a primordium
    self.V_0 = V_0                               # used in speedField function to calculate velocity of primordia

    # Simulation parameters
    self.maxDistance = maxDistance               # If a primordium is at a distance greater than maxDistance, its contribution to the inhib field is no longer taken into account
    self.primordiaNb = primordiaNb               # Maximum number of primordia generated by a complete simulation of the model
    #self.T = T                                   # Time period at which primordia are created (this only used in Hofmeister's model)
    self.initDt = initDt                         # Initial time step
    self.ringSize = ringSize                     # Number of the sampling points at the periphery of the central zone for which we calculate the inhibition field
    self.addDelay = addDelay                     # Boolean variable, if true a delay is added to the inhibtion created by primordia
    self.addGaussianNoise = addGaussianNoise     # Boolean variable, if true, a Guassian noise is added to the inhibitory field of primordia. The value of the noise stays constant for each primordium after its generation.
    self.parastichiesDistThreshold = parastichiesDistThreshold        # To calculate the parastiches, the first nearest primordium as well as any primordia whose distance to the first nearest primordium is less than 'parastichiesDistThreshold' are taken into account.

    self.dr = dr
    self.plotResults = False                     # Boolean variable, if true the inhibition filed as well as divergence angles are plotted
    self.dumpParastichiesGraph = True            # Boolean variable, if true the parastichies graph is dumped on the disk using the pickle module
    
    # Initialisation parameters
    self.initAngle = initAngle                   # The angular position of the first primordium    
    self.initialDivAngle = initialDivAngle                      # Initial divergence angle that is used to initialize the system (especially used in the bifurcation diagrams)
    self.initialDivAngleNumber = initialDivAngleNumber               # Number of primordia whith predefined intial divergence angle (i.e. initialDivAngle) used to initialize the system
    
    # Simulation state    
    self.ringElmAngle = 360.0 /ringSize          # Angular distance between two consecutive sampling points at the periphery of the the central zone
    self.inhibField = np.empty(ringSize)            # an array whose elements are inhibitory field values at the periphery of the central zone
    self.divergenceAngles = []                   # List of simulated divergence angles for one individual plant
    self.primordiaPositions = []                 # List of primordia positions in 3D space
    self.previousAbsoluteAngle = 0
    self.plastochrons = []
    self.initiationTimes = []
    
#    self.inhibFieldDivAngleFig = plt.figure(1)   # The figure which contains the inhibition field plot as a function of absolute angle, as well as divergence angles plot
#    self.polarInhibFieldFig = plt.figure(2)      # The figure which contains the inhibition field plot in a polar plot

    self.samplingPointsAngularPosition = np.radians(self.ringElmAngle * np.arange(self.ringSize))        # Angular positions of sampling points in radians at the periphery of the central zone
    self.samplingPointsPositions = np.column_stack((np.zeros(self.ringSize), self.CZRadius * np.cos(self.samplingPointsAngularPosition), self.CZRadius * np.sin(self.samplingPointsAngularPosition)) )        # Sampling points positions at the periphery of the central zone
    
    self.generatedPrimordiaNb = 0                # Number of generated primordia, we increment this variable as a new primordium appears
    self.simulationStartTime = time()
    self.newPrimordiumGenerated = False
    self.equipotentialSpaceResolution = equipotentialSpaceResolution        # spaceResolution represents the pair of number of points in x grid vector as well as number of points in y grid vector used in meshgrid
    self.drawEquipotential = drawEquipotential        # Boolean variable, if true the primordia contributions to the inhibition field space are taken into account to plot the equipotential lines
    self.Y = np.linspace(self.maxDistance, - self.maxDistance, self.equipotentialSpaceResolution[0])
    self.Z = np.linspace(self.maxDistance, - self.maxDistance, self.equipotentialSpaceResolution[1])
    self.YY, self.ZZ = np.meshgrid(self.Y, self.Z)
    self.fieldValues = np.zeros(self.equipotentialSpaceResolution)
    self.timePrec = timePrec        # time precision used in the simulations            
    self.currentTPrec = self.dt = self.initDt
    self.timePrecRefined = False
    
    
  def speedField(self, p):
    """
    Calculate the velocity of primodia dirfting away from the central zone
    """
    return self.V_0 * norm(p) /self.CZRadius      
  
  def inhibition(self, dist, t, fieldStrength, exponent = 3):
    """
    Calculate inhibition created by a primordium at a given distance
    Note: According to Douady and Couder (1996), similar fucntions generate qualitatively the same phyllotactic cascade patterns paper I, p 296 (figure 4 legend)
    """
    inhibValue = ( 1.0 / ( dist ** exponent ))
    if self.addGaussianNoise:
      inhibValue *= fieldStrength
    if self.addDelay:
      inhibValue *= self.delayFunction(t)  
    return inhibValue
  
  def delayFunction(self, t, b = 1.0):
    return (1.0 / (1.0 + np.exp(- (t ) * b)))


  def stepInitialize(self):
    self.inhibField.fill(0)
    self.primordiaPositions = []
    self.fieldValues.fill(0)
    
  def primordiumContribution2InhibField(self, p, t, fieldStrength):   
    value = np.sum( ( self.samplingPointsPositions - p ) ** 2, axis = 1 ) ** ( 1.0 / 2.0 )   
    self.inhibField += self.inhibition( value, t, fieldStrength)
    self.primordiaPositions.append(p)
    if self.drawEquipotential:
      self.fieldValues += self.inhibition(((self.YY - p[1]) ** 2 + (self.ZZ - p[2]) ** 2) ** (1 / 2.0),  t, fieldStrength)    

  def computeParastichies(self):
    """
    Calculate paratichies and put them a graph
    """
    primDist = distance.cdist(self.primordiaPositions, self.primordiaPositions)        # Computes the distance between each pair of primPositions, i.e. primDist[i, j] is the dsitance between primPositions[i] and primPositions[j]
    primordiaNb = len(self.primordiaPositions)
    closestNeighborsList = []
    for i in xrange(primordiaNb):
      neighborsSorted = np.argsort(primDist[i,:])
      k = 1
      while (k < primordiaNb - 1) and neighborsSorted[k] < i:
        k += 1 
      sortedArgs = np.where(primDist[i][neighborsSorted] - primDist[i][neighborsSorted[k]] < self.parastichiesDistThreshold)
      newList = [j for j in neighborsSorted[sortedArgs][1:] if j > i]
      closestNeighborsList.append(newList)
    parastichiesGraph = Graph()
    for i in xrange(primordiaNb):
      parastichiesGraph.add_vertex(i)    
    for i in xrange(primordiaNb):
      for j in closestNeighborsList[i]:
          parastichiesGraph.add_edge(i, j)
    return closestNeighborsList, parastichiesGraph
    
  def addParastichiesToScene(self, scene, parastichiesGraph, edgeRadius, primPositions):
    color = Material(Color3(0, 0, 200))
    for edgeId in parastichiesGraph.edges():
      geom = Polyline([primPositions[parastichiesGraph.source(edgeId)], primPositions[parastichiesGraph.target(edgeId)]], width= 1 +  int(edgeRadius))
      shape = Shape(geom, color)
      scene.add(shape)
        
  def growthCurve(self, minval, maxval, speed, x):
    return minval + maxval * (1 - np.exp(-speed * x))
    
  def addNewPrimordium(self, divAngle, previousAbsoluteAngle):
    self.generatedPrimordiaNb += 1
    self.divAngle = divAngle
    self.divergenceAngles.append(divAngle)
    self.previousAbsoluteAngle = previousAbsoluteAngle
    self.primordiaPositions.append(Vector3([0.0, self.CZRadius * np.cos((self.previousAbsoluteAngle/180.0) * np.pi), self.CZRadius * np.sin((self.previousAbsoluteAngle /180.0) * np.pi)]))
    self.newPrimordiumGenerated = True
    self.primFieldStrength = normal(loc = 1.0, scale = 0.02)
    
  def spaceField(self):
    return self.Y, self.Z, self.fieldValues  
    
  def resetForNextPrimordium(self):
    self.currentTPrec = self.dt = self.initDt
    self.newPrimordiumGenerated = False
             
class HofmeisterModel(IFTPhyllotaxisModel):
  def __init__(self, CZRadius, R, PInitRadius, V_0, initAngle, ringSize, maxDistance, primordiaNb, initDt, timePrec, addDelay, addGaussianNoise, dr, parastichiesDistThreshold, initialDivAngle, initialDivAngleNumber, equipotentialSpaceResolution, drawEquipotential):
    super(HofmeisterModel, self).__init__(CZRadius, R, PInitRadius, V_0, initAngle, ringSize, maxDistance, primordiaNb, initDt, timePrec,  addDelay, addGaussianNoise, dr, parastichiesDistThreshold, initialDivAngle, initialDivAngleNumber, equipotentialSpaceResolution, drawEquipotential)
    self.dt = self.initDt
    self.maxDerivationNb = self.primordiaNb * 2 + 1
    
  def next(self):
    """
    Calculates divergence angle given the inhibition field at the periphery of the central zone and the angular position of the preceding primordium.
    """
    if self.generatedPrimordiaNb == 0:      
      self.addNewPrimordium(self.initAngle % 360, 90 )      
    elif self.generatedPrimordiaNb <= self.initialDivAngleNumber:
      self.addNewPrimordium(self.initialDivAngle % 360, (self.previousAbsoluteAngle + self.initialDivAngle ) % 360)
    else:
      minAbsoluteAngle = self.inhibField.argmin() * self.ringElmAngle        # angular position of point where inhibition created by primordia is minimum 
      self.addNewPrimordium((minAbsoluteAngle - self.previousAbsoluteAngle) % 360, minAbsoluteAngle)       # (minAbsoluteAngle - previousAbsoluteAngle) is divergence angle
    
  def HofmeisterControlParameter(self):
    """
    Return the control parameter of the system based on the Hofmiester hypotheses.
    """
    return  self.initDt * self.V_0 / self.CZRadius

  def info(self):
    print "Hofmeister Model"
      

class SnowAndSnowModel(IFTPhyllotaxisModel):
  def __init__(self, CZRadius, R, PInitRadius, V_0, initAngle, ringSize, maxDistance, primordiaNb, initDt, timePrec, addDelay, addGaussianNoise, energyThreshold, dr, parastichiesDistThreshold, initialDivAngle, initialDivAngleNumber, equipotentialSpaceResolution, drawEquipotential):
    super(SnowAndSnowModel, self).__init__(CZRadius, R, PInitRadius, V_0, initAngle, ringSize, maxDistance, primordiaNb, initDt, timePrec, addDelay, addGaussianNoise, dr, parastichiesDistThreshold, initialDivAngle, initialDivAngleNumber, equipotentialSpaceResolution, drawEquipotential)
    self.maxDerivationNb = np.inf
    self.energyThreshold = energyThreshold
 
  def next(self):
    """
    Calculates divergence angle given the inhibition field at the periphery of the central zone and the angular position of the preceding primordium.
    """
    if self.generatedPrimordiaNb == 0:
      self.addNewPrimordium(self.initAngle % 360, 90)      
    elif self.generatedPrimordiaNb <= self.initialDivAngleNumber: 
      self.addNewPrimordium(self.initialDivAngle % 360, (self.previousAbsoluteAngle + self.initialDivAngle) % 360)
    else:
      inhibFieldMin = self.inhibField.min()
      if inhibFieldMin <= self.energyThreshold:        
       if np.where(self.inhibField < self.energyThreshold)[0].shape[0] == 1 or self.currentTPrec < self.timePrec:
        minAbsoluteAngle = self.inhibField.argmin() * self.ringElmAngle        # angular position of point where inhibition created by primordia is minimum  
        self.addNewPrimordium((minAbsoluteAngle - self.previousAbsoluteAngle) % 360, minAbsoluteAngle)        # (minAbsoluteAngle - previousAbsoluteAngle) is divergence angle       
        self.timePrecRefined = False
       else:
         self.currentTPrec /= 2.0
         self.dt -= self.currentTPrec                  
         self.timePrecRefined = True
      else:       
        if self.timePrecRefined:
          self.currentTPrec /= 2.0
          self.dt += self.currentTPrec
      
  def info(self):
    print "S&S Model"