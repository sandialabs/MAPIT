#!/usr/bin/env bash
{
  source $HOME/miniconda/etc/profile.d/conda.sh
  conda activate MAPIT_env
  python -c "from MAPIT.GUI.mainGUI import mainrun; mainrun()"
} || { echo Something went wrong

}
