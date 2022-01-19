#!/usr/bin/env bash
source $CONDA_PREFIX/etc/profile.d/conda.sh
echo removing MAPIT environment...
conda remove --name MAPIT_env --all -y &> /dev/null
echo removal completed
