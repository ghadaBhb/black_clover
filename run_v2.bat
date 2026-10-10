@echo off
title GDG x Black Clover v2 - Reality Managed Platform
echo ========================================================
echo     GOOGLE DEVELOPER GROUPS (GDG) OPEN DAY 2026
echo     BLACK CLOVER: 20 MANA FLOWERS HUNT [v2 REALITY]
echo ========================================================
echo.
echo Starting v2 Reality Desk on http://localhost:5001 ...
echo Public Scoreboard:  http://localhost:5001/
echo Stage Projector:    http://localhost:5001/projector
echo Admin Command Desk: http://localhost:5001/admin (PIN: 10GDG-open10DAY26)
echo.

IF EXIST "C:\Users\ghada\AppData\Local\Python\pythoncore-3.14-64\python.exe" (
    "C:\Users\ghada\AppData\Local\Python\pythoncore-3.14-64\python.exe" v2\app.py
) ELSE (
    python v2\app.py
)

pause
