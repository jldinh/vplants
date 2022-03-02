###################################################
#
print "parameters"
#
###################################################
#begin parameters
m = 1. #(kg) #mass of the sphere attached to the spring
l0 = 1. #(m) #ref length
S = 0.01 #(m2) #section
E = 1e3 #(N.m-2) #Young's modulus
lamb = 1. #(N.m-1.s) #friction coefficient

K = S * E / l0

x0 = 1.2 #(m) #initial position of the sphere
vx0 = 0. #(m.s-1) #initial speed of the sphere
state0 = [x0,vx0] #initial state of the system
t0 = 0. #(s) #starting time
dt = 1e-1 #(s) #time step used to observe the system

#end parameters
###################################################
#
print "energy"
#
###################################################
#begin energy
def W (t, state) :
	x,vx = state
	
	return 0.5 * K * (x - l0)**2 + 0.5 * m * vx**2

#end energy
###################################################
#
print "gradient of energy"
#
###################################################
#begin gradient of energy
def gradW (t, state) :
	x,vx = state
	
	return K * (x - l0) + lamb * vx

#end gradient of energy
###################################################
#
print "system evolution"
#
###################################################
#begin evolution
def evolution (t, state) :
	x,vx = state
	
	F = gradW(t,state)
	return [vx, - F / m]

#end evolution
###################################################
#
print "jacobian"
#
###################################################
#begin jacobian
def jacobian (t, state) :
	x,vx = state
	return [[0,1],[- K / m,- lamb / m]]

#end jacobian
###################################################
#
print "compute evolution"
#
###################################################
#begin compute evolution
from scipy import zeros
from scipy.integrate import ode

r = ode(evolution,jacobian)
r.set_integrator('vode', method = 'bdf', with_jacobian = True)
r.set_initial_value(state0,t0)

nb_steps = 100
res = zeros( (nb_steps,2) )
res[0,:] = state0
W_list = [W(t0,state0)]
t_list = [t0]
for i in xrange(1,nb_steps) :
	state = r.integrate(r.t + dt)
	res[i,:] = state
	W_list.append(W(r.t,state) )
	t_list.append(r.t)

#end compute evolution
###################################################
#
print "plot evolution"
#
###################################################
#begin plot
from pylab import figure,close,plot,show,legend,axhline,xlabel

fig = figure()
plot(t_list,res[:,0] - l0,label = 'dx in m')
plot(t_list,res[:,1],label = 'vx in m.s-1')
plot(t_list,W_list,label = "W in J")
axhline(y = 0,dashes = [2,2])
xlabel("time in s")
legend(loc = 'upper right')
fig.savefig("result.png")
show()
close(fig)

#end plot

