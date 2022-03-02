def division(tissuedb, prop, threshold):
	''' Divide the tissue for all cells
	where prop > threshold
	'''
	def func () :
		# write the node code here.
		mesh = tissuedb.get_topology("mesh_id","config")
		pos = tissuedb.get_property("position")
		for cid,val in prop.items() :
			if val > threshold :
				#print "divide",cid
				pid1,pid2 = mesh.borders(1,cid)
				pid = mesh.add_wisp(0)
				pos[pid] = (pos[pid1] + pos[pid2]) / 2.
				cid1 = mesh.add_wisp(1)
				cid2 = mesh.add_wisp(1)
				for propname,quant in tissuedb._property.iteritems() :#TODO
					try :
						val = quant.pop(cid)
						quant[cid1] = val
						quant[cid2] = val
					except KeyError :
						pass
				mesh.remove_wisp(1,cid)
				mesh.link(1,cid1,pid1)
				mesh.link(1,cid1,pid)
				mesh.link(1,cid2,pid2)
				mesh.link(1,cid2,pid)
	
	# return outputs
	return func,

