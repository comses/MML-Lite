#!usr/python
import sys, os, time
from subprocess import Popen, list2cmdline

##############################
## EDIT THE COMMAND YOU WANT TO BLAST OUT TO ALL AVAILABLE PROCS
repetitions = 40
commands = []
for n in range(repetitions):
    commands.append('r.agropast.adaptive-fire.py years=500 prfx=%s_pastoral a_p_ratio=0.80 costsurf=INIT_cost@catchments agcatch=catchment_agriculture_20pct@catchments grazecatch=catchment_grazing_80pct_intensive@catchments fodder_rules=/home/user/Dropbox/Scripts_Working_Dir/rules/fodder_rules.txt inlcov=INIT_Woodland@catchments infert=INIT_fertility@catchments fireprob=INIT_fire_prob@catchments lc_rules=/home/user/Dropbox/Scripts_Working_Dir/rules/luse_reclass_rules.txt cfact_rules=/home/user/Dropbox/Scripts_Working_Dir/rules/cfactor_recode_rules.txt elev=INIT_DEM@catchments initbdrk=INIT_BDRK@catchments' % str(n).zfill(2))

##############################


def cpu_count():
    '''Returns the number of CPUs in the system'''
    num = 1
    if sys.platform == 'win32':
        try:
            num = int(os.environ['NUMBER_OF_PROCESSORS'])
        except (ValueError, KeyError):
            pass
    elif sys.platform == 'darwin':
        try:
            num = int(os.popen('sysctl -n hw.ncpu').read())
        except ValueError:
            pass
    else:
        try:
            num = os.sysconf('SC_NPROCESSORS_ONLN')
        except (ValueError, OSError, AttributeError):
            pass

    return num


def exec_commands(cmds):
    ''' Execute commands in "parallel" as multiple processes across as
        many CPU's as are available'''
    if not cmds: return # empty list

    def done(p):
        return p.poll() is not None
    def success(p):
        return p.returncode == 0
    def fail():
        sys.exit(1)

    max_task = cpu_count()
    processes = []
    while True:
        while cmds and len(processes) < max_task:
            task = cmds.pop()
            print list2cmdline(task)
            processes.append(Popen(task))

        for p in processes:
            if done(p):
                if success(p):
                    processes.remove(p)
                else:
                    fail()

        if not processes and not cmds:
            break
        else:
            time.sleep(0.05)

if __name__ == "__main__":    
    exec_commands(commands) # execute all of the experiments using every available core until they are all done
    sys.exit(0)