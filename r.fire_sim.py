#!/usr/bin/python
#
############################################################################
#
# MODULE:               r.fire_sim
#
# AUTHOR(S):            Isaac Ullah, San Diego State University
#
# PURPOSE:              Simulates agricultural and pastoral landuse and tracks 
#                       yields and environmental impacts. Farming and grazing
#                       strategies and yield goals are predetermined by the 
#                       researcher, and do not change (adapt) during the 
#                       simulation. However, catchment sizes can be adapted 
#                       over time to meet these goals. This version implments 
#                       a land tenuring alogrithm. Requires r.landscape.evol.
#
# ACKNOWLEDGEMENTS:     National Science Foundation Grant #BCS0410269, Center 
#                       for Comparative Archaeology at the University of 
#                       Pittsburgh, Center for Social Dynamics and Complexity 
#                       at Arizona State University, San Diego State University
#
# COPYRIGHT:            (C) 2018 by Isaac Ullah, San Diego State University
#
#                   This program is free software under the GNU General Public
#                   License (>=v2). Read the file COPYING that comes with GRASS
#                   for details.
#
#############################################################################


#%Module
#%  description: Simulates natural fires for input into landscape evolution simulation

##################################
#Simulation Control
##################################
#%option
#% key: years
#% type: integer
#% description: Number of iterations ("years") to run
#% answer: 200
#% required: yes
#% guisection: Simulation Control
#%END
#%option
#% key: prfx
#% type: string
#% description: Prefix for all output maps
#% answer: sim
#% required: yes
#% guisection: Simulation Control
#%END
##################################
#Landcover Dynamics Options
##################################
#%option
#% key: inlcov
#% type: string
#% gisprompt: old,cell,raster
#% description: Input landcover map (Coded according to landcover rules file below)
#% guisection: Landcover Dynamics
#%END
#%option
#% key: infert
#% type: string
#% gisprompt: old,cell,raster
#% description: Input fertility map (Coded according to percentage retained fertility, with 100 being full fertility)
#% guisection: Landcover Dynamics
#%END
#%option
#% key: fireprob
#% type: string
#% gisprompt: old,cell,raster
#% description: Map of fire probabilities due to natural lightning strikes (coded 0 to 1)
#% guisection: Landcover Dynamics
#%END
#%option
#% key: maxlcov
#% type: string
#% gisprompt: old,cell,raster
#% description: Maximum value of landcover for the landscape (Can be a single numerical value or a cover map of different maximum values. Shouldn't exceed maximum value in rules file')
#% answer: 50
#% guisection: Landcover Dynamics
#%END
#%option
#% key: lc_rules
#% type: string
#% gisprompt: string
#% description: Path to reclass rules file for landcover map
#% answer: /home/iullah/Dropbox/Scripts_Working_Dir/rules/luse_reclass_rules.txt
#% guisection: Landcover Dynamics
#%END
#%option
#% key: cfact_rules
#% type: string
#% gisprompt: string
#% description: Path to recode rules file for c-factor map
#% answer: /home/iullah/Dropbox/Scripts_Working_Dir/rules/cfactor_recode_rules.txt
#% guisection: Landcover Dynamics
#%END
#%flag
#% key: c
#% description: -c Keep C-factor (and rainfall excess) maps for each year
#% guisection: Landcover Dynamics
#%end

