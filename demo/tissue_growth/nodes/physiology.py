###################################################
#
#	physiology
#
###################################################
from openalea.tissueshape import edge_length,face_surface_2D
from openalea.physics.chemistry import GraphDiffusion,Reaction

def compute_physio_equilibrium (mesh, graph, pos, morphogen, alpha, beta, D) :#perform computation
	#reaction
	algo_reaction = Reaction(alpha,beta)
	#diffusion
	V = dict( (vid,face_surface_2D(mesh,pos,vid)) for vid in graph.vertices() ) #(m3) volume of the cells
	Dcoeff = dict( (eid,edge_length(mesh,pos,eid) * val) for eid,val in D.iteritems() ) #(m.s-1) diffusion constant of the walls
	algo_diffusion = GraphDiffusion(graph,V,Dcoeff)
	#find equilibrium
	dt_physio = 0.1
	epsilon = 10.
	while epsilon > 0.001 :
		mem_morphogen = dict(morphogen)
		for i in xrange(10) :
			algo_reaction.react(morphogen,dt_physio,1)
			algo_diffusion.react(morphogen,dt_physio,1)
		epsilon = max( abs(morphogen[cid] - conc) for cid,conc in mem_morphogen.iteritems() )
		print "physio",epsilon

def init_physiology (param) :
	param.mesh = None
	param.graph = None
	param.pos = None
	
	param.morphogen = {} #concentration in morphogen in mol.m-2
	param.alpha = {} #creation in mol.s-1
	param.beta = {} #decay rate in mol.mol-1.s-1
	param.D = {} #diffusivity of walls in mol.m-2.s-1
	return param,

def physiology_process (param) :
	def process (time, dt) :
		compute_physio_equilibrium(param.mesh,param.graph,param.pos,param.morphogen,param.alpha,param.beta,param.D)
	return (process,"physiology"),

