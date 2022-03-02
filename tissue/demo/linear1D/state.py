def state(tissuedb):
    '''Compute the state of a tissue
    '''
    def func () :
        mesh = tissuedb.get_topology("mesh_id","config")
        pos = tissuedb.get_property("position")
        V = tissuedb.get_property("volume")
        for cid in mesh.wisps(1) :
            pid1,pid2 = mesh.borders(1,cid)
            V[cid] = abs(pos[pid2] - pos[pid1])
    # return outputs
    return func,
