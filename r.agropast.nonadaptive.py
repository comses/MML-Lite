#!/usr/bin/python
#
############################################################################
#
# MODULE:       	r.agropast.nonadaptive.py
# AUTHOR(S):		Isaac Ullah, University of Pittsburgh
# PURPOSE:		Simulates agricultural and pastoral landuse and tracks yields and environmental
#                          impacts. Farming and grazing strategies and catchments are predetermined by the
#                          researcher, and do not change (adapt) during the simulation. Requires
#                          r.landscape.evol.
# ACKNOWLEDGEMENTS:	National Science Foundation Grant #BCS0410269, Center for Comparative Archaeology at
#                          the University of Pittsburgh, Center for Social Dynamics and Complexity at Arizona
#                          State University
# COPYRIGHT:		(C) 2014 by Isaac Ullah, University of Pittsburgh
#			This program is free software under the GNU General Public
#			License (>=v2). Read the file COPYING that comes with GRASS
#			for details.
#
#############################################################################


#%Module
#%  description: Simulates agricultural and pastoral landuse and tracks yields and environmental impacts. Farming and grazing strategies and catchments are predetermined by the researcher, and do not change (adapt) during the simulation. Requires r.landscape.evol. Note that some stats files will be written to current mapset, and will be appended to if you run the simulation again with the same prefix.
#%END

##################################
#Simulation Control
##################################
#%option
#% key: years
#% type: integer
#% description: Number of iterations ("years") to run
#% answer: 50
#% guisection: Simulation Control
#%END
#%option
#% key: prfx
#% type: string
#% description: Prefix for all output maps
#% answer: simulation
#% guisection: Simulation Control
#%END

##################################
#Farming Options
##################################
#%option
#% key: agcatch
#% type: string
#% gisprompt: old,cell,raster
#% description: Input extensive agricultural catchment map (From r.catchment or r.buffer, where catchment is a single integer value, and all else is NULL)
#% guisection: Farming
#%END
#%option
#% key: agpercent
#% type: double
#% description: Percent of area to be used as farm fields (Exact site of fields is random)
#% answer: 20
#% guisection: Farming
#%END
#%option
#% key: nsfieldsize
#% type: double
#% description: North-South dimension of fields in map units (Large field sizes may lead to some overshoot of catchment boundaries)
#% answer: 45
#% guisection: Farming
#%END
#%option
#% key: ewfieldsize
#% type: double
#% description: East-West dimension of fields in map units (Large field sizes may lead to some overshoot of catchment boundaries)
#% answer: 45
#% guisection: Farming
#%END
#%option
#% key: farmval
#% type: double
#% description: The landcover value for farmed fields (Should correspond to an appropriate value from your landcover rules file.)
#% answer: 5
#% guisection: Farming
#%END
#%option
#% key: farmimpact
#% type: double
#% description: The mean and standard deviation of the amount to which farming a patch decreases its fertility (in percentage points of maximum fertility, entered as: "mean,std_dev"). Fertility impact values of indvidual farm plots will be randomly chosen from a gaussian distribution that has this mean and std_dev.
#% answer: 5,2
#% multiple: yes
#% guisection: Farming
#%END
#%option
#% key: maxwheat
#% type: double
#% description: Maximum amount of wheat that can be grown (kg/ha)
#% answer: 3000
#% guisection: Farming
#%END
#%option
#% key: maxbarley
#% type: double
#% description: Maximum amount of barley that can be grown (kg/ha)
#% answer: 3000
#% guisection: Farming
#%END