##################################
#Landscape Evolution Options
##################################
#%option
#% key: elev
#% type: string
#% gisprompt: old,cell,raster
#% description: Input elevation map (DEM of surface)
#% guisection: Landscape Evolution
#%end
#%option
#% key: initbdrk
#% type: string
#% gisprompt: old,cell,raster
#% description: Bedrock elevations map (DEM of bedrock)
#% answer:
#% guisection: Landscape Evolution
#%end
#%option
#% key: k
#% type: double
#% gisprompt: old,cell,raster
#% description: Soil erodability index (K factor) map or constant
#% answer: 0.42
#% guisection: Landscape Evolution
#%end
#%option
#% key: sdensity
#% type: double
#% gisprompt: old,cell,raster
#% description: Soil density map or constant [T/m3] for conversion from mass to volume
#% answer: 1.2184
#% guisection: Landscape Evolution
#%end
#%option
#% key: kt
#% type: double
#% description: Stream transport efficiency variable (0.001 for a soft substrate, 0.0001 for a normal substrate, 0.00001 for a hard substrate, 0.000001 for a very hard substrate)
#% answer: 0.0001
#% options: 0.001,0.0001,0.00001,0.000001
#% guisection: Landscape Evolution
#%end
#%option
#% key: loadexp
#% type: double
#% description: Stream transport type variable (1.5 for mainly bedload transport, 2.5 for mainly suspended load transport)
#% answer: 1.5
#% options: 1.5,2.5
#% guisection: Landscape Evolution
#%end
#%option
#% key: manningn
#% type: string
#% gisprompt: old,cell,raster
#% description: Map or constant of the value of Manning's "N" value for channelized flow.
#% answer: 0.05
#% required : no
#% guisection: Landscape Evolution
#%end
#%option
#% key: kappa
#% type: double
#% description: Hillslope diffusion (Kappa) rate map or constant [m/kyr]
#% answer: 1
#% guisection: Landscape Evolution
#%end
#%option
#% key: rain
#% type: string
#% gisprompt: old,cell,raster
#% description: Precip totals for the average storm [mm] (or path to climate file of comma separated values of "rain,R,storms,stormlength", with a new line for each year of the simulation)
#% answer: 20.61
#% guisection: Landscape Evolution
#%end
#%option
#% key: r
#% type: string
#% description: Rainfall (R factor) constant (AVERAGE FOR WHOLE MAP AREA) (or path to climate file of comma separated values of "rain,R,storms,stormlength", with a new line for each year of the simulation)
#% answer: 4.54
#% guisection: Landscape Evolution
#%end
#%option
#% key: storms
#% type: string
#% description: Number of storms per year (integer) (or path to climate file of comma separated values of "rain,R,storms,stormlength", with a new line for each year of the simulation)
#% answer: 25
#% guisection: Landscape Evolution
#%end
#%option
#% key: stormlength
#% type: string
#% description: Average length of the storm [h] (or path to climate file of comma separated values of "rain,R,storms,stormlength", with a new line for each year of the simulation)
#% answer: 24.0
#% guisection: Landscape Evolution
#%end
#%option
#% key: speed
#% type: double
#% description: Average velocity of flowing water in the drainage [m/s]
#% answer: 1.4
#% guisection: Landscape Evolution
#%end
#%option
#% key: cutoff1
#% type: double
#% description: Flow accumulation breakpoint value for shift from diffusion to overland flow
#% answer: 0
#% guisection: Landscape Evolution
#%end
#%option
#% key: cutoff2
#% type: double
#% description: Flow accumulation breakpoint value for shift from overland flow to rill/gully flow (if value is the same as cutoff1, no sheetwash procesess will be modeled)
#% answer: 100
#% guisection: Landscape Evolution
#%end
#%option
#% key: cutoff3
#% type: double
#% description: Flow accumulation breakpoint value for shift from rill/gully flow to stream flow (if value is the same as cutoff2, no rill procesess will be modeled)
#% answer: 100
#% guisection: Landscape Evolution
#%end
#%option
#% key: smoothing
#% type: string
#% description: Amount of additional smoothing (answer "no" unless you notice large spikes in the erdep rate map)
#% answer: no
#% options: no,low,high
#% guisection: Landscape Evolution
#%end
#%flag
#% key: 1
#% description: -1 Calculate streams as 1D difference instead of 2D divergence
#% guisection: Landscape Evolution
#%end
#%flag
#% key: k
#% description: -k Keep ALL temporary maps (overides flags -drst). This will make A LOT of maps!
#% guisection: Landscape Evolution
#%end
#%flag
#% key: d
#% description: -d Don't output yearly soil depth maps
#% guisection: Landscape Evolution
#%end
#%flag
#% key: r
#% description: -r Don't output yearly maps of the erosion/deposition rates ("ED_rate" map, in vertical meters)
#% guisection: Landscape Evolution
#%end
#%flag
#% key: s
#% description: -s Keep all slope maps
#% guisection: Landscape Evolution
#%end
#%flag
#% key: t
#% description: -t Keep yearly maps of the Transport Capacity at each cell ("Qs" maps)
#% guisection: Landscape Evolution
#%end
#%flag
#% key: e
#% description: -e Keep yearly maps of the Excess Transport Capacity (divergence) at each cell ("DeltaQs" maps)
#% guisection: Landscape Evolution
#%end

