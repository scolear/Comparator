import os
from os import sep
from glob import iglob
from timeit import default_timer as timer

import numpy as np
import pandas as pd

import functions as fu
from functions import Euler, Verlet, RK4, clear_logs, Reset, Acceleration
import RK_DP as rk
from RK_DP import Derivatives, RungeKutta


def main():
	
	# Decide if log library is to be cleared:
	a = 1
	if os.path.exists('.' + sep + 'logs' + sep + 'CPUlogs.csv'):
		a = clear_logs()

	start = timer()
	try:
		method = w_Ich.result				# Integrator method selection
		Ttot = w_Ttot.result				# Total integration time
		inbb = w_InnPl.result				# Include inner planets?
		ts_range_max = w_ts_range.result[1]
		ts_range_min = w_ts_range.result[0]
		tol_range_max = w_err_range.result[1]
		tol_range_min = w_err_range.result[0]

	except NameError:						# Defaults if not interactive
		print('Running with default values.')
		method = 'All'
		Ttot = 36524
		inbb = False
		ts_range_max = 10
		ts_range_min = 8
		tol_range_max = 6
		tol_range_min = 5

	T = 0									# Time at start of integration
	step = 0
	M = 10									# Logging frequency for fixed ts methods (!!!)
	
	# Creating the initial SS, like a meticulous god:
	planets = fu.SolarSystem_init('.' + sep + 'addendum' + sep + 'start_pos.csv', inbb)
	N = len(planets)						# Number of bodies
	
	# If this is first run / library was cleared, write header for CPUlogs:
	if a == 1:
		cpu_logs = open('.' + sep + 'logs' + sep + 'CPUlogs.csv', 'w')	
		cpu_logs.write('Type Method Name Step CPU\n')
	elif a == 0:
		cpu_logs = open('.' + sep + 'logs' + sep + 'CPUlogs.csv', 'a')
	
	print(f"Number of objects: {N}",
			f"\nTotal time [days]: {Ttot}",
			f"\nTimeStep range: {ts_range_min} - {ts_range_max}",
			f"\nTolerance range: 1.0E-{tol_range_min} - 1.0E-{tol_range_max}\n")

	if method == 'All' or method == 'Euler':
		print('Euler integration...')
	
		for dT in range(ts_range_min, ts_range_max+1):
			
			print('{} days timestep:'.format(dT), end='\t')
			
			# Resetting initial pos,vel,T:
			T, step = Reset(planets, T, step)
			nsteps = Ttot//dT
			
			# Adaptive filenaming:
			filename = '.' + sep + 'logs' + sep + 'output_E_' + str(dT) + '.csv'				
			dat_file = open(filename, 'w')
			name = 'E_' + str(dT)
			
			# Logging header and initial data:
			fu.log_data(dat_file, step, T, N, planets)
	
			startE = timer()
			
			# Start integration:
			# Running it M times before logging:
			for i in range(round(nsteps / M)):
				for j in range(M):								
					step += 1
					T += dT
					Euler(N, planets, dT)
				fu.log_data(dat_file, step, T, N, planets)
			
			# Logging CPU time:
			cpuE = timer() - startE
			print('{:.4f} seconds.\n'.format(cpuE))
			cpu_logs.write('fix E '+name+' '+str(dT)+' '+str(cpuE)+'\n')
			dat_file.close()
			
	if method == 'All' or method == 'Verlet':
		print('Verlet integration...')
	
		for dT in range(ts_range_min, ts_range_max+1):
		
			print('{} days timestep:'.format(dT), end='\t')
			nsteps = Ttot//dT
			T, step = Reset(planets, T, step)					# Resetting initial pos,vel,T
			filename = '.' + sep + 'logs' + sep + 'output_V_' + str(dT) + '.csv'				# adaptive filenaming
			dat_file = open(filename, 'w')
			name = 'V_' + str(dT)
			fu.log_data(dat_file, step, T, N, planets)
	
			startV = timer()
			Acceleration(N,planets)								# initial acceleration
			for i in range(round(nsteps / M)):

				for j in range(M):									# Running it M times before logging
					step += 1
					T += dT
					Verlet(N, planets, dT)						# Stepper

				fu.log_data(dat_file, step, T, N, planets)

			cpuV = timer()-startV
			print('{:.4f} seconds.\n'.format(cpuV))
			dat_file.close()
			
			cpu_logs.write('fix V '+name+' '+str(dT)+' '+str(cpuV)+'\n')

			
	if method == 'All' or method == 'RK4':
		print('RK4 integration...')
		nodes = (2*N)
		
		for dT in range(ts_range_min, ts_range_max+1):
		
			print('{} days timestep:'.format(dT), end='\t')
			nsteps = Ttot//dT
			T, step = Reset(planets, T, step)
			filename = '.' + sep + 'logs' + sep + 'output_RK4_' + str(dT) + '.csv'
			dat_file = open(filename, 'w')
			name = 'RK4_' + str(dT)
			fu.log_data(dat_file, step, T, N, planets)
			
			# Creating the state-vector
			u = []
			for i in range(N):
				u.append(planets[i].pos)
				u.append(planets[i].vel)
			u = np.array(u)
			
			startRK4 = timer()
			
			for i in range(round(nsteps / M)):
				for j in range(M):									# Running it M times before logging
					step += 1
					T += dT
					dudt = Derivatives(T, u, planets)
					u = RK4(u, dudt, nodes, T, dT, Derivatives, planets)		# Step		
				fu.log_data(dat_file, step, T, N, planets)
				
			cpuRK4 = timer()-startRK4
			print('{:.4f} seconds.\n'.format(cpuRK4))
			
			dat_file.close()
			cpu_logs.write('fix RK4 '+name+' '+str(dT)+' '+str(cpuRK4)+'\n')
			
			
	if method == 'All' or method == 'RKDP':
		print('Runge-Kutta Dormand-Prince integration...')
		
		for k in range(tol_range_min, tol_range_max + 1):
		
			tol = pow(10, -k)
			print('{} tolerance:'.format(tol), end='\t')
			dT = ts_range_min
			T, step = Reset(planets, T, step)
			name = 'RKDP_' + str(k)
			filename = '.' + sep + 'logs' + sep + 'output_RKDP_' + str(k) + '.csv'
			errfile = '.' + sep + 'logs' + sep + 'RKDP_ERRS_'+ str(k)+'.csv'
			
			startRK = timer()

			RungeKutta(Ttot, planets, dT, tol, filename, errfile)
			
			cpuRKDP = timer()-startRK
			print('{:.4f} seconds.\n'.format(cpuRKDP))
			
			cpu_logs.write('adap RKDP '+name+' '+str(k)+' '+str(cpuRKDP)+'\n')

			
	cpuTot = timer()-start
	print('Whole program took {0:.2f} seconds.'.format(cpuTot))	
	cpu_logs.close()
	

if __name__ == "__main__":
	main()
