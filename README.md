# Asistente-de-Estudio-Anki
# 🧠 Asistente de Estudio y Analítica Pro para Anki

Un complemento (*add-on*) avanzado para Anki diseñado para estudiantes e investigadores que manejan bases de datos masivas. Originalmente concebido para dominar la compleja taxonomía y morfología en el campo de la agronomía, este asistente transforma los datos crudos de tus repasos en métricas claras, pronósticos de estudio y planes de acción para exámenes.

## ✨ Características Principales

Este *add-on* se integra directamente en el menú de engranaje de cada mazo y ofrece tres herramientas clave:

* **⏳ Pronóstico a Ritmo Actual:** Interroga tu historial de los últimos 7 días y calcula en qué fecha exacta terminarás de ver todas las tarjetas nuevas de un mazo si mantienes tu velocidad actual.
* **🎯 Planificador de Metas / Exámenes:** Selecciona una fecha límite en el calendario interactivo. El sistema cruzará tu tiempo de respuesta histórico, tu tasa de retención y la carga de tarjetas para decirte cuántas debes estudiar al día, cuánto tiempo te tomará y cuál es tu porcentaje de probabilidad de éxito.
* **📊 Reporte de Analítica Pro:** Un *dashboard* avanzado generado con HTML/CSS puro (compatible con el Modo Oscuro de Anki) que expone la salud del mazo:
    * Barras de progreso visuales (Dominadas vs. Jóvenes vs. Nuevas).
    * Tasa de retención real y velocidad de respuesta (en segundos).
    * Distribución de la carga de trabajo de los botones (Otra vez, Difícil, Bien, Fácil).
    * Detección de tarjetas "sanguijuela" (*leeches*) sobre-estudiadas.
* **🌍 Soporte Multilingüe (i18n):** Sistema de carga dinámica mediante archivos `.json`. Autodetecta el idioma de la interfaz de Anki (incluye Inglés y Español por defecto).

## 🤖 Desarrollo Asistido por Inteligencia Artificial

Este proyecto es un testimonio de la colaboración humano-máquina. La arquitectura, la lógica de las bases de datos SQL integradas en Anki, y el diseño de la interfaz gráfica en PyQt6 fueron desarrollados, refactorizados y optimizados en estrecha colaboración con inteligencia artificial (Gemini). 

El uso de la IA permitió:
1.  **Acelerar el ciclo de desarrollo:** Resolviendo discrepancias de compatibilidad con las versiones más recientes de Anki (Qt6 y Python 3.13).
2.  **Mejorar la robustez:** Implementando sistemas de manejo de errores, como la autogeneración de archivos de traducción y la renderización segura de gráficas CSS sin dependencias externas.
3.  **Democratizar el código:** Permitiendo enfocar el esfuerzo humano en la lógica del aprendizaje espaciado y la experiencia de usuario, delegando la escritura de código repetitivo a la IA.

## 🛠️ Tecnologías y Compatibilidad

* **Lenguaje:** Python 3.13+
* **Interfaz Gráfica:** PyQt6 (Qt Rich Text)
* **Base de datos:** Consultas directas a la base SQLite local de Anki (`revlog`, `cards`, `decks`).
* **Compatibilidad:** Anki 23.x, 24.x y 25.x (Utiliza el método optimizado `deck_and_child_ids` y *hooks* nativos).

## 🚀 Instalación

**Opción A: Vía AnkiWeb (Recomendado)**
1. Abre Anki y ve a *Herramientas > Complementos > Descargar complementos*.
2. Introduce el código: `[CODIGO DE ANKI PENDIENTE]`

**Opción B: Instalación Manual**
1. Descarga el archivo `.zip` desde la sección de *Releases* en este repositorio.
2. Abre Anki, ve a *Herramientas > Complementos > Ver archivos*.
3. Descomprime el contenido en una nueva carpeta dentro de `addons21`.
4. Reinicia Anki.

## 🤝 Contribuciones y Traducciones

¡Las contribuciones son bienvenidas! Si deseas añadir soporte para tu idioma nativo:
1. Navega a la carpeta `translations/`.
2. Duplica el archivo `en.json` y renómbralo con el código de tu idioma (ej. `pt.json` para portugués, `fr.json` para francés).
3. Traduce los valores y envía un *Pull Request*.
