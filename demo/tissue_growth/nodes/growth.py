###################################################
#
#	growth
#
###################################################
from openalea.physics.mechanics import LinearSpring2D

def grow1 (mesh, pos, l0, growth_threshold, gamma, dt) :
	strain_max = 0.
	strain_min = 10.
	for eid,l in l0.iteritems() :
		pid1,pid2 = mesh.borders(1,eid)
		spring = LinearSpring2D(pid1,pid2,0.,l0[eid])
		strain = spring.strain(pos)
		strain_max = max(strain_max,strain)
		strain_min = min(strain_min,strain)
		if strain > growth_threshold :
			gam = min(gamma[cid] for cid in mesh.regions(1,eid))
			l0[eid] = l0[eid] * (1 + (strain - growth_threshold) * gam * dt)
	print "strain",strain_min,strain_max

def grow2 (mesh, morphogen, l0, growth_threshold, gamma, dt) :
	for eid,l in l0.iteritems() :
		Cmoy = sum(morphogen[cid] for cid in mesh.regions(1,eid)) / mesh.nb_regions(1,eid)
		if Cmoy > growth_threshold :
			gam = min(gamma[cid] for cid in mesh.regions(1,eid))
			l0[eid] = l0[eid] * (1 + (Cmoy - growth_threshold) * gam * dt)

def init_growth (param) :
	param.mesh = None
	param.pos = None
	param.morphogen = {}
	param.l0 = {}
	
	param.growth_threshold = 0.1 #(m.m-1)
	param.gamma = {} #(m.m-1.s-1 TODO) #wall synthesis rate speed
	return param,

def growth_process1 (param) :
	def process (time, dt) :
		grow1(param.mesh,param.pos,param.l0,param.growth_threshold,param.gamma,dt)
	return (process,"growth"),

def growth_process2 (param) :
	def process (time, dt) :
		grow1(param.mesh,param.morphogen,param.l0,param.growth_threshold,param.gamma,dt)
	return (process,"growth"),


