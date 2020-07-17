import os
import sys
import shutil
import datetime

# Get environment variables from cylc task
year = os.getenv('YEAR')
month = os.getenv('MONTH')
day = os.getenv('DAY')
hour = os.getenv('HOUR')
resol = os.getenv('CYLC_TASK_PARAM_resol')
nhours_fcst = os.getenv('NHOURS_FCST')

# Get specific date formats
ldate = os.getenv('LDATE') #yearmonthdayhour
edate = os.getenv('EDATE') #year-month-day_hour

# DT_ICE has to be set as a variable so that istep0 can be calculated properly
cice5dt = os.getenv('DT_ICE')
print("DT_ICE is ",cice5dt)

print(year,month,day,hour,resol,ldate,edate,nhours_fcst)
print(os.environ)

# Get scratch directory
scratch = os.getenv('SCRATCH')

# Get run directory
rundir = os.getenv('RUNDIR')

# Get input data directory
datadir = os.getenv('DATADIR')

# Get location of configuration files
configdir = ''.join([datadir,'/',resol,'/','config/warm_start'])

# Check to see if there is an existing run directory
if not os.path.isdir(rundir):
    sys.exit(''.join(["Invalid run directory ",rundir,". Cold start run required, exiting."]))

# Copy configuration files to rundir
print("Copying config files")
shutil.copy(''.join([configdir,'/','input.nml']),rundir)
shutil.copy(''.join([configdir,'/','model_configure']),rundir)
shutil.copy(''.join([configdir,'/','nems.configure']),rundir)
shutil.copy(''.join([configdir,'/','ice_in']),rundir)
shutil.copy(''.join([configdir,'/','suite_FV3_GFS_v15p2_coupled.xml']),rundir)

# Make case-specific edits to ice_in
# First, get the start date of the run
sdate = datetime.datetime.strptime(ldate,'%Y%m%d%H')
dt = sdate.timetuple().tm_yday-1 # We want 01/01 to be day 0
istep0 = dt*86400/int(cice5dt)

fname_ice_in=''.join([rundir,'/','ice_in'])
with open(fname_ice_in,'r') as file:
    filedata = file.read()
    filedata = filedata.replace('START_YEAR',year)
    filedata = filedata.replace('DT_ICE',cice5dt)
    filedata = filedata.replace('ISTEP0',str(istep0))
with open(fname_ice_in,'w') as file:
    file.write(filedata)

# Make case-specific edits to nems.configure
fname_nems=''.join([rundir,'/','nems.configure'])
with open(fname_nems,'r') as file:
    filedata = file.read()
    filedata = filedata.replace('LDATE',ldate)
with open(fname_nems,'w') as file:
    file.write(filedata)

# Make case-specific edits to model_configure
fname_model=''.join([rundir,'/','model_configure'])
with open(fname_model,'r') as file:
    filedata = file.read()
    filedata = filedata.replace('START_YEAR',year)
    filedata = filedata.replace('START_MONTH',month)
    filedata = filedata.replace('START_DAY',day)
    filedata = filedata.replace('NHOURS_FCST',nhours_fcst)
with open(fname_model,'w') as file:
    file.write(filedata)

# Make case-specific edits to INPUT/MOM_input
fname_mom=''.join([rundir,'/','INPUT','/','MOM_input'])
with open(fname_mom,'r') as file:
    filedata = file.read()
    filedata = filedata.replace('LDATE',ldate)
with open(fname_mom,'w') as file:
    file.write(filedata)

