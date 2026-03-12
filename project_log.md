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

