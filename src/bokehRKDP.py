"""
This module plots the error terms of the RKDP method
(differences of the fourth and fifth order methods) using bokeh.
Also plots StepSize changes in a subplot, using a shared y_axes range.
"""
from os import sep
import pandas as pd
from bokeh.io import show, output_notebook, export_png, save, output_file
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, BoxAnnotation
from bokeh.models.widgets import Panel, Tabs
from bokeh.layouts import column

from glob import iglob
output_notebook()

PLOT_WIDTH = 700
PLOT_HEIGHT = 500

def process_rkdp_err(path):
	""" This function gets a filepath (path) to a log file of errors in the RKDP method, and draws the two subplots using dataframes. Creates the layout, which is stored in a tab; the tab is returned.
	"""
	name = (path.rstrip('.csv')).lstrip('.' + sep + 'logs' + sep + 'RKDP_')
	df_ERR = pd.read_csv(path, delim_whitespace= True, float_precision = 'high')
	
	method = '.' + sep + 'logs' + sep + 'output_RKDP_'+(name.lstrip('ERRS_'))+'.csv'
	df_RKDP = pd.read_csv(method, delim_whitespace= True, float_precision = 'high')
	
	source = ColumnDataSource(df_ERR)
	source2 = ColumnDataSource(df_RKDP)
	
	p = figure(plot_height = (3*PLOT_HEIGHT//4), plot_width = PLOT_WIDTH, title = 'Scaled error of variables vs. Time', active_drag = "box_zoom")
	
	for col in source.column_names[1:-1]:
		if col == '67P/C-G_r_err':
			color = 'red'
			legend = '67P/C-G(pos)'
		elif col == '67P/C-G_v_err':
			color = 'gold'
			legend = '67P/C-G(vel)'
		elif col == 'Venus_r_err':
			color = 'navy'
			legend = 'Venus(pos)'
		else: 
			color = 'green'
			legend = 'Other'
			
		line = p.line(x = 'T', y = col, source = source, line_width = 2, color = color, legend = legend)
		p.add_tools(HoverTool(renderers = [line], tooltips=[("Name", col)]))
	
	p.yaxis.axis_label = "Error (scaled)"
	p.ygrid.minor_grid_line_color = 'navy'
	p.ygrid.minor_grid_line_alpha = 0.1
	
	error_box = BoxAnnotation(top=1, bottom = 0, fill_alpha=0.1, fill_color='gray')
	p.add_layout(error_box)
	
	# Creating the subplot of StepSizes, and linking the two x_axes together:
	
	p2 = figure(plot_width = PLOT_WIDTH, plot_height = (PLOT_HEIGHT//3), x_range = p.x_range, tools = "save")
	p2.line(x = 'T', y = 'StepSize', source = source2, color = 'navy')
	
	p2.yaxis.axis_label = "Time Step [days]"
	p2.xaxis.axis_label = "Time [days]"
	p2.add_tools(HoverTool(tooltips = [("Time", "@T{0}"), ("Step size", "@StepSize")], mode = 'vline'))
	
	lay = column(p, p2)							# Outlay
	
	tab = Panel(child = lay, title = str(name))
	#output_file((str(name)+'.png'))
	#export_png(tab, filename = (str(name)+'.png'))
	return tab
	

def main():

	tablist = []
	
	for path in iglob('.' + sep + 'logs' + sep + 'RKDP_*'):
		tablist.append(process_rkdp_err(path))
	
	tabs = Tabs(tabs=tablist)
	show(tabs)

	
if __name__ == "__main__":
	main()