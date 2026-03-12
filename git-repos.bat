@echo off
:: Wrapper script for git_tracker.py to support the 'goto' (-g) command

:: Set the path to the python script
set "TRACKER_SCRIPT=%~dp0git_tracker.py"
set "CD_FILE=%~dp0.cd_path"

:: Ensure any old cd file is removed
if exist "%CD_FILE%" del "%CD_FILE%"

:: Run the python script with all passed arguments
python "%TRACKER_SCRIPT%" %*

:: If the python script created a cd file, read it and change directory
if exist "%CD_FILE%" (
    set /p TARGET_DIR=<"%CD_FILE%"
    cd /d "!TARGET_DIR!"
    del "%CD_FILE%"
)
