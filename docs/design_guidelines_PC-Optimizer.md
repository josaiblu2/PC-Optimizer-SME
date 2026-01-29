Documento de Requerimientos Final: PC Optimizer "SME Edition"
1. Objetivo General
Desarrollar una aplicación de escritorio para Windows 11 que permita realizar tareas de mantenimiento y optimización del sistema de forma transparente, segura y bajo el control total del usuario, sustituyendo las alertas genéricas de software de terceros.

2. Arquitectura y Entorno
Lenguaje: Python 3.10+

Interfaz Gráfica (GUI): customtkinter (Apariencia moderna, modo oscuro).

Estructura de Carpetas: /src (código), /logs (trazabilidad), /docs (manuales).

Seguridad: Uso de entorno virtual (.venv).

3. Funcionalidades y Guía de Ayuda (Pop-ups)
Cada módulo debe incluir un botón de información "(i)" o mostrar un pop-up que explique lo siguiente:

Módulo de Limpieza (Junk Files):

Ayuda: "Elimina archivos temporales acumulados por el sistema y el navegador. Beneficio: Libera espacio en disco y reduce la indexación innecesaria de archivos basura."

Módulo de RAM (psutil):

Ayuda: "Muestra procesos que consumen >500MB. Beneficio: Al cerrar aplicaciones pesadas que no estás usando, liberas memoria volátil para mejorar la respuesta de tus herramientas de trabajo."

Módulo de Salud (SFC/DISM):

Ayuda: "Escanea y repara archivos corruptos del núcleo de Windows. Beneficio: Previene pantallazos azules y errores de ejecución sin necesidad de formatear el equipo."

4. Mecanismos de Control y Seguridad
Modo de Prueba (Dry Run): Switch para simular acciones sin cambios reales.

Confirmación Obligatoria: Popup modal antes de cualquier acción crítica.

Logs Rotatorios: RotatingFileHandler (5MB por archivo, máx. 3 archivos).

Reporte Final: Resumen de acciones exitosas, fallidas y espacio recuperado.

5. Documentación y Aprendizaje
Código: Comentarios detallados en español en cada bloque de funciones.

Salida: Archivo INSTRUCCIONES.txt con guía de operación y solución de errores comunes.

