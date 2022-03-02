Comparison of environmental programs simulating light interception with Lpy
############################################################################

The problem setting
===================


We want to compare the results of several programs that allow illuminating a 3D scene produced with LPy.
Such programs are already available as openAlea Packages : Caribu (Chelle et al), and fractalysis (Da Silva et al).
A third programm (QuasiMC, Cieslack) is available for windows user of Virrtual plant teams (download latest QuasiMC egg at https://gforge.inria.fr/frs/download.php/31115/VPlants.quasimc-1.0.0-py2.7-win32.egg)

The tested scene
================

We will use a simple Lpy programm that generates a triangle soap. The Lsystem code could be foulund in the shared data duiirectoryin the file trianglemix.lpy.
Runing Lpy should provide the following output: 

Alternatively, under Visualea, you could use the OpenLpy package under Vplants/tiutorial.
The starting dataflow is 'triangle mix basic'

Lpy solution
============

A straightforward solutiion consists of importing external module from within Lpy programm and use the 'endeach()' section to perform computations.
In the endeach section, the user has access to the simulated string (lstring) together witgh the scene produced by the homomorphism (lscene)
Import of modules is done by including the following lines at the top of the lpy file: 

 .. code-block:: python
 
	#import environmental modules

	#muslim/factalysis
	from openalea.fractalysis.light.directLight import *
	# caribu
	from alinea.caribu.CaribuScene import CaribuScene
	import alinea.caribu.sky_tools.turtle as sky_turtle
	# quasimc 
	import vplants.quasimc.quasimc as qmcobject

	
All thee modules operates on a 3D scene. They however returns several variables and uses specific inputs describing light sources and optical properties of elements.
We can hide this diversity by adding adapters that returns a comparable output (the light incidence oneach triangle), 
from a standadised input (lstring and lscene): 

 .. code-block:: python

	def apply_muslim(lstring, lscene, ligthsources):
		res = directionalInterception(lscene,ligthsources)
		for id,v in res.items():
		  if lstring[id].name == 'Triangle':
			lstring[id].p.fractlight = v
		return res

	def apply_quasimc(lstring, lscene, ligthsources):
		qmc = qmcobject.QuasiMC()
		
		tessel = Tesselator()
		for shape in lscene:
			qmc.add_shape(shape,tessel)
		
		# weight,x_dir,y_dir,z_dir
		qmc.add_light_sources(ligthsources)
		  
		qmc.run()
		# download latest QuasiMC egg to get access to get_sunlit_leaf_area() function
		# https://gforge.inria.fr/frs/download.php/31115/VPlants.quasimc-1.0.0-py2.7-win32.egg
		qres = qmc.get_sunlit_leaf_area()
		
		for id,v in qres.items():
		  if lstring[id].name == 'Triangle':
			lstring[id].p.qmclight = v
		return qres

	def apply_caribu(lstring, lscene, ligthsources):
		c_scene = CaribuScene()    
		idmap = c_scene.add_Shapes(lscene)    
		c_scene.addSources(ligthsources)
		
		output = c_scene.runCaribu(infinity=False)
		c_res = c_scene.output_by_id(output, idmap)['Einc']
		
		for id,v in c_res.items():
			if lstring[id].name == 'Triangle':
			  lstring[id].p.caribulight = v
		return c_res

Finally, we add in the endeach section calls to function, time them and plot results: 

 .. code-block:: python
 
	 def EndEach(lstring,scene):
	  if not scene is None:
		global cmap
		
		print 'setting lights sources and tesselator'
		
		energy, emission, direction, elevation , azimuth  = sky_turtle.turtle()  
		
		if MUSLIM:
		  print 'computing with muslim'
		  start=time()
		  # weighting of sources is made according to emission intensity rather than incidence on an horizontal plane
		  ligthsources = zip(azimuth, elevation, emission)
		  muslimres = apply_muslim(lstring, scene, ligthsources)
		  dfract = time() - start
		
		if QUASIMC:  
		  print 'computing with quasimc'
		  start = time()
		  ligthsources = [(e,) + p for e,p in zip(energy,direction)]
		  quasimcres = apply_quasimc(lstring, scene, ligthsources)
		  dqmc = time() -start
		
		
		if CARIBU:
		  print 'computing with Caribu'
		  start=time()
		  ligthsources = zip(energy,direction)
		  caribures =  apply_caribu(lstring, scene, ligthsources)      
		  dcaribu= time() - start
		
		
		nblightsimulation = MUSLIM+QUASIMC+CARIBU

		if nblightsimulation >= 2 :
		  clf()
		  caribulist=[]
		  muslimlist=[]
		  quasimclist=[]
		  for k in caribures.iterkeys():
			if CARIBU:   caribulist.append(caribures[k])
			if MUSLIM:   muslimlist.append(muslimres[k])
			if QUASIMC:  quasimclist.append(quasimcres[k])
			
		  if MUSLIM and CARIBU: plot(caribulist,muslimlist,'.',label='fractalysis')    
		  if QUASIMC and CARIBU:  plot(caribulist,quasimclist,'.',label='QuasiMC')
		  if nblightsimulation == 2 and QUASIMC and MUSLIM:  plot(muslimlist,quasimclist,'.',label='QuasiMC')
		  
		  title('Caribu/QuasiMc/Fractalysis comparison')
		  if CARIBU : xlabel('Caribu')
		  else : xlabel('Muslim')
		  
		  if nblightsimulation == 3:
			ylabel('Fractalysis/QuasiMc')
		  else:
			if QUASIMC: ylabel('QuasiMc')
			else : ylabel('Fractalysis')
		  
		  M = 0
		  if CARIBU:   M = max(M,max(caribulist))
		  if MUSLIM:   M = max(M,max(muslimlist))
		  if QUASIMC:  M = max(M,max(quasimclist))
		  
		  plot([0,M],[0,M])
		  legend(loc = 0)
		  show()
		
		if MUSLIM:   print 'fractalysis : ', dfract ,'sec.'
		if QUASIMC:  print 'QMc:' ,dqmc ,'sec.'
		if CARIBU:   print 'Caribu: ', dcaribu ,'sec.'
	  return lstring

	  
The complete demo is in 'lighted triuanglemix.lpy' and in 'lpy integrated solution' dataflows.

it results in: 

  .. image:: images/OpenLpy_lightComparison.png

Visualea solution
=================

An alternative method is to leave the lpy program unchanged, and use visualea nodes of environmnental program.

This result in 'visualea solution dataflow'. All the nodes were found in caribu/factalysis packages. QuasiMC has no visualee interface and thus is not used here.

  .. image:: images/OpenLpy_Visualea.png

We however had to code for linking betwenn modules outputs and input of plottiong function.It reads:

  .. code-block:: python
  
	def zip_outputs(caribu_output, muslim_output):
	'''    
	'''
	caribulist = []
	muslim_list = []
	for k in caribu_output:
		if k in muslim_output:
		caribulist.append(caribu_output[k])
		muslim_list.append(muslim_output[k])
	return caribulist, muslim_list,

Note that such a dataflow could be re-used for other Lpy programs / other scene