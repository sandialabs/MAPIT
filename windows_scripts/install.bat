@ECHO OFF
echo Creating environment
call %LocalAppData%\Continuum\anaconda3\Scripts\activate.bat
echo Downloading and installing requirements
call conda env create -f %cd%/requirements.yml >nul 2>&1
if  errorlevel 1 goto ERROR
echo Install complete
PAUSE
goto EOF

:ERROR
echo Install failed
PAUSE

:EOF
