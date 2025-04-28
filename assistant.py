import tkinter as tk
from tkinter import ttk, scrolledtext
import speech_recognition as sr
from gtts import gTTS
import sounddevice as sd
import soundfile as sf
import numpy as np
import pygame
from datetime import datetime
from deep_translator import GoogleTranslator
import threading
import time
import os

class EnhancedMultilingualAssistant:
    def __init__(self):
        self.setup_core_components()
        self.setup_gui()
        
    def setup_core_components(self):
        self.recognizer = sr.Recognizer()
        self.recording = False
        self.sample_rate = 44100
        self.energy_threshold = 300
        self.duration = 3
        pygame.mixer.init()
        
        self.languages = {
            'العربية': {'code': 'ar-EG', 'tts_code': 'ar'},
            'English': {'code': 'en-US', 'tts_code': 'en'},
            'Türkçe': {'code': 'tr-TR', 'tts_code': 'tr'},
            'Français': {'code': 'fr-FR', 'tts_code': 'fr'},
            'Deutsch': {'code': 'de-DE', 'tts_code': 'de'},
            'Español': {'code': 'es-ES', 'tts_code': 'es'}
        }
        
        self.common_phrases = {
            'العربية': ["", "لا", "أحتاج مساعدة", "أشعر بالتعب", "أريد الماء", "شكراً لك"],
            'English': ["Yes", "No", "I need help", "I'm tired", "I want water", "Thank you"],
            'Türkçe': ["Evet", "Hayır", "Yardıma ihtiyacım var", "Yorgunum", "Su istiyorum", "Teşekkür ederim"]
        }
        
        self.current_language = 'العربية'
        self.translation_language = 'tr'
    def setup_gui(self):
        self.window = tk.Tk()
        self.window.title(" حسام فضل قدور")
        self.window.geometry("1200x800")
        
        style = ttk.Style()
        style.configure('Custom.TButton', padding=5)
        
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        self.create_audio_settings(main_frame)
        self.create_language_settings(main_frame)
        self.create_phrase_buttons(main_frame)
        self.create_text_area(main_frame)
        self.create_control_buttons(main_frame)
        
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        
    def create_audio_settings(self, parent):
        audio_frame = ttk.LabelFrame(parent, text="إعدادات الصوت", padding="5")
        audio_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky="ew")
        
        ttk.Label(audio_frame, text="حساسية الميكروفون:").grid(row=0, column=0, padx=5)
        self.sensitivity_scale = ttk.Scale(
            audio_frame,
            from_=100,
            to=1000,
            orient='horizontal',
            value=self.energy_threshold,
            command=self.update_sensitivity
        )
        self.sensitivity_scale.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(audio_frame, text="معدل أخذ العينات:").grid(row=1, column=0, padx=5)
        self.sample_rates = ['8000', '16000', '32000', '44100', '48000']
        self.sample_rate_var = tk.StringVar(value=str(self.sample_rate))
        sample_rate_combo = ttk.Combobox(
            audio_frame,
            textvariable=self.sample_rate_var,
            values=self.sample_rates,
            state='readonly'
        )
        sample_rate_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        sample_rate_combo.bind('<<ComboboxSelected>>', self.update_sample_rate)
        
    def create_language_settings(self, parent):
        lang_frame = ttk.LabelFrame(parent, text="إعدادات اللغة", padding="5")
        lang_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")
        
        ttk.Label(lang_frame, text="لغة التحدث:").grid(row=0, column=0, padx=5)
        self.language_var = tk.StringVar(value=self.current_language)
        language_menu = ttk.Combobox(
            lang_frame,
            textvariable=self.language_var,
            values=list(self.languages.keys()),
            state='readonly'
        )
        language_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        language_menu.bind('<<ComboboxSelected>>', self.change_language)
        
        ttk.Label(lang_frame, text="لغة الترجمة:").grid(row=1, column=0, padx=5)
        self.translation_var = tk.StringVar(value=self.translation_language)
        translation_menu = ttk.Combobox(
            lang_frame,
            textvariable=self.translation_var,
            values=[lang['tts_code'] for lang in self.languages.values()],
            state='readonly'
        )
        translation_menu.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
    def create_phrase_buttons(self, parent):
        self.phrases_frame = ttk.LabelFrame(parent, text="العبارات الشائعة", padding="5")
        self.phrases_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        self.update_phrase_buttons()
        
    def create_text_area(self, parent):
        text_frame = ttk.LabelFrame(parent, text="النص والترجمة", padding="5")
        text_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky="nsew")
        
        self.text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, width=70, height=15)
        self.text_area.pack(fill="both", expand=True)
        
    def create_control_buttons(self, parent):
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=4, column=0, columnspan=2, pady=5)
        
        self.record_button = ttk.Button(
            control_frame,
            text="بدء التسجيل",
            command=self.toggle_recording,
            style='Custom.TButton'
        )
        self.record_button.pack(side="left", padx=5)
        
        ttk.Button(
            control_frame,
            text="ترجمة النص",
            command=self.translate_text,
            style='Custom.TButton'
        ).pack(side="left", padx=5)
        
        ttk.Button(
            control_frame,
            text="مسح النص",
            command=self.clear_text,
            style='Custom.TButton'
        ).pack(side="left", padx=5)
        
        self.status_label = ttk.Label(parent, text="جاهز للتسجيل")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=5)
    def update_sensitivity(self, value):
        self.energy_threshold = int(float(value))
        self.recognizer.energy_threshold = self.energy_threshold

    def update_sample_rate(self, event=None):
        self.sample_rate = int(self.sample_rate_var.get())

    def change_language(self, event=None):
        self.current_language = self.language_var.get()
        self.update_phrase_buttons()

    def update_phrase_buttons(self):
        for widget in self.phrases_frame.winfo_children():
            widget.destroy()

        phrases = self.common_phrases.get(self.current_language, [])
        for i, phrase in enumerate(phrases):
            btn = ttk.Button(
                self.phrases_frame,
                text=phrase,
                command=lambda p=phrase: self.speak_phrase(p),
                style='Custom.TButton'
            )
            btn.grid(row=i//3, column=i%3, padx=5, pady=5, sticky="ew")

    def speak_phrase(self, phrase):
        lang_code = self.languages[self.current_language]['tts_code']
        self.text_to_speech(phrase, lang_code)
        self.append_text(f"\n{phrase}\n")

    def text_to_speech(self, text, lang_code):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"speech_{timestamp}.mp3"
            
            # محاولات متعددة لحذف الملف القديم
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    if os.path.exists(filename):
                        pygame.mixer.music.unload()
                        os.remove(filename)
                    break
                except Exception:
                    time.sleep(0.5)
                    continue
            
            # إنشاء وحفظ الملف الصوتي
            tts = gTTS(text=text, lang=lang_code)
            tts.save(filename)
            
            # تشغيل الصوت
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            
            # انتظار انتهاء التشغيل
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # تنظيف الملفات
            pygame.mixer.music.unload()
            if os.path.exists(filename):
                os.remove(filename)
                
        except Exception as e:
            self.append_text(f"خطأ في تحويل النص إلى كلام: {str(e)}\n")

    def toggle_recording(self):
        if not self.recording:
            self.recording = True
            self.record_button.configure(text="إيقاف التسجيل")
            self.status_label.configure(text="جاري التسجيل...")
            threading.Thread(target=self.recording_thread, daemon=True).start()
        else:
            self.recording = False
            self.record_button.configure(text="بدء التسجيل")
            self.status_label.configure(text="تم إيقاف التسجيل")

    def recording_thread(self):
        while self.recording:
            self.status_label.configure(text="جاري التسجيل والاستماع...")
            audio_data = self.record_chunk()
            
            if audio_data is not None:
                text = self.process_audio(audio_data)
                if text:
                    self.append_text(f"\n--- النص المسجل ---\n{text}\n")
                    self.save_text(f"النص المسجل: {text}\n")
                    self.handle_command(text)
            
            time.sleep(0.1)
        
        self.status_label.configure(text="جاهز للتسجيل")
    def record_chunk(self):
        try:
            audio = sd.rec(
                int(self.duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.int16
            )
            sd.wait()
            return audio
        except Exception as e:
            self.append_text(f"خطأ في التسجيل: {str(e)}\n")
            return None

    def process_audio(self, audio_data):
        try:
            audio_segment = sr.AudioData(
                audio_data.tobytes(),
                self.sample_rate,
                audio_data.dtype.itemsize
            )
            lang_code = self.languages[self.current_language]['code']
            return self.recognizer.recognize_google(
                audio_segment,
                language=lang_code
            ).lower()
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            self.append_text("خطأ في الاتصال بخدمة التعرف على الصوت\n")
            return None

    def translate_text(self):
        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            self.append_text("لا يوجد نص للترجمة\n")
            return

        target_lang = self.translation_var.get()
        try:
            translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
            self.append_text(f"\n--- الترجمة ({target_lang}) ---\n{translated}\n")
            self.save_text(f"النص المترجم: {translated}\n")
        except Exception as e:
            self.append_text(f"خطأ في الترجمة: {str(e)}\n")

    def handle_command(self, text):
        if "توقف" in text.lower():
            self.recording = False
            self.window.after(0, lambda: self.record_button.configure(text="بدء التسجيل"))
        elif "مسح" in text.lower():
            self.window.after(0, self.clear_text)
        elif "خروج" in text.lower():
            self.window.after(0, self.window.quit)

    def append_text(self, text):
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)

    def clear_text(self):
        self.text_area.delete("1.0", tk.END)

    def save_text(self, text):
        filename = "assistant_log.txt"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(filename, "a", encoding="utf-8") as file:
            file.write(f"[{timestamp}] {text}\n")

    def run(self):
        self.window.mainloop()

def main():
    app = EnhancedMultilingualAssistant()
    app.run()

if __name__ == "__main__":
    main()        