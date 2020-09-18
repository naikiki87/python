@echo off

mode con cols=40 lines=3

:ALIVE_CHK
echo CHECK
tasklist /v /fi "windowtitle eq MainWindow" | find "Running"
if %ERRORLEVEL% == 0 (
goto ALIVE
) ELSE (
goto DEAD
)

:ALIVE
cls
echo ALIVE
goto ALIVE_CHK

:DEAD
cls
echo NOT RESPONDING
taskkill /f /fi "windowtitle eq MainWindow"
goto ALIVE_CHK