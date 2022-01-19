@ECHO OFF
echo Loading MAPIT, please wait
call %LocalAppData%\Continuum\anaconda3\Scripts\activate.bat
call conda activate MAPIT_env
call python ../src/MAPIT.py
