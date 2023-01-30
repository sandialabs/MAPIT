#!/usr/bin/env bash
{
  source $HOME/miniconda/etc/profile.d/conda.sh
  conda activate MAPIT_env
  python ../GUI/MAPIT_main.py
} || { echo Something went wrong

}
