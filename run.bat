@echo off
title GDG x Black Clover - Open Day Game Launcher
cls
echo ================================================================
echo           GOOGLE DEVELOPER GROUPS (GDG) OPEN DAY 2026
echo             BLACK CLOVER: 20 MANA FLOWERS SCAVENGER HUNT
echo ================================================================
echo.
echo Please choose which version to run:
echo.
echo [1] Launch v1 (Online/Mobile Self-Service)
echo     - Teams enter Rune Codes on their phones
echo     - Runs on http://localhost:5000
echo.
echo [2] Launch v2 (Recommended: Reality Managed by GDG Desk)
echo     - Teams find physical flowers and bring them to GDG Booth
echo     - Admin registers teams and clicks flowers to award points
echo     - Public Spectator / Auditorium Projector (read-only for crowd)
echo     - Runs on http://localhost:5001
echo.
set /p choice="Enter choice [1 or 2]: "

if "%choice%"=="1" (
    call run_v1.bat
) else (
    call run_v2.bat
)
