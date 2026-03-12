@echo off
:: Desconfigurar alias antiguos
git config --global --unset alias.repos

:: Configurar el alias principal "git repos"
:: Nota: Usamos git_tracker.py como entrada tal como solicitaste, el cual delega a git_tracker.py
git config --global alias.repos "!python \"%~dp0git_tracker.py\""

echo.
echo Git Tracker configurado correctamente.
echo.
echo Ahora todo funciona a traves del comando "git repos":
echo.
echo   git repos              - Muestra todos los repositorios
echo   git repos [TERMINO]    - Busca repositorios por nombre o ruta
echo   git repos -s [PATH]    - Escanea disco o carpeta para encontrar repos
echo   git repos -a [PATH]    - Agrega un repositorio manual
echo   git repos -u           - Verifica y actualiza existencia de repos
echo   git repos -r [ID|PATH] - Elimina un repositorio del registro
echo.
echo.
pause
