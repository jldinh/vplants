from random import random
from celltissue import open_tissue
from physics.chemistry import Reaction
from root import Root
from physics.chemistry import Diffusion,Transport,Reaction
from celltissue.algo import TissueTopoMesh,TissueGraph,CellPropertyAdapter,PointPropertyAdapter,VertexPropertyAdapter
from celltissue.data import DensityProperty,UniformDensityProperty,EdgeUniformProperty,TPropertyMap

def initialize (r) :

        if (type(r)== int):
           # import a digitalized tissue and the associated pump map
	   f=open_tissue("digit root/mockup02",'r')
	   t,pos,info=f.read()
	   pumps=f.read_property("pumps")
	   f.close()
	   root=Root(t,pos)
	   root.fixed_pumps=pumps
        else :
           root = r

	aux=root.auxin
	t=root.tissue
	root.wallgraph=TissueGraph(0,t)
	pos=root.pos
	root.cell_volume=dict( (wid,t.geometry(0,wid).volume(pos)) for wid in t.wisps(0) )
	root.topomesh=TissueTopoMesh(0,t)

	# create and initialize physiology parameters
	root.timerange = 10000
	root.dt=100.
	root.b=0.2
	root.a=0.5*root.b
	root.gamma=0.1*root.a
	root.beta=100*root.gamma/0.9
	root.alpha=5*root.beta
	root.xi=0.25
	root.zeta=2.
	root.yota =5.
	root.pump_creation=EdgeUniformProperty(TissueGraph(0,t),root.alpha)
	root.pump_decay=EdgeUniformProperty(TissueGraph(0,t),root.beta)
	root.auxin_production_coeff = TPropertyMap(0,0.,((cid,0.) for cid in t.wisps(0)))
        root.auxin_degradation_coeff = TPropertyMap(0,0.,((cid,0.00005) for cid in t.wisps(0)))
	root.diffusion_coeff=UniformDensityProperty(1,t,pos,0.005)


	#initialize auxin field and boundary conditions (boundary valable for tissue 2 whole root)
	for cid in t.wisps(0) :
		aux[cid]=0.1
	root.fixed_conc={367: 0., 381: 0, 371: 1., 372: 1., 373: 1., 374: 1., 375: 1., 376: 1., 377: 1.}
	aux[367]=0.
	aux[381]=0.
	aux[371]=1.
	aux[372]=1.
	aux[373]=1.
	aux[374]=1.
	aux[375]=1.
	aux[376]=1.
	aux[377]=1.

	#initialize pumps strength
	root.fixed_eP = {}
	root.eP = {}
	for wid in t.wisps(0) :
	    for nid in t.neighbors(0,wid) :
	    	root.eP[root.wallgraph.edge(wid,nid)] = 0.
	    	root.fixed_eP[root.wallgraph.edge(wid,nid)] = 0.
     	for wid,(sid,tid) in root.fixed_pumps.iteritems() :
	    root.fixed_eP[root.wallgraph.edge(sid,tid)] = root.alpha/root.beta
	    root.eP[root.wallgraph.edge(sid,tid)] = root.alpha/root.beta

        #complete cap transporter map
        for eid in [(44,43),(17,18),(16,20),(21,22),(85,86),(45,44),(15,17),(14,16),(13,21),(84,85),(48,45),(46,15),(1,14),(12,13),(83,84),(49,48),(0,46),(2,1),(11,12),(82,83),(51,47),(3,0),(5,2),(10,11),(81,82),(43,42),(18,19),(20,23),(22,25),(86,90)]:
            root.fixed_eP[eid] = root.alpha/root.beta
        for eid in [(47,51),(0,3),(2,5),(11,10),(82,81),(50,47),(49,47),(46,0),(1,2),(12,11),(83,82),(48,49),(45,48),(15,46),(14,1),(13,12),(84,83),(44,45),(17,15),(16,14),(21,13),(85,84),(43,44),(18,17),(20,16),(22,21),(86,85),(51,52),(3,4),(5,7),(10,59),(81,59)]:
            root.fixed_eP[eid] = root.alpha/root.beta
        for eid in [(18,43),(17,44),(15,45),(46,48),(46,49)]:
            root.fixed_eP[eid] = root.alpha/root.beta
        for eid in [(43,18),(18,20),(20,22),(22,86),(44,17),(17,16),(16,21),(21,85),(45,15),(15,14),(14,13),(13,84),(48,46),(46,1),(1,12),(12,83),(49,46),(47,0),(0,2),(2,11),(11,82),(51,3),(3,5),(5,10),(10,81)]:
            root.fixed_eP[eid] = root.alpha/root.beta

       	#algorithms (auxin production/degradation, diffusion and transport)
        root.progradation=Reaction(root.auxin_production_coeff,root.auxin_degradation_coeff)
	root.diffusion=Diffusion(root.topomesh,CellPropertyAdapter(root.cell_volume,root.topomesh),PointPropertyAdapter(root.diffusion_coeff.as_quantity(),root.topomesh),CellPropertyAdapter(root.fixed_conc,root.topomesh),{})
	root.transport=Transport(root.wallgraph,VertexPropertyAdapter(root.cell_volume,root.wallgraph),root.eP,VertexPropertyAdapter(root.fixed_conc,root.wallgraph),{})

	#pump autoamplification
	root.autoamplified_pumps = False

	# tools to follow the auxin accumulation and fluxes
	root.aux_plot={}
	root.flux_plot={}
	root.time_plot=[]

 	return root


