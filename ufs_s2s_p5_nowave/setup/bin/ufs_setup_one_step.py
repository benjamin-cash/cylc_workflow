import os
import sys
import shutil
import datetime
from glob import glob

# Get environment variables from cylc task
year = os.getenv('YEAR')
month = os.getenv('MONTH')
day = os.getenv('DAY')
hour = os.getenv('HOUR')
resol = os.getenv('CYLC_TASK_PARAM_resol')
nhours_fcst = os.getenv('NHOURS_FCST')

# DT_ICE has to be set as a variable so that istep0 can be calculated properly
cice5dt = os.getenv('DT_ICE')
print("DT_ICE is ",cice5dt)

# Get specific date formats
ldate = os.getenv('LDATE') #yearmonthdayhour
ymddate = os.getenv('YMDDATE') #yearmonthday
edate = os.getenv('EDATE') #year-month-day_hour
print(year,month,day,hour,resol,ldate,ymddate,edate)

# Get scratch directory
scratch = os.getenv('SCRATCH')

# Get run directory
rundir = os.getenv('RUNDIR')

# Get input data directory
datadir = os.getenv('DATADIR')

# Get executable name and module setup
modelexe = os.getenv('MODELEXE')
modulesetup =  os.getenv('MODULESETUP')

# Get location of fixed input data
atmfixdir = ''.join([datadir,'/',resol,'/','fixed'])
ocnfixdir = ''.join([datadir,'/MOM6/fixed'])
icefixdir = ''.join([datadir,'/CICE6/fixed'])

# Get location of configuration files
configdir = ''.join([datadir,'/',resol,'/','config/one_step'])

# Get location of FV3, resolution dependent initial conditions
atmicdir = ''.join([datadir,'/',resol,'/',ldate])

# Get location of MOM6 initial conditions
ocnicdir = ''.join([datadir,'/','MOM6','/',ldate])

# Get location of CICE6 initial conditions
iceicdir = ''.join([datadir,'/','CICE6','/',ldate])

# Define input directory
inputdir = ''.join([rundir,'/','INPUT'])

# Check to see if paths fixed data are valid
print("Checking for fixed data directory:",atmfixdir)
if not os.path.isdir(atmfixdir):
    print(atmfixdir)
    sys.exit("Invalid atmosphere fixed data directory, exiting")
if not os.path.isdir(ocnfixdir):
    print(ocnfixdir)
    sys.exit("Invalid ocean fixed data directory, exiting")
if not os.path.isdir(icefixdir):
    print(icefixdir)
    sys.exit("Invalid ice fixed data directory, exiting")

# Check to see if paths to initial conditions are valid
print("Checking for fixed data directory:",atmicdir)
if not os.path.isdir(atmicdir):
    sys.exit("Invalid atmosphere initial condition directory, exiting")
if not os.path.isdir(ocnicdir):
    sys.exit("Invalid ocean initial condition data directory, exiting")
if not os.path.isdir(iceicdir):
    sys.exit("Invalid ice initial condition data directory, exiting")

#Create the run directory
os.makedirs(rundir)
os.makedirs(''.join([rundir,'/INPUT']))
os.makedirs(''.join([rundir,'/history']))
os.makedirs(''.join([rundir,'/RESTART']))
os.makedirs(''.join([rundir,'/MOM6_OUTPUT']))
os.makedirs(''.join([rundir,'/MOM6_RESTART']))

# Copy atmospheric fixed files to rundir.
atmfixlist=glob(''.join([atmfixdir,'/*']))
for afname in atmfixlist:
    if not os.path.isdir(afname):
      print("Copying",afname,"to",rundir)
      shutil.copy2(afname,rundir)

# Copy atmospheric fixed INPUT files to rundir/INPUT.
atmfixinlist=glob(''.join([atmfixdir,'/INPUT/*']))
for ainfname in atmfixinlist:
    print("Copying",ainfname,"to",inputdir)
    shutil.copy2(ainfname,inputdir)

# Copy ocean fixed files to rundir/INPUT dir.
ocnfixlist=glob(''.join([ocnfixdir,'/*']))
for ofname in ocnfixlist:
    print("Copying",ofname,"to",inputdir)
    shutil.copy2(ofname,inputdir)

# Copy ice fixed files to rundir.
icefixlist=glob(''.join([icefixdir,'/*']))
for ifname in icefixlist:
    print("Copying",ifname,"to",rundir)
    shutil.copy2(ifname,rundir)

# Copy land-atmosphere ICs to rundir/INPUT
gfs_list = [''.join([atmicdir,'/','gfs_data.tile',tilenum,'.nc']) for tilenum in ['1','2','3','4','5','6']]
sfc_list = [''.join([atmicdir,'/','sfc_data.tile',tilenum,'.nc']) for tilenum in ['1','2','3','4','5','6']]
cntrl = ''.join([atmicdir,'/','gfs_ctrl.nc'])
latm_list = gfs_list+sfc_list
latm_list.append(cntrl)
for fname in latm_list:
    print("Copying",fname,"to",inputdir)
    shutil.copy2(fname,inputdir)

# Copy MOM6 IC file to rundir/INPUT
momlist = [''.join([ocnicdir,'/',fname]) for fname in ['MOM.res.nc', 'MOM.res_1.nc','MOM.res_2.nc','MOM.res_3.nc','MOM.res_4.nc']]
for momname in momlist:
   print("Copying",momname,"to",inputdir)
   shutil.copy(momname, inputdir)

# Copy CICE5 IC file to rundir
cicename = ''.join([iceicdir,'/','cice5_model_0.25.res_',ldate,'.nc'])
print("Copying",cicename,"to",rundir)
shutil.copy(cicename, ''.join([rundir,'/','cice5_model.res_',ldate,'.nc']))

# Copy model executable and module environment to rundir
print("Copying executable")
shutil.copy(modelexe,rundir)
shutil.copy(''.join([modulesetup,'/module-setup.sh']),rundir)
shutil.copy(''.join([modulesetup,'/modules.fcst']),rundir)

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
istep0 = int(dt*86400/int(cice5dt))

fname_ice_in=''.join([rundir,'/','ice_in'])
with open(fname_ice_in,'r') as file:
    filedata = file.read()
    filedata = filedata.replace('START_YEAR',year)
    filedata = filedata.replace('DT_ICE',cice5dt)
    filedata = filedata.replace('ISTEP0',str(istep0))
    filedata = filedata.replace('LDATE',ldate)
with open(fname_ice_in,'w') as file:
    file.write(filedata)

# Make case-specific edits to nems.configure
fname_nems=''.join([rundir,'/','nems.configure'])
with open(fname_nems,'r') as file:
    filedata = file.read()
    filedata = filedata.replace('LDATE',ldate)
    filedata = filedata.replace('NHOURS_FCST',nhours_fcst)
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

# Make case-specific edits to model_configure
fname_input=''.join([rundir,'/','input.nml'])
with open(fname_input,'r') as file:
    filedata = file.read()
    filedata = filedata.replace('NHOURS_FCST',nhours_fcst)
with open(fname_input,'w') as file:
    file.write(filedata)
