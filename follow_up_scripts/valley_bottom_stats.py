import grass.script as grass
import numpy as np
import os

###############################
#  EDIT VALS BELOW THIS LINE  #
###############################

PREFIX = "30pmx_"                                #Map prefix used in the original sim
ELEVPATTERN = '*_Year_%s_Elevation_Map*'            #Name stem for elevation maps. Use standard wild card search operators for prefix/suffix, and string substitution operator for infixed year number
INTERVAL = 50                                         #Interval for the routine (routine will only run for years that are a multiple of this number
DIGITS = 3                                            #Number of digits in the infixed year number. Will use zfill to pad zeros to this number of digits.
FINALYEAR = 300                                        #Number of the last year to include in the analysis
INITDEM = "filledDEM@PERMANENT"                            #Full name (with @'mapset') of the initial dem used in the sim
VBMAP = "TRUE_valley_bottom@stats"    #Full name of the valley bottom map
BASEPATH = '/home/mdlpd/GIS_DataBase/Exp_2/stats_files'
OUTPUTFILE = "VB_ERDEP_STATS"                            #Name stem for the output stats files. One file will be made for each interval.

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
        grass.mapcalc("${outname}=(${elevmap} - ${dem})", quiet = 'True', overwrite="True", outname = outname, dem = INITDEM, elevmap = map1)
        cumerdeplist.append(outname)
    statslist = []
    rows = np.array(['summed erosion','summed deposition','mean erosion','mean deposition','max erosion','max deposition'], dtype='|S20')
    for map1 in cumerdeplist:
        grass.mapcalc("${OUT}=if(isnull(${VBMAP}), null(), if(${CUMERDEP} < 0, ${CUMERDEP}, null()))", quiet = 'True', overwrite="True", OUT = "temporary_EROSION_%s_" % map1.split("@")[0], VBMAP = VBMAP, CUMERDEP = map1)
        grass.mapcalc("${OUT}=if(isnull(${VBMAP}), null(), if(${CUMERDEP} > 0, ${CUMERDEP}, null()))", quiet = 'True', overwrite="True", OUT = "temporary_DEPOSITION_%s_" % map1.split("@")[0], VBMAP = VBMAP, CUMERDEP = map1)
        a = grass.parse_command('r.univar', flags = 'g', map = "temporary_EROSION_%s_" % map1.split("@")[0])
        b = grass.parse_command('r.univar', flags = 'g', map = "temporary_DEPOSITION_%s_" % map1.split("@")[0])
        statslist.append([float(a['sum']), float(b['sum']), float(a['mean']), float(b['mean']), float(a['min']), float(b['max'])])
    statsarray = np.array(statslist)
    np.savetxt("%s%sYear_%s_%s.csv" % (BASEPATH, os.sep, str(looper).zfill(DIGITS), OUTPUTFILE), np.vstack((rows, statsarray)), delimiter=",", fmt = "%s")
    if looper == FINALYEAR:
      break
    else:
      looper = looper + INTERVAL
