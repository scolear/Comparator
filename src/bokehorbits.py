from glob import iglob
from os import sep
import math

from astroquery.jplhorizons import Horizons

import pandas as pd
import numpy as np

from bokeh.io import show, output_notebook
from bokeh.plotting import figure
from bokeh.models.widgets import Panel, Tabs
from bokeh.models import ColumnDataSource, HoverTool
output_notebook()

def jd_to_date(jd):
    """
    Convert Julian Day to date.
	:Author: Matt Davis
    
    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet', 
        4th ed., Duffet-Smith and Zwart, 2011.
    
    Parameters
    ----------
    jd : float
        Julian Day
        
    Returns
    -------
    year : int
        Year as integer. Years preceding 1 A.D. should be 0 or negative.
        The year before 1 A.D. is 0, 10 B.C. is year -9.
        
    month : int
        Month as integer, Jan = 1, Feb. = 2, etc.
    
    day : float
        Day, may contain fractional part.
        
    Examples
    --------
    Convert Julian Day 2446113.75 to year, month, and day.
    
    >>> jd_to_date(2446113.75)
    (1985, 2, 17.25)
    
    """
    jd = jd + 0.5
    
    F, I = math.modf(jd)
    I = int(I)
    
    A = math.trunc((I - 1867216.25)/36524.25)
    
    if I > 2299160:
        B = I + 1 + A - math.trunc(A / 4.)
    else:
        B = I
        
    C = B + 1524
    
    D = math.trunc((C - 122.1) / 365.25)
    
    E = math.trunc(365.25 * D)
    
    G = math.trunc((C - E) / 30.6001)
    
    day = C - E + F - math.trunc(30.6001 * G)
    
    if G < 13.5:
        month = G - 1
    else:
        month = G - 13
        
    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715
        
    return year, month, day

	
def page_setup(pages, df_JPL_CG, df_JPL_JUP, hover):
	"""
	Plotting JPL data for C-G and Jupiter on every figure and setting up styling.
	"""
	sourceCG = ColumnDataSource(df_JPL_CG)
	sourceJUP = ColumnDataSource(df_JPL_JUP)

	for page in pages:
		page.line(x = 'x', y = 'y', source = sourceCG, line_color = 'black', line_dash = 'solid', legend = 'JPL_CG')
		page.line(x = 'x', y = 'y', source = sourceJUP, line_color = 'gray', line_dash = [10, 120], line_width = 1, legend = 'JPL_JUP')
		page.add_tools(hover)
		page.yaxis.axis_label = "Y [AU]"
		page.xaxis.axis_label = "X [AU]"
		

def JPL_query(Ttot, ts):
	"""
	Querying JPL Horizons system for the state-vectors of Jupiter and 67P/C-G,
	then converting the tables to pandas dataframes.
	"""
	JD_period_end = 2415020.5 + Ttot
	
	if JD_period_end > 2667387.5:
		print('Timescale is too large for query. Using previously downloaded HORIZONS data.')
		df1 = pd.read_csv('.' + sep + 'addendum' + sep + 'Jupiter_1900_2000_1.csv', skipinitialspace = True, float_precision = 'high')
		df2 = pd.read_csv('.' + sep + 'addendum' + sep + '67P_1900_2000_1.csv', skipinitialspace = True, float_precision = 'high')
		
	else:
		endy, endm, endd = jd_to_date(JD_period_end)
		end = str(endy) + '-' + str(endm) + '-' + str(endd)
	
		print(f'Querying HORIZONS with a {ts} days timestep...')
	
		# Jupiter data:
		Jup = Horizons(id = '599', id_type = 'id', location = '500@0', epochs = {'start': '1900-01-01', 'stop': end, 'step': (str(ts)+'d')})
		vec = Jup.vectors()
	
		df1 = vec.to_pandas()
	
		# 67P/C-G data:
		CG = Horizons(id = '900681', id_type = 'id', location = '500@0', epochs = {'start': '1900-01-01', 'stop': end, 'step': (str(ts)+'d')})
		vec2 = CG.vectors()
	
		df2 = vec2.to_pandas()
		
		print('Done.')
		
	return df1, df2
	

