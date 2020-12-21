@echo off

title signksy

mode con cols=150 lines=10

start d:\exe\batch.bat
timeout /t 10

:_getTime
cls
echo [CHECK]
tasklist /v /fi "windowtitle eq MainWindow" | find "Running"
if %ERRORLEVEL% == 0 (
goto RUN
) ELSE (
goto NOTRUN
)

:RUN
echo [RUNNING]
timeout /t 2
goto _getTIme

:NOTRUN
echo [NOT RUNNING]
taskkill /f /fi "windowtitle eq MainWindow"
start d:\exe\batch.bat
echo [RESTARTED]
goto START_CHECK

:START_CHECK
tasklist /fi "windowtitle eq MainWindow" | find "python.exe"
if %ERRORLEVEL% == 0 (
goto _getTime
)
timeout /t 1 > NUL
goto START_CHECK