import fnmatch
import os
import numpy as np

###############################
#EDIT VALS BELOW THIS LINE
BASEPATH = '/home/mdlpd/GIS_DataBase/Exp_2/stats_files'
FILEPATTERN = '30pmx_*_erdep_stats.txt'
COLUMN = 2,3,4,6,7,8	#Comma separated list of columns to loop through. Columns should match the names on OUTPUTFILE.
SKIPHEADER = 3
OUTPUTFILE = "mean_erosion.csv","mean_deposition.csv","mean_soil_depth.csv","stdev_erosion.csv","stdev_deposition.csv","stdev_soil_depth.csv"	#Comma separated list of output text file names. Should match the columns in COLUMN.
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