##################################
#Grazing Options
##################################
#%option
#% key: grazecatch
#% type: string
#% gisprompt: old,cell,raster
#% description: Input grazing catchment map (From r.catchment or r.buffer, where catchment is a single integer value, and all else is NULL)
#% guisection: Grazing
#%END
#%option
#% key: grazespatial
#% type: double
#% description: Spatial dependency of the grazing pattern in map units. This value determines how "clumped" grazing will be. A value close to 0 will produce a perfectly randomized grazing pattern, and larger values will produce increasingly clumped grazing patterns, with the size of the clumps corresponding to the value of grazespatial (in map units).
#% answer: 100
#% guisection: Grazing
#%END
#%option
#% key: grazepatchy
#% type: double
#% description: Coefficient that determines the patchiness of the grazing catchemnt. Value must be non-zero, and usually will be <= 1.0. Values close to 0 will create a patchy grazing pattern, values close to 1 will create a "smooth" grazing pattern. Actual grazing patches will be sized to the resolution of the input landcover map.
#% answer: 1.0
#% guisection: Grazing
#%END
#%option
#% key: maxgrazeimpact
#% type: integer
#% description: Maximum impact of grazing in units of "landcover.succession". Grazing impact values of individual patches will be chosen from a gaussian distribution between 1 and this maximum value (i.e., most values will be between 1 and this max). Value must be >= 1.
#% answer: 2
#% guisection: Grazing
#%END
#%option
#% key: manurerate
#% type: double
#% description: Base rate for animal dung contributes to fertility increase on a grazed patch in units of percentage of maximum fertility regained per increment of grazing impact. Actual fertility regain values are thus calculated as "manure_rate x grazing_impact", so be aware that this variable interacts with the grazing impact settings you have chosen.
#% answer: 0.2
#% guisection: Grazing
#%END
#%option
#% key: fodder_rules
#% type: string
#% gisprompt: string
#% description: Path to foddering rules file for calculation of fodder gained by grazing
#% answer: /home/iullah/Scripts_Working_Dir/rules/fodder_rules.txt
#% guisection: Grazing
#%END
#%flag
#% key: f
#% description: -f Do not graze in unused portions of the agricultural catchment (i.e., do not graze on "fallowed" fields, and thus no "manuring" of those fields will occur)
#% guisection: Grazing
#%end
#%flag
#% key: g
#% description: -g Do not allow "stubble grazing" on harvested fields (and thus no "manuring" of fields)
#% guisection: Grazing
#%end

##################################
#Landcover Dynamics Options
##################################
#%option
#% key: fertilrate
#% type: double
#% description: Comma separated list of the mean and standard deviation of the natural fertility recovery rate (percentage by which soil fertility increases per year if not farmed, entered as: "mean,stdev".) Fertility recovery values of individual landscape patches will be randomly chosen from a gaussian distribution that has this mean and std_dev.
#% answer: 1,0.5
#% multiple: yes
#% guisection: Landcover Dynamics
#%END
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
#% key: maxlcov
#% type: string
#% gisprompt: old,cell,raster
#% description: Maximum value of landcover for the landscape (Can be a single numerical value or a cover map of different maximum values. Shouldn't exceed maximum value in rules file')
#% answer: 50
#% guisection: Landcover Dynamics
#%END
#%option
#% key: maxfert
#% type: string
#% gisprompt: old,cell,raster
#% description: Maximum value of fertility for the landscape (Can be a single numerical value or a cover map of different maximum values. Shouldn't exceed 100)
#% answer: 100
#% guisection: Landcover Dynamics
#%END
#%option
#% key: lc_rules
#% type: string
#% gisprompt: string
#% description: Path to reclass rules file for landcover map
#% answer: /home/iullah/Scripts_Working_Dir/rules/luse_reclass_rules.txt
#% guisection: Landcover Dynamics
#%END
#%option
#% key: cfact_rules
#% type: string
#% gisprompt: string
#% description: Path to recode rules file for c-factor map
#% answer: /home/iullah/Scripts_Working_Dir/rules/cfactor_recode_rules.txt
#% guisection: Landcover Dynamics
#%END
#%flag
#% key: c
#% description: -c Keep C-factor maps for each year
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
#% key: K
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
#% key: Kt
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
#% key: kappa
#% type: double
#% description: Hillslope diffusion (Kappa) rate map or constant [m/kyr]
#% answer: 1
#% guisection: Landscape Evolution
#%end
#%option
#% key: rain
#% type: double
#% gisprompt: old,cell,raster
#% description: Precip totals for the average storm [mm] (or path to climate file of comma separated values of "rain,R,storms,stormlength", with a new line for each year of the simulation)
#% answer: 20.61
#% guisection: Landscape Evolution
#%end
#%option
#% key: R
#% type: double
#% description: Rainfall (R factor) constant (AVERAGE FOR WHOLE MAP AREA) (or path to climate file of comma separated values of "rain,R,storms,stormlength", with a new line for each year of the simulation)
#% answer: 4.54
#% guisection: Landscape Evolution
#%end
#%option
#% key: storms
#% type: integer
#% description: Number of storms per year (integer) (or path to climate file of comma separated values of "rain,R,storms,stormlength", with a new line for each year of the simulation)
#% answer: 25
#% guisection: Landscape Evolution
#%end
#%option
#% key: stormlength
#% type: double
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
#% answer: 0.65
#% guisection: Landscape Evolution
#%end
#%option
#% key: cutoff2
#% type: double
#% description: Flow accumulation breakpoint value for shift from overland flow to rill/gully flow (if value is the same as cutoff1, no sheetwash procesess will be modeled)
#% answer: 2.25
#% guisection: Landscape Evolution
#%end
#%option
#% key: cutoff3
#% type: double
#% description: Flow accumulation breakpoint value for shift from rill/gully flow to stream flow (if value is the same as cutoff2, no rill procesess will be modeled)
#% answer: 7
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
#% description: -1 Calculate streams as 1D difference instead of 2D divergence (forces heavy incision in streams)
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


