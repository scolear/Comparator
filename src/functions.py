import numpy as np
from numpy.linalg import norm
import pandas as pd

G = 1.487856e-34	# [AU^3*d^-2*kg^-1]

class Planet:
	""" An object with name, mass, pos, vel, acc, frc.
	The force(self, other) function calculates newtonian gravitational force applied upon this object by the 'other'.
	"""
	def __init__(self, name, mass):
		self.name = name
		self.mass = mass
		self.pos = np.array([])
		self.pos_init = np.array([])
		self.vel = np.array([])
		self.vel_init = np.array([])
		self.acc = np.array([0.,0.,0.])
		self.acc_temp = np.array([0.,0.,0.])
		self.frc = np.array([0.,0.,0.])
		
	def force(self, other):
	
		ms = self.mass * other.mass
		dist = other.pos - self.pos
		
		fr = G * ms * dist / (norm(dist)**3)
		return fr
		
		
def SolarSystem_init(init_file_path, inbb):
	""" This function reads a csv file containing the Names, Masses,
	initial positions and velocities of the planets, and stores them in
	a list called 'planets', which it returns.
	Also receives a flag 'inbb', which is True, if it should include the inner planets (except Mercury),
	and False if not.
	"""
	
	df_start = pd.read_csv(init_file_path, skipinitialspace = True, float_precision = 'high')
	planets = []
	
	for i in range(len(df_start)):
		sel_pl = df_start.iloc[i]
		name = sel_pl['Name']
		
		if not inbb:									# Skip inner planets, if inbb flag is False
			if name in ['Venus', 'Earth', 'Mars']:
				continue
		
		mass = sel_pl['Mass']
		planet = Planet(name, mass)
		planet.pos_init = np.array([sel_pl['X'], sel_pl['Y'], sel_pl['Z']])
		planet.vel_init = np.array([sel_pl['VX'], sel_pl['VY'], sel_pl['VZ']])
		planet.pos = planet.pos_init
		planet.vel = planet.vel_init
		
		planets.append(planet)
		
	return planets

	
def Acceleration(N, planets):
	""" Calculates the applied resultant force on 'N' 'planets' by all the others.
	Then calculates acceleration as well.
	"""
	Fmat = [[[0.0] for x in range(N)] for x in range(N)]	# Redrawing the forcematrix every time
	for i in range(N):
		j = i+1
		planets[i].frc = np.array([0.,0.,0.])				# Emptying every time
	
		while j < N:
			Fmat[i][j] = planets[i].force(planets[j])		# Forcematrix
			Fmat[j][i] = (-1) * Fmat[i][j]
			j += 1
		
		for k in range(N):
			planets[i].frc += Fmat[i][k]					# Resultant force
		
		#print(planets[i].name, planets[i].frc) 
		
		planets[i].acc = planets[i].frc / planets[i].mass	# Calculating acceleration


def Euler(N, pl, dt):
	""" One round of Euler integration for N planets, using a fixed dt timestep.
	Putting the acceleration update between the pos and vel updates creates the Euler-Cromer method,
	which is a much more stable alternative."""
	
	Acceleration(N, pl)									# acceleration update
	
	for i in range(N):
		pl[i].pos = pl[i].pos + dt * pl[i].vel			# position update
		pl[i].vel = pl[i].vel + dt * pl[i].acc		# velocity update


def Verlet(n, pl, dt):
	""" Does one round of Verlet integration from initial r, v, a of 'n' number of planets, using 'pl' as a list of planet objects, and using a 'dt' timestep.
	"""
	
	#update x using acc(x) for all planets
	for i in range(n):
		pl[i].pos = pl[i].pos + pl[i].vel * dt + 0.5 * pl[i].acc * dt**2
		#store acc(x) in temp
		pl[i].acc_temp = pl[i].acc
		
	#calc acc(x+1)
	Acceleration(n, pl)
	
	#calc v(x+1) using temp+acc(x+1)
	for i in range(n):
		pl[i].vel = pl[i].vel + 0.5 * (pl[i].acc_temp + pl[i].acc) * dt


