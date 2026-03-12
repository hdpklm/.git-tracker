@echo off
:: Desconfigurar alias antiguos
git config --global --unset alias.repos

:: Configurar el alias principal "git repos"
:: Usa el wrapper git-repos.bat para permitir cambiar de directorio CMD con "goto" (-g)
git config --global alias.repos "!\"%~dp0git-repos.bat\""

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
echo   git repos -r [ID|PATH] - Oculta un repositorio de la lista
echo   git repos -g [ID]      - Navega directamente a la ruta del repo (cd)
echo   git repos -v [FLAGS]   - Muestra detalles del repo (ej: -v lomp)
echo.
echo.
pause
