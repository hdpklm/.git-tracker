@echo off
git config --global core.hooksPath "%USERPROFILE%/.git-tracker/hooks"
echo Git hooks configurados correctamente
echo.
echo Configuracion actual "core.hooksPath":
git config --global --get core.hooksPath
pause
