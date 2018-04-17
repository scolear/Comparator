from astroquery.jplhorizons import Horizons
import pandas as pd

JPL_JUP = []
JPL_CG= []


def main():
	for ts in range(w_ts_range.result[0], w_ts_range.result[1]):
		
		# since epoch only takes a dictionary of the following form, we could work around it by creating a list of JDs, and then passing them as discrete times. These should be profiled....
		
		
		Jup = Horizons(id = '599', id_type = 'id', epochs = {'start': '1900-01-01 00:00', 'stop': , 'step': (str(ts)+'d')})
		vec = Jup.vectors()
		
		df = vec.to_pandas()
		JPL_JUP.append(df)
		
		CG = Horizons(id = '900681', id_type = 'id', epochs = {'start': '1900-01-01 00:00', 'stop': , 'step': (str(ts)+'d')})
		
if __name__ == "__main__":
	main()