import sys
import os
import tempfile
import grass.script as grass


#main block of code starts here
def main():
    grass.message("Setting up Simulation........")
    #setting up Land Use variables for use later on
    inlcov = options['inlcov']
    fireprob = options['fireprob']
    years = int(options['years'])
    maxlcov = options['maxlcov']
    prfx = options['prfx']
    lc_rules = options['lc_rules']
    cfact_rules = options['cfact_rules']
    infert = options['infert']
    elev = options["elev"]
    initbdrk = options["initbdrk"]
    k = options["k"]
    sdensity = options["sdensity"]
    kappa = options["kappa"]
    manningn = options["manningn"]
    cutoff1 = options["cutoff1"]
    cutoff2 = options["cutoff2"]
    cutoff3 = options["cutoff3"]
    speed = options["speed"]
    kt = options["kt"]
    loadexp = options["loadexp"]
    smoothing = options["smoothing"]
    #these values could be read in from a climate file, so check that, and act accordingly
    rain2 = []
    try:
        rain1 = float(options['rain'])
        for year in range(int(years)):
            rain2.append(rain1)
    except:
        with open(options['rain'], 'rU') as f:
            for line in f:
                rain2.append(line.split(",")[0])
        #check for text header and remove if present
        try:
            float(rain2[0])
        except:
            del rain2[0]
        #throw a fatal error if there aren't enough values in the column
        if len(rain2) != int(years):
            grass.fatal("Number of rows of rainfall data in your climate file\n do not match the number of iterations you wish to run.\n Please ensure that these numbers match and try again")
            sys.exit(1)
    R2 = []
    try:
        R1 = float(options['r'])
        for year in range(int(years)):
            R2.append(R1)
    except:
        with open(options['r'], 'rU') as f:
            for line in f:
                R2.append(line.split(",")[1])
        #check for text header and remove if present
        try:
            float(R2[0])
        except:
            del R2[0]
        #throw a fatal error if there aren't enough values in the column
        if len(R2) != int(years):
            grass.fatal("Number of rows of R-Factor data in your climate file\n do not match the number of iterations you wish to run.\n Please ensure that these numbers match and try again")
            sys.exit(1)
    storms2 = []
    try:
        storms1 = float(options['storms'])
        for year in range(int(years)):
            storms2.append(storms1)
    except:
        with open(options['storms'], 'rU') as f:
            for line in f:
                storms2.append(line.split(",")[2])
        #check for text header and remove if present
        try:
            float(storms2[0])
        except:
            del storms2[0]
        #throw a fatal error if there aren't enough values in the column
        if len(storms2) != int(years):
            grass.fatal("Number of rows of storm frequency data in your climate file\n do not match the number of iterations you wish to run.\n Please ensure that these numbers match and try again")
            sys.exit(1)
    stormlength2 = []
    try:
        stormlength1 = float(options['stormlength'])
        for year in range(int(years)):
            stormlength2.append(stormlength1)
    except:
        with open(options['stormlength'], 'rU') as f:
            for line in f:
                stormlength2.append(line.split(",")[3])
        #check for text header and remove if present
        try:
            float(stormlength2[0])
        except:
            del stormlength2[0]
        #throw a fatal error if there aren't enough values in the column
        if len(stormlength2) != int(years):
            grass.fatal("Number of rows of storm length data in your climate file\n do not match the number of iterations you wish to run.\n Please ensure that these numbers match and try again")
            sys.exit(1)
    #get the process id to tag any temporary maps we make for easy clean up in the loop
    pid = os.getpid()
    #we need to separate out flags used by this script, and those meant to be sent to r.landscape.evol. We will do this by popping them out of the default "flags" dictionary, and making a new dictionary called "use_flags"
    use_flags = {}
    use_flags.update({'g': flags.pop('g'), 'f': flags.pop('f'), 'c': flags.pop('c'), 'p': flags.pop('p')})
    #now assemble the flag string for r.landscape.evol'
    levol_flags = []
    for flag in flags:
        if flags[flag] is True:
            levol_flags.append(flag)
    #check if maxlcov is a map or a number, and grab the actual max value for the stats file
    try:
        maxval = int(float(maxlcov))
    except:
        maxlcovdict = grass.parse_command('r.univar', flags = 'ge', map = maxlcov)
        maxval = int(float(maxlcovdict['max']))
    #set up the stats files names
    env = grass.gisenv()
    statsdir = os.path.join(env['GISDBASE'], env['LOCATION_NAME'], env['MAPSET'])
    textout = statsdir + os.sep + prfx + '_landcover_temporal_matrix.txt'
    statsout = statsdir + os.sep + prfx + '_erdep_stats.txt'
    # Make color rules for landcover, cfactor, and soil fertilty maps
    lccolors = tempfile.NamedTemporaryFile()
    lccolors.write('0 grey\n10 red\n20 orange\n30 brown\n40 yellow\n%s green' % maxval)
    lccolors.flush()
    cfcolors = tempfile.NamedTemporaryFile()
    cfcolors.write('0.1 grey\n0.05 red\n0.03 orange\n0.01 brown\n0.008 yellow\n0.005 green')
    cfcolors.flush()
    #find out number of digits in 'years' for zero padding
    digits = len(str(abs(years)))
    grass.message('Simulation will run for %s iterations.\n\n............................STARTING SIMULATION...............................' % years)
    #Set up loop
    for year in range(int(years)):
        now = str(year + 1).zfill(digits)
        then = str(year).zfill(digits)
