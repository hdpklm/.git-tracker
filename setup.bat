@echo off
git config --global init.templatedir "%USERPROFILE%/.git-tracker"
echo Git hooks configurados correctamente
echo.
echo Configuracion actual:
git config --global --get init.templatedir
pause