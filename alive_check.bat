@echo off

mode con cols=40 lines=3

:ALIVE_CHK
echo CHECK
timeout /t 1 > NUL
tasklist /v /fi "windowtitle eq MainWindow" | find "Not Responding"
if %ERRORLEVEL% == 0 (
goto DEAD
) ELSE (
goto ALIVE
)

:ALIVE
cls
echo ALIVE
goto ALIVE_CHK

:DEAD
taskkill /f /fi "windowtitle eq MainWindow"
taskkill /f /fi "imagename eq alive_check.exe"