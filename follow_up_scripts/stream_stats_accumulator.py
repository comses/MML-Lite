import fnmatch
import os
import numpy as np
from scipy import stats

###############################
#EDIT VALS BELOW THIS LINE
BASEPATH = '/home/mdlpd/Dropbox/Barrancos/results/Filled_DEM_initial_results/Exp_6.1'
FILEPATTERN = 'Year_*_STREAM_PROFILE_STATS.csv'
COLUMN = [0]	#Comma separated list of columns to loop through. Columns should match the names on OUTPUTFILE.
SKIPHEADER = 0
OUTPUTFILE = ["All_stream_profiles_distances.csv"]	#Comma separated list of output text file names. Should match the columns in COLUMN.
##############################

matches = []
for root, dirnames, filenames in os.walk(BASEPATH):
  for filename in fnmatch.filter(filenames, FILEPATTERN):
    matches.append(os.path.join(root, filename))
matches.sort()
for col,fname in zip(COLUMN, OUTPUTFILE):
  print col, fname
  n = matches[0]
  all_data = np.genfromtxt(matches.pop(0), dtype=float, delimiter=',', skip_header=SKIPHEADER, usecols=(col))
  print n, len(all_data)
  for match in matches:
    data = np.genfromtxt(match, dtype=float, delimiter=',', skip_header=SKIPHEADER, usecols=(col))
    print match, len(data)
    all_data = np.vstack((all_data, data))
  np.savetxt("%s%s%s" % (BASEPATH, os.sep, fname), all_data.T, delimiter=",")
