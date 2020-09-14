import pandas as pd
import numpy as np
from scipy import optimize
from scipy import integrate
from datetime import datetime

N0 = 0
t = 0
SIR0 = 0

def SIR_model(y_data, population):
    global SIR0, t, N0

    ydata = np.array(y_data)
    t = np.arange(len(ydata))

    N0 = population
    I0=ydata[0]
    S0=N0-I0
    R0=0
    SIR0 = (S0,I0,R0)

    popt = [0.4, 0.1]
    
    fit_odeint(t, *popt)

    popt, pcov = optimize.curve_fit(fit_odeint, t, ydata, bounds=(0,[.6,.2]))
    perr = np.sqrt(np.diag(pcov))

    print('standard deviation errors : ',str(perr), ' start infect:',ydata[0])
    print("Optimal parameters: beta =", popt[0], " and gamma = ", popt[1])

    fitted=fit_odeint(t, *popt)

    return t, fitted

def SIR_model_t(SIR,t,beta,gamma):
    ''' 
        S: susceptible population
        I: infected people
        R: recovered people
        t: time step, mandatory for integral.odeint
        beta: infection spread
        gamma: recovery rate

        dS+dI+dR=0
        S+I+R= N (constant size of population)

    '''

    S,I,R=SIR
    dS_dt=-beta*S*I/N0
    dI_dt=beta*S*I/N0-gamma*I
    dR_dt=gamma*I
    return dS_dt,dI_dt,dR_dt

def fit_odeint(x, beta, gamma):
    return integrate.odeint(SIR_model_t, SIR0, t, args = (beta, gamma))[:,1]