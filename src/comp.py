import numpy as np
import pandas as pd
import os
from os import sep
from glob import iglob
from timeit import default_timer as timer

import functions as fu
from functions import clear_logs
import RK_DP as rk


def main():
	
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
	cpu_logs = open('.' + sep + 'logs' + sep + 'CPUlogs.csv', 'a')
	if a == 1:								
		cpu_logs.write('Type Method Name Step CPU\n')
	

	print('Number of objects:', N,
			'\nTotal time [days]:', Ttot, 
			'\nTimeStep range: {} - {}'.format(ts_range_min,ts_range_max),
			'\nTolerance range: 1.0E-{} - 1.0E-{}'.format(tol_range_min, tol_range_max),
			'\n')
	
	if method == 'All' or method == 'Euler':
		print('Euler integration...')
	
		for dT in range(ts_range_min, ts_range_max+1):
			
			print('{} days timestep:'.format(dT), end='\t')
			nsteps = Ttot//dT
			T, step = fu.Reset(planets, T, step)					# Resetting initial pos,vel,T
			filename = '.' + sep + 'logs' + sep + 'output_E_' + str(dT) + '.csv'				# adaptive filenaming
			dat_file = open(filename, 'w')
			name = 'E_' + str(dT)
			fu.log_data(dat_file, step, T, N, planets)
	
			startE = timer()
			for i in range(round(nsteps / M)):

				for j in range(M):									# Running it M times before logging
					step += 1
					T += dT
					fu.Euler(N, planets, dT)						# Stepper

				fu.log_data(dat_file, step, T, N, planets)
				
			cpuE = timer() - startE
			print('{:.4f} seconds.\n'.format(cpuE))
			dat_file.close()
			
			cpu_logs.write('fix E '+name+' '+str(dT)+' '+str(cpuE)+'\n')
			
	if method == 'All' or method == 'Verlet':
		print('Verlet integration...')
	
		for dT in range(ts_range_min, ts_range_max+1):
		
			print('{} days timestep:'.format(dT), end='\t')
			nsteps = Ttot//dT
			T, step = fu.Reset(planets, T, step)					# Resetting initial pos,vel,T
			filename = '.' + sep + 'logs' + sep + 'output_V_' + str(dT) + '.csv'				# adaptive filenaming
			dat_file = open(filename, 'w')
			name = 'V_' + str(dT)
			fu.log_data(dat_file, step, T, N, planets)
	
			startV = timer()
			fu.Acceleration(N,planets)								# initial acceleration
			for i in range(round(nsteps / M)):

				for j in range(M):									# Running it M times before logging
					step += 1
					T += dT
					fu.Verlet(N, planets, dT)						# Stepper

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
			T, step = fu.Reset(planets, T, step)
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
					
					dudt = rk.Derivatives(T, u, planets)
					u = fu.RK4(u, dudt, nodes, T, dT, rk.Derivatives, planets)		# Step
					
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
			T, step = fu.Reset(planets, T, step)
			name = 'RKDP_' + str(k)
			filename = '.' + sep + 'logs' + sep + 'output_RKDP_' + str(k) + '.csv'
			errfile = '.' + sep + 'logs' + sep + 'RKDP_ERRS_'+ str(k)+'.csv'
			
			startRK = timer()
			rk.RungeKutta(Ttot, planets, dT, tol, filename, errfile)
			
			cpuRKDP = timer()-startRK
			print('{:.4f} seconds.\n'.format(cpuRKDP))
			
			cpu_logs.write('adap RKDP '+name+' '+str(k)+' '+str(cpuRKDP)+'\n')
		
	cpuTot = timer()-start
	print('Whole program took {0:.2f} seconds.'.format(cpuTot))
	
	cpu_logs.close()
	

if __name__ == "__main__":
	main()
