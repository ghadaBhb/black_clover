@echo off
title GDG x Black Clover v1 - Self-Service Platform
echo ========================================================
echo     GOOGLE DEVELOPER GROUPS (GDG) OPEN DAY 2026
echo     BLACK CLOVER: 20 MANA FLOWERS HUNT [v1 ONLINE]
echo ========================================================
echo.
echo Starting v1 Platform on http://localhost:5000 ...
echo Teams Claim / Grimoires / Leaderboard: http://localhost:5000
echo.

IF EXIST "C:\Users\ghada\AppData\Local\Python\pythoncore-3.14-64\python.exe" (
    "C:\Users\ghada\AppData\Local\Python\pythoncore-3.14-64\python.exe" app.py
) ELSE (
    python app.py
)

pause
