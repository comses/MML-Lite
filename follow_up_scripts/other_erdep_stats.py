#!/usr/pin/python

#%Module
#%  description: Creates a raster buffer of specified area around vector points using cost distances using r.walk. NOTE: please run g.region first to make sure region boundaries and resolution match input elevation map.
#%END


#%option
#% key: vbmap
#% type: string
#% gisprompt: new,cell,raster
#% description: Full name of the valley bottom map
#% required : yes
#%END
#%option
#% key: pattern
#% type: string
#% description: Name stem for elevation maps. Use standard wild card search operators for prefix/suffix, and string substitution operator for infixed year number
#% answer: *YEAR%s_Exp*_CUMERDEP_*
#% required : no
#%END
#%option
#% key: basepath
#% type: string
#% description: Full path to output stats file to
#% answer: /home/mdlpd/Dropbox/Barrancos/results/Filled_DEM_results/Exp_1/
#% required : yes
#%END
#%option
#% key: outputfile
#% type: string
#% description: Name stem for the output stats files. One file will be made for each interval.
#% answer: NON_VB_ERDEP_STATS
#% required : no
#%END
#%option
#% key: interval
#% type: integer
#% description: Interval for the routine (routine will only run for years that are a multiple of this number
#% answer: 50
#% required : no
#%END
#%option
#% key: digits
#% type: integer
#% description: Number of digits in the infixed year number. Will use zfill to pad zeros to this number of digits.
#% answer: 3
#% required : no
#%END
#%option
#% key: finalyear
#% type: integer
#% description: Number of the last year to include in the analysis
#% answer: 300
#% required : no
#%END

import grass.script as grass
import numpy as np
import os


def main():
    ###############################
    #  EDIT VALS BELOW THIS LINE  #
    ###############################
    PATTERN = options["pattern"]            #Name stem for elevation maps. Use standard wild card search operators for prefix/suffix, and string substitution operator for infixed year number
    INTERVAL = int(options["interval"])                                         #Interval for the routine (routine will only run for years that are a multiple of this number
    DIGITS = int(options["digits"])                                            #Number of digits in the infixed year number. Will use zfill to pad zeros to this number of digits.
    FINALYEAR = int(options["finalyear"])                                        #Number of the last year to include in the analysis
    VBMAP = options["vbmap"]                                    #Full name of the valley bottom map
    BASEPATH = options["basepath"]
    OUTPUTFILE = options["outputfile"]                            #Name stem for the output stats files. One file will be made for each interval.

    ###############################
    # DO NOT EDIT BELOW THIS LINE #
    ###############################

    #calculate the number of iterations.
    iterations = FINALYEAR / INTERVAL
    #setup the loop, and start looping
    looper = INTERVAL
    ###################################
    for iteration in range(iterations):
        namestem = PATTERN % str(looper).zfill(DIGITS)
        cumerdeplist = grass.read_command('g.list', flags='m', type='raster', pattern=namestem, separator=',').strip().split(',')
        statslist = []
        rows = np.array(['summed erosion','summed deposition','mean erosion','mean deposition','max erosion','max deposition'], dtype='|S20')
        for map1 in cumerdeplist:
            grass.mapcalc("${OUT}=if(${VBMAP}, null(), if(${CUMERDEP} < 0, ${CUMERDEP}, null()))", quiet = 'True', overwrite="True", OUT = "temporary_notvb_EROSION_%s_" % map1.split("@")[0], VBMAP = VBMAP, CUMERDEP = map1)
            grass.mapcalc("${OUT}=if(${VBMAP}, null(), if(${CUMERDEP} > 0, ${CUMERDEP}, null()))", quiet = 'True', overwrite="True", OUT = "temporary_notvb_DEPOSITION_%s_" % map1.split("@")[0], VBMAP = VBMAP, CUMERDEP = map1)
            a = grass.parse_command('r.univar', flags = 'g', map = "temporary_notvb_EROSION_%s_" % map1.split("@")[0])
            b = grass.parse_command('r.univar', flags = 'g', map = "temporary_notvb_DEPOSITION_%s_" % map1.split("@")[0])
            statslist.append([float(a['sum']), float(b['sum']), float(a['mean']), float(b['mean']), float(a['min']), float(b['max'])])
        statsarray = np.array(statslist)
        np.savetxt("%s%sYear_%s_%s.csv" % (BASEPATH, os.sep, str(looper).zfill(DIGITS), OUTPUTFILE), np.vstack((rows, statsarray)), delimiter=",", fmt = "%s")
        if looper == FINALYEAR:
          break
        else:
          looper = looper + INTERVAL
if __name__ == "__main__":
    options, flags = grass.parser()
    main()
    exit(0)
