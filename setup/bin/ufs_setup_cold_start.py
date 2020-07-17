import os
import shutil
import datetime

# Get environment variables from cylc task
year = os.getenv('YEAR')
month = os.getenv('MONTH')
day = os.getenv('DAY')
hour = os.getenv('HOUR')
resol = os.getenv('CYLC_TASK_PARAM_resol')

# DT_ICE has to be set as a variable so that istep0 can be calculated properly
cice5dt = os.getenv('DT_ICE')
print("DT_ICE is ",cice5dt)

# Get specific date formats
ldate = os.getenv('LDATE') #yearmonthdayhour
edate = os.getenv('EDATE') #year-month-day_hour
print(year,month,day,hour,resol,ldate,edate)

# Get scratch directory
scratch = os.getenv('SCRATCH')

# Get run directory
rundir = os.getenv('RUNDIR')

# Get input data directory
datadir = os.getenv('DATADIR')

# Get executable name
modelexe = os.getenv('MODELEXE')

# Get location of fixed input data
fixdir = ''.join([datadir,'/',resol,'/','fixed'])

# Get location of configuration files
configdir = ''.join([datadir,'/',resol,'/','config/cold_start'])

# Get location of FV3, resolution dependent initial conditions
icdir = ''.join([datadir,'/',resol,'/',ldate])

# Get location of MOM6 initial conditions
momdir = ''.join([datadir,'/','MOM6','/',ldate])

# Get location of CICE5 initial conditions
cicedir = ''.join([datadir,'/','CICE5','/',ldate])

# Define input directory
inputdir = ''.join([rundir,'/','INPUT'])

# Check to see if path to fixed data is valid
print("Checking for fixed data directory:",fixdir)
if not os.path.isdir(fixdir):
    sys.exit("Invalid fixed data directory, exiting")

# Check to see if path to IC files is valid
print("Checking for initial condition data directory:",icdir)
if not os.path.isdir(icdir):
     sys.exit("Invalid initial condition data directory, exiting")

# Copy fixed files to rundir. This command automatically creates the directory tree
# in the process and will fail if the directory exists. Since this is meant to be a
# cold start this is acceptable
try:
    shutil.copytree(fixdir,rundir)
except:
    print("Warning! Directory already exists! NO files copied.")

# Copy land-atmosphere ICs to rundir/INPUT
gfs_list = [''.join([icdir,'/','gfs_data.tile',tilenum,'.nc']) for tilenum in ['1','2','3','4','5','6']]
sfc_list = [''.join([icdir,'/','sfc_data.tile',tilenum,'.nc']) for tilenum in ['1','2','3','4','5','6']]
cntrl = ''.join([icdir,'/','gfs_ctrl.nc'])
latm_list = gfs_list+sfc_list
latm_list.append(cntrl)
for fname in latm_list:
    print("Copying",fname,"to",inputdir)
    shutil.copy2(fname,inputdir)

# Copy MOM6 IC file to rundir/INPUT
momname = ''.join([momdir,'/','oras5_MOM6_IC_TS.',ldate,'.nc'])
print("Copying",momname,"to",inputdir)
shutil.copy(momname, inputdir)

# Copy CICE5 IC file to rundir/INPUT
cicename = ''.join([cicedir,'/','cice5_',ldate,'_oras5.nc'])
print("Copying",cicename,"to",rundir)
shutil.copy(cicename, ''.join([rundir,'/','cice5_model.res.nc']))

# Copy model executable to rundir
print("Copying executable")
shutil.copy(modelexe,rundir)

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
with open(fname_model,'w') as file:
    file.write(filedata)

# Make case-specific edits to INPUT/MOM_input
fname_mom=''.join([rundir,'/','INPUT','/','MOM_input'])
with open(fname_mom,'r') as file:
    filedata = file.read()
    filedata = filedata.replace('LDATE',ldate)
with open(fname_mom,'w') as file:
    file.write(filedata)

