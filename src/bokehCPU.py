from glob import iglob
from os import sep

import pandas as pd
import numpy as np
from scipy import stats

from bokeh.io import show, output_notebook
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, NumeralTickFormatter, Label
from bokeh.models.widgets import Panel, Tabs 
from bokeh.transform import factor_cmap
from bokeh.palettes import viridis, inferno, Category20, Category10
output_notebook()

PLOT_WIDTH = 780
PLOT_HEIGHT = 500


def all_cpu_tab(df_CPU):
	""" Creates the tab showing every methods' CPU time, from reading in the dataframe supplied to it.
	"""
	source = ColumnDataSource(df_CPU)
	hover = HoverTool(tooltips=[
		("Name", "@Name"),
		("TimeStep/Tolerance", "@Step"),
		("CPU Time", "@CPU s")	  
		], mode ='vline')

	p1 = figure(x_range = list(df_CPU['Name']), y_range = (0, (1.1*df_CPU['CPU'].max())), plot_height = PLOT_HEIGHT, plot_width = PLOT_WIDTH, tools = "save")

	cmap = factor_cmap('Name', palette = viridis(len(list(df_CPU['Name']))), factors = list(df_CPU['Name']))

	p1.vbar(x ='Name', top ='CPU', source = source, width = 0.9, line_color = 'white', fill_color = cmap)

	p1.title.text = "CPU timings for all methods"
	p1.add_tools(hover)
	p1.xgrid.grid_line_color = None
	p1.x_range.range_padding = 0.1
	p1.yaxis.axis_label = "CPU time [s]"
	p1.xaxis.axis_label = "Method"
	p1.xaxis.major_label_orientation = 1
	p1.ygrid.minor_grid_line_color = 'navy'
	p1.ygrid.minor_grid_line_alpha = 0.1
	
	tab = Panel(child = p1, title = 'CPU: All')
	return tab

	
def fix_cpu_tab(df_CPU):
	"""
	Here comes the second tab, containing Fixed TimeStep methods:
	"""
	dfix = df_CPU[df_CPU['Type'] == 'fix'].copy()
	dfix.Step = dfix.Step.astype(str)
	group = dfix.groupby(['Step', 'Method'])

	source = ColumnDataSource(group)

	p2 = figure(plot_height = PLOT_HEIGHT, plot_width = PLOT_WIDTH, x_range = group, tools = "save")

	cmap2 = factor_cmap('Step_Method', palette = viridis(len(list(dfix.Method.unique()))), factors = sorted(dfix.Method.unique()), start = 1)

	p2.vbar(x = 'Step_Method', top = 'CPU_max', width = 1, line_color = "white", source = source, fill_color = cmap2)

	p2.title.text = "Fixed TimeStep Methods: CPU time"
	p2.add_tools(HoverTool(tooltips = [("Step, Method", "@Step_Method"), ("CPU", "@CPU_max")]))
	p2.xaxis.major_label_orientation = 1
	p2.x_range.range_padding = 0.05
	p2.yaxis.axis_label = "CPU time [s]"
	p2.xaxis.axis_label = "Time Step [days]"

	p2.y_range.start = 0
	p2.ygrid.minor_grid_line_color = 'navy'
	p2.ygrid.minor_grid_line_alpha = 0.1
	
	tab7 = Panel(child = p2, title = 'CPU: Fixed')
	return tab7

	
def energy_change_perstep_tab(dtfrms):

	p3 = figure(plot_height = PLOT_HEIGHT, plot_width = PLOT_WIDTH, toolbar_location="right", tools = "pan, wheel_zoom, box_zoom, reset, save", active_drag = "box_zoom")
	i = 0
	
	for name in dtfrms:
		elem = dtfrms[name]['Etot']
		ser = []
		
		# Calculating change in Total energy by percentage, compared to previous step:
		for j in range(1, len(elem)):
			percentage_change = (((elem[j]) - (elem[j-1])) / (elem[j-1])) * 100
			ser.append(-1*percentage_change)

		# Creating new column in dataframe:
		dtfrms[name]['Ediff'] = pd.Series(ser)
	
		line = p3.line(x = dtfrms[name]['T'], y = dtfrms[name]['Ediff'], legend = name, line_width = 3, line_color = Category20[20][i], line_join = "round",)
	
		p3.add_tools(HoverTool(renderers = [line], tooltips = [("Day", "$x{0,0}"), ("Name", name)]))
		i += 1
		if i >= 20: 
			i = 0

	p3.legend.location = 'bottom_right'
	p3.legend.click_policy = "hide"
	p3.title.text = 'Relative Total Energy change vs. Time'
	p3.yaxis.axis_label = "Change in Total Energy/step [%]"
	p3.xaxis.axis_label = "Time [days]"
	p3.xaxis[0].formatter = NumeralTickFormatter(format="0,0")
	
	tab = Panel(child = p3, title = 'Total Energy change/step')
	return tab

	
