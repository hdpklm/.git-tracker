@echo off
git config --global --unset alias.repos

git config --global core.hooksPath "%USERPROFILE%/.git-tracker/hooks"
git config --global alias.repos "!python \"${USERPROFILE//\\//}/.git-tracker/find_repo.py\""
echo Git hooks configurados correctamente
echo.
echo Configuracion actual "core.hooksPath":
git config --global --get core.hooksPath
pause
