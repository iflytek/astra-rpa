@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1
title Pack Tool
echo ========================================
echo         Pack Tool Script
echo ========================================

REM Handle command line arguments
set "CUSTOM_7ZIP_PATH="
set "PYTHON_SOURCE_DIR="
if not "%~1"=="" (
    set "CUSTOM_7ZIP_PATH=%~1"
    echo [INFO] Using custom 7-Zip path: %CUSTOM_7ZIP_PATH%
) else (
    echo [INFO] Using default 7-Zip paths
)
if not "%~2"=="" (
    set "PYTHON_SOURCE_DIR=%~2"
    echo [INFO] Using custom Python source directory: %PYTHON_SOURCE_DIR%
) else (
    REM Try to find default Python directories
    if exist "Python313" (
        set "PYTHON_SOURCE_DIR=Python313"
        echo [INFO] Found default Python directory: Python313
    ) else if exist "C:\Python313" (
        set "PYTHON_SOURCE_DIR=C:\Python313"
        echo [INFO] Found system Python directory: C:\Python313
    ) else (
        echo [WARN] No default Python directory found, please specify one
    )
)

REM Check/create pack_workspace folder
if not exist "pack_workspace" (
    echo [INFO] pack_workspace folder not found, creating...
    mkdir pack_workspace
    echo [DONE] pack_workspace folder created
) else (
    echo [INFO] pack_workspace folder exists
)

echo.
echo [INFO] Cleaning previous build artifacts...

REM Clean wheels directory
if exist "pack_workspace\wheels" (
    echo [INFO] Cleaning pack_workspace\wheels directory...
    rmdir /s /q "pack_workspace\wheels" >nul 2>&1
    if exist "pack_workspace\wheels" (
        echo [WARN] Cannot completely clean wheels directory, some files may be in use
    ) else (
        echo [DONE] wheels directory cleaned successfully
    )
)

REM Clean python_base directory
if exist "pack_workspace\python_base" (
    echo [INFO] Cleaning pack_workspace\python_base directory...
    rmdir /s /q "pack_workspace\python_base" >nul 2>&1
    if exist "pack_workspace\python_base" (
        echo [WARN] Cannot completely clean python_base directory, some files may be in use
    ) else (
        echo [DONE] python_base directory cleaned successfully
    )
)

REM Clean python_core directory
if exist "pack_workspace\python_core" (
    echo [INFO] Cleaning pack_workspace\python_core directory...
    rmdir /s /q "pack_workspace\python_core" >nul 2>&1
    if exist "pack_workspace\python_core" (
        echo [WARN] Cannot completely clean python_core directory, some files may be in use
    ) else (
        echo [DONE] python_core directory cleaned successfully
    )
)

echo [DONE] Previous build artifacts cleaning completed

REM Check if Python source directory exists
if "%PYTHON_SOURCE_DIR%"=="" (
    echo [ERROR] No Python source directory specified!
    echo [INFO] Please provide a valid Python installation directory path.
    echo [INFO] Usage examples:
    echo [INFO]   pack.bat "" "C:\Python313"
    echo [INFO]   pack.bat "" "D:\Python" 
    echo [INFO]   pack.bat "" "Python313"
    pause
    exit /b 1
)

if not exist "%PYTHON_SOURCE_DIR%" (
    echo [ERROR] Python source directory "%PYTHON_SOURCE_DIR%" not found!
    echo [INFO] Please provide a valid Python installation directory path.
    echo [INFO] Usage examples:
    echo [INFO]   pack.bat "" "C:\Python313"
    echo [INFO]   pack.bat "" "D:\Python" 
    echo [INFO]   pack.bat "" "Python313"
    pause
    exit /b 1
)

echo.
echo [INFO] Creating Python environments from source directory...

REM Copy first copy as python_base
if exist "pack_workspace\python_base" (
    echo [INFO] python_base folder exists, skipping creation
) else (
    echo [INFO] Copying "%PYTHON_SOURCE_DIR%" to python_base...
    xcopy "%PYTHON_SOURCE_DIR%" "pack_workspace\python_base" /e /i /h /y >nul
    if !errorlevel! equ 0 (
        echo [DONE] python_base folder created successfully
    ) else (
        echo [ERROR] Failed to create python_base folder, code: !errorlevel!
        echo [INFO] Please check if the source directory exists and is accessible
        pause
        exit /b 1
    )
)

REM Copy second copy as python_core
if exist "pack_workspace\python_core" (
    echo [INFO] python_core folder exists, skipping creation
) else (
    echo [INFO] Copying "%PYTHON_SOURCE_DIR%" to python_core...
    xcopy "%PYTHON_SOURCE_DIR%" "pack_workspace\python_core" /e /i /h /y >nul
    if !errorlevel! equ 0 (
        echo [DONE] python_core folder created successfully
    ) else (
        echo [ERROR] Failed to create python_core folder, code: !errorlevel!
        echo [INFO] Please check if the source directory exists and is accessible
        pause
        exit /b 1
    )
)

echo.
echo [INFO] Building shared packages and installing to python_core...

REM Check engine/shared directory
if not exist "engine\shared" (
    echo [ERROR] engine\shared directory not found!
    pause
    exit /b 1
)

REM Define shared packages (first batch - independent packages)
set "SHARED_PACKAGES=rpaframe rpawebsocket rpawebsocket-client"

REM Define dependent packages (second batch - packages that depend on wheels from first batch)
set "DEPENDENT_PACKAGES=table_helper locator"

REM Define execkit packages (third batch - packages in engine\execkit that depend on wheels)
set "EXECKIT_PACKAGES=atomic tools recording param_utils executor"

