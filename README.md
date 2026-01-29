# PC Optimizer SME Edition

PC Optimizer SME Edition es una aplicación robusta diseñada para Windows 11 que permite la gestión eficiente de archivos temporales y memoria RAM, con un enfoque primordial en la seguridad del sistema y la transparencia para el usuario.

## 🚀 Descripción

Esta herramienta permite optimizar el rendimiento de tu estación de trabajo eliminando archivos basura acumulados y liberando memoria volátil ocupada por procesos pesados, todo bajo una interfaz moderna y segura que protege procesos críticos de Windows.

## ✨ Características Principales

- **Seguridad Inteligente**: Protección contra el cierre de procesos críticos del sistema (System, lsass, etc.).
- **Modo de Prueba (Dry Run)**: Permite simular las acciones de limpieza sin realizar cambios reales para verificar qué se borraría.
- **Logs Rotatorios**: Sistema de registro detallado en `/logs` que se autogestiona para no ocupar espacio excesivo.
- **Feedback Detallado**: Reportes granulares al finalizar cada operación, indicando exactamente qué archivos o procesos fueron afectados.
- **Interfaz Moderna**: Construida con CustomTkinter para una experiencia visual premium en modo oscuro.
- **Threading**: Ejecución de escaneos en segundo plano para mantener la fluidez de la aplicación.

## 🛠️ Instrucciones de Uso Rápido

1. **Ejecutar como Administrador**: Para que las funciones de limpieza de sistema (como DISM) y salud de archivos (SFC) funcionen correctamente, es necesario iniciar el ejecutable con privilegios elevados.
2. **Revisar Logs**: Todas las operaciones quedan registradas en la carpeta `/logs/mantenimiento_pc.log`.
3. **Fase de Escaneo**: Presiona "Ejecutar" en cualquier módulo para detectar elementos potenciales de optimización.
4. **Resumen y Confirmación**: Revisa la lista de elementos detectados y confirma la ejecución.

## 👨‍💻 Créditos

Desarrollado por **Salvador Ibarra**, un Subject Matter Expert (SME) en **O-RAN** enfocado en la optimización de sistemas complejos y la eficiencia operativa.

---
*Optimiza con seguridad, optimiza con precisión.*
