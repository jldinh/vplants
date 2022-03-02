from pylab import plot,show,ylim,text,legend

alpha1 = 2.
beta1 = 2.

alpha2 = 0.5
beta2 = 0.5

times = [0.]
IAA1 = [0.]
IAA2 = [0.]

def step (dt) :
	times.append( times[-1] + dt )
	IAA1.append( (IAA1[-1] + alpha1 * dt) / (1 + beta1 * dt) )
	IAA2.append( (IAA2[-1] + alpha2 * dt) / (1 + beta2 * dt) )

for i in xrange(800) :
	step(0.01)

plot(times,IAA1,label=r"$\alpha=2.,\ \beta=2.$")
plot(times,IAA2,label=r"$\alpha=0.5,\ \beta=0.5$")
plot( (times[0],times[-1]),(1.,1.),'r--')
ylim(0.,1.1)
legend(loc = 'lower right')
text(0.2,1.,r"$\alpha / \beta$")
show()