REM Define components packages (fourth batch - packages in engine\components that depend on wheels)
set "COMPONENTS_PACKAGES=rpagui rpasystem rpasoftware rpadialog rpaencrypt rpawindow rpabrowser rpawinele rpascript rpareport rpaopenapi rpadocx rpaemail rpaexcel rpaenterprise rpanetwork rpahelper rpaverifycode rpademo rpaai rpacv rpadatabase rpadataprocess rpapdf"

REM Get python_core Python executable path
set "PYTHON_CORE_EXE=%~dp0pack_workspace\python_core\python.exe"

REM Get python_base Python executable path
set "PYTHON_BASE_EXE=%~dp0pack_workspace\python_base\python.exe"
echo [DEBUG] Checking Python path: %PYTHON_CORE_EXE%
if not exist "%PYTHON_CORE_EXE%" (
    echo [ERROR] Python executable not found: %PYTHON_CORE_EXE%!
    echo [INFO] Trying other possible paths...
    
    REM Check other possible paths
    if exist "%~dp0pack_workspace\python_core\Scripts\python.exe" (
        set "PYTHON_CORE_EXE=%~dp0pack_workspace\python_core\Scripts\python.exe"
        echo [INFO] Found Python in Scripts directory: %PYTHON_CORE_EXE%
    ) else if exist "%~dp0pack_workspace\python_core\python3.exe" (
        set "PYTHON_CORE_EXE=%~dp0pack_workspace\python_core\python3.exe"
        echo [INFO] Found python3.exe: %PYTHON_CORE_EXE%
    ) else (
        echo [ERROR] Cannot find Python executable!
        echo [INFO] Please check pack_workspace\python_core directory structure
        pause
        exit /b 1
    )
)

echo [INFO] Using Python path: %PYTHON_CORE_EXE%

echo [DEBUG] Checking Python base path: %PYTHON_BASE_EXE%
if not exist "%PYTHON_BASE_EXE%" (
    echo [ERROR] Python base executable not found: %PYTHON_BASE_EXE%!
    echo [INFO] Trying other possible paths...
    
    REM Check other possible paths for python_base
    if exist "%~dp0pack_workspace\python_base\Scripts\python.exe" (
        set "PYTHON_BASE_EXE=%~dp0pack_workspace\python_base\Scripts\python.exe"
        echo [INFO] Found Python in Scripts directory: %PYTHON_BASE_EXE%
    ) else if exist "%~dp0pack_workspace\python_base\python3.exe" (
        set "PYTHON_BASE_EXE=%~dp0pack_workspace\python_base\python3.exe"
        echo [INFO] Found python3.exe: %PYTHON_BASE_EXE%
    ) else (
        echo [ERROR] Cannot find Python base executable!
        echo [INFO] Please check pack_workspace\python_base directory structure
        pause
        exit /b 1
    )
)

echo [INFO] Using Python base path: %PYTHON_BASE_EXE%

REM Process each shared package
for %%p in (%SHARED_PACKAGES%) do call :process_package %%p

echo.
echo [INFO] Processing dependent packages that require wheels dependencies...

REM Process each dependent package
for %%p in (%DEPENDENT_PACKAGES%) do call :process_dependent_package %%p

echo.
echo [INFO] Processing execkit packages that require wheels dependencies...

REM Process each execkit package
for %%p in (%EXECKIT_PACKAGES%) do call :process_execkit_package %%p

echo.
echo [INFO] Processing components packages that require wheels dependencies...

REM Process each components package
for %%p in (%COMPONENTS_PACKAGES%) do call :process_components_package %%p

goto :build_complete

:process_package
set "PACKAGE_NAME=%1"
echo.
echo [INFO] Processing package: %PACKAGE_NAME%

REM Check if package directory exists
if not exist "engine\shared\%PACKAGE_NAME%" (
    echo [WARN] Package directory engine\shared\%PACKAGE_NAME% not found, skipping...
    goto :eof
)

REM Enter package directory
pushd "engine\shared\%PACKAGE_NAME%"

REM Clean old build artifacts
if exist "dist" (
    echo [INFO] Cleaning old build artifacts for %PACKAGE_NAME%...
    rmdir /s /q "dist" >nul 2>&1
    if exist "dist" (
        echo [WARN] Cannot completely clean dist directory, continuing...
    ) else (
        echo [DONE] dist directory cleaned successfully
    )
)

REM Build package using uv build
echo [INFO] Building package %PACKAGE_NAME%...
uv build
if !errorlevel! neq 0 (
    echo [ERROR] Building package %PACKAGE_NAME% failed, code: !errorlevel!
    popd
    pause
    exit /b 1
)

REM Check dist directory and whl files
if not exist "dist" (
    echo [ERROR] dist directory not found after build
    popd
    pause
    exit /b 1
)

REM Create wheels directory in pack_workspace if it doesn't exist
if not exist "%~dp0pack_workspace\wheels" (
    echo [INFO] Creating pack_workspace\wheels directory...
    mkdir "%~dp0pack_workspace\wheels"
    echo [DONE] wheels directory created
)

