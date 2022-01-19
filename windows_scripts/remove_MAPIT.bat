@ECHO OFF
call %LocalAppData%\Continuum\anaconda3\Scripts\activate.bat
echo removing MAPIT environment...
call conda remove --name MAPIT_env --all -y >nul 2>&1
echo removal completed
PAUSE
