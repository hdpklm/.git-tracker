@echo off
git config --global core.hooksPath "%USERPROFILE%/.git-templates/hooks"
echo Git hooks configurados correctamente
echo.
echo Configuracion actual "core.hooksPath":
git config --global --get core.hooksPath
pause
