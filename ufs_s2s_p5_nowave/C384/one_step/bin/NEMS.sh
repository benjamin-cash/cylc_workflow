#!/bin/bash

rm -f logf* ocn.log.* field_*nc array_*nc phyf*.tile*.nc dynf*.tile*.nc PET* log.out logfile.000000.out *.vtk cice.stdout time_stamp.out ice_diag.d  atmos_4xdaily*nc atmos_static*.nc 
qsub NEMS.job
