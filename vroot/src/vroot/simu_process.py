from openalea.physics.chemistry import GraphDiffusion,Reaction,GraphTransport,FixedConcentration,FixedFlux
from simu_params import *

def constraint_auxin (root, time, dt) :
	algo=FixedConcentration(root.fixed_concentration)
	algo.react(root.auxin,dt)


def react_auxin (root, time, dt) :
	algo=Reaction(root.auxin_creation,root.auxin_degradation)
	algo.react(root.auxin,dt)


def diffuse_auxin (root, time, dt) :
	algo=GraphDiffusion(root.diffusion_graph(), root.cell_volume, root.diffusion_coeff)
	return algo.react(root.auxin,dt)

def diffuse_wall_auxin (root, time, dt) :
	algo=GraphDiffusion(root.WW_diffusion_graph(), root.wall_surface, root.diffusion_coeff)
	return algo.react(root.auxin,dt)

def transport_auxin (root, time, dt) :
	pumps={}
	for pid,pump_value in root.relative_pumps.iteritems() :
		wid=root.wall(pid)
		pumps[pid]=pump_value*global_pump_force*root.wall_surface[wid]
	algo=GraphTransport(root.transport_graph(), root.cell_volume, pumps)
	return algo.react(root.auxin,dt)


def react_pumps (root, time, dt) :
	algo=Reaction(root.pump_creation,root.pump_degradation)
	algo.react(root.relative_pumps,dt)
	for pid in root.relative_pumps.keys():
		if root.relative_pumps[pid] > 1 :
			root.relative_pumps[pid] = 1
		if root.relative_pumps[pid] < 0 :
			root.relative_pumps[pid] = 0


def linear_phi (coeff, flux) :
	return coeff*flux

def cubic_phi (coeff, flux) :
	return coeff*flux**3

def quadratic_phi (coeff, flux) :
	if (flux>0) :
		ret = coeff*flux**2
	else :
		ret = 0 #- coeff*flux**2
	return ret

def canalize_auxin (root, time , dt) :
	total_fluxes= {}
	#compute diffusion and store fluxes
	dg = root.diffusion_graph()
	diff_fluxes = diffuse_auxin(root,time,dt)
	for eid, flux in diff_fluxes.iteritems() :
		total_fluxes[(dg.source(eid),dg.target(eid))] = flux
		total_fluxes[(dg.target(eid),dg.source(eid))] = -flux
	#compute transport and store fluxes
	tg = root.transport_graph()
	trans_fluxes = transport_auxin(root,time,dt)
	for eid, flux in trans_fluxes.iteritems() :
		total_fluxes[(tg.source(eid),tg.target(eid))]+=flux
		total_fluxes[(tg.target(eid),tg.source(eid))]-=flux
	#compute the new pump distribution according to canalization hypothesis
	for pid in tg.edges() :
		flux = total_fluxes[(tg.source(pid),tg.target(pid))]
		root.pump_creation[pid] = base_pump_creation + linear_phi(canalization_coeff,flux)



def intersection(list1, list2):
	int_dict = {}
	list1_dict = {}
	for e in list1:
		list1_dict[e] = 1
	for e in list2:
		if list1_dict.has_key(e):
			int_dict[e] = 1
	return int_dict.keys()


def union(list1, list2):
	union_dict = {}
	for e in list1:
		union_dict[e] = 1
	for e in list2:
		union_dict[e] = 1
	return union_dict.keys()




def orient_flux(root, time, dt) : 

	tg = root.transport_graph()
	cap = [44,17,16,21,85,45,15,14,13,84,48,46,1,12,83,49,0,2,11,82,50,47]
	up = [(44,43),(17,18),(16,20),(21,22),(85,86),(45,44),(15,17),(14,16),(13,21),(84,85),(48,45),(46,15),(1,14),(12,13),(83,84),(49,48),(0,46),(2,1),(11,12),(82,83),(51,47),(3,0),(5,2),(10,11),(81,82)]
	down = [(47,51),(0,3),(2,5),(11,10),(82,81),(50,47),(49,47),(46,0),(1,2),(12,11),(83,82),(48,49),(45,48),(15,46),(14,1),(13,12),(84,83),(44,45),(17,15),(16,14),(21,13),(85,84),(43,44),(18,17),(20,16),(22,21),(86,85)]
	side = 1



	if time in range(50,75)+range(100,125)+range(150,175):
		for cid in cap:
			for wid in root.walls_of_cell[cid]:
				for pid in root.associated_pumps(wid):
					if tg.source(pid) == cid:
						root.relative_pumps[pid] = 0.
		for (cid1,cid2) in up:
                	for wid in intersection(root.walls_of_cell[cid1],root.walls_of_cell[cid2]):
                		for pid in root.associated_pumps(wid):
                			if tg.source(pid) == cid1:
                				root.relative_pumps[pid] = 1.
                for (cid1,cid2) in down:
                	for wid in intersection(root.walls_of_cell[cid1],root.walls_of_cell[cid2]):
                		for pid in root.associated_pumps(wid):
                			if tg.source(pid) == cid1:
						root.relative_pumps[pid] = 0.

	if time in range(75,100)+range(125,150)+range(175,200):
		for cid in cap:
			for wid in root.walls_of_cell[cid]:
				for pid in root.associated_pumps(wid):
					if tg.source(pid) == cid:
						root.relative_pumps[pid] = 0.
		for (cid1,cid2) in up:
                	for wid in intersection(root.walls_of_cell[cid1],root.walls_of_cell[cid2]):
                		for pid in root.associated_pumps(wid):
                			if tg.source(pid) == cid1:
                				root.relative_pumps[pid] = 0.
                for (cid1,cid2) in down:
                	for wid in intersection(root.walls_of_cell[cid1],root.walls_of_cell[cid2]):
                		for pid in root.associated_pumps(wid):
                			if tg.source(pid) == cid1:
						root.relative_pumps[pid] = 1.



#		for (cid1,cid2) in down:
#                	for wid in intersection(root.walls_of_cell[cid1],root.walls_of_cell[cid2]):
#                		root.relative_pumps[wid] = 0.
#
#	else :
##		for (cid1,cid2) in down:
#                	for wid in intersection(root.walls_of_cell[cid1],root.walls_of_cell[cid2]):
#                		root.relative_pumps[wid] = 1.
##		for (cid1,cid2) in up:
 #               	for wid in intersection(root.walls_of_cell[cid1],root.walls_of_cell[cid2]):
 #               		root.relative_pumps[wid] = 0.

