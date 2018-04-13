import ipywidgets as widgets
from ipywidgets import interact, interactive, Layout, Box
from IPython.display import display

style = {'description_width': 'initial'}

def integrator_choice(x):
	return x
	
def total_choice(x):
	print("Total integration time in years: {0:.2f} \n".format(x/365.2422))
	print("Integration starts from 1900-01-01 00:00")
	return x
		
def timestep_range(x):
	n = x[1]-x[0] + 1
	print("Fixed-timestep simulations will run {0} times. \n".format(n))
	print("Adaptive Runge-Kutta will start with a timestep of {0} days. \n".format(x[1]))
	return x

def error_range(x):
	n = x[1]-x[0] + 1
	print("RKDP simulation will run {0} times. \n".format(n))
	return x
	
def cg_choice(x):
	return x
	
def innpl_choice(x):
	return x
	
w_Ttot = interactive(total_choice, x = widgets.BoundedIntText(
	value = 36524,
	min = 10,				#integration time limits! [days]
	max = 1000000,			
	description = '2.) Total integration time [days]:',
	style = style,
	disabled = False
))

w_ts_range = interactive(timestep_range, x = widgets.IntRangeSlider(
	value=[8, 10],
	min=1,
	max=20,
	step=1,
	description='3.) TimeStep range:',
	disabled=False,
	continuous_update=False,
	orientation='horizontal',
	readout=True,
	style = style,
	readout_format='d',
))

w_err_range = interactive(error_range, x = widgets.IntRangeSlider(
	value=[5, 7],
	min=4,
	max=10,
	step=1,
	description='4.) RKDP tolerance: 1.0E-',
	disabled=False,
	continuous_update=False,
	orientation='horizontal',
	readout=True,
	style = style,
	readout_format='d',
))

w_Ich = interactive(integrator_choice, x = widgets.ToggleButtons(
	options = ['Euler', 'Verlet', 'RK4', 'RKDP', 'All'],
	value = 'All',
	description = '1.) Integrator:',
	disabled = False,
	button_style = '',
	layout = Layout(flex_flow='column'),
	tooltips = ['A simple forward Euler integrator', 'Velocity Verlet, a symplectic integrator', 'Fixed-timestep Runge-Kutta 4', 'Adaptive Runge-Kutta Dormand-Prince integrator', 'Run all integrators successively']
))

w_cg = interactive(cg_choice, x = widgets.Checkbox(
	value = True,
	description = 'Include 67P/C-G'
))

w_InnPl = interactive(innpl_choice, x = widgets.Checkbox(
	value = False,
	description = 'Include inner planets'
))

print("Please set the required parameters:")
display(w_Ich)
display(w_Ttot)
display(w_ts_range)
display(w_err_range)
display(w_cg)
display(w_InnPl)