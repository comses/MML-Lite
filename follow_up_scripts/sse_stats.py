import fnmatch
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

###############################
#  EDIT VALS BELOW THIS LINE  #
###############################

BASEPATH = '/home/mdlpd/GIS_DataBase/New_penag/records'
FILEPATTERN = '30pf10sim_*_yields_stats.txt'
COLUMN = 15
SKIPHEADER = 35
OUTPUTFILE = "ALL_ANIM_DATA.csv"

###############################
# DO NOT EDIT BELOW THIS LINE #
###############################

#Recursively search through a base directory and all subdirectories for files that match the given search pattern, and put their names in a list.
matches = []
for root, dirnames, filenames in os.walk(BASEPATH):
  for filename in fnmatch.filter(filenames, FILEPATTERN):
      matches.append(os.path.join(root, filename))
#Grab the first of these files, and take the data from the specified column to set up the numpy array to 
all_data = np.genfromtxt(matches.pop(0), dtype=float, delimiter=',', skip_header=SKIPHEADER, usecols=(COLUMN))

for match in matches:
  data = np.genfromtxt(match, dtype=float, delimiter=',', skip_header=SKIPHEADER, usecols=(COLUMN))
  all_data = np.vstack((all_data, data))

np.savetxt("%s%s%s" % (BASEPATH, os.sep, OUTPUTFILE), all_data.T, delimiter=",")

#compute standard error of an array, first randomly shuffle the rows (actually columns), and do this 100 times so that the data are bootstrapped, then loop through the shuffled dataset and calculate the sum SE for every n in the sequence

#first get the standard errors for the unshuffled data, and make that an array
loopctrl = range(len(all_data))
el = []
for x in loopctrl:
  #z = stats.sem(all_data[0:x+1], axis=None, ddof=0)
  z = stats.sem(all_data[0:x+1])
  el.append(np.sum(z))
  #z = np.mean(all_data[0:x+1])
  #el.append(np.mean(z))

errorlist = [el]

#now do a nested loop of this, but reshuffling each time 
for n in loopctrl:
  a2 = np.random.permutation(all_data)
  el2 = []
  for x in loopctrl:
    #z = stats.sem(a2[0:x+1], axis=None, ddof=0)
    z = stats.sem(a2[0:x+1])
    el2.append(np.sum(z))
    #z = np.mean(a2[0:x+1])
    #el2.append(np.mean(z))
  errorlist.append(el2)

errorarray = np.array(errorlist)

np.savetxt("%s%s%s_errors.csv" % (BASEPATH, os.sep, OUTPUTFILE), errorarray.T, delimiter=",")
