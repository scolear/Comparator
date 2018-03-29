import sys
import warnings

import numpy as np
from numpy.linalg import norm

from functions import Acceleration, total_energy

TINY = sys.float_info.epsilon
SAFETY = 0.9
PGROW = -0.2
PSHRINK = -0.25
ERRCON = 1.89E-4
# EPS = 1.0E-06									

		
def Derivatives(t, u, planets):
	""" This function returns the derivatives of the elements of state 'u = [r1, v1, r2, v2, ...]'. Returns velocity and acceleration 'diffs = [dr1dt, dv1dt, ...] = [v1, a1, v2, a2, ...]'.
	"""
	N = len(planets)
	z = 0
	for i in range(N):
		planets[i].pos = u[z]
		planets[i].vel = u[z+1]		# u has 2N elements: r1, v1, r2, v2, etc.
		z += 2
		
	Acceleration(N, planets)		# calculates dvdt = acc on N planets
	diffs = []
	
	for i in range(N):
		diffs.append(planets[i].vel)
		diffs.append(planets[i].acc)
	
	return np.array(diffs)			# Return the staggered array of the differentials. 
	
	
def RKDP(u, dudt, n, t, h, derivs, planets):
	""" Given values for 'n' variables 'u[1,..n]' and their derivatives 'dudt[1..n]' known at 't',
	this function takes one step of Runge-Kutta Dormand-Prince (RKDP) integration over an interval of 'h', 
	and returns the incremented values as array 'unew[1,..n]'. 
	Also returns an estimate of the local truncation error using the embedded fourth-order method.
	The Coefficients are based on Dormand-Prince (1980).
	"""
	a21 = (1.0/5.0)
	a31 = (3.0/40.0)
	a32 = (9.0/40.0)
	a41 = (44.0/45.0)
	a42 = (-56.0/15.0)
	a43 = (32.0/9.0)
	a51 = (19372.0/6561.0)
	a52 = (-25360.0/2187.0)
	a53 = (64448.0/6561.0)
	a54 = (-212.0/729.0)
	a61 = (9017.0/3168.0)
	a62 = (-355.0/33.0)
	a63 = (46732.0/5247.0)
	a64 = (49.0/176.0)
	a65 = (-5103.0/18656.0)
	a71 = (35.0/384.0)
	a72 = (0.0)
	a73 = (500.0/1113.0)
	a74 = (125.0/192.0)
	a75 = (-2187.0/6784.0)
	a76 = (11.0/84.0)
 
	c2 = (1.0 / 5.0)
	c3 = (3.0 / 10.0)
	c4 = (4.0 / 5.0)
	c5 = (8.0 / 9.0)
	c6 = (1.0)
	c7 = (1.0)
 
	b1 = (35.0/384.0)
	b2 = (0.0)
	b3 = (500.0/1113.0)
	b4 = (125.0/192.0)
	b5 = (-2187.0/6784.0)
	b6 = (11.0/84.0)
	b7 = (0.0)
 
	b1p = (5179.0/57600.0)
	b2p = (0.0)
	b3p = (7571.0/16695.0)
	b4p = (393.0/640.0)
	b5p = (-92097.0/339200.0)
	b6p = (187.0/2100.0)
	b7p = (1.0/40.0)
	
	K2, K3, K4, K5, K6, K7 = [np.array([]) for _ in range(6)]	
	utemp = [np.array([]) for _ in range(n)]
	unew = [np.array([]) for _ in range(n)]					# Fifth order
	unewp = [np.array([]) for _ in range(n)]					# Fourth order
	error = [np.array([]) for _ in range(n)]
	
	for i in range(n):						# First step
		utemp[i] = u[i] + h*a21*dudt[i]
	K2 = derivs(t + c2*h, utemp, planets)	# Second step; Array!
	
	for i in range(n):						
		utemp[i] = u[i] + h*(a31*dudt[i] + a32*K2[i])
	K3 = derivs(t + c3*h, utemp, planets)	# Third step
	
	for i in range(n):
		utemp[i] = u[i] + h*(a41*dudt[i] + a42*K2[i] + a43*K3[i])
	K4 = derivs(t + c4*h, utemp, planets)	# Fourth step
	
	for i in range(n):
		utemp[i] = u[i] + h*(a51*dudt[i] + a52*K2[i] + a53*K3[i] + a54*K4[i])
	K5 = derivs(t + c5*h, utemp, planets)	# Fifth step
	
	for i in range(n):
		utemp[i] = u[i] + h*(a61*dudt[i] + a62*K2[i] + a63*K3[i] + a64*K4[i] + a65*K5[i])
	K6 = derivs(t + c6*h, utemp, planets)	# Sixth step
	
	for i in range(n):
		utemp[i] = u[i] + h*(a71*dudt[i] + a73*K3[i] + a74*K4[i] + a75*K5[i] + a76*K6[i])
	K7 = derivs(t + c7*h, utemp, planets)	# Seventh step
	
	for i in range(n):						
		unew[i] = u[i] + h*(b1*dudt[i] + b3*K3[i] + b4*K4[i] + b5*K5[i] + b6*K6[i])			# Accumulate increments
		
		unewp[i] = u[i] + h*(b1p*dudt[i] + b3p*K3[i] + b4p*K4[i] + b5p*K5[i] + b6p*K6[i] + b7p*K7[i]) # Embedded fourth-order
		
		error[i] = abs(unew[i] - unewp[i])	# Calculate error as difference
		
	return unew, error						# Returns an array of incremented values, and the errors of the values


