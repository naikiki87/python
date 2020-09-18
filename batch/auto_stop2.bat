@echo off

taskkill /fi "windowtitle eq MainWindow"
taskkill /fi "imagename eq rt_check.exe"
taskkill /fi "imagename eq alive_check.exe"