def main():

	if w_cg.result is True:
		name_list = ["67P/C-G", "Jupiter", "Saturn", "Uranus", "Neptune"]
		name = "67P/C-G"
	else:
		name_list = ["Jupiter", "Saturn", "Uranus", "Neptune"]
		name = "Jupiter"
	
	Ttot = w_Ttot.result
	ts_range_max = w_ts_range.result[1]
	ts_range_min = w_ts_range.result[0]
	tol_range_max = w_err_range.result[1]
	tol_range_min = w_err_range.result[0]	
	
	# If timescale allows, query the HORIZONS system for accurate data, using the same stepsize:
	df_JPL_JUP, df_JPL_CG = JPL_query(Ttot, ts_range_min)
	
	# Creating T column of JPL dataframes:
	for df in [df_JPL_JUP, df_JPL_CG]:
		elem = df['datetime_jd']
		sera = []
		for i in range(1, len(elem)):
			sera.append(elem[i] - elem[0])
		df['T'] = pd.Series(sera)

	pages = []

	plot_width = 780
	plot_height = 500
	circle_size = 6

	hover = HoverTool(tooltips=[
		("index", "$index"),
		("(x,y)", "($x, $y)"),
		("Day", "@T{0,0}"),
	])

	page1 = figure(plot_width = plot_width, plot_height = plot_height, active_drag = "box_zoom")
	pages.append(page1)
	
	pageE = figure(plot_width = plot_width, plot_height = plot_height, active_drag = "box_zoom")
	pages.append(pageE)

	pageV = figure(plot_width = plot_width, plot_height = plot_height, active_drag = "box_zoom") 
	pages.append(pageV)

	pageRK4 = figure(plot_width = plot_width, plot_height = plot_height, active_drag = "box_zoom", x_range = pageV.x_range, y_range = pageV.y_range)
	pages.append(pageRK4)

	pageRKDP = figure(plot_width = plot_width, plot_height = plot_height, active_drag = "box_zoom", x_range = pageV.x_range, y_range = pageV.y_range)
	pages.append(pageRKDP)
	
	# Setting up pages and plotting JPL:
	page_setup(pages, df_JPL_CG, df_JPL_JUP, hover)
	
	# Setting up color codings:
	alpha_arr_fix = np.linspace(0.1, 1.0, num=(ts_range_max - ts_range_min + 1))
	alpha_arr_ada = np.linspace(0.1, 1.0, num=(tol_range_max - tol_range_min + 1))
	i, j, k, l = 0, 0, 0, 0
	
	# Reading every dataframe produced by 'comp.py':
	for path in iglob('.' + sep + 'logs' + sep + 'output_*'):					

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
			pageRKDP.circle(x = namex, y = namey, source = source, size = circle_size, color = (r+5*ts_tol, g, b+10*ts_tol), fill_alpha = alpha_arr_ada[k], line_color = 'black', legend = nombre)
			page1.circle(x = namex, y = namey, source = source, size = circle_size, color = (r+5*ts_tol, g, b+10*ts_tol), fill_alpha = alpha_arr_ada[k], line_color = 'black', legend = nombre)
			k += 1
		
		elif nombre[:nombre.rfind('_')] == 'V':
			r, g, b = 255, 255, 0
			pageV.circle(x = namex, y = namey, source = source, size = circle_size, color = (r, g, b+10*ts_tol), fill_alpha = alpha_arr_fix[l], line_color = 'black', legend = nombre)
			page1.circle(x = namex, y = namey, source = source, size = circle_size, color = (r, g, b+10*ts_tol), fill_alpha = alpha_arr_fix[l], line_color = 'black', legend = nombre)
			l += 1
			
	page1.legend.location = "bottom_left"
	
	# The figure in the end consists of separate tabs, each containing one 'page':
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
