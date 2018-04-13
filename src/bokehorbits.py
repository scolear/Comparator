from glob import iglob
from os import sep

import pandas as pd
import numpy as np

from bokeh.io import show, output_notebook
from bokeh.plotting import figure
from bokeh.models.widgets import Panel, Tabs
from bokeh.models import ColumnDataSource, HoverTool
output_notebook()

def page_setup(pages, df_JPL_CG, df_JPL_JUP, hover):
	# Plotting JPL data for C-G on every figure and setting up styling
	sourceCG = ColumnDataSource(df_JPL_CG)
	sourceJUP = ColumnDataSource(df_JPL_JUP)

	for page in pages:
		page.line(x = 'X', y = 'Y', source = sourceCG, line_color = 'black', line_dash = 'solid', legend = 'JPL_CG')
		page.line(x = 'X', y = 'Y', source = sourceJUP, line_color = 'gray', line_dash = [10, 140], line_width = 1, legend = 'JPL_JUP')
		page.add_tools(hover)
		page.yaxis.axis_label = "Y [AU]"
		page.xaxis.axis_label = "X [AU]"
		

def main():

	if w_cg.result is True:
		name_list = ["67P/C-G", "Jupiter", "Saturn", "Uranus", "Neptune"]
		name = "67P/C-G"
	else:
		name_list = ["Jupiter", "Saturn", "Uranus", "Neptune"]
		name = "Jupiter"
	
	ts_range_max = w_ts_range.result[1]
	ts_range_min = w_ts_range.result[0]
	tol_range_max = w_err_range.result[1]
	tol_range_min = w_err_range.result[0]	

	df_JPL_JUP = pd.read_csv('.' + sep + 'addendum' + sep + 'Jupiter_1900_2000_1.csv', skipinitialspace = True, float_precision = 'high')
	df_JPL_CG = pd.read_csv('.' + sep + 'addendum' + sep + '67P_1900_2000_1.csv', skipinitialspace = True, float_precision = 'high')
	
	# Creating T column of JPL dataframes:
	for df in [df_JPL_JUP, df_JPL_CG]:
		elem = df['JDTDB']
		sera = []
		for i in range(1, len(elem)):
			sera.append(elem[i] - elem[0])
		df['T'] = pd.Series(sera)

	pages = []

	plot_width = 700
	plot_height = 500
	circle_size = 6

	hover = HoverTool(tooltips=[
		("index", "$index"),
		("(x,y)", "($x, $y)"),
		("Day", "@T"),
	])

	page1 = figure(plot_width = plot_width, plot_height = plot_height, active_drag = "box_zoom")
	pages.append(page1)
	
	pageE = figure(plot_width = plot_width, plot_height = plot_height, active_drag = "box_zoom")
	pages.append(pageE)

	pageV = figure(plot_width = plot_width, plot_height = plot_height, active_drag = "box_zoom") 
	pages.append(pageV)

	pageRK4 = figure(plot_width = plot_width, plot_height = plot_height, active_drag = "box_zoom")
	pages.append(pageRK4)

	pageRKDP = figure(plot_width = plot_width, plot_height = plot_height, active_drag = "box_zoom")
	pages.append(pageRKDP)
	
	# Setting up pages and plotting JPL:
	page_setup(pages, df_JPL_CG, df_JPL_JUP, hover)
	
	alpha_arr_fix = np.linspace(0.1, 1.0, num=(ts_range_max - ts_range_min + 1))
	alpha_arr_ada = np.linspace(0.1, 1.0, num=(tol_range_max - tol_range_min + 1))
	i, j, k, l = 0, 0, 0, 0
	
	for path in iglob('.' + sep + 'logs' + sep + 'output_*'):					# Reading every dataframe produced by 'comp.py'

		nombre = (path.rstrip('.csv')).lstrip('.' + sep + 'logs' + sep + 'output_')
		ts_tol = int((path[path.rfind('_') + 1:]).rstrip('.csv'))
	
		dataframe = pd.read_csv(path, delim_whitespace = True, float_precision = 'high')
	
		source = ColumnDataSource(dataframe)
		
		namex = name+'X'
		namey = name+'Y'
	
		if nombre[:nombre.rfind('_')] == 'RK4':
			r, g, b = 255, 0, 0
			pageRK4.circle(x = namex, y = namey, source = source, size = circle_size, color = (r, g, b), fill_alpha = alpha_arr_fix[i], line_color = 'black', legend = nombre)
			page1.circle(x = namex, y = namey, source = source, size = circle_size, color = (r, g, b), fill_alpha = alpha_arr_fix[i], line_color = 'black', legend = nombre)
			i += 1
		elif nombre[:nombre.rfind('_')] == 'E':
			r, g, b = 0, 0, 255
			pageE.circle(x = namex, y = namey, source = source, size = circle_size, color = ((r+5*ts_tol), g+10*ts_tol, b), fill_alpha = alpha_arr_fix[j], line_color = 'black', legend = nombre)
			page1.circle(x = namex, y = namey, source = source, size = circle_size, color = ((r+5*ts_tol), g+10*ts_tol, b), fill_alpha = alpha_arr_fix[j], line_color = 'black', legend = nombre)
			j += 1
		
		elif nombre[:nombre.rfind('_')] == 'RKDP':
			r, g, b = 0, 255, 0
			pageRKDP.circle(x = namex, y = namey, source = source, size = circle_size, color = (r+5*ts_tol, g, b+10*ts_tol), fill_alpha = alpha_arr_fix[k], line_color = 'black', legend = nombre)
			page1.circle(x = namex, y = namey, source = source, size = circle_size, color = (r+5*ts_tol, g, b+10*ts_tol), fill_alpha = alpha_arr_fix[k], line_color = 'black', legend = nombre)
			k += 1
		
		elif nombre[:nombre.rfind('_')] == 'V':
			r, g, b = 255, 255, 0
			pageV.circle(x = namex, y = namey, source = source, size = circle_size, color = (r, g, b+10*ts_tol), fill_alpha = alpha_arr_fix[l], line_color = 'black', legend = nombre)
			page1.circle(x = namex, y = namey, source = source, size = circle_size, color = (r, g, b+10*ts_tol), fill_alpha = alpha_arr_fix[l], line_color = 'black', legend = nombre)
			l += 1
			
	page1.legend.location = "bottom_left"
	
	tablist = []
	z = 0
	for page in pages:
	
		page.legend.click_policy = "hide"
		
		title = ['All', 'Euler', 'Verlet', 'RK4', 'RKDP']
		tab = Panel(child = page, title = title[z])
		tablist.append(tab)
		z += 1
		
	tabs = Tabs(tabs = tablist)
	show(tabs)
	
if __name__ == "__main__":
	main()
