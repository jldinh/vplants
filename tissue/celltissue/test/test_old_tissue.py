from openalea.celltissue import read_old, topen

t, props = read_old("stade2.zip")

t.remove_type(0)
t.remove_type(1)

f = topen("new_tissue.zip", 'w')
f.write(t)
for name, (prop, descr) in props.iteritems() :
	f.write(prop, name, descr)

f.close()

