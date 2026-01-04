@echo off
echo Building FileOrganizer.exe...

pyinstaller --onefile --windowed --hidden-import=customtkinter --hidden-import=darkdetect --collect-all=customtkinter main.py

if exist dist\main.exe (
    echo.
    echo Build successful! Output: dist\main.exe
) else (
    echo Build failed!
)
