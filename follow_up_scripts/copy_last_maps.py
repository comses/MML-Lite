import grass.script as grass

###############################
#  EDIT VALS BELOW THIS LINE  #
###############################

PREFIX = "120pmx_"						#Map prefix used in the original sim
YEAR = 300									#Number of the year (infixed to map name) to copy all maps

###############################
# DO NOT EDIT BELOW THIS LINE #
###############################

#use g.mlist to generate a list of all the maps in all mapsets to copy
maplist = grass.read_command('g.list', flags='m', type='rast', pattern="*%s*" % YEAR, separator=',').strip().split(',')
#Now loop through that list, and run g.copy, but change the name a bit to make it clear what maps are what
for inmap in maplist:
	outmap = "%s_%s" % (inmap.split('@')[0], inmap.split('@')[1])
	grass.run_command("g.copy", quiet= "True", rast="%s,%s" % (inmap, outmap))
