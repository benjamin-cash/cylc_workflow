import os
import sys
import shutil

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
print(year,month,day,hour,resol,ldate,edate,nhours_fcst)

# Get scratch directory
scratch = os.getenv('SCRATCH')

# Get run directory
rundir = os.getenv('RUNDIR')

# Get input data directory
datadir = os.getenv('DATADIR')

# Get location of configuration files
configdir = ''.join([datadir,'/',resol,'/','config/restart'])

# Check to see if there is an existing run directory
if not os.path.isdir(rundir):
    sys.exit(''.join(["Invalid run directory ",rundir,". Previous run required, exiting."]))

# Copy restart files to INPUT

# Copy restart configuration files to rundir
print("Copying config files")
shutil.copy(''.join([configdir,'/','input.nml']),rundir)
shutil.copy(''.join([configdir,'/','model_configure']),rundir)
shutil.copy(''.join([configdir,'/','nems.configure']),rundir)
shutil.copy(''.join([configdir,'/','ice_in']),rundir)
shutil.copy(''.join([configdir,'/','suite_FV3_GFS_v15p2_coupled.xml']),runddir)

# Make case-specific edits to ice_in
fname_ice_in=''.join([rundir,'/','ice_in'])
with open(fname_ice_in,'r') as file:
    filedata = file.read()
    filedata = filedata.replace('START_YEAR',year)
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
with open(fname_nems,'r') as file:
    filedata = file.read()
    filedata = filedata.replace('LDATE',ldate)
with open(fname_mom,'w') as file:
    file.write(filedata)