REM Find and install .whl files
for %%w in (dist\*.whl) do (
    echo [INFO] Installing %%w to python_core...
    echo [DEBUG] Using Python: "%PYTHON_CORE_EXE%"
    echo [DEBUG] Installing package: "%%~fw"
    "%PYTHON_CORE_EXE%" -m pip install "%%~fw" --force-reinstall
    if !errorlevel! neq 0 (
        echo [ERROR] Installing %%w failed, code: !errorlevel!
        echo [DEBUG] Current directory: %CD%
        echo [DEBUG] Full file path: %%~fw
        popd
        pause
        exit /b 1
    )
    echo [DONE] %%w installed to python_core successfully
    
    echo [INFO] Installing %%w to python_base...
    echo [DEBUG] Using Python: "%PYTHON_BASE_EXE%"
    echo [DEBUG] Installing package: "%%~fw"
    "%PYTHON_BASE_EXE%" -m pip install "%%~fw"
    if !errorlevel! neq 0 (
        echo [ERROR] Installing %%w to python_base failed, code: !errorlevel!
        echo [DEBUG] Current directory: %CD%
        echo [DEBUG] Full file path: %%~fw
        popd
        pause
        exit /b 1
    )
    echo [DONE] %%w installed to python_base successfully
    
    REM Copy wheel file to pack_workspace\wheels
    echo [INFO] Copying %%w to pack_workspace\wheels...
    copy "%%~fw" "%~dp0pack_workspace\wheels\" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [DONE] %%w copied to wheels directory
    ) else (
        echo [WARN] Failed to copy %%w to wheels directory
    )
)

REM Return to original directory
popd
goto :eof

:process_dependent_package
set "PACKAGE_NAME=%1"
echo.
echo [INFO] Processing dependent package: %PACKAGE_NAME%

REM Check if package directory exists
if not exist "engine\shared\%PACKAGE_NAME%" (
    echo [WARN] Package directory engine\shared\%PACKAGE_NAME% not found, skipping...
    goto :eof
)

REM Enter package directory
pushd "engine\shared\%PACKAGE_NAME%"

REM Clean old build artifacts
if exist "dist" (
    echo [INFO] Cleaning old build artifacts for %PACKAGE_NAME%...
    rmdir /s /q "dist" >nul 2>&1
    if exist "dist" (
        echo [WARN] Cannot completely clean dist directory, continuing...
    ) else (
        echo [DONE] dist directory cleaned successfully
    )
)

REM Update pyproject.toml to use local wheel dependencies
echo [INFO] Updating pyproject.toml to use local wheel dependencies...

