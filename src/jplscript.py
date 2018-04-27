from astroquery.jplhorizons import Horizons

import math
import datetime as dt

import pandas as pd

JPL_JUP = []
JPL_CG= []

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

	
def main():
	"""
	Querying JPL Horizons system for the state-vectors of Jupiter and 67P/C-G,
	then converting the tables as pandas dataframes and storing them in a global list,
	which is to be accessed from the interactive jupyter namespace. 
	"""
	
	try:
		Ttot = w_Ttot.result
		ts_range_max = w_ts_range.result[1]
		ts_range_min = w_ts_range.result[0]
	except NameError:
		print('Run the cell calling jupyter_init.py first!')
		raise
	
	# Creating the necessary date format for querying:
	endy, endm, endd = jd_to_date(2415020.5 + Ttot)
	end = str(endy)+'-'+str(endm)+'-'+str(endd)
	ts = ts_range_min
	
	print(f'Querying HORIZONS with a {ts} days timestep...')
	
	# Jupiter data:
	Jup = Horizons(id = '599', id_type = 'id', location = '500@0', epochs = {'start': '1900-01-01', 'stop': end, 'step': (str(ts)+'d')})
	vec = Jup.vectors()
	
	df = vec.to_pandas()
	JPL_JUP.append(df)
	
	# 67P/C-G data:
	CG = Horizons(id = '900681', id_type = 'id', location = '500@0', epochs = {'start': '1900-01-01', 'stop': end, 'step': (str(ts)+'d')})
	vec2 = CG.vectors()
	
	df2 = vec2.to_pandas()
	JPL_CG.append(df2)
	
	
	# This following part is reduntant, but preserved in case there is need to implement a comparison with JPL data.
	
	# for ts in range(ts_range_min, ts_range_max+1):
	
		# print(f'Querying HORIZONS with timestep: {ts} days...')
		
		# # Jupiter data:
		# Jup = Horizons(id = '599', id_type = 'id', location = '500@0', epochs = {'start': '1900-01-01', 'stop': end, 'step': (str(ts)+'d')})
		# vec = Jup.vectors()
		
		# df = vec.to_pandas()
		# JPL_JUP.append(df)
		
		# # 67P/C-G data:
		# CG = Horizons(id = '900681', id_type = 'id', location = '500@0', epochs = {'start': '1900-01-01', 'stop': end, 'step': (str(ts)+'d')})
		# vec2 = CG.vectors()
		
		# df2 = vec2.to_pandas()
		# JPL_CG.append(df2)
		
if __name__ == "__main__":
	main()
