from pylab import plot,show,ylim,text,legend

D1 = 1.
D2 = 2.

times = [0.]
IAAL1 = [1.]
IAAR1 = [0.]

IAAL2 = [1.]
IAAR2 = [0.]

def step (dt) :
	times.append( times[-1] + dt )
	flux1 = (IAAL1[-1] - IAAR1[-1]) * D1 * dt
	IAAL1.append( IAAL1[-1] - flux1 )
	IAAR1.append( IAAR1[-1] + flux1 )
	flux2 = (IAAL2[-1] - IAAR2[-1]) * D2 * dt
	IAAL2.append( IAAL2[-1] - flux2 )
	IAAR2.append( IAAR2[-1] + flux2 )

for i in xrange(800) :
	step(0.004)

plot(times,IAAL1,'b',label=r"$left,\ D=1.$")
plot(times,IAAR1,'b--',label=r"$right,\ D=1.$")
plot(times,IAAL2,'g',label=r"$left,\ D=2.$")
plot(times,IAAR2,'g--',label=r"$right,\ D=2.$")
plot( (times[0],times[-1]),(0.5,0.5),'r--')
ylim(0.,1.)
legend(loc = 'lower right')
text(0.,0.5,r"$(left + right)/2.$")
show()