REM Backup original pyproject.toml
if exist "pyproject.toml" (
    copy "pyproject.toml" "pyproject.toml.backup" >nul 2>&1
    echo [INFO] Backed up original pyproject.toml
    
    REM Create PowerShell script to update dependencies
    echo [INFO] Creating PowerShell script to update dependencies...
    (
        echo # Read file with proper encoding detection
        echo $bytes = [System.IO.File]::ReadAllBytes('pyproject.toml'^)
        echo $encoding = [System.Text.Encoding]::UTF8
        echo try {
        echo     $content = $encoding.GetString($bytes^)
        echo } catch {
        echo     Write-Host "[WARN] UTF-8 decode failed, trying Windows-1252..."
        echo     $encoding = [System.Text.Encoding]::GetEncoding('Windows-1252'^)
        echo     $content = $encoding.GetString($bytes^)
        echo }
        echo.
        echo $wheelsDir = '%~dp0pack_workspace\wheels'
        echo $wheelFiles = Get-ChildItem "$wheelsDir\*.whl"
        echo.
        echo foreach ($wheelFile in $wheelFiles^) {
        echo     $wheelName = $wheelFile.BaseName -replace '-.*$', ''
        echo     $wheelPath = $wheelFile.FullName -replace '\\', '/'
        echo     $wheelUrl = "file:///$wheelPath"
        echo     Write-Host "[INFO] Processing wheel: $wheelName -> $wheelUrl"
        echo     # Match quoted package name with optional version constraints
        echo     $pattern = "`"$wheelName[^`"]*`""
        echo     $replacement = "`"$wheelName @ $wheelUrl`""
        echo     $content = $content -replace $pattern, $replacement
        echo }
        echo.
        echo # Write back as UTF-8 without BOM
        echo $utf8 = New-Object System.Text.UTF8Encoding($false^)
        echo [System.IO.File]::WriteAllText('pyproject.toml', $content, $utf8^)
    ) > update_deps.ps1
    
    REM Execute PowerShell script
    powershell -ExecutionPolicy Bypass -File "update_deps.ps1"
    set "ps_result=!errorlevel!"
    
    REM Clean up PowerShell script
    del "update_deps.ps1" >nul 2>&1
    
    if !ps_result! equ 0 (
        echo [DONE] Updated pyproject.toml with local wheel dependencies
    ) else (
        echo [ERROR] Failed to update pyproject.toml
        copy "pyproject.toml.backup" "pyproject.toml" >nul 2>&1
        popd
        pause
        exit /b 1
    )
) else (
    echo [ERROR] pyproject.toml not found in %PACKAGE_NAME% directory!
    popd
    pause
    exit /b 1
)

REM Build package using uv build
echo [INFO] Building dependent package %PACKAGE_NAME%...
uv build
if !errorlevel! neq 0 (
    echo [ERROR] Building package %PACKAGE_NAME% failed, code: !errorlevel!
    popd
    pause
    exit /b 1
)

REM Check dist directory and whl files
if not exist "dist" (
    echo [ERROR] dist directory not found after build
    popd
    pause
    exit /b 1
)

REM Create wheels directory in pack_workspace if it doesn't exist
if not exist "%~dp0pack_workspace\wheels" (
    echo [INFO] Creating pack_workspace\wheels directory...
    mkdir "%~dp0pack_workspace\wheels"
    echo [DONE] wheels directory created
)

REM Find and install .whl files
for %%w in (dist\*.whl) do (
    echo [INFO] Installing %%w to python_core...
    echo [DEBUG] Using Python: "%PYTHON_CORE_EXE%"
    echo [DEBUG] Installing package: "%%~fw"
    "%PYTHON_CORE_EXE%" -m pip install "%%~fw"
    if !errorlevel! neq 0 (
        echo [ERROR] Installing %%w failed, code: !errorlevel!
        echo [DEBUG] Current directory: %CD%
        echo [DEBUG] Full file path: %%~fw
        popd
        pause
        exit /b 1
    )
    echo [DONE] %%w installed to python_core successfully
    
    echo [INFO] Installing %%w to python_base...
    echo [DEBUG] Using Python: "%PYTHON_BASE_EXE%"
    echo [DEBUG] Installing package: "%%~fw"
    "%PYTHON_BASE_EXE%" -m pip install "%%~fw"
    if !errorlevel! neq 0 (
        echo [ERROR] Installing %%w to python_base failed, code: !errorlevel!
        echo [DEBUG] Current directory: %CD%
        echo [DEBUG] Full file path: %%~fw
        popd
        pause
        exit /b 1
    )
    echo [DONE] %%w installed to python_base successfully
    
    REM Copy wheel file to pack_workspace\wheels
    echo [INFO] Copying %%w to pack_workspace\wheels...
    copy "%%~fw" "%~dp0pack_workspace\wheels\" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [DONE] %%w copied to wheels directory
    ) else (
        echo [WARN] Failed to copy %%w to wheels directory
    )
)

REM Restore original pyproject.toml
if exist "pyproject.toml.backup" (
    echo [INFO] Restoring original pyproject.toml...
    copy "pyproject.toml.backup" "pyproject.toml" >nul 2>&1
    del "pyproject.toml.backup" >nul 2>&1
    echo [DONE] Original pyproject.toml restored
)

REM Return to original directory
popd
goto :eof

:process_execkit_package
set "PACKAGE_NAME=%1"
echo.
echo [INFO] Processing execkit package: %PACKAGE_NAME%

REM Check if package directory exists
if not exist "engine\execkit\%PACKAGE_NAME%" (
    echo [WARN] Package directory engine\execkit\%PACKAGE_NAME% not found, skipping...
    goto :eof
)

REM Enter package directory
pushd "engine\execkit\%PACKAGE_NAME%"

REM Clean old build artifacts
if exist "dist" (
    echo [INFO] Cleaning old build artifacts for %PACKAGE_NAME%...
    rmdir /s /q "dist" >nul 2>&1
    if exist "dist" (
        echo [WARN] Cannot completely clean dist directory, continuing...
    ) else (
        echo [DONE] dist directory cleaned successfully
    )
)

REM Update pyproject.toml to use local wheel dependencies
echo [INFO] Updating pyproject.toml to use local wheel dependencies...

REM Backup original pyproject.toml
if exist "pyproject.toml" (
    copy "pyproject.toml" "pyproject.toml.backup" >nul 2>&1
    echo [INFO] Backed up original pyproject.toml
    
    REM Create PowerShell script to update dependencies
    echo [INFO] Creating PowerShell script to update dependencies...
    (
        echo # Read file with proper encoding detection
        echo $bytes = [System.IO.File]::ReadAllBytes('pyproject.toml'^)
        echo $encoding = [System.Text.Encoding]::UTF8
        echo try {
        echo     $content = $encoding.GetString($bytes^)
        echo } catch {
        echo     Write-Host "[WARN] UTF-8 decode failed, trying Windows-1252..."
        echo     $encoding = [System.Text.Encoding]::GetEncoding('Windows-1252'^)
        echo     $content = $encoding.GetString($bytes^)
        echo }
        echo.
        echo $wheelsDir = '%~dp0pack_workspace\wheels'
        echo $wheelFiles = Get-ChildItem "$wheelsDir\*.whl"
        echo.
        echo foreach ($wheelFile in $wheelFiles^) {
        echo     $wheelName = $wheelFile.BaseName -replace '-.*$', ''
        echo     $wheelPath = $wheelFile.FullName -replace '\\', '/'
        echo     $wheelUrl = "file:///$wheelPath"
        echo     Write-Host "[INFO] Processing wheel: $wheelName -> $wheelUrl"
        echo     # Match quoted package name with optional version constraints
        echo     $pattern = "`"$wheelName[^`"]*`""
        echo     $replacement = "`"$wheelName @ $wheelUrl`""
        echo     $content = $content -replace $pattern, $replacement
        echo }
        echo.
        echo # Write back as UTF-8 without BOM
        echo $utf8 = New-Object System.Text.UTF8Encoding($false^)
        echo [System.IO.File]::WriteAllText('pyproject.toml', $content, $utf8^)
    ) > update_deps.ps1
    
    REM Execute PowerShell script
    powershell -ExecutionPolicy Bypass -File "update_deps.ps1"
    set "ps_result=!errorlevel!"
    
    REM Clean up PowerShell script
    del "update_deps.ps1" >nul 2>&1
    
    if !ps_result! equ 0 (
        echo [DONE] Updated pyproject.toml with local wheel dependencies
    ) else (
        echo [ERROR] Failed to update pyproject.toml
        copy "pyproject.toml.backup" "pyproject.toml" >nul 2>&1
        popd
        pause
        exit /b 1
    )
) else (
    echo [ERROR] pyproject.toml not found in %PACKAGE_NAME% directory!
    popd
    pause
    exit /b 1
)

