#!/bin/bash

# Activate appropriate conda environment
source ~/.bashrc
conda deactivate
conda activate xesmf_env

# Execute regrid
python ./phyf_regrid.py
