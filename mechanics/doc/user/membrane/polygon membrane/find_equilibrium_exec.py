execfile("create_mesh.py")
execfile("create_springs.py")
execfile("create_boundary.py")

#logout = open("logout.txt",'w')
execfile("find_equilibrium.py")
#logout.close()

from pickle import dump

dump(dict( (pid,tuple(v) ) for pid,v in pos.iteritems() ),
     open("equilibrium_pos.pkl",'w') )