def RKQS(u, dudt, n, t, htry, uscale, derivs, eps, planets, err_file):
	""" 
	--- Runge-Kutta Quality Controlled Step ---
	Fifth order RKDP step with monitoring of local truncation error. 
	'u' = state at the beginning of step, 'dudt' = starting derivatives, 'eps' = tolerance, array 'uscale' = scaling of error-checking,
	Returns the new state 'unew', the next time value 'tnew', and the estimated next step-size 'hnext'.
	Based on the code from "Numerical Recipes in C" (ISBN 0-521-43108-5)
	"""
	
	h = htry					# step-size to be tried
	utry = np.array([])			# state to be tried
	unew = np.array([])		
	errors = np.array([])		# local truncation errors of variables
	scalee = [np.array([]) for _ in range(n)]
	
	while True:
		utry, errors = RKDP(u, dudt, n, t, h, derivs, planets)			# Take a step
		for i in range(n):
			scalee[i] = (errors[i]/uscale[i])/eps
			
		log_errors(err_file, t, n, planets, scalee)
		
		errmax = 0.0											
		for i in range(n):
			errmax = max(errmax, abs(norm(errors[i]/uscale[i])))		# Determine largest error
		errmax /= eps
		
		if (errmax <= 1.0):
			break												# Step succeeded! On to the next one.
		
		htemp = SAFETY * h * errmax**PSHRINK					# Error too large, reduce step-size
		h = max(htemp, 0.1*h)									# Not more than a factor of 10
		tunder = t + h											# Stepping time
		if (tunder == t): warnings.warn('Stepsize underflow in RKQS!')
		
	# After a successful step:
	if (errmax > ERRCON):
		hnext = SAFETY * h * errmax**PGROW
	else:
		hnext = 5.0 * h											# Maximum factor of 5 increase
	hdid = h
	tnew = t + h
	unew = utry
	
	return unew, tnew, hnext, hdid, errmax
		
		
def RungeKutta(Ttot, planets, dtstart, eps, filename, errfile):
	
	
	dat_file_RK = open(filename, 'w')
	err_file = open(errfile,'w')
	h = dtstart
	T = 0
	step = 0
	N = len(planets)
	nodes = (2*N)					# number of ODES

	u = []							# Creating the state-vector
	for i in range(N):		
		u.append(planets[i].pos)
		u.append(planets[i].vel)
	u = np.array(u)

	uscale = [np.array([]) for _ in range(nodes)]
	log_RK(dat_file_RK, step, T, h, 0, N, planets)									# Initial logging
	
	while (T < Ttot):
	
		dudt = Derivatives(T, u, planets)											# Starting diffs
		
		for i in range(nodes):
			uscale[i] = abs(u[i]) + abs(dudt[i] * h) + TINY						# Scaling for monitoring accuracy
		
		if ((T + h - Ttot) * (T + h) > 0.0):										# If step-size oveshoots, decrease.
			h = Ttot - T			
			
		u, T, h, hdid, errmax = RKQS(u, dudt, nodes, T, h, uscale, Derivatives, eps, planets, err_file) # Take a QC step.
		step += 1
		
		log_RK(dat_file_RK, step, T, hdid, errmax, N, planets)							# Log data
		
	dat_file_RK.close()
	err_file.close()


def log_RK(file, step, T, hsize, err, N, planets):
	""" This function logs the current Step, time T, Total energy of the system, StepSize, Error, and the x,y,z coordinates of all the objects."""
	
	Etot = total_energy(N, planets)
	
	if T == 0:
		file.write('Step T Etot StepSize Error ')
		for i in range(N):
			file.write(planets[i].name + 'X ' + planets[i].name + 'Y ' + planets[i].name + 'Z ')
		file.write('\n' + str(step) + ' ' + str(T) + ' ' + str(Etot) + ' ' + str(hsize) + ' ' + str(err) + ' ')
		for i in range(N):
			for j in range(3):
				file.write(str(planets[i].pos[j]) + ' ')
	else:
		file.write('\n' + str(step) + ' ' + str(T) + ' ' + str(Etot) + ' ' + str(hsize) + ' ' + str(err) + ' ')
		for i in range(N):
			for j in range(3):
				file.write(str(planets[i].pos[j]) + ' ')
				
				
def log_errors(file, T, nodes, planets, errors):
	""" This function logs the errors of the RKQS step.
	"""
	if T == 0:
		file.write('T ')
		for i in range(int(nodes/2)):
			file.write(planets[i].name+'_r_err '+planets[i].name+'_v_err ')
		file.write('\n')
	else:
		file.write(str(T) + ' ')
		for i in range(nodes):
			file.write(str(norm(errors[i]))+' ')
		file.write('\n')