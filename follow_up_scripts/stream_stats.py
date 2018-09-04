import grass.script as grass
import numpy as np
from scipy import stats
import os

###############################
#  EDIT VALS BELOW THIS LINE  #
###############################

PREFIX = "120pmx_"								#Map prefix used in the original sim
ELEVPATTERN = '*_Year_%s_Elevation_Map*'			#Name stem for elevation maps. Use standard wild card search operators for prefix/suffix, and string substitution operator for infixed year number
INTERVAL = 50 										#Interval for the routine (routine will only run for years that are a multiple of this number
DIGITS = 3											#Number of digits in the infixed year number. Will use zfill to pad zeros to this number of digits.
FINALYEAR = 300										#Number of the last year to include in the analysis
INITDEM = "DEM@PERMANENT"							#Full name (with @'mapset') of the initial dem used in the sim
STREAM = "masdis_stream_extract_costs@PERMANENT"	#Full name of the stream map
BASEPATH = '/home/medland/GIS_Database/Exp6/exp6_records'
OUTPUTFILE = "STREAM_STATS"							#Name stem for the output stats files. One file will be made for each interval.
ERRORCALC = False									#If True, then also calculate the sum standard error for each year, and output stats files.

###############################
# DO NOT EDIT BELOW THIS LINE #
###############################

#calculate the number of iterations.
iterations = FINALYEAR / INTERVAL
#setup the loop, and start looping
looper = INTERVAL
###################################
for iteration in range(iterations):
	namestem = ELEVPATTERN % str(looper).zfill(DIGITS)
	elevmaps = grass.read_command('g.list', flags='m', type='rast', pattern=namestem, separator=',').strip().split(',')
	cumerdeplist = []
	for map1 in elevmaps:
		print map1
		#print namestem.strip('*')
		outname = "YEAR%s_%s_CUMERDEP_%s" % (str(looper).zfill(DIGITS), map1.split('%s@' % namestem.strip('*'))[1], map1.split('%s@' % namestem.strip('*'))[0].strip(PREFIX))
		print outname
		grass.mapcalc("${outname}=(${elevmap} - ${dem})", overwrite="True", outname = outname, dem = INITDEM, elevmap = map1)
		cumerdeplist.append(outname)
	statslist = []
	for map1 in cumerdeplist:
		a = grass.parse_command('r.stats', flags='1n', input="%s,%s" % (STREAM, map1), separator='=')
		l1 = []
		for key in sorted(a):
			l1.append(float(a[key]))
		statslist.append(l1)
	statsarray = np.array(statslist)
	np.savetxt("%s%sYear_%s_%s.csv" % (BASEPATH, os.sep, str(looper).zfill(DIGITS), OUTPUTFILE), statsarray.T, delimiter=",")
################################
	if ERRORCALC is True:
		#compute standard error of an array, first randomly shuffle the rows (actually columns), and do this 100 times so that the data are bootstrapped, then loop through the shuffled dataset and calculate SE for every n in the sequence
		#first get the standard errors for the unshuffled data, and make that an array
		loopctrl = range(len(statsarray))
		el = []
		for x in loopctrl:
			#z = stats.sem(statsarray[0:x+1], axis=None, ddof=0)
			z = stats.sem(statsarray[0:x+1])
			el.append(np.sum(z))
		errorlist = [el]
		#now do a nested loop of this, but reshuffling each time 
		for n in loopctrl:
			a2 = np.random.permutation(statsarray)
			el2 = []
			for x in loopctrl:
				#z = stats.sem(a2[0:x+1], axis=None, ddof=0)
				z = stats.sem(a2[0:x+1])
				el2.append(np.sum(z))
			errorlist.append(el2)
		errorarray = np.array(errorlist)
		np.savetxt("%s%sYear_%s_%s_errors.csv" % (BASEPATH, os.sep, str(looper).zfill(DIGITS), OUTPUTFILE), errorarray.T, delimiter=",")
###############################
	if looper == FINALYEAR:
	  break
	else:
	  looper = looper + INTERVAL
