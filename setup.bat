@echo off
git config --global --unset alias.repos
git config --global --unset alias.tracker

git config --global core.hooksPath "%USERPROFILE%/.git-tracker/hooks"
git config --global alias.repos "!python \"${USERPROFILE//\\//}/.git-tracker/find_repo.py\""
git config --global alias.tracker "!python \"${USERPROFILE//\\//}/.git-tracker/git_tracker.py\""

echo Git hooks y comandos personalizados configurados correctamente
echo.
echo Configuracion actual "core.hooksPath":
git config --global --get core.hooksPath
echo.
echo Comandos disponibles:
echo   git repos [TERMINO]   - Busca repositorios por nombre o ruta
echo   git tracker -h        - Muestra ayuda de git tracker
echo   git tracker -s [PATH] - Escanea disco o carpeta para encontrar repos
echo   git tracker -a [PATH] - Agrega un repositorio
echo   git tracker -u        - Actualiza y verifica repositorios
echo   git tracker -r [ARGS] - Elimina repositorios
echo.
pause
