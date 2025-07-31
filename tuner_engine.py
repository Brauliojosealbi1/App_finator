# -----------------------------------------------------------------------------
# ARCHIVO 1: tuner_engine.py
#
# RESPONSABILIDAD:
# - Capturar audio del micrófono.
# - Procesar la señal en un hilo separado.
# - Detectar el tono (pitch) usando el algoritmo YIN (aubio).
# - Analizar el espectro de frecuencia usando FFT (numpy).
# - Poner los resultados en una cola para que la interfaz los consuma.
# -----------------------------------------------------------------------------

import sounddevice as sd
import numpy as np
import aubio
import threading

class AudioProcessor:
    """
    Encapsula toda la lógica de procesamiento de audio en un hilo separado.
    """
    def __init__(self, data_queue):
        # --- Constantes de Audio ---
        self.sample_rate = 44100
        self.buffer_size = 2048

        # --- Estado y Comunicación ---
        self.data_queue = data_queue
        self.is_running = False
        self._thread = None

        # --- Configuración de Aubio ---
        self.pitch_o = aubio.pitch("yin", self.buffer_size * 2, self.buffer_size, self.sample_rate)
        self.pitch_o.set_unit("Hz")
        self.pitch_o.set_tolerance(0.8)

    def start(self):
        """Inicia el hilo de procesamiento de audio."""
        if self._thread is not None:
            return # Ya está en ejecución
        
        print("Iniciando hilo de audio...")
        self.is_running = True
        self._thread = threading.Thread(target=self._processing_loop)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        """Detiene el hilo de procesamiento de audio."""
        print("Deteniendo hilo de audio...")
        self.is_running = False
        if self._thread is not None:
            self._thread.join() # Esperar a que el hilo termine
        self._thread = None

    def _audio_callback(self, indata, frames, time, status):
        """
        Función llamada por sounddevice para cada bloque de audio.
        Realiza el análisis y pone los datos en la cola.
        """
        if not self.is_running:
            raise sd.CallbackStop

        # VÍA A: Detección de Tono Precisa (YIN)
        samples = np.frombuffer(indata, dtype=aubio.float_type)
        pitch = self.pitch_o(samples)[0]
        confidence = self.pitch_o.get_confidence()

        # VÍA B: Análisis Visual (FFT)
        fft_spectrum = np.abs(np.fft.rfft(indata[:, 0]))
        
        # Poner los datos en la cola para que la UI los procese
        self.data_queue.put({'pitch': pitch, 'confidence': confidence, 'spectrum': fft_spectrum})

    def _processing_loop(self):
        """
        El bucle principal del hilo, donde se mantiene activo el stream de audio.
        """
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=self.buffer_size,
                channels=1,
                dtype='float32',
                callback=self._audio_callback
            ):
                while self.is_running:
                    sd.sleep(100) # Mantener el hilo vivo mientras is_running es True
        except Exception as e:
            print(f"Error en el stream de audio: {e}")
        
        print("El bucle de procesamiento de audio ha terminado.")