#        if numpeople == 0:
#            grass.fatal("Everybody is dead. \nSimulation stopped at year %s." % then)
        #grab the current climate vars from the lists
        rain = rain2[year]
        r = R2[year]
        storms = storms2[year]
        stormlength = stormlength2[year]
        #figure out total precip (in meters) for the year for use in the veg growth and farm yields formulae
        precip = 0.001 * (float(rain) * float(storms))
        grass.message('_____________________________\nSIMULATION YEAR: %s\n--------------------------' % now)
        #make some map names
        outlcov = "%s_Year_%s_Landcover_Map" % (prfx, now)
        outcfact = "%s_Year_%s_Cfactor_Map" % (prfx, now)
        outxs = "%s_Year_%s_Rainfall_Excess_Map" % (prfx, now)
        natural_fires = "%s_Year_%s_Natural_Fires_map" % (prfx, now)
        #check if this is year one, use the starting landcover and soilfertily and calculate soildepths
        if (year + 1) == 1:
            oldlcov = inlcov
            oldsdepth = "%s_Year_%s_Soil_Depth_Map" % (prfx, then)
            grass.mapcalc("${sdepth}=(${elev}-${bdrk})", quiet ="True", sdepth = oldsdepth, elev = elev, bdrk = initbdrk)
        else:
            oldlcov = "%s_Year_%s_Landcover_Map" % (prfx, then)
            oldsdepth = "%s_Year_%s_Soil_Depth_Map" % (prfx, then)
            
        # Calculate natural (lightning-caused) fire ignition on the landscape
        # parse fire probability map into three with mapcalc:
        lowprobmap = "%stemp_fireprob_low" % pid
        medprobmap = "%stemp_fireprob_med" % pid
        hiprobmap = "%stemp_fireprob_hi" % pid
        # Hardcoding cutoffs for no, low, medium, high probability based on histogram of spanish fire probability map.
        grass.mapcalc("${lowprobmap}=if(${fireprob} <= 0.2, 1, null())", quiet = "True", fireprob=fireprob, lowprobmap=lowprobmap)
        grass.mapcalc("${medprobmap}=if(${fireprob} > 0.2 || ${fireprob} <= 0.6, 1, null())", quiet = "True", fireprob=fireprob, medprobmap=medprobmap)
        grass.mapcalc("${hiprobmap}=if(${fireprob} > 0.6, 1, null())", quiet = "True", fireprob=fireprob, hiprobmap=hiprobmap)
        # randomly sample each of these maps at different densities (find out actual densities from Grant):
        fires1 = "%sfires_low" % pid
        fires2 = "%sfires_med" % pid
        fires3 = "%sfires_hi" % pid
        grass.run_command('r.random', quiet = 'True', input="lowprobmap", raster=fires1, npoints="5%")
        grass.run_command('r.random', quiet = 'True', input="medprobmap", raster=fires2, npoints="10%")
        grass.run_command('r.random', quiet = 'True', input="hiprobmap", raster=fires3, npoints="15%")
        # patch those back to make final map of fire locations
        grass.run_command('r.patch', input="fires1,fires2,fires3", output=natural_fires)
        #update landcover
        # calculating rate of regrowth based on current soil fertility, spil depths, and precipitation. Recoding fertility (0 to 100%), depth (0 to >= 1m), and precip (0 to >= 1000mm) with a power regression curve from 0 to 1, then taking the mean of the two as the regrowth rate
        growthrate = "%stemporary_vegetation_regrowth_map" % pid
        grass.mapcalc('${growthrate}=eval(x=if(${sdepth} <= 1.0, ( -0.000118528 * (exp((100*${sdepth}),2.0))) + (0.0215056 * (100*${sdepth})) + 0.0237987, 1), y=if(${precip} <= 1.0, ( -0.000118528 * (exp((100*${precip}),2.0))) + (0.0215056 * (100*${precip})) + 0.0237987, 1), z=(-0.000118528 * (exp(${outfert},2.0))) + (0.0215056 * ${outfert}) + 0.0237987, a=if(x <= 0 || z <= 0, 0, (x+y+z)/3), if(a < 0, 0, a) )', quiet = "True", growthrate = growthrate,  sdepth = oldsdepth, outfert = infert, precip = precip)
        #Calculate this year's landcover impacts and regrowth
        #If there was a fire, vegetation goes to 0 no matter what was there, otherwise regrow at calculated rate.
        grass.mapcalc("${outlcov}=eval(a=if(${oldlcov} + ${growthrate} >= ${maxlcov}, ${maxlcov}, ${oldlandcov} + ${growthrate}), b=if(isnull(${natural_fires}), a, 0))", quiet = "True", overwrite = "True", outlcov = outlcov, oldlcov=oldlcov, growthrate=growthrate, natural_fires = natural_fires)
        #Make a rainfall excess map to send to r.landcape.evol. This is a logarithmic regression (R^2=0.99.) for the data pairs: 0,90;3,85;8,70;13,60;19,45;38,30;50,20. These are the same succession cutoffs that are used in the c-factor coding.
        grass.mapcalc("${outxs}=193.522 - (42.3272 * log(${lcov} + 10.9718))", quiet = "True", outxs = outxs, lcov = outlcov)
        #if rules set exists, create reclassed landcover labels map
        try:
            temp_reclass = "%stemporary_reclassed_landcover" %pid
            grass.run_command('r.reclass', quiet = "True",  input = outlcov,  output = temp_reclass,  rules = lc_rules)
            grass.mapcalc('${out}=${input}', quiet = "True", overwrite = "True", out = outlcov, input = temp_reclass)
        except:
            grass.warning("No landcover labling rules found at path \"%s\"\nOutput landcover map will not have text labels in queries" % lc_rules)
        grass.run_command('r.colors',  quiet = "True",  map = outlcov, rules = lccolors.name)
        #collect and write landcover temporal matrix
        grass.message('Collecting some landcover and fertility stats from this year....')
        f = open(textout, 'a')
        if os.path.getsize(textout) == 0:
            f.write("Temporal Matrix of Landcover\n\nYear," + ",".join(str(i) for i in range(maxval + 1)) + "\n")
        statdict = grass.parse_command('r.stats', quiet = "True",  flags = 'ani', input = outlcov, separator = '=', nv ='*')
        f.write("%s," % now)
        for key in range(maxval + 1):
            try:
                f.write(statdict[str(key)] + "," )
            except:
                f.write("0,")
        f.write("\n")
        f.close()
        #creating c-factor map
        grass.message('Creating C-factor map for r.landscape.evol')
        try:
            grass.run_command('r.recode', quiet = True, input = outlcov, output = outcfact, rules = cfact_rules)
        except:
            grass.fatal("NO CFACTOR RECLASS RULES WERE FOUND AT PATH \"%s\"\nPLEASE ENSURE THAT THE CFACTOR RECODE RULES EXIST AND ARE WRITTEN PROPERLY, AND THEN TRY AGAIN" % cfact_rules)
            sys.exit(1)
        grass.run_command('r.colors',  quiet = True, map = outcfact, rules = cfcolors.name)
        #Run r.landscape.evol with this years' cfactor map
        grass.message('Running landscape evolution for this year....')
        #set the prefix for r.landscape.evol output files
        prefix = prfx + "_Year_%s_" % now
        #check if this is year one, and use the starting dem if so
        if (year + 1) == 1:
            inelev = elev
        else:
            inelev = "%s_Year_%s_Elevation_Map" % (prfx, then)
        try:
            grass.run_command('r.landscape.evol', quiet = "True", number = 1, prefx = prefix, c = outcfact, elev = inelev, initbdrk = initbdrk, outdem = "Elevation_Map", outsoil = "Soil_Depth_Map", r = r, k = k, sdensity = sdensity, kappa = kappa, manningn = manningn, flowcontrib = outxs, cutoff1 = cutoff1, cutoff2 = cutoff2, cutoff3 = cutoff3, rain = rain, storms = storms, stormlength = stormlength, speed = speed, kt = kt, loadexp = loadexp, smoothing = smoothing, statsout = statsout, flags = ''.join(levol_flags))
        except:
            grass.fatal("Something is wrong with the values you sent to r.landscape.evol. Did you forget something? Check the values and try again...\nSimulation terminated with an error at time step %s" % now)
            sys.exit(1)
        #delete C-factor map, unless asked to save it
        if use_flags['c'] is False:
            grass.run_command("g.remove", quiet = "True", flags = 'f', type = "rast", name = "%s,%s" %  (outcfact,outxs))
        else:
            pass
        #clean up temporary maps
        grass.run_command('g.remove', quiet = "True", flags = 'f', type = "rast", pattern = '%s*' % pid)
        grass.message('Completed year %s of the simulation' % now)
    lccolors.close()
    cfcolors.close()
    return(grass.message(".........................SIMULATION COMPLETE...........................\nCheck in the current mapset for farming/grazing yields, landcover, fertility, and erosion/depostion stats files from this run."))
        


#Here is where the code in "main" actually gets executed. This way of programming is neccessary for the way g.parser needs to run.
if __name__ == "__main__":
    options, flags = grass.parser()
    main()
    exit(0)