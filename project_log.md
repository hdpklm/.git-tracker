# Project Log - Git Tracker

## Backup
(No logic replaced yet)

## Change History

### 📝 Registro: [v1.0.0] - Initial Setup
- **Problema**: Necesidad de organizar múltiples repositorios Git en el disco.
- **Causa**: Crecimiento desordenado de proyectos.
- **Solución**: Creación de Git Tracker para escaneo y búsqueda centralizada.

### 📝 Registro: [v1.1.0] - Mejora de Escaneo y Corrección de "C:"
- **Problema**: El escaneo era lento, detectaba incorrectamente "C:" como un repo y no encontraba todos los repositorios reales.
- **Causa**: Falta de filtros de exclusión para carpetas del sistema, mala normalización de rutas de raíz de disco y falta de manejo de errores de permisos.
- **Solución**: Se implementó una lista de exclusión (`EXCLUDE_DIRS`), se corrigió el manejo de raíces proyectándolas como `C:/`, se añadió limpieza automática de entradas erróneas y se reemplazaron símbolos Unicode por ASCII para compatibilidad con Windows CMD. Se encontraron 20 nuevos repositorios.

### 📝 Registro: [v1.2.0] - IDs Persistentes y Compatibilidad ASCII
- **Problema**: Los resultados de búsqueda generaban nuevos IDs (0, 1, 2...), lo que causaba el borrado de repositorios incorrectos si se usaba el comando `-r`. Además, los símbolos Unicode/Emojis seguían fallando en CMD.
- **Causa**: Falta de un mapa global de IDs durante el filtrado y uso persistente de caracteres no ASCII.
- **Solución**: Se implementó una función para generar un mapa global de IDs (`path -> ID`) y se actualizó `print_hierarchical_tree` en ambos scripts para usarlo. Se eliminaron todos los caracteres Unicode (Emojis y box-drawing) reemplazándolos con ASCII puro.

### 📝 Registro: [v1.3.0] - Unificación de CLI en "git repos"
- **Problema**: El uso de dos comandos (`git tracker` y `git repos`) resultaba redundante y confuso para el usuario.
- **Causa**: La lógica de búsqueda estaba en `find_repo.py` y la lógica de administración en `git_tracker.py`.
- **Solución**: Se integró la lógica principal en `git_tracker.py`. Ahora `git_tracker.py` permite que el alias `git repos` (configurado en `setup.bat`) procese tanto texto de búsqueda directo como subcomandos (`-s`, `-a`, etc.). Se limpiaron los alias viejos en `setup.bat`.

