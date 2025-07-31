# Afinador Profesional de Escritorio (Estilo Retro)

Un afinador cromático de escritorio, desarrollado en Python, que ofrece detección de tono de alta precisión y un visualizador de espectro en tiempo real. La interfaz está diseñada con una estética nostálgica de Windows 95.



## Características

* **Detección Precisa:** Utiliza el robusto algoritmo **YIN** para una identificación de frecuencia fundamental precisa, minimizando errores de octava.
* **Visualización Dual:**
    * **Indicador de Afinación:** Una aguja y un código de colores (rojo, verde, azul) muestran claramente si el tono es alto, bajo o correcto.
    * **Visualizador de Espectro:** Un gráfico de barras en tiempo real muestra el espectro completo de frecuencias (fundamental y armónicos).
* **Doble Notación:** Permite cambiar al instante entre la notación anglosajona (C, D, E) y la latina (Do, Re, Mi).
* **Interfaz Retro:** Diseño inspirado en la clásica interfaz de usuario de Windows 95 para una experiencia visual única.
* **Arquitectura Modular:** El código está limpiamente separado entre el motor de procesamiento de audio (`tuner_engine.py`) y la interfaz gráfica (`tuner_gui.py`).

## Pila Tecnológica

* **Lenguaje:** Python 3
* **Interfaz Gráfica (GUI):** Tkinter
* **Procesamiento de Audio:**
    * **Entrada/Salida:** `sounddevice`
    * **Detección de Tono:** `aubio`
    * **Análisis Numérico y FFT:** `NumPy`

## Instalación y Ejecución

Sigue estos pasos para ejecutar la aplicación en tu máquina local.


1. Clona el repositorio:

```bash
git clone [https://github.com/TU_USUARIO/afinador-escritorio.git](https://github.com/TU_USUARIO/afinador-escritorio.git)
cd afinador-escritorio


2. Crea un entorno virtual (recomendado):

python -m venv venv
source venv/bin/activate  # En Windows usa: venv\Scripts\activate


3. Instala las dependencias:

Las librerías requeridas son sounddevice, numpy, y aubio. Puedes instalarlas con pip:

pip install sounddevice numpy aubio


4. Ejecuta la aplicación:

El archivo principal que lanza la interfaz es tuner_gui.py.

python tuner_gui.py


Agradecimientos
Este proyecto se basa en el poder de las siguientes librerías de código abierto, sin las cuales no sería posible:

Aubio para la detección de tono.

SoundDevice para la interacción con el hardware de audio.

NumPy para el procesamiento numérico eficiente.