import os
import tempfile
import grass.script as grass

#main block of code starts here
def main():
    grass.message("Setting up Simulation........")
    #setting up Land Use variables for use later on
    agcatch = options['agcatch']
    agpercent = options['agpercent'] + '%'
    nsfieldsize = options['nsfieldsize']
    ewfieldsize = options['ewfieldsize']
    grazecatch = options['grazecatch']
    grazespatial = options['grazespatial']
    grazepatchy = options['grazepatchy']
    maxgrazeimpact = options['maxgrazeimpact']
    manurerate = options['manurerate']
    inlcov = options['inlcov']
    years = int(options['years'])
    farmval = options['farmval']
    maxlcov = options['maxlcov']
    prfx = options['prfx']
    lc_rules = options['lc_rules']
    cfact_rules = options['cfact_rules']
    fodder_rules = options['fodder_rules']
    infert = options['infert']
    maxfert = options['maxfert']
    maxwheat = options['maxwheat']
    maxbarley = options['maxbarley']
    #these are various rates with min and max values entered in the gui that we need to parse
    farmimpact = map(float, options['farmimpact'].split(','))
    fertilrate = map(float, options['fertilrate'].split(','))
    #Setting up Landscape Evol variables to write the r.landscape.evol command later
    elev = options["elev"]
    initbdrk = options["initbdrk"]
    K = options["K"]
    sdensity = options["sdensity"]
    kappa = options["kappa"]
    cutoff1 = options["cutoff1"]
    cutoff2 = options["cutoff2"]
    cutoff3 = options["cutoff3"]
    speed = options["speed"]
    Kt = options["Kt"]
    loadexp = options["loadexp"]
    smoothing = options["smoothing"]
    #these values could be read in from a climate file, so check that, and act accordingly
    rain2 = []
    try:
        rain1 = float(options["rain"])
        for year in range(int(years)):
            rain2.append(rain1)
    except:
        with open(options["rain"], 'rU') as f:
            for line in f:
                rain2.append(line.split(",")[0])
    R2 = []
    try:
        R1 = float(options["R"])
        for year in range(int(years)):
            R2.append(R1)
    except:
        with open(options["R"], 'rU') as f:
            for line in f:
                R2.append(line.split(",")[1])
    storms2 = []
    try:
        storms1 = float(options["R"])
        for year in range(int(years)):
            storms2.append(storms1)
    except:
        with open(options["storms"], 'rU') as f:
            for line in f:
                storms2.append(line.split(",")[2])
    stormlength2 = []
    try:
        stormlength1 = float(options["R"])
        for year in range(int(years)):
            stormlength2.append(stormlength1)
    except:
        with open(options["stormlength"], 'rU') as f:
            for line in f:
                stormlength2.append(line.split(",")[3])
    #get the process id to tag any temporary maps we make for easy clean up in the loop
    pid = os.getpid()
    #check if the -g -f or -c flags are marked, pop them if so, and set a boolean value for their prescence/abscence
    if flags['g'] is True:
        g_flag = flags.pop('g')
    else:
        g_flag = {'g': False}
    if flags['f'] is True:
        f_flag = flags.pop('f')
    else:
        f_flag = {'f': False}
    if flags['c'] is True:
        c_flag = flags.pop('c')
    else:
        c_flag = {'c': False}
    #assemble the flag string for r.landscape.evol'
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
    #check if maxfert is a map or a number, and grab the actual max value for the stats file
    try:
        maxfertval = int(float(maxfert))
    except:
        maxfertdict = grass.parse_command('r.univar', flags = 'ge', map = maxfert)
        maxfertval = int(float(maxfertdict['max']))
    #set up the stats files names
    env = grass.gisenv()
    statsdir = os.path.join(env['GISDBASE'], env['LOCATION_NAME'], env['MAPSET'])
    textout = statsdir + os.sep + prfx + '_landcover_temporal_matrix.txt'
    textout2 = statsdir + os.sep + prfx + '_fertility_temporal_matrix.txt'
    textout3 = statsdir + os.sep + prfx + '_yields_stats.txt'
    textout4 = statsdir + os.sep + prfx + '_landcover_and_fertility_stats.txt'
    statsout = statsdir + os.sep + prfx + '_erdep_stats.txt'
    # Make color rules for landcover, cfactor, and soil fertilty maps
    lccolors = tempfile.NamedTemporaryFile()
    lccolors.write('0 grey\n10 red\n20 orange\n30 brown\n40 yellow\n%s green' % maxval)
    lccolors.flush()
    cfcolors = tempfile.NamedTemporaryFile()
    cfcolors.write('0.1 grey\n0.05 red\n0.03 orange\n0.01 brown\n0.008 yellow\n0.005 green')
    cfcolors.flush()
    fertcolors = tempfile.NamedTemporaryFile()
    fertcolors.write('0 white\n20 grey\n40 yellow\n60 orange\n80 brown\n100 black')
    fertcolors.flush()
    #Figure out the number of cells per hectare and per square meter to use as conversion factors for yields
    region = grass.region()
    cellperhectare = 100000 / (float(region['nsres']) * float(region['ewres']))
    #cellpersqm = 1 / (float(region['nsres']) * float(region['ewres']))
    #find out number of digits in 'years' for zero padding
    digits = len(str(abs(years)))
    grass.message('............................STARTING SIMULATION............................\nSimulation will run for %s iterations.' % years)
    #Set up loop
    for year in range(int(years)):
        now = str(year + 1).zfill(digits)
        then = str(year).zfill(digits)
        #grab the current climate vars from the lists
        rain = rain2[year]
        R = R2[year]
        storms = storms2[year]
        stormlength = stormlength2[year]
        #figure out total precip (in meters) for the year for use in the veg growth and farm yields formulae
        precip = 0.001 * (float(rain) * float(storms))
        grass.message('_____________________________\nSIMULATION YEAR: %s\n--------------------------' % now)
        #make some map names
        fields = "%s_Year_%s_Farming_Impacts_Map" % (prfx, now)
        outlcov = "%s_Year_%s_Landcover_Map" % (prfx, now)
        outfert = "%s_Year_%s_Soil_Fertilty_Map" % (prfx, now)
        outcfact = "%s_Year_%s_Cfactor_Map" % (prfx, now)
        grazeimpacts = "%s_Year_%s_Gazing_Impacts_Map" % (prfx, now)
        #check if this is year one, and use the starting landcover and soilfertily if so, and calculate soildepths
        if (year + 1) == 1:
            oldlcov = inlcov
            oldfert = infert
            oldsdepth = "%s_Year_%s_Soil_Depth_Map" %(prfx, then)
            grass.mapcalc("${sdepth}=${elev}-${bdrk}", quiet ="True", sdepth = oldsdepth, elev = elev, bdrk = initbdrk)
        else:
            oldlcov = "%s_Year_%s_Landcover_Map" % (prfx, then)
            oldfert = "%s_Year_%s_Soil_Fertilty_Map" % (prfx, then)
            oldsdepth = "%s_Year_%s_Soil_Depth_Map" %(prfx, then)
        #GENERATE MAPS OF POTENTIAL FARM AND GRAZING YIELDS
        grass.message("Calculating potential farming and grazing yields.....")
        #Calculate the wheat yield map (kg/cell)
        tempwheatreturn = "%stemporary_wheat_yields_map" % pid
        grass.mapcalc("${tempwheatreturn}=eval(x=if(${precip} > 0, (0.51*log(${precip}))+1.03, 0), y=if(${sfertil} > 0, (0.28*log(${sfertil}))+0.87, 0), z=if(${sdepth} > 0, (0.19*log(${sdepth}))+1, 0), a=((((x*y*z)/3)*${maxwheat})/${cellperhectare}), if(a < 0, 0, a))", quiet = "True", tempwheatreturn = tempwheatreturn, precip = precip, sfertil = oldfert, sdepth = oldsdepth, maxwheat = maxwheat, cellperhectare = cellperhectare)
        #Calculate barley yield map (kg/cell)
        tempbarleyreturn = "%stemporary_barley_terurn_map" % pid
        grass.mapcalc("${tempbarleyreturn}=eval(x=if(${precip} > 0, (0.48*log(${precip}))+1.51, 0), y=if(${sfertil} > 0, (0.34*log(${sfertil}))+1.09, 0), z=if(${sdepth} > 0, (0.18*log(${sdepth}))+0.98, 0), a=((((x*y*z)/3)*${maxbarley})/${cellperhectare}), if(a < 0, 0, a))", quiet = "True", tempbarleyreturn = tempbarleyreturn, precip = precip, sfertil = oldfert, sdepth = oldsdepth, maxbarley = maxbarley, cellperhectare = cellperhectare)
        #Calculate grazing yield map (kg/cell)
        tempgrazereturn = "%stemporary_grazing_returns_map" % pid
        grass.run_command('r.recode', quiet = 'True',  input = oldlcov, output = tempgrazereturn, rules = fodder_rules)
        #GENERATE FARM IMPACTS
        grass.message('Generating new farmed fields in %s percent of agcatch...' % agpercent)
        #create some temp map names
        tempfields = "%stemporary_fields_map" % pid
        tempimpacta = "%stemporary_farming_fertility_impact" % pid
        #temporarily change region resolution to align to farm field size
        grass.use_temp_region()
        grass.run_command('g.region', quiet = 'True',nsres = nsfieldsize, ewres = ewfieldsize)
        #run r.random to get fields
        grass.run_command('r.random', quiet = 'True', input = agcatch, n = agpercent, raster_output = tempfields)
        #use r.surf.gaussian to cacluate fertily impacts in these areas
        grass.run_command('r.surf.gauss', quiet = "True", output = tempimpacta, mean = farmimpact[0], sigma = farmimpact[1])
        grass.mapcalc("${fields}=if(isnull(${a}), null(), ${b})", quiet = "True", fields = fields, a = tempfields, b = tempimpacta)
        #grab some yiled stats while region is still aligned to desired field size
        #first make a temporary "zone" map for the farmed areas in which to run r.univar
        tempfarmzone = "%stemporary_farming_zones_map" % pid
        grass.mapcalc("${tempfarmzone}=if(isnull(${fields}), null(), 1)", quiet = "True", tempfarmzone = tempfarmzone, fields = fields)
        #now use this zone map to grab some yeilds for this year's farmed fields
        wheatstats = grass.parse_command('r.univar', flags = 'ge', percentile = '90', map = tempwheatreturn, zones = tempfarmzone)
        barleystats = grass.parse_command('r.univar', flags = 'ge', percentile = '90', map = tempbarleyreturn, zones = tempfarmzone)
        #reset region to original resolution
        grass.del_temp_region()
        #GENERATE GRAZING IMPACTS
        grass.message('Generating new grazing patches in grazecatch...')
        tempimpactg = "%stemporary_grazing_impact" % pid
        #generate basic impact values
        grass.run_command("r.random.surface", quiet = "True", output = tempimpactg, distance = grazespatial, exponent = grazepatchy, high = maxgrazeimpact)
        #determine locational options, and clip them to the grazing catchment, or allow in the fallowed areas of the agricultural catchment
        if f_flag['f'] is False:
            grass.mapcalc("${grazeimpacts}=if(${grazecatch} && isnull(${fields}),${tempimpactg}, null())", quiet = "True", grazeimpacts = grazeimpacts, grazecatch = grazecatch, tempimpactg = tempimpactg, fields = fields)
        else:
            grass.mapcalc("${grazeimpacts}=if(${grazecatch} && isnull(${agcatch}), ${tempimpactg}, null())", quiet = "True", grazeimpacts = grazeimpacts, grazecatch = grazecatch, tempimpactg = tempimpactg, agcatch = agcatch)
        #now get some grazing yields stats
        #first make a temporary "zone" map for the grazed areas (checking if stubble grazing is allowed or not) in which to run r.univar
        tempgrazezone = "%stemporary_grazing_zones_map" % pid
        if g_flag['g'] is False:
            grass.mapcalc("${tempgrazezone}=if(isnull(${grazeimpacts}), null(), 1)", quiet = "True", tempgrazezone = tempgrazezone, grazeimpacts = grazeimpacts)
        else:
            grass.mapcalc("${tempgrazezone}=if(isnull(${grazeimpacts}) && isnull(${fields}), null(), 1)", quiet = "True", tempgrazezone = tempgrazezone, grazeimpacts = grazeimpacts, fields = fields)
        #now grab the univar stats with this zone file
        grazestats = grass.parse_command('r.univar', flags = 'ge', percentile = '90', map = tempgrazereturn, zones = tempgrazezone)
        #write the yield stats to the stats file
        grass.message('Collecting some farming and grazing yields stats from this year....')
        f = open(textout3, 'a')
        if os.path.getsize(textout3) == 0:
            f.write("Farming and Grazing Yields Stats\nFarming stats in Kg wheat or barley seeds per farmplot. Note that both barley and wheat stats are calculated as if ONLY barley OR wheat was grown.\nGrazing stats in Kg of digestable matter per grazing plot. Note that this may also include stubble grazing if enabled.\n\nYear,,Mean Barley,Standard Deviation Barley,Minimum Barley,First Quartile Barley,Median Barley,Third Quartile Barley,Maximum Barley,Total Barley Harvested,,Mean Wheat,Standard Deviation Wheat,Minimum Wheat,First Quartile Wheat,Median Wheat,Third Quartile Wheat,Maximum Wheat,Total Wheat Harvested,,Mean Fodder,Standard Deviation Fodder,Minimum Fodder,First Quartile Fodder,Median Fodder,Third Quartile Fodder,Maximum Fodder, Total Fodder Consumed")
        f.write('\n%s' % now + ',,' + barleystats['mean'] + ',' + barleystats['stddev'] + ',' + barleystats['max'] + ',' + barleystats['third_quartile'] + ',' + barleystats['median'] + ',' + barleystats['first_quartile'] + ',' + barleystats['min'] + ',' + barleystats['sum'] + ',,' + wheatstats['mean'] + ',' + wheatstats['stddev'] + ',' + wheatstats['min'] + ',' + wheatstats['first_quartile'] + ',' + wheatstats['median'] + ',' + wheatstats['third_quartile'] + ',' + wheatstats['max'] + ',' + wheatstats['sum'] + ',,' + grazestats['mean'] + ',' + grazestats['stddev'] + ',' + grazestats['min'] + ',' + grazestats['first_quartile'] + ',' + grazestats['median'] + ',' + grazestats['third_quartile'] + ',' + grazestats['max'] + ',' + grazestats['sum'])
        #UPDATE LANDCOVER AND SOIL FERTILITY
        grass.message('Updating landcover and soil fertility with new impacts')
        #update fertility
        tempfertil = "%stemporary_fertility_regain_map" % pid
        #use r.surf.gaussian to cacluate fertily regain map
        grass.run_command('r.surf.gauss', quiet = "True", output = tempfertil, mean = fertilrate[0], sigma = fertilrate[1])
        #figure out what happened to fertility (see if stubble-grazing is enabled, and make sure to add some manure where grazing occured, scaled to the degree of graing that happened)
        if g_flag['g'] is False:
            grass.mapcalc("${outfert}=eval(a=if(isnull(${grazeimpacts}) && isnull(${fields}), ${tempfertil}, ${tempfertil} + (${manurerate} * ${tempimpactg})), b=if(isnull(${fields}), ${oldfert}, ${oldfert} - ${fields}), if(b <= ${maxfert} - a, b + a, ${maxfert}))", quiet = "True", outfert = outfert, oldfert = oldfert, fields = fields, tempimpactg = tempimpactg, grazeimpacts = grazeimpacts, manurerate = manurerate, maxfert = maxfert, tempfertil = tempfertil)
        else:
            grass.mapcalc("${outfert}=eval(a=if(isnull(${grazeimpacts}), ${tempfertil}, ${tempfertil} + (${manurerate} * ${tempimpactg})), b=if(isnull(${fields}), ${oldfert}, ${oldfert} - ${fields}), if(b <= ${maxfert} - a, b + a, ${maxfert}))", quiet = "True", outfert = outfert, oldfert = oldfert, fields = fields, tempimpactg = tempimpactg, grazeimpacts = grazeimpacts, manurerate = manurerate, maxfert = maxfert, tempfertil = tempfertil)
        grass.run_command('r.colors', quiet = "True", map = outfert, rules = fertcolors.name)
        #update landcover
        # calculating rate of regrowth based on current soil fertility, spil depths, and precipitation. Recoding fertility (0 to 100%), depth (0 to >= 1m), and precip (0 to >= 1000mm) with a power regression curve from 0 to 1, then taking the mean of the two as the regrowth rate
        growthrate = "%stemporary_vegetation_regrowth_map" % pid
        grass.mapcalc('${growthrate}=eval(x=if(${sdepth} <= 1.0, ( -0.000118528 * (exp((100*${sdepth}),2.0))) + (0.0215056 * (100*${sdepth})) + 0.0237987, 1), y=if(${precip} <= 1.0, ( -0.000118528 * (exp((100*${precip}),2.0))) + (0.0215056 * (100*${precip})) + 0.0237987, 1), z=(-0.000118528 * (exp(${sfertil},2.0))) + (0.0215056 * ${sfertil}) + 0.0237987, if(x <= 0 && y <= 0 && z <= 0, 0, (x+y+z)/3) )', quiet = "True", growthrate = growthrate,  sdepth = oldsdepth,  sfertil = outfert, precip = precip)
        #Calculate this year's landcover impacts and regrowth
        grass.mapcalc("${outlcov}=eval(a=if(isnull(${fields}), ${oldlcov} - ${grazeimpacts} + ${growthrate}, ${farmval}) ,if(${oldlcov} < (${maxlcov} - ${growthrate}) && isnull(a), ${oldlcov} + ${growthrate}, if(isnull(a), ${maxlcov}, a) ))", quiet = "True", outlcov = outlcov, oldlcov = oldlcov, maxlcov = maxlcov, growthrate = growthrate, fields = fields, farmval = farmval, grazeimpacts = grazeimpacts)
        #if rules set exists, create reclassed landcover labels map
        try:
            temp_reclass = "%stemporary_reclassed_landcover" %pid
            grass.run_command('r.reclass', quiet = "True",  input = outlcov,  output = temp_reclass,  rules = lc_rules)
            grass.mapcalc('${out}=${input}', quiet = "True", overwrite = "True", out = outlcov, input = temp_reclass)
        except:
            grass.message("No landcover labling rules found at path \"%s\"\nOutput landcover map will not have text labels in queries" % lc_rules)
        grass.run_command('r.colors',  quiet = "True",  map = outlcov, rules = lccolors.name)
        #collect and write landcover and fertiltiy temporal matrices
        grass.message('Collecting some landcover and fertility stats from this year....')
        f = open(textout, 'a')
        if os.path.getsize(textout) == 0:
            f.write("Temporal Matrix of Landcover\n\nYear," + ",".join(str(i) for i in range(maxval + 1)) + "\n")
        statdict = grass.parse_command('r.stats', quiet = "True",  flags = 'ani', input = outlcov, fs = '=', nv ='*')
        f.write("%s," % now)
        for key in range(maxval + 1):
            try:
                f.write(statdict[str(key)] + "," )
            except:
                f.write("0,")
        f.write("\n")
        f.close()
        f = open(textout2, 'a')
        if os.path.getsize(textout2) == 0:
            f.write("Temporal Matrix of Soil Fertility\n\nYear," + ",".join(str(i) for i in range(maxfertval + 1)) + "\n")
        statdict = grass.parse_command('r.stats', quiet = "True",  flags = 'ani', input = outfert, fs = '=', nv ='*')
        f.write("%s," % now)
        for key in range(maxfertval + 1):
            try:
                f.write(statdict[str(key)] + "," )
            except:
                f.write("0,")
        f.write("\n")
        f.close()
        #collect and write univariate stats
        lcovstats = grass.parse_command('r.univar', flags = 'ge', percentile = '90', map = outlcov, zones = grazecatch)
        fertstats = grass.parse_command('r.univar', flags = 'ge', percentile = '90', map = outfert, zones = agcatch)
        f = open(textout4, 'a')
        if os.path.getsize(textout4) == 0:
            f.write("Landcover and Soil Fertility Stats\nNote that these stats are collected within the grazing catchment (landcover) and agricultural catchment (fertility) ONLY. Rest of the map is ignored.\n\nYear,,Mean Landcover,Standard Deviation Landcover,Minimum Landcover,First Quartile Landcover,Median Landcover,Third Quartile Landcover,Maximum Landcover,,Mean Soil Fertility,Standard Deviation Soil Fertility,Minimum Soil Fertility,First Quartile Soil Fertility,Median Soil Fertility,Third Quartile Soil Fertility,Maximum Soil Fertility")
        f.write('\n%s' % now + ',,' + lcovstats['mean'] + ',' + lcovstats['stddev'] + ',' + lcovstats['max'] + ',' + lcovstats['third_quartile'] + ',' + lcovstats['median'] + ',' + lcovstats['first_quartile'] + ',' + lcovstats['min'] + ',,' + fertstats['mean'] + ',' + fertstats['stddev'] + ',' + fertstats['min'] + ',' + fertstats['first_quartile'] + ',' + fertstats['median'] + ',' + fertstats['third_quartile'] + ',' + fertstats['max'])
        #creating c-factor map
        grass.message('Creating C-factor map for r.landscape.evol')
        try:
            grass.run_command('r.recode', quiet = True, input = outlcov, output = outcfact, rules = cfact_rules)
        except:
            grass.message("NO CFACTOR RELCLASS RULES WERE FOUND AT PATH \"%s\"\nPLEASE ENSURE THAT THE CFACTOR RECODE RULES EXIST AND ARE WRITTEN PROPERLY, AND THEN TRY AGAIN" % cfact_rules)
            exit(1)
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
        #grass.message('Year %s\norig elev map: %s\nusing elevation map: \"%s\"' % (now, elev, inelev)) #a  debugging message
        try:
            capture = grass.run_command('r.landscape.evol.py', quiet = "True", number = 1, prefx = prefix, C = outcfact, elev = inelev, initbdrk = initbdrk, outdem = "Elevation_Map", outsoil = "Soil_Depth_Map", R = R, K = K, sdensity = sdensity, kappa = kappa, cutoff1 = cutoff1, cutoff2 = cutoff2, cutoff3 = cutoff3, rain = rain, storms = storms, stormlength = stormlength, speed = speed, Kt = Kt, loadexp = loadexp, smoothing = smoothing, statsout = statsout, flags = ''.join(levol_flags))
        except:
            grass.message("Something is wrong with the values you sent to r.landscape.evol. Did you forget something? Check the values and try again...\nSimulation terminated with an error at time step %s" % now)
            exit(1)
        #delete C-factor map, unless asked to save it
        if c_flag['c'] is False:
            grass.run_command("g.remove", quiet = "True", rast = outcfact)
        else:
            pass
        #clean up temporary maps
        grass.run_command('g.mremove', quiet = "True", flags = 'f', rast = '%s*' % pid)
        grass.message('Completed year %s of the simulation' % now)
    lccolors.close()
    cfcolors.close()
    fertcolors.close()
    return(grass.message(".........................SIMULATION COMPLETE...........................\nCheck in the current mapset for farming/grazing yields, landcover, fertility, and erosion/depostion stats files from this run."))


#Here is where the code in "main" actually gets executed. This way of programming is neccessary for the way g.parser needs to run.
if __name__ == "__main__":
    options, flags = grass.parser()
    main()
