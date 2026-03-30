import sys
sys.path.append(r"C:\Program Files (x86)\Gamry Instruments\Python37-32\Lib\site-packages")
import argparse
import mux as mx
import toolkitpy as tkp
import numpy as np
import time
import math
import os


def	initialize_pstat(pstat):
	#These were copied from Gamry's potentiostatic_eis.py, which mostly matches the 'Potentiostatic EIS.exp' Framework script
	#RY added comments and made a couple of changes
	pstat.set_cell(False)		   
	pstat.set_ach_select(tkp.ACHSELECT_GND)
	pstat.set_ctrl_mode(tkp.PSTATMODE) #added.
	pstat.set_ie_stability(tkp.STABILITY_FAST)
	pstat.set_ca_speed(tkp.CASPEED_MEDFAST) #changed from tkp.CASPEED_NORM
	pstat.set_ground(tkp.FLOAT)
	pstat.set_i_convention(tkp.ICONVENTION.ANODIC)
	pstat.set_ich_range(3.0) #in V
	pstat.set_ich_range_mode(False)
	pstat.set_ich_filter(5.0) #in Hz. changed from 3.0, based on what was logged in EISPOT .DTA files
	pstat.set_vch_range(3.0) #in V
	pstat.set_ich_range_mode(False)
	pstat.set_vch_range_mode(False)
	pstat.set_ich_offset_enable(True)
	pstat.set_vch_offset_enable(True)
	pstat.set_vch_filter(5.0) #in Hz; changed from 2.5, based on what was logged in EISPOT .DTA files
	pstat.set_ach_range(3.0) #in V
	pstat.set_ie_range(0.03) #(does this relaly matter? IE range gets set again later)
	pstat.set_ie_range_mode(False)
	pstat.set_ie_range_lower_limit(0)
	pstat.set_analog_out(0.0)
	pstat.set_pos_feed_enable(False)
	pstat.set_irupt_mode(tkp.IRUPTOFF)


def	potentiostatic_eis(pstat, parameter_list):
	#Parameters
	#------------------------------------------------------------------
	initial_freq = parameter_list.get("initial_freq", 100000)	 #Hz
	final_freq = parameter_list.get("final_freq", 1)			#Hz
	ac_voltage = parameter_list.get("ac_voltage", .03)			#V
	dc_voltage = parameter_list.get("dc_voltage", 0.0)			#V
	estimated_z	= parameter_list.get("estimated_z",	10000)		#ohm
	points_per_decade =	parameter_list.get("points_per_decade",	5)	 # none

	# internal state - pre 1st measurement
	gain = 1.0
	inoise = 0.0
	vnoise = 0.0
	ienoise	= 0.0
 
	#-----------------------------------------------------------
	final_freq = abs(final_freq)
	initial_freq = abs(initial_freq)

	freq_lim_lower = pstat.freq_limit_lower()
	freq_lim_upper = pstat.freq_limit_upper()
	if(initial_freq	> freq_lim_upper):
		print("Inital frequency	exceeds	upper frequency	limit")
		initial_freq = freq_lim_upper
	if(final_freq >	freq_lim_upper):
		final_freq = freq_lim_upper
		print("Final frequency exceeds upper frequency limit")
	if(initial_freq	< freq_lim_lower):
		initial_freq = freq_lim_lower
		print("Inital frequency	exceeds	lower frequency	limit")
	if(final_freq <	freq_lim_lower):
		final_freq = freq_lim_lower
		print("Final frequency exceeds lower frequency limit")

	#==========================================
	initialize_pstat(pstat)
	time.sleep(0.1) #wait a bit after intialization

	Sdc	= dc_voltage
	Sac	= ac_voltage
	pstat.set_voltage(Sdc)
	pstat.set_cell(tkp.CELL_ON)
	dc_current = pstat.measure_i()
	ac_current = estimated_z * ac_voltage
	ie_range = pstat.test_ie_range(abs(dc_current) + 1.414*abs(ac_current))
	pstat.set_ie_range(ie_range)

	readz =	tkp.ReadZ(pstat)
	readz.set_gain(gain)
	readz.set_inoise(inoise)
	readz.set_vnoise(vnoise)
	readz.set_ienoise(ienoise)
	readz.set_zmod(estimated_z)
	readz.set_vdc(dc_voltage)
	readz.set_speed(1) #Normal
	readz.set_drift_cor(False)
	readz.set_idc(dc_current)

	#==========================================
	log_increment =	1.0/points_per_decade
	if initial_freq	> final_freq:
		log_increment =	-log_increment
	max_points = tkp.check_eis_points(initial_freq,	final_freq,	points_per_decade)
	zcurve = tkp.ZCurve(max_points)
	
	print('Acquiring {} points'.format(max_points),	end='')

	added =	True
	current_points = 0

	while current_points < max_points:
		freq = math.pow(10.0, math.log10(initial_freq) + current_points	* log_increment)
		Status = readz.Measure(freq, ac_voltage,dc_voltage)
		if Status == False:
			print('X', end ='', flush=True)
			current_points += 1
			continue
		else:
			print('.', end='', flush=True)
			zcurve.add_point(readz)
			data = zcurve.acq_data()
			nextpoint =	zcurve.point
			lastpoint =	nextpoint-1
		current_points +=1

	print()
	pstat.set_cell(False)

	return zcurve


