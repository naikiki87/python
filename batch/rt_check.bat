@echo off

mode con cols=30 lines=2

:_getTime
cls
set HOUR=%time:~0,2%
set MINUTE=%time:~3,2%
set SECOND=%time:~6,2%

tasklist /fi "windowtitle eq MainWindow" | find "python.exe"
if %ERRORLEVEL% == 0 (
goto RUN
) ELSE (
goto NOTRUN
)

:RUN
echo RUNNING
timeout /t 1 > NUL
goto _getTIme

:NOTRUN
echo NOT RUNNING
start d:\exe\batch.bat
echo RESTARTED
goto START_CHECK

:START_CHECK
tasklist /fi "windowtitle eq MainWindow" | find "python.exe"
if %ERRORLEVEL% == 0 (
goto _getTime
)
timeout /t 1 > NUL
goto START_CHECK


