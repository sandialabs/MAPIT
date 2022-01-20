::----------------------------------------------
:: The purpose of this script is to
:: remove the MAPIT environment -- usually in
:: case an install was broken. Most of the code is
:: focused on just figuring out where Anaconda is.
:: This is done by looking at the environments
:: file, which SHOULD be in the same place for
:: conda installs.
::----------------------------------------------


::----------------------------------------------
:: Read in the list of paths (note that
:: we are going to assume the shortest is
:: the base path to the conda activation
:: script)
::----------------------------------------------

@echo off
set "file=C:\Users\%USERNAME%\.conda\environments.txt"
set /A i=0

for /F "usebackq delims=" %%a in ("%file%") do (
set /A i+=1
call set array[%%i%%]=%%a
call set n=%%i%%
)


::----------------------------------------------
:: Below is a macro for determining the
:: length of a string. Taken from this SO
:: https://stackoverflow.com/questions/12407800
::----------------------------------------------


setlocal disableDelayedExpansion

:: -------- Begin macro definitions ----------
set ^"LF=^
%= This creates a variable containing a single linefeed (0x0A) character =%
^"
:: Define %\n% to effectively issue a newline with line continuation
set ^"\n=^^^%LF%%LF%^%LF%%LF%^^"

:: @strLen  StrVar  [RtnVar]
::
::   Computes the length of string in variable StrVar
::   and stores the result in variable RtnVar.
::   If RtnVar is is not specified, then prints the length to stdout.
::
set @strLen=for %%. in (1 2) do if %%.==2 (%\n%
  for /f "tokens=1,2 delims=, " %%1 in ("!argv!") do ( endlocal%\n%
    set "s=A!%%~1!"%\n%
    set "len=0"%\n%
    for %%P in (4096 2048 1024 512 256 128 64 32 16 8 4 2 1) do (%\n%
      if "!s:~%%P,1!" neq "" (%\n%
        set /a "len+=%%P"%\n%
        set "s=!s:~%%P!"%\n%
      )%\n%
    )%\n%
    for %%V in (!len!) do endlocal^&if "%%~2" neq "" (set "%%~2=%%V") else echo %%V%\n%
  )%\n%
) else setlocal enableDelayedExpansion^&setlocal^&set argv=,

:: -------- End macro definitions ----------


::----------------------------------------------
:: This next block is going to actually
:: find the shortest string
::----------------------------------------------


call set /a minStrLen=9999


set /a minStrLen=9999
set cpath=none

SETLOCAL ENABLEDELAYEDEXPANSION
for /L %%i in (1,1,%n%) do (
%@strLen% array[%%i] out
IF !out! leq !minStrLen! (
set /a minStrLen=!out!
set cpath=!array[%%i]!)
)

::----------------------------------------------
:: Having now found the path, we remove the
:: default MAPIT environment
::----------------------------------------------

call !cpath!\Scripts\activate.bat
echo removing MAPIT environment...
call conda remove --name MAPIT_env --all -y >nul 2>&1
echo removal completed
PAUSE
