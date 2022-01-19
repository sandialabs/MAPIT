#!/usr/bin/env bash
{
  echo Installing MAPIT environment, please wait... &&
  conda env create -f ../requirements.yml &> /dev/null && echo MAPIT environment install completed
} || { echo Something went wrong: Install failed

}
