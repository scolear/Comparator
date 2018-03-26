"""

"""
from os import sep
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from numpy.linalg import norm

#df_E = pd.read_csv('output_E.csv', delim_whitespace = True, float_precision = 'high')
#df_V = pd.read_csv('output_V.csv', delim_whitespace = True, float_precision = 'high')
# df_JPL_JUP = pd.read_csv('./logs/Jupiter_1900_2000_10.csv', skipinitialspace = True, float_precision = 'high')
# df_JPL_CG = pd.read_csv('./logs/67P_1900_2100_10.csv', skipinitialspace = True, float_precision = 'high')

path = '.' + sep + 'logs' + sep + 'output_RKDP_'+str(w_err_range.result[1])+'.csv'
df_RK = pd.read_csv(path, delim_whitespace = True, float_precision = 'high')

fig1, ax1 = plt.subplots(1,1)
ax1.set_xlim((-8,8))
ax1.set_ylim((-8,8))
ax1.set_xlabel('X [AU]')
ax1.set_ylabel('Y [AU]')
ax1.legend()

planet1_choice = 'Jupiter'
pl1_x = planet1_choice+'X'
pl1_y = planet1_choice+'Y'
planet2_choice = '67P/C-G'
pl2_x = planet2_choice+'X'
pl2_y = planet2_choice+'Y'

pointJ, = ax1.plot([],[], 'or', ms = 5)
pointJt, = ax1.plot([],[], 'or', ms = 2)
pointJtt, = ax1.plot([],[], 'or', ms = 1)
pointCG, = ax1.plot([],[], 'ob', ms = 5)
pointCGt, = ax1.plot([],[], 'ob', ms = 2)
pointCGtt, = ax1.plot([],[], 'ob', ms = 1)
pointS, = ax1.plot([],[], 'oy', ms = 5)

time_text = ax1.text(0.02, 0.95, '', transform=ax1.transAxes)
step_text = ax1.text(0.02, 0.90, '', transform=ax1.transAxes)

framz = len(df_RK)

def init():
	pointJ.set_data([],[])
	pointCG.set_data([],[])
	pointS.set_data([],[])
	time_text.set_text('')
	step_text.set_text('')
	return pointJ, pointCG, time_text, step_text

def animate(i):
	Jx = df_RK[pl1_x][i]
	Jy = df_RK[pl1_y][i]
	Jxt = df_RK[pl1_x][i-1]
	Jyt = df_RK[pl1_y][i-1]
	Jxtt = df_RK[pl1_x][i-2]
	Jytt = df_RK[pl1_y][i-2]
	pointJ.set_data(Jx, Jy)
	pointJt.set_data(Jxt, Jyt)
	pointJtt.set_data(Jxtt, Jytt)
	CGx = df_RK[pl2_x][i]
	CGy = df_RK[pl2_y][i]
	CGxt = df_RK[pl2_x][i-1]
	CGyt = df_RK[pl2_y][i-1]
	CGxtt = df_RK[pl2_x][i-2]
	CGytt = df_RK[pl2_y][i-2]
	pointCG.set_data(CGx,CGy)
	pointCGt.set_data(CGxt, CGyt)
	pointCGtt.set_data(CGxtt, CGytt)
	Sx = df_RK['SunX'][i]
	Sy = df_RK['SunY'][i]
	pointS.set_data(Sx, Sy)
	time_text.set_text('Time = %.2f days' % df_RK['T'][i])
	step_text.set_text('StepSize= %.2f days' % df_RK['StepSize'][i])
	return pointJ, pointJt, pointJtt, pointCG, pointCGt, pointCGtt, pointS, time_text, step_text
