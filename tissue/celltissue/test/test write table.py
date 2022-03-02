from random import randint
from openalea.celltissue import open_table

prop = dict( (pid,randint(0,10) ) for pid in xrange(11) )

f = open_table("table.txt",'w',"%.4d", ";")
f.write(0,prop)
f.close()

prop[10] = randint(0,10)
f = open_table("table.txt",'a')
f.write(1,prop)
f.close()

f = open_table("table.txt",'a')
for i in xrange(3) :
	prop[10] = randint(0,10)
	f.write(i + 2,prop)

f.close()


