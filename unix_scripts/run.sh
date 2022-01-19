#!/usr/bin/env bash
source $CONDA_PREFIX/etc/profile.d/conda.sh
conda activate MAPIT_env
python ../src/MAPIT.py
conda deactivate
