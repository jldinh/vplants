#!/usr/bin/env python
"""Canalization test of Mitchison system (for 2 cells).

<Long description of the module functionality.>

:todo:
    Nothing.

:bug:
    None known.
    
:organization:
    INRIA

"""
# Module documentation variables:
__authors__="""Szymon Stoma    
"""
__contact__=""
__license__="Cecill-C"
__date__="<Timestamp>"
__version__="0.1"
__docformat__= "restructuredtext en"
__revision__="$Id: 07-12-03-canPlusUTGinTwoCells.py 7875 2010-02-08 18:24:36Z cokelaer $"

import scipy, scipy.integrate, pylab

class ConfigODE(object):
    """Class containing data for integration.
    
    The main idea is to keep the eq. params  separeted from equations.
    """

    c_desc = """These params with two_cell_Canalization dydt function give two solutions:
    1/ converging to fixed conc. in both cells (1.)
    2/ regular oscilation of concentration
    The bigger diffusion constant the less probable that we will have an oscilation system.
    
    Additional assumptions (in general):
    * No IAA production (the sum of IAA is equal to 2.)
    * PIN tends to 0.1
    * The oscilation depands on diffusion strength.
    * y0: iaa(cell1)=2.;iaa(cell1)=0.;pin(cell1/2->cell2/1)=c_sigma_p/c_theta_p
    * phi funtion: linear with saturation point
    """
    c_sigma_a = 0.0
    c_theta_a = 0.0
    c_gamma = 0.0
    c_delta =  0.0
    c_sigma_p = 0.0001
    c_theta_p = 0.001
    
    c_time_end = 5000
    c_time_step = 10.
    
    c_rtol = .001
    c_atol = .001
    
    y0 = (2,0.,c_sigma_p/c_theta_p,c_sigma_p/c_theta_p) # initial conditions: aux0, aux1, pin0, pin1
    desc=["aux0", "aux1", "pin0->1", "pin1->0"]
    marker = ["r", "g", "b--", "m--"]
    

    @staticmethod 
    def fi( x ):
        """Function defining feedback between the flux and PIN synthesis.
        
        Refer to Fougier (2005) for more details.
        
        Look also: Mitchison (1981), Rolland-Lagan&Prusinkiewicz (2005),  
        
        :parameters:
            x : `float`
                Flux.
        :rtype: `float`
        :return: Dependancy between flux and PIN synthesis. Usually monotonuesly growing, 0 for negative.
        """
        c_step  = 0.01
        if x > 0:
            if x < c_step:
                return x
            else:
                return c_step
        else:
            return 0

def two_cell_Canalization(y, t, config ):
    """Function integrating Canalization equation in Mitchison form for two cells.
    
    <Long description of the function functionality.>
    
    :parameters:
        y : `List4(float)`
            List containing (in order): aux0, aux1, pin0->pin1, pin1->pin0.
        t : `float`
            Time.
        y : `ConfigODE`
            Parameters for the equations.

    :rtype: `List4(float)`
    :return: Next values for y.
    """
    c = config
    aux0, aux1, pin0, pin1 = y
    j0 = (aux0 - aux1)
    j1 = (aux0*pin0 - aux1*pin1)
    aux0p = c.c_sigma_a - c.c_theta_a*aux0 + c.c_gamma* -j0 + c.c_delta*-j1
    aux1p = c.c_sigma_a - c.c_theta_a*aux1 + c.c_gamma* j0 + c.c_delta*j1
    pin0p = c.c_sigma_p - c.c_theta_p*pin0 + c.fi((c.c_gamma*j0+c.c_delta*j1))
    pin1p = c.c_sigma_p - c.c_theta_p*pin1 + c.fi(-(c.c_gamma*j0+c.c_delta*j1))
    #print t, [ aux0p, aux1p, pin0p, pin1p ]
    return [ aux0p, aux1p, pin0p, pin1p ]


def experiment( config, function ):
    c = config
    y0 = c.y0 # initial conditions: aux0, aux1, pin0, pin1
    ts = scipy.arange( 0., c.c_time_end, c.c_time_step) # time values
    y_trajectory = scipy.integrate.odeint( function, y0, ts, rtol=c.c_rtol, atol=c.c_atol, args=(config,))
    
    for i in range(4):
        pylab.plot( ts, y_trajectory[:,i], c.marker[i])
    pylab.legend(c.desc)
    pylab.show()


c = ConfigODE()
print c.c_desc

for j in [0, .005, .01, 0.02, 0.04]:
    for i in [0, .005, .01, 0.02, 0.04]:
        c.c_delta=i
        c.c_gamma=j
        experiment( c, two_cell_Canalization)
        pylab.title("Diffusion strength: gamma="+str(c.c_gamma)+ " delta="+str(c.c_delta))
        pylab.figure()