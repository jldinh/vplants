###################################################
#
#	mechanics, expansion
#
###################################################
from vplants.plantgl.math import Vector2,norm
from openalea.tissueshape import centroid,edge_length,face_surface_2D
from openalea.physics.mechanics import LinearSpring2D,ForwardEuler2D

def compute_turgor_forces (mesh, pos, turgor) :
	turgor_force = dict( (pid,Vector2()) for pid in mesh.wisps(0) )
	for cid,P in turgor.iteritems() :
		bary = centroid(mesh,pos,2,cid)
		for eid in mesh.borders(2,cid) :
			pid1,pid2 = mesh.borders(1,eid)
			#direction
			ori = pos[pid2] - pos[pid1]
			#normal
			normal = Vector2(ori.y,-ori.x)
			if normal * ( (pos[pid1] + pos[pid2]) / 2. - bary) < 0 :
				normal *= -1
			#update forces
			turgor_force[pid1] += normal * (P / 2.)
			turgor_force[pid2] += normal * (P / 2.)
	return turgor_force

def compute_meca_equilibrium (mesh, pos, K, l0, weight, turgor) : #perform computation
	#springs
	springs = []
	for eid in mesh.wisps(1) :
		pid1,pid2 = mesh.borders(1,eid)
		springs.append( LinearSpring2D(pid1,pid2,K[eid],l0[eid]) )
	#physical boundary condition
	def bound (solver) :
		turgor_forces = compute_turgor_forces(mesh,pos,turgor)
		#update solver
		for pid,F in turgor_forces.iteritems() :
			solver.set_force(pid,solver.fx(pid) + F.x,solver.fy(pid) + F.y)
	#find equilibrium
	algo = ForwardEuler2D(weight,springs,bound)
	dt_meca = 0.1
	epsilon = 10.
	while epsilon > 0.0001 :
		mem_pos = dict( (pid,Vector2(vec)) for pid,vec in pos.iteritems() )
		algo.deform(pos,dt_meca,10)
		epsilon = max(norm(pos[pid] - vec) for pid,vec in mem_pos.iteritems())
		print "meca",epsilon

def init_mechanics (param) :
	param.mesh = None
	param.pos = None
	
	param.K = {} #stiffness of walls in N.m-1.m
	param.l0 = {} #rest length of walls in m
	param.weight = {} #weigth of points in kg
	param.turgor = {} #turgor pressure in MPa
	return param,

def mechanics_process (param) : #TODO passer les morphogens en argument
	def process (time, dt) :
		#push morphogen state
		morphogen_quantity = dict( (cid,conc * face_surface_2D(param.mesh,param.pos,cid)) for cid,conc in param.morphogen.iteritems() )
		#expand
		compute_meca_equilibrium(param.mesh,param.pos,param.K,param.l0,param.weight,param.turgor)
		#pop morphogen state
		param.morphogen = dict( (cid,q / face_surface_2D(param.mesh,param.pos,cid)) for cid,q in morphogen_quantity.iteritems() )
	return (process,"mechanics"),