def main():
	###
	# Program Arguments
	###
	ap = argparse.ArgumentParser(description='MUXed Potentiostatic EIS Tool')
	og = ap.add_argument_group('MUX Device')
	og.add_argument('--mux-debug', action='store_true', help='enable communication debugging')
	og.add_argument('--mux-port', default='com3', help='connect to specified mux COM port')
	og.add_argument('--mux-read-timeout', type=float, default=1.0, help='COM port read time-out seconds')
	og.add_argument('--mux-write-timeout', type=float, default=1.0, help='COM port write time-out seconds')

	og = ap.add_argument_group('PS EIS Parameters')
	og.add_argument('--eis-freq-start', type=float, default=100.0e3, help='start frequency')
	og.add_argument('--eis-freq-stop', type=float, default=1.0, help='stop frequency')
	og.add_argument('--eis-points-per-decade', type=int, default=5, help='points per frequency decade')
	og.add_argument('--eis-dc-voltage', type=float, default=0.0, help='DC bias voltage')
	og.add_argument('--eis-estimated-z', type=float, default=10.0e3, help='Estimated impedance magnitude')
	
	og = ap.add_argument_group('Channels')
	og.add_argument('--channels', type=int, nargs='+', metavar='CH', default=[0,1,2,3,4,5,6,7,
																		   8,9,10,11,12,13,14,15,
																		   16,17,18,19,20,21,22,23,
																		   24,25,26,27,28,29,30,31], help='channels to sweep')
	# og.add_argument('--channels', type=int, nargs='+', metavar='CH', default=[0,1,2,3,4,5,6,7,
	# 																	   8,9,10,11,12,13,14,15,16,17], help='channels to sweep')
	og.add_argument('--channel-switch-delay', type=float, default=0.1, help='Time to wait after channel switch before sweep')
	
	og = ap.add_argument_group('Output Parameters')
	og.add_argument('--file-path', type=str, default='data', help='Output file path')
	og.add_argument('--file-name-format', type=str, default='{}_{:02d}.csv', help='Output file name format')
	og.add_argument('--dataset-name', type=str, default='test', help='Output file prefix')
	og.add_argument('--no-dataset-directory', action='store_true', help='enable communication debugging')
	args = ap.parse_args()

	###### MUX SETUP ######
	mux = mx.Mux(args.mux_port, args.mux_debug, args.mux_read_timeout, args.mux_write_timeout)
	mux.none()

	###### POTENTIOSTAT SET-UP #########
	print('Initialising the potentiostat...')
	tkp.toolkitpy_init("ps-eis-mux-RY.py") #initialize toolkitpy
	pstat = tkp.Pstat("PSTAT") #create pstat object in order to send commands to potentiostat. this method grabs the fisrt pstat object.


	###
	# EIS Parameters
	###
	parameter_list = { }
	parameter_list['initial_freq']= args.eis_freq_start
	parameter_list['final_freq'] = args.eis_freq_stop
	parameter_list['points_per_decade'] = args.eis_points_per_decade
	parameter_list['estimated_z'] = args.eis_estimated_z
	parameter_list['dc_voltage'] = args.eis_dc_voltage
	
	###
	# Output Location
	###
	dir_name = args.file_path
	if not args.no_dataset_directory:
		dir_name = os.path.join(args.file_path, args.dataset_name)
	os.makedirs(dir_name, exist_ok=True)
	print('Output directory: {}'.format(dir_name))
	
	###
	# Sweeps
	###
	for ch in args.channels:
		print('Sweeping channel: {}'.format(ch))
		
		# select channel
		mux.set(ch)
		time.sleep(args.channel_switch_delay)

		# perform sweep
		zcurve = potentiostatic_eis(pstat, parameter_list)
		file_name = os.path.join(dir_name, args.file_name_format.format(args.dataset_name, ch))
		print('Writing file: {}'.format(file_name))
		np.savetxt(file_name, zcurve.acq_data(), delimiter = ',', header = 'Point, Freq(Hz), Zreal (ohm), Zimag (ohm), IE Range')
		
		# deselect channel
		mux.reset(ch)
	
	###
	# Clean Up
	###
	del pstat
	tkp.toolkitpy_close()

	mux.none()
	mux.close()

if __name__ == "__main__":
	main()