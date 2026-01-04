@echo off
setlocal
pushd %~dp0
echo Building PDFTools.exe...

pyinstaller --noconfirm --clean main.spec

if exist dist\main.exe (
    echo.
    echo Build successful! Output: dist\main.exe
) else (
    echo Build failed!
)

popd
endlocal
