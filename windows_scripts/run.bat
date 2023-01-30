::----------------------------------------------
:: The purpose of this script is to
:: activate the MAPIT environment and run
:: MAPIT. Most of the code is focused on
:: just figuring out where Anaconda is.
:: This is done by looking at the environments
:: file, which SHOULD be in the same place for
:: conda installs.
::----------------------------------------------

@echo off
echo Loading MAPIT, please wait
call %userprofile%\Miniconda3\condabin\activate.bat
call conda activate MAPIT_env
call python ../GUI/MAPIT_main.py
