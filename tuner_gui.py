# -----------------------------------------------------------------------------
# ARCHIVO 2: tuner_gui.py
#
# RESPONSABILIDAD:
# - Crear y mostrar la ventana principal y todos sus widgets (botones, etc.).
# - Importar y utilizar la clase AudioProcessor como motor.
# - Iniciar y detener el motor de audio cuando el usuario hace clic.
# - Leer los datos de la cola y actualizar la interfaz en tiempo real.
#
# INSTRUCCIONES:
# - Guarda este archivo y `tuner_engine.py` en el mismo directorio.
# - Ejecuta ESTE archivo para lanzar la aplicación: python tuner_gui.py
# -----------------------------------------------------------------------------

import tkinter as tk
from tkinter import font as tkfont
import numpy as np
import queue
from tuner_engine import AudioProcessor # Importa el motor

class TunerApp(tk.Tk):
    """
    Clase principal de la aplicación que maneja la GUI.
    """
    def __init__(self):
        super().__init__()

        # --- Constantes de Afinación ---
        self.A4 = 440
        self.NOTE_STRINGS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.LATIN_NOTE_STRINGS = ["Do", "Do#", "Re", "Re#", "Mi", "Fa", "Fa#", "Sol", "Sol#", "La", "La#", "Si"]
        
        # --- Estado de la aplicación ---
        self.notation_system = 'anglo' # 'anglo' o 'latin'
        self.current_indicator_color = '#008000' # Color por defecto para el espectro

        # --- Colores Estilo Windows 95 ---
        self.win95_bg = '#c0c0c0'
        self.win95_text = '#000000'
        self.win95_green = '#008000'
        self.win95_blue = '#000080'
        self.win95_red = '#800000'

        # --- Configuración de la Ventana ---
        self.title("Afinador Profesional (Estilo Win95)")
        self.geometry("400x600")
        self.configure(bg=self.win95_bg)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # --- Comunicación y Motor ---
        self.data_queue = queue.Queue()
        self.audio_processor = AudioProcessor(self.data_queue)

        # --- Fuentes ---
        self.title_font = tkfont.Font(family="Courier", size=9, weight="bold")
        self.note_font = tkfont.Font(family="Courier", size=24, weight="bold")
        self.info_font = tkfont.Font(family="Courier", size=8)
        self.button_font = tkfont.Font(family="Courier", size=9, weight="bold")

        # --- Creación de Widgets ---
        self.create_widgets()
        self.update_ui_from_queue()

    def create_widgets(self):
        main_frame = tk.Frame(self, bg=self.win95_bg)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        tk.Label(main_frame, text="Afinador de voz", font=self.title_font, bg=self.win95_bg, fg=self.win95_text).pack(pady=(0, 10))
        self.note_label = tk.Label(main_frame, text="--", font=self.note_font, bg=self.win95_bg, fg=self.win95_text)
        self.note_label.pack()

        self.indicator_canvas = tk.Canvas(main_frame, width=300, height=50, bg=self.win95_bg, highlightthickness=0)
        self.indicator_canvas.pack(pady=10)
        self.draw_indicator_base()
        
        self.tuning_status_label = tk.Label(main_frame, text="", font=self.info_font, bg=self.win95_bg, fg='gray')
        self.tuning_status_label.pack()

        self.spectrum_canvas = tk.Canvas(main_frame, width=350, height=200, bg="#E0E0E0", highlightthickness=1, highlightbackground="gray")
        self.spectrum_canvas.pack(pady=15, expand=True, fill=tk.BOTH)

        # Frame para los botones
        button_frame = tk.Frame(main_frame, bg=self.win95_bg)
        button_frame.pack(pady=(20, 10), side=tk.BOTTOM)

        self.control_button = tk.Button(button_frame, text="Activar Micrófono", font=self.button_font, 
                                        bg=self.win95_bg, fg=self.win95_text,
                                        relief=tk.RAISED, borderwidth=2,
                                        command=self.toggle_stream, width=20, height=2)
        self.control_button.pack(side=tk.LEFT, padx=5)

        self.notation_button = tk.Button(button_frame, text="Do, Re, Mi", font=self.button_font, 
                                         bg=self.win95_bg, fg=self.win95_text,
                                         relief=tk.RAISED, borderwidth=2,
                                         command=self.toggle_notation, width=15, height=2)
        self.notation_button.pack(side=tk.LEFT, padx=5)

    def draw_indicator_base(self):
        width = 300
        height = 50
        self.indicator_canvas.create_rectangle(0, 20, width, 30, fill="#a0a0a0", outline="gray")
        self.indicator_canvas.create_line(width/2, 10, width/2, 40, fill=self.win95_green, width=3)
        self.indicator_needle = self.indicator_canvas.create_line(width/2, 15, width/2, 35, fill=self.win95_text, width=5)

    def toggle_stream(self):
        if self.audio_processor.is_running:
            self.audio_processor.stop()
            self.control_button.config(text="Activar Micrófono", relief=tk.RAISED)
        else:
            self.audio_processor.start()
            self.control_button.config(text="Desactivar Micrófono", relief=tk.SUNKEN)

    def toggle_notation(self):
        if self.notation_system == 'anglo':
            self.notation_system = 'latin'
            self.notation_button.config(text="C, D, E")
        else:
            self.notation_system = 'anglo'
            self.notation_button.config(text="Do, Re, Mi")

    def update_ui_from_queue(self):
        try:
            data = self.data_queue.get_nowait()
            
            if data['confidence'] > 0.75:
                pitch = data['pitch']
                note_num = 12 * (np.log2(pitch / self.A4)) + 69
                note_index = int(round(note_num))
                detune = 1200 * np.log2(pitch / (self.A4 * 2**((note_index - 69) / 12)))
                
                if self.notation_system == 'anglo':
                    note_name = self.NOTE_STRINGS[note_index % 12]
                else:
                    note_name = self.LATIN_NOTE_STRINGS[note_index % 12]
                
                self.note_label.config(text=note_name)
                self.update_indicator(detune)
            else:
                self.note_label.config(text="--")
                self.update_indicator(0, silent=True)
            
            self.update_spectrum(data['spectrum'])

        except queue.Empty:
            pass
        finally:
            self.after(20, self.update_ui_from_queue)

    def update_indicator(self, detune, silent=False):
        width = 300
        center_x = width / 2
        max_offset = width / 2 - 10
        clamped_detune = max(-50, min(50, detune))
        offset = (clamped_detune / 50) * max_offset
        
        self.indicator_canvas.coords(self.indicator_needle, center_x + offset, 15, center_x + offset, 35)

        if silent:
            self.tuning_status_label.config(text="", fg="gray")
            self.indicator_canvas.itemconfig(self.indicator_needle, fill=self.win95_text)
            self.current_indicator_color = self.win95_green # Color por defecto para el espectro en silencio
        elif abs(detune) < 5:
            self.tuning_status_label.config(text="Afinado", fg=self.win95_green)
            self.indicator_canvas.itemconfig(self.indicator_needle, fill=self.win95_green)
            self.current_indicator_color = self.win95_green
        elif detune < -5:
            self.tuning_status_label.config(text="Bajo", fg=self.win95_blue)
            self.indicator_canvas.itemconfig(self.indicator_needle, fill=self.win95_blue)
            self.current_indicator_color = self.win95_blue
        else:
            self.tuning_status_label.config(text="Alto", fg=self.win95_red)
            self.indicator_canvas.itemconfig(self.indicator_needle, fill=self.win95_red)
            self.current_indicator_color = self.win95_red

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def update_spectrum(self, spectrum_data):
        canvas = self.spectrum_canvas
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        log_spectrum = np.log1p(spectrum_data)
        if not np.max(log_spectrum) > 0: return

        normalized_spectrum = log_spectrum / np.max(log_spectrum)
        
        num_bars = 100
        bar_width = width / num_bars
        gap = 1
        
        base_r, base_g, base_b = self.hex_to_rgb(self.current_indicator_color)
        
        for i in range(num_bars):
            start = int(len(normalized_spectrum) * (i / num_bars))
            end = int(len(normalized_spectrum) * ((i + 1) / num_bars))
            if start >= end: continue
            
            bar_height_normalized = np.mean(normalized_spectrum[start:end])
            bar_height = bar_height_normalized * height
            
            # Lógica para el color difuminado basado en el color del indicador
            r = int(base_r * bar_height_normalized)
            g = int(base_g * bar_height_normalized)
            b = int(base_b * bar_height_normalized)
            color = f'#{r:02x}{g:02x}{b:02x}'

            x0 = i * bar_width
            y0 = height - bar_height
            x1 = x0 + bar_width - gap
            y1 = height
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

    def on_closing(self):
        if self.audio_processor.is_running:
            self.audio_processor.stop()
        self.destroy()

if __name__ == "__main__":
    app = TunerApp()
    app.mainloop()