def RK4(u, dudt, n, t, h, derivs, planets):

	a21 = (1.0 / 2.0)
	a31 = 0
	a32 = (1.0 / 2.0)
	a41 = 0
	a42 = 0
	a43 = 1.0
	
	c2 = (1.0 / 2.0)
	c3 = (1.0 / 2.0)
	c4 = 1.0
	
	b1 = (1.0 / 6.0)
	b2 = (1.0 / 3.0)
	b3 = (1.0 / 3.0)
	b4 = (1.0 / 6.0)
	
	K1, K2, K3, K4 = [np.array([]) for _ in range(4)]	
	K1 = [np.array([]) for _ in range(n)]								# So it is indexable
	utemp = [np.array([]) for _ in range(n)]
	unew = [np.array([]) for _ in range(n)]
	
	for i in range(n):					  # First step
		K1[i] = dudt[i]					  # Just for brevity
		utemp[i] = u[i] + h*a21*K1[i]
	K2 = derivs(t + c2*h, utemp, planets)	# Second step; Array!
	
	for i in range(n):						
		utemp[i] = u[i] + h*(a31*K1[i] + a32*K2[i])
	K3 = derivs(t + c3*h, utemp, planets)	# Third step
	
	for i in range(n):
		utemp[i] = u[i] + h*(a41*K1[i] + a42*K2[i] + a43*K3[i])
	K4 = derivs(t + c4*h, utemp, planets)	# Fourth step
	
	for i in range(n):						
		unew[i] = u[i] + h*(b1*K1[i] + b2*K2[i] + b3*K3[i] + b4*K4[i])			# Accumulate increments
		
	return unew


def Reset(planets, T, step):
	for i in range(len(planets)):
		planets[i].pos = planets[i].pos_init
		planets[i].vel = planets[i].vel_init
	return 0, 0
	
def total_energy(N, planets):
	""" Calculates total energy of the system of N planets by calculating Kinetic energy K, and Potential energy U."""
	K = 0
	U = 0
	
	for i in range(N):
		K += 0.5 * planets[i].mass * (norm(planets[i].vel))**2
	
	for i in range(N-1):
		for j in range(i+1, N):
			U += (G * planets[i].mass * planets[j].mass) / norm(planets[j].pos - planets[i].pos)

	E = K - U
	return E


def log_data(file, step, T, N, planets):
	""" This function logs the current time T, the total energy of the system, and the x,y,z coordinates of all the objects."""

	Etot = total_energy(N, planets)
	
	if T == 0:
		file.write('Step T Etot ')
		for i in range(N):
			file.write(planets[i].name + 'X ' + planets[i].name + 'Y ' + planets[i].name + 'Z ')
		file.write('\n' + str(step) + ' ' + str(T) + ' ' + str(Etot) + ' ')
		for i in range(N):
			for j in range(3):
				file.write(str(planets[i].pos[j]) + ' ')
	else:
		file.write('\n' + str(step) + ' ' + str(T) + ' ' + str(Etot) + ' ')
		for i in range(N):
			for j in range(3):
				file.write(str(planets[i].pos[j]) + ' ')

def clear_logs():
	del_choice = input('Do you want to clear library of previous logs? [y/n]: ')
	if del_choice == 'y' or del_choice == 'yes':
		for path in iglob('.' + sep + 'logs' + sep + 'output*'):		# Clearing previous runs
			os.remove(path)
		os.remove('.' + sep + 'logs' + sep + 'CPUlogs.csv')
		for path in iglob('.' + sep + 'logs' + sep + 'RKDP_ERRS_*'):
			os.remove(path)
		print("Library cleared.\n")
		return 1
	elif del_choice == 'n' or del_choice == 'no':
		print('Leaving previous logs intact.\n')
		return 0