REM Build package using uv build
echo [INFO] Building execkit package %PACKAGE_NAME%...
uv build
if !errorlevel! neq 0 (
    echo [ERROR] Building package %PACKAGE_NAME% failed, code: !errorlevel!
    popd
    pause
    exit /b 1
)

REM Check dist directory and whl files
if not exist "dist" (
    echo [ERROR] dist directory not found after build
    popd
    pause
    exit /b 1
)

REM Create wheels directory in pack_workspace if it doesn't exist
if not exist "%~dp0pack_workspace\wheels" (
    echo [INFO] Creating pack_workspace\wheels directory...
    mkdir "%~dp0pack_workspace\wheels"
    echo [DONE] wheels directory created
)

REM Find and install .whl files to python_base
for %%w in (dist\*.whl) do (
    echo [INFO] Installing %%w to python_base...
    echo [DEBUG] Using Python: "%PYTHON_BASE_EXE%"
    echo [DEBUG] Installing package: "%%~fw"
    "%PYTHON_BASE_EXE%" -m pip install "%%~fw"
    if !errorlevel! neq 0 (
        echo [ERROR] Installing %%w failed, code: !errorlevel!
        echo [DEBUG] Current directory: %CD%
        echo [DEBUG] Full file path: %%~fw
        popd
        pause
        exit /b 1
    )
    echo [DONE] %%w installed successfully
    
    REM Copy wheel file to pack_workspace\wheels
    echo [INFO] Copying %%w to pack_workspace\wheels...
    copy "%%~fw" "%~dp0pack_workspace\wheels\" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [DONE] %%w copied to wheels directory
    ) else (
        echo [WARN] Failed to copy %%w to wheels directory
    )
)

REM Restore original pyproject.toml
if exist "pyproject.toml.backup" (
    echo [INFO] Restoring original pyproject.toml...
    copy "pyproject.toml.backup" "pyproject.toml" >nul 2>&1
    del "pyproject.toml.backup" >nul 2>&1
    echo [DONE] Original pyproject.toml restored
)

REM Return to original directory
popd
goto :eof

:process_components_package
set "PACKAGE_NAME=%1"
echo.
echo [INFO] Processing components package: %PACKAGE_NAME%

REM Check if package directory exists
if not exist "engine\components\%PACKAGE_NAME%" (
    echo [WARN] Package directory engine\components\%PACKAGE_NAME% not found, skipping...
    goto :eof
)

REM Enter package directory
pushd "engine\components\%PACKAGE_NAME%"

REM Clean old build artifacts
if exist "dist" (
    echo [INFO] Cleaning old build artifacts for %PACKAGE_NAME%...
    rmdir /s /q "dist" >nul 2>&1
    if exist "dist" (
        echo [WARN] Cannot completely clean dist directory, continuing...
    ) else (
        echo [DONE] dist directory cleaned successfully
    )
)

REM Update pyproject.toml to use local wheel dependencies
echo [INFO] Updating pyproject.toml to use local wheel dependencies...

