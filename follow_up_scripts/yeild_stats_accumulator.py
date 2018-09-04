import fnmatch
import os
import numpy as np

###############################
#EDIT VALS BELOW THIS LINE
BASEPATH = '/hdd/GRASS_DB/Spain_EAA2018_ETRS89_z30/'
FILEPATTERN = '*_pastoral_yields_stats.txt'
COLUMN = 1,3,9,10,13,15,16,19,20,28	#Comma separated list of columns to loop through. Columns should match the names on OUTPUTFILE.
SKIPHEADER = 35
OUTPUTFILE = "population.csv","number_of_fields.csv","per_field_harvest_mean.csv","per_field_harvest_stdv.csv","cereals_surplus.csv","number_of_herd_animals.csv","percent_of_grazing_catchment_used.csv","grazing_patch_mean.csv","grazing_patch_stdv.csv","fodder_surplus.csv"	#Comma separated list of output text file names. Should match the columns in COLUMN.
##############################

matches = []
for root, dirnames, filenames in os.walk(BASEPATH):
  for filename in fnmatch.filter(filenames, FILEPATTERN):
    matches.append(os.path.join(root, filename))
for col,fname in zip(COLUMN, OUTPUTFILE):
  print col, fname
  all_data = np.genfromtxt(matches.pop(0), dtype=float, delimiter=',', skip_header=SKIPHEADER, usecols=(col))
  print len(all_data)
  for match in matches:
    data = np.genfromtxt(match, dtype=float, delimiter=',', skip_header=SKIPHEADER, usecols=(col))
    print match, len(data)
    all_data = np.vstack((all_data, data))
  np.savetxt("%s%s%s" % (BASEPATH, os.sep, fname), all_data.T, delimiter=",")
