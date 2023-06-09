::----------------------------------------------
:: The purpose of this script is to
:: remove the MAPIT environment -- usually in
:: case an install was broken. Most of the code is
:: focused on just figuring out where Anaconda is.
:: This is done by looking at the environments
:: file, which SHOULD be in the same place for
:: conda installs.
::----------------------------------------------

echo off
call %userprofile%\Miniconda3\condabin\activate.bat
echo removing MAPIT environment...
call conda remove --name MAPIT_env --all -y >nul 2>&1
echo removing Miniconda3...
rmdir /s /q %userprofile%\Miniconda3
call move %userprofile%\Desktop\MAPIT.lnk .
del .\Miniconda3-latest-Windows-x86_64.exe
echo removal complete
PAUSE