def total_energy_change_tab(dtfrms):

	p4 = figure(plot_height = PLOT_HEIGHT, plot_width = PLOT_WIDTH, toolbar_location="right", tools = "pan, wheel_zoom, box_zoom, reset, save", active_drag = "box_zoom")
	i = 0
	
	for name in dtfrms:

		line = p4.line(x = dtfrms[name]['T'], y = dtfrms[name]['percTot'], legend = name, line_width = 3, line_color = Category20[20][i], line_join = "round",)
	
		p4.add_tools(HoverTool(renderers = [line], tooltips = [("Day", "$x{0,0}"), ("Name", name)]))
		i += 1
		if i >= 20: 
			i = 0

	p4.legend.location = 'bottom_right'
	p4.legend.click_policy = "hide"
	p4.title.text = 'Accumulated Total Energy change vs. Time'
	p4.yaxis.axis_label = "Total Energy change [%]"
	p4.xaxis.axis_label = "Time [days]"
	p4.xaxis[0].formatter = NumeralTickFormatter(format="0,0")
	
	tab = Panel(child = p4, title = 'Total Energy change')
	return tab
	
	
def drift_vs_cpu_tab(dtfrms, df_CPU, label):
 
	p5 = figure(plot_height = PLOT_HEIGHT, plot_width = PLOT_WIDTH, toolbar_location="right", tools = "pan, wheel_zoom, box_zoom, reset, save", active_drag = "box_zoom", x_axis_type = "log")
	i = 0
	marker_size = 13
	
	for name in dtfrms:
	
		dataframe = dtfrms[name]
		nam = name[:name.rfind('_')]
		
		# Linear regression fitting on the change of Total Energy:
		y = np.array(dataframe['percTot'])
		x = np.array(dataframe['T'])
		slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
		slope = abs(slope)
		
		# Getting CPU time for method:
		selected_df = df_CPU[df_CPU['Name'] == name].copy()
		CPU_value = selected_df['CPU']
		
		if nam == 'RK4':
			m = p5.circle(x = slope, y = CPU_value, size = marker_size, color = Category10[4][3], line_color = 'black', legend = nam)
		elif nam == 'E':
			m = p5.square(x = slope, y = CPU_value, size = marker_size, color = Category10[4][0], line_color = 'black', legend = nam)
		elif nam == 'RKDP':
			m = p5.triangle(x = slope, y = CPU_value, size = marker_size, color = Category10[4][2], line_color = 'black', legend = nam)
		elif nam == 'V':
			m = p5.inverted_triangle(x = slope, y = CPU_value, size = marker_size, color = Category10[4][1], line_color = 'black', legend = nam)
		
		p5.add_tools(HoverTool(renderers = [m], tooltips = [("CPU","$y"), ("Slope","$x"), ("Method", name)]))
		i += 1
		if i >= 20: 
			i = 0
			
	p5.title.text = 'Energy drift vs. CPU time'
	p5.yaxis.axis_label = "CPU time [sec]"
	p5.y_range.start = 0
	p5.xaxis.axis_label = "Energy Drift"
	p5.xgrid.minor_grid_line_color = 'navy'
	p5.xgrid.minor_grid_line_alpha = 0.1
	
	p5.add_layout(label)
	
	tab = Panel(child = p5, title = 'Energy Drift vs. CPU time')
	return tab
	
	
def path_to_dataframes(path):
	""" This function reads every log file in 'path', 
	and creates a dictionary containing every dataframe, structured as such: 
	{method1_stepsize1 : dataframe11, method1_stepsize2 : dataframe12, ..., 
	method2stepsize1 : dataframe21, ...}
	"""
	
	dtfrms_dict = {}
	for patho in iglob(path):
		nombre = (patho.rstrip('.csv')).lstrip('.' + sep + 'logs' + sep + 'output_')
		dataframe = pd.read_csv(patho, delim_whitespace = True, float_precision = 'high')
		dtfrms_dict[nombre] = dataframe
	return dtfrms_dict


def add_E_change_column(dtfrms):

	for name in dtfrms:
		elem = dtfrms[name]['Etot']
		ser = []
		
		for j in range(0,len(elem)):
			ser.append(-((elem[j]-elem[0])/elem[0]))
			
		dtfrms[name]['percTot'] = pd.Series(ser)
		
	return dtfrms
	
	
def main():
	
	try:
		Ttot = w_Ttot.result
	except NameError:
		Ttot = 36524
	
	# Creating annotation text:
	label_text = 'Integration time: '+str(Ttot)+' days'
	label = Label(x=280, y=397, x_units='screen', y_units='screen', 
			text=label_text, render_mode='canvas',  border_line_color='black', border_line_alpha=0.1, background_fill_color='white', background_fill_alpha=1.0)
	
	df_CPU = pd.read_csv('.' + sep + 'logs' + sep + 'CPUlogs.csv', delim_whitespace = True, float_precision = 'high')
	df_CPU.Method = df_CPU.Method.astype(str)

	# Creating dataframe dictionary:
	dtfrms = path_to_dataframes('.' + sep + 'logs' + sep + 'output_*')
	dtfrms = add_E_change_column(dtfrms)
	
	# Constructing the tabular structure:
	tabs_list = []
	tabs_list.append(all_cpu_tab(df_CPU))
	tabs_list.append(fix_cpu_tab(df_CPU))
	tabs_list.append(total_energy_change_tab(dtfrms))
	tabs_list.append(energy_change_perstep_tab(dtfrms))
	tabs_list.append(drift_vs_cpu_tab(dtfrms, df_CPU, label))
	
	tabs_all = Tabs(tabs=tabs_list)
	show(tabs_all)

	
if __name__ == "__main__":
	main()