REM Backup original pyproject.toml
if exist "pyproject.toml" (
    copy "pyproject.toml" "pyproject.toml.backup" >nul 2>&1
    echo [INFO] Backed up original pyproject.toml
    
    REM Create PowerShell script to update dependencies
    echo [INFO] Creating PowerShell script to update dependencies...
    (
        echo # Read file with proper encoding detection
        echo $bytes = [System.IO.File]::ReadAllBytes('pyproject.toml'^)
        echo $encoding = [System.Text.Encoding]::UTF8
        echo try {
        echo     $content = $encoding.GetString($bytes^)
        echo } catch {
        echo     Write-Host "[WARN] UTF-8 decode failed, trying Windows-1252..."
        echo     $encoding = [System.Text.Encoding]::GetEncoding('Windows-1252'^)
        echo     $content = $encoding.GetString($bytes^)
        echo }
        echo.
        echo $wheelsDir = '%~dp0pack_workspace\wheels'
        echo $wheelFiles = Get-ChildItem "$wheelsDir\*.whl"
        echo.
        echo foreach ($wheelFile in $wheelFiles^) {
        echo     $wheelName = $wheelFile.BaseName -replace '-.*$', ''
        echo     $wheelPath = $wheelFile.FullName -replace '\\', '/'
        echo     $wheelUrl = "file:///$wheelPath"
        echo     Write-Host "[INFO] Processing wheel: $wheelName -> $wheelUrl"
        echo     # Match quoted package name with optional version constraints
        echo     $pattern = "`"$wheelName[^`"]*`""
        echo     $replacement = "`"$wheelName @ $wheelUrl`""
        echo     $content = $content -replace $pattern, $replacement
        echo }
        echo.
        echo # Write back as UTF-8 without BOM
        echo $utf8 = New-Object System.Text.UTF8Encoding($false^)
        echo [System.IO.File]::WriteAllText('pyproject.toml', $content, $utf8^)
    ) > update_deps.ps1
    
    REM Execute PowerShell script
    powershell -ExecutionPolicy Bypass -File "update_deps.ps1"
    set "ps_result=!errorlevel!"
    
    REM Clean up PowerShell script
    del "update_deps.ps1" >nul 2>&1
    
    if !ps_result! equ 0 (
        echo [DONE] Updated pyproject.toml with local wheel dependencies
    ) else (
        echo [ERROR] Failed to update pyproject.toml
        copy "pyproject.toml.backup" "pyproject.toml" >nul 2>&1
        popd
        pause
        exit /b 1
    )
) else (
    echo [ERROR] pyproject.toml not found in %PACKAGE_NAME% directory!
    popd
    pause
    exit /b 1
)

REM Build package using uv build
echo [INFO] Building components package %PACKAGE_NAME%...
uv build
if !errorlevel! neq 0 (
    echo [ERROR] Building package %PACKAGE_NAME% failed, code: !errorlevel!
    popd
    pause
    exit /b 1
)

REM Check dist directory and whl files
if not exist "dist" (
    echo [ERROR] dist directory not found after build
    popd
    pause
    exit /b 1
)

REM Create wheels directory in pack_workspace if it doesn't exist
if not exist "%~dp0pack_workspace\wheels" (
    echo [INFO] Creating pack_workspace\wheels directory...
    mkdir "%~dp0pack_workspace\wheels"
    echo [DONE] wheels directory created
)

REM Find and install .whl files to python_base
for %%w in (dist\*.whl) do (
    echo [INFO] Installing %%w to python_base...
    echo [DEBUG] Using Python: "%PYTHON_BASE_EXE%"
    echo [DEBUG] Installing package: "%%~fw"
    "%PYTHON_BASE_EXE%" -m pip install "%%~fw"
    if !errorlevel! neq 0 (
        echo [ERROR] Installing %%w failed, code: !errorlevel!
        echo [DEBUG] Current directory: %CD%
        echo [DEBUG] Full file path: %%~fw
        popd
        pause
        exit /b 1
    )
    echo [DONE] %%w installed to python_base successfully
    
    REM Copy wheel file to pack_workspace\wheels
    echo [INFO] Copying %%w to pack_workspace\wheels...
    copy "%%~fw" "%~dp0pack_workspace\wheels\" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [DONE] %%w copied to wheels directory
    ) else (
        echo [WARN] Failed to copy %%w to wheels directory
    )
)

REM Restore original pyproject.toml
if exist "pyproject.toml.backup" (
    echo [INFO] Restoring original pyproject.toml...
    copy "pyproject.toml.backup" "pyproject.toml" >nul 2>&1
    del "pyproject.toml.backup" >nul 2>&1
    echo [DONE] Original pyproject.toml restored
)

REM Return to original directory
popd
goto :eof

:build_complete

echo.
echo [INFO] Installing requirements.txt to python_core...

REM Check if requirements.txt exists
if not exist "engine\requirements.txt" (
    echo [ERROR] engine\requirements.txt file not found!
    pause
    exit /b 1
)

echo [INFO] Found engine\requirements.txt, installing dependencies...
echo [INFO] Using Python: "%PYTHON_CORE_EXE%"

REM Upgrade pip to latest version
echo [INFO] Upgrading pip to latest version...
"%PYTHON_CORE_EXE%" -m pip install --upgrade pip
if !errorlevel! neq 0 (
    echo [WARN] pip upgrade failed, continuing with current version...
)

REM Install dependencies from requirements.txt
echo [INFO] Installing dependencies from requirements.txt...
call :install_requirements_with_retry
if !errorlevel! equ 0 (
    echo [DONE] requirements.txt installed successfully
    goto :requirements_complete
)

echo [ERROR] Installing requirements.txt failed after all attempts
echo [INFO] Trying to install packages individually with retry...

REM Read and install line by line with retry
for /f "usebackq delims= tokens=*" %%a in ("engine\requirements.txt") do (
    set "package=%%a"
    if not "!package!"=="" (
        if not "!package:~0,1!"=="#" (
            echo [INFO] Installing package: !package!
            call :install_package_with_retry "!package!"
            if !errorlevel! neq 0 (
                echo [WARN] Installing !package! failed after retries, skipping...
            ) else (
                echo [DONE] !package! installed successfully
            )
        )
    )
)

:requirements_complete

echo.
echo [INFO] Copying engine files to pack_workspace...

REM Create engine directory in pack_workspace
if not exist "pack_workspace\engine" (
    echo [INFO] Creating pack_workspace\engine directory...
    mkdir "pack_workspace\engine"
    echo [DONE] pack_workspace\engine directory created
) else (
    echo [INFO] pack_workspace\engine directory already exists
)

REM Copy engine/components directory
if exist "engine\components" (
    echo [INFO] Copying engine\components...
    if exist "pack_workspace\engine\components" (
        echo [INFO] Removing existing components directory...
        rmdir /s /q "pack_workspace\engine\components" >nul 2>&1
    )
    xcopy "engine\components" "pack_workspace\engine\components" /e /i /h /y >nul
    if !errorlevel! equ 0 (
        echo [DONE] engine\components copied successfully
    ) else (
        echo [ERROR] Failed to copy engine\components, code: !errorlevel!
        pause
        exit /b 1
    )
) else (
    echo [WARN] engine\components directory not found, skipping...
)

REM Copy engine/shared directory
if exist "engine\shared" (
    echo [INFO] Copying engine\shared...
    if exist "pack_workspace\engine\shared" (
        echo [INFO] Removing existing shared directory...
        rmdir /s /q "pack_workspace\engine\shared" >nul 2>&1
    )
    xcopy "engine\shared" "pack_workspace\engine\shared" /e /i /h /y >nul
    if !errorlevel! equ 0 (
        echo [DONE] engine\shared copied successfully
    ) else (
        echo [ERROR] Failed to copy engine\shared, code: !errorlevel!
        pause
        exit /b 1
    )
) else (
    echo [WARN] engine\shared directory not found, skipping...
)

REM Copy engine/execkit directory
if exist "engine\execkit" (
    echo [INFO] Copying engine\execkit...
    if exist "pack_workspace\engine\execkit" (
        echo [INFO] Removing existing execkit directory...
        rmdir /s /q "pack_workspace\engine\execkit" >nul 2>&1
    )
    xcopy "engine\execkit" "pack_workspace\engine\execkit" /e /i /h /y >nul
    if !errorlevel! equ 0 (
        echo [DONE] engine\execkit copied successfully
    ) else (
        echo [ERROR] Failed to copy engine\execkit, code: !errorlevel!
        pause
        exit /b 1
    )
) else (
    echo [WARN] engine\execkit directory not found, skipping...
)

REM Copy engine/core directory
if exist "engine\core" (
    echo [INFO] Copying engine\core...
    if exist "pack_workspace\engine\core" (
        echo [INFO] Removing existing core directory...
        rmdir /s /q "pack_workspace\engine\core" >nul 2>&1
    )
    xcopy "engine\core" "pack_workspace\engine\core" /e /i /h /y >nul
    if !errorlevel! equ 0 (
        echo [DONE] engine\core copied successfully
    ) else (
        echo [ERROR] Failed to copy engine\core, code: !errorlevel!
        pause
        exit /b 1
    )
) else (
    echo [WARN] engine\core directory not found, skipping...
)

REM Copy single files from engine directory
echo [INFO] Copying engine single files...
for %%f in (engine\*.py engine\*.txt engine\*.md engine\*.json engine\*.toml engine\*.cfg engine\*.ini) do (
    if exist "%%f" (
        echo [INFO] Copying %%f...
        copy "%%f" "pack_workspace\engine\" >nul 2>&1
        if !errorlevel! equ 0 (
            echo [DONE] %%f copied successfully
        ) else (
            echo [WARN] Failed to copy %%f, skipping...
        )
    )
)

echo.
echo [INFO] Creating 7z archives from pack_workspace contents...

REM Check if 7-Zip is available (reuse the logic from earlier)
set "SEVENZIP_EXE="
if not "%CUSTOM_7ZIP_PATH%"=="" (
    if exist "%CUSTOM_7ZIP_PATH%" (
        set "SEVENZIP_EXE=%CUSTOM_7ZIP_PATH%"
        echo [INFO] Using custom 7-Zip: "%SEVENZIP_EXE%"
    )
)

if "%SEVENZIP_EXE%"=="" (
    if exist "C:\Program Files\7-Zip\7z.exe" (
        set "SEVENZIP_EXE=C:\Program Files\7-Zip\7z.exe"
        echo [INFO] Using 7-Zip: "%SEVENZIP_EXE%"
    ) else if exist "C:\Program Files (x86)\7-Zip\7z.exe" (
        set "SEVENZIP_EXE=C:\Program Files (x86)\7-Zip\7z.exe"
        echo [INFO] Using 7-Zip: "%SEVENZIP_EXE%"
    ) else (
        echo [ERROR] 7-Zip not found! Cannot create archives.
        echo [INFO] Please install 7-Zip or specify path with: pack.bat "path\to\7z.exe"
        pause
        exit /b 1
    )
)

REM Create archives directory if it doesn't exist
if not exist "archives" (
    echo [INFO] Creating archives directory...
    mkdir "archives"
    echo [DONE] archives directory created
)

REM Archive python_base
if exist "pack_workspace\python_base" (
    echo [INFO] Creating python_base.7z archive...
    if exist "archives\python_base.7z" (
        echo [INFO] Removing existing python_base.7z...
        del /f /q "archives\python_base.7z" >nul 2>&1
    )
    pushd "pack_workspace\python_base"
    "%SEVENZIP_EXE%" a -t7z "..\..\archives\python_base.7z" "*" -m0=lzma2 -mx=5 -mmt=8
    set "archive_result=!errorlevel!"
    popd
    if !archive_result! equ 0 (
        echo [DONE] python_base.7z created successfully
    ) else (
        echo [ERROR] Failed to create python_base.7z, code: !archive_result!
        pause
        exit /b 1
    )
) else (
    echo [WARN] pack_workspace\python_base not found, skipping archive creation
)

REM Archive python_core
if exist "pack_workspace\python_core" (
    echo [INFO] Creating python_core.7z archive...
    if exist "archives\python_core.7z" (
        echo [INFO] Removing existing python_core.7z...
        del /f /q "archives\python_core.7z" >nul 2>&1
    )
    pushd "pack_workspace\python_core"
    "%SEVENZIP_EXE%" a -t7z "..\..\archives\python_core.7z" "*" -m0=lzma2 -mx=5 -mmt=8
    set "archive_result=!errorlevel!"
    popd
    if !archive_result! equ 0 (
        echo [DONE] python_core.7z created successfully
    ) else (
        echo [ERROR] Failed to create python_core.7z, code: !archive_result!
        pause
        exit /b 1
    )
) else (
    echo [WARN] pack_workspace\python_core not found, skipping archive creation
)

REM Archive engine
if exist "pack_workspace\engine" (
    echo [INFO] Creating engine.7z archive...
    if exist "archives\engine.7z" (
        echo [INFO] Removing existing engine.7z...
        del /f /q "archives\engine.7z" >nul 2>&1
    )
    pushd "pack_workspace\engine"
    "%SEVENZIP_EXE%" a -t7z "..\..\archives\engine.7z" "*" -m0=lzma2 -mx=5 -mmt=8
    set "archive_result=!errorlevel!"
    popd
    if !archive_result! equ 0 (
        echo [DONE] engine.7z created successfully
    ) else (
        echo [ERROR] Failed to create engine.7z, code: !archive_result!
        pause
        exit /b 1
    )
) else (
    echo [WARN] pack_workspace\engine not found, skipping archive creation
)

echo.
echo [DONE] All operations completed successfully!
echo - pack_workspace folder is ready
echo - Python directory copied from "%PYTHON_SOURCE_DIR%" to pack_workspace
echo - python_core folder created (copy of source Python)
echo - python_base folder created (copy of source Python)
echo - All shared packages built and installed to python_core and python_base
echo - Dependent packages built and installed to python_core
echo - Execkit packages built and installed to python_base
echo - Components packages built and installed to python_base
echo - All package wheels copied to pack_workspace\wheels
echo - engine\requirements.txt installed to python_core
echo - engine directories and files copied to pack_workspace\engine
echo - Created archives: python_base.7z, python_core.7z, engine.7z

echo.
echo [INFO] Moving archives to tauri resources...

REM Set tauri resources directory path
set "TAURI_RESOURCES_DIR=frontend\packages\tauri-app\src-tauri\resources"

REM Create resources directory if it doesn't exist
if not exist "%TAURI_RESOURCES_DIR%" (
    echo [INFO] Creating tauri resources directory...
    mkdir "%TAURI_RESOURCES_DIR%"
)

REM Move archive files
if exist "archives\python_base.7z" (
    echo [INFO] Moving python_base.7z...
    move "archives\python_base.7z" "%TAURI_RESOURCES_DIR%\" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [DONE] python_base.7z moved successfully
    ) else (
        echo [WARN] Failed to move python_base.7z
    )
) else (
    echo [WARN] python_base.7z not found in archives directory
)

if exist "archives\python_core.7z" (
    echo [INFO] Moving python_core.7z...
    move "archives\python_core.7z" "%TAURI_RESOURCES_DIR%\" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [DONE] python_core.7z moved successfully
    ) else (
        echo [WARN] Failed to move python_core.7z
    )
) else (
    echo [WARN] python_core.7z not found in archives directory
)

if exist "archives\engine.7z" (
    echo [INFO] Moving engine.7z...
    move "archives\engine.7z" "%TAURI_RESOURCES_DIR%\" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [DONE] engine.7z moved successfully
    ) else (
        echo [WARN] Failed to move engine.7z
    )
) else (
    echo [WARN] engine.7z not found in archives directory
)

echo.
echo [DONE] Archives moved to tauri resources successfully!

echo.
echo ========================================
echo Usage:
echo   Specify Python directory: pack.bat "" "PYTHON_DIRECTORY_PATH"
echo   Specify 7-Zip path: pack.bat "7ZIP_PATH" ""
echo   Both custom paths: pack.bat "7ZIP_PATH" "PYTHON_DIRECTORY_PATH"
echo   Examples:
echo     pack.bat "" "C:\Python313"
echo     pack.bat "" "D:\Python"
echo     pack.bat "" "Python313"
echo     pack.bat "D:\Tools\7-Zip\7z.exe" "C:\Python313"
echo ========================================
echo.
echo Please tell me what to do next...
pause



REM Function to install requirements.txt with retry mechanism
:install_requirements_with_retry
set "RETRY_COUNT=0"
set "MAX_RETRIES=3"

:req_retry_loop
set /a RETRY_COUNT+=1
echo [INFO] Attempt %RETRY_COUNT%/%MAX_RETRIES% installing requirements.txt...

REM Try different installation strategies for requirements.txt
if %RETRY_COUNT% equ 1 (
    REM First attempt: normal install
    "%PYTHON_CORE_EXE%" -m pip install -r "engine\requirements.txt"
) else if %RETRY_COUNT% equ 2 (
    REM Second attempt: use --user flag
    echo [INFO] Trying requirements.txt with --user flag...
    "%PYTHON_CORE_EXE%" -m pip install -r "engine\requirements.txt" 
) else (
    REM Third attempt: wait and try with no-cache
    echo [INFO] Waiting 3 seconds and trying with --no-cache-dir...
    timeout /t 3 /nobreak >nul
    "%PYTHON_CORE_EXE%" -m pip install -r "engine\requirements.txt" --no-cache-dir
)

if !errorlevel! equ 0 (
    echo [SUCCESS] requirements.txt installed successfully on attempt %RETRY_COUNT%
    exit /b 0
)

if %RETRY_COUNT% geq %MAX_RETRIES% (
    echo [ERROR] All %MAX_RETRIES% attempts failed for requirements.txt
    exit /b 1
)

echo [WARN] Requirements.txt attempt %RETRY_COUNT% failed, retrying...
timeout /t 2 /nobreak >nul
goto :req_retry_loop

REM Function to install individual package with retry mechanism
:install_package_with_retry
set "PACKAGE=%~1"
set "RETRY_COUNT=0"
set "MAX_RETRIES=3"

:pkg_retry_loop
set /a RETRY_COUNT+=1

REM Try different installation strategies for individual packages
if %RETRY_COUNT% equ 1 (
    REM First attempt: normal install
    "%PYTHON_CORE_EXE%" -m pip install "%PACKAGE%" >nul 2>&1
) else if %RETRY_COUNT% equ 2 (
    REM Second attempt: use --user flag
    "%PYTHON_CORE_EXE%" -m pip install "%PACKAGE%" --user >nul 2>&1
) else (
    REM Third attempt: wait and try with no-cache
    timeout /t 1 /nobreak >nul
    "%PYTHON_CORE_EXE%" -m pip install "%PACKAGE%" --no-cache-dir >nul 2>&1
)

if !errorlevel! equ 0 (
    goto :eof
)

if %RETRY_COUNT% geq %MAX_RETRIES% (
    exit /b 1
)

timeout /t 1 /nobreak >nul
goto :pkg_retry_loop 