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

K = S * E / l0

x0 = 1.2 #(m) #initial position of the sphere in the Ox direction
y0 = 0. #(m) #initial position of the sphere in Oy direction
vx0 = 0. #(m.s-1) #initial speed of the sphere in the Ox direction
vy0 = 0.1 #(m.s-1) #initial speed of the sphere in the Oy direction
state0 = [x0,y0,vx0,vy0] #initial state of the system
t0 = 0. #(s) #starting time
dt = 1e-1 #(s) #time step used to observe the system

#end parameters
###################################################
#
print "energy"
#
###################################################
#begin energy
from math import sqrt

def W (t, state) :
	x,y,vx,vy = state
	
	return 0.5 * K * (sqrt(x**2 + y**2) - l0)**2 + 0.5 * m * (vx**2 + vy**2)

#end energy
###################################################
#
print "gradient of energy"
#
###################################################
#begin gradient of energy
def gradW (t, state) :
	x,y,vx,vy = state
	
	l = sqrt(x**2 + y**2)
	Fx = K * (l - l0) / l * x
	Fy = K * (l - l0) / l * y
	
	return (Fx,Fy)

#end gradient of energy
###################################################
#
print "system evolution"
#
###################################################
#begin evolution
def evolution (t, state) :
	x,y,vx,vy = state
	
	Fx,Fy = gradW(t,state)
	return [vx,vy, - Fx / m, - Fy / m]

#end evolution
###################################################
#
print "compute evolution"
#
###################################################
#begin compute evolution
from scipy import zeros
from scipy.integrate import ode

r = ode(evolution)
r.set_integrator('vode', method = 'bdf', with_jacobian = False)
r.set_initial_value(state0,t0)

nb_steps = 1000
res = zeros( (nb_steps,4) )
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
plot(t_list,res[:,0],label = 'x in m')
plot(t_list,res[:,1],label = 'y in m')
plot(t_list,res[:,2],label = 'vx in m.s-1')
plot(t_list,res[:,3],label = 'vy in m.s-1')
plot(t_list,W_list,label = "W in N")
axhline(y = 0,dashes = [2,2])
xlabel("time in s")
legend(loc = 'upper right')
fig.savefig("result.png")
show()
close(fig)

#end plot


