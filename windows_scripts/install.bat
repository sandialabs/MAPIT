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
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe --ssl-no-revoke
start /wait Miniconda3-latest-Windows-x86_64.exe /InstallationType=JustMe /RegisterPython=0 /S /D=%userprofile%\Miniconda3

echo Creating environment
call %userprofile%\Miniconda3\condabin\activate.bat
call conda env create -f ../requirements.yml >nul 2>&1
if  errorlevel 1 goto ERROR
echo Install complete
echo Creating MAPIT module 
call cd ../../
call robocopy MAPIT-master %userprofile%\Miniconda3\envs\MAPIT_env\Lib\site-packages\MAPIT /E
call rmdir /s /q %userprofile%\Miniconda3\envs\MAPIT_env\Lib\site-packages\MAPIT\windows_scripts
call rmdir /s /q %userprofile%\Miniconda3\envs\MAPIT_env\Lib\site-packages\MAPIT\unix_scripts
PAUSE
goto EOF

:ERROR
echo Install failed
PAUSE

:EOF
