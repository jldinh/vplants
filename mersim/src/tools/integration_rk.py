#!/usr/bin/env python
"""model.py
Canalisation model in 1D.

:version: 2006-05-15 15:21:06CEST
:author:  szymon stoma
"""


class RungeKutta:
    """
    Runge-Kutta 4th order solver
    """
    def __init__(self):
	    pass
        
    def step(self, f, x, t,delta_t):
        # compute the k1's
        k1 = delta_t*f(t,x)
        # compute the k2's
        tmpx = x + k1/2
        k2 = delta_t*f(t+delta_t/2, tmpx)
        # compute the k3's
        tmpx = x + k2/2 
        k3 = delta_t*f(t+delta_t/2, tmpx)
        # compute the k4's
        tmpx = x + k3
        k4 = delta_t*f(t+delta_t, tmpx)
        # compute the new variables
        newx = x + ( k1+2*k2+2*k3+k4 )/6
        return newx

def rk4(f, x, t,delta_t):
        # compute the k1's
        k1 = delta_t*f(x,t)
        # compute the k2's
        tmpx = x + k1/2
        k2 = delta_t*f( tmpx, t+delta_t/2)
        # compute the k3's
        tmpx = x + k2/2 
        k3 = delta_t*f( tmpx, t+delta_t/2)
        # compute the k4's
        tmpx = x + k3
        k4 = delta_t*f( tmpx, t+delta_t)
        # compute the new variables
        newx = x + ( k1+2*k2+2*k3+k4 )/6
        return newx

