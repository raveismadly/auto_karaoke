# Создаем main.py
with open('main.py', 'w') as f:
    f.write('''
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import logging
from pathlib import Path
import time

from audio_processor import AudioProcessor
from text_recognizer import TextRecognizer
from karaoke_generator import KaraokeGenerator
from utils import check_ffmpeg, is_audio_file, is_video_file, get_temp_directory, clean_filename

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("autokaraoke.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Application(tk.Tk):
    """
    Основное приложение для создания караоке
    """
    
    def __init__(self):
        """
        Инициализация приложения
        """
        super().__init__()
        
        # Проверяем наличие FFmpeg
        if not check_ffmpeg():
            messagebox.showerror(
                "Ошибка", 
                "FFmpeg не найден в системе! Установите FFmpeg для работы с приложением."
            )
            sys.exit(1)
        
        # Инициализируем классы для обработки
        self.audio_processor = AudioProcessor()
        self.text_recognizer = TextRecognizer("small")  # Можно изменить на "medium" для лучшего распознавания
        self.karaoke_generator = KaraokeGenerator()
        
        # Настройка окна приложения
        self.title("AutoKaraoke - Генератор караоке для macOS")
        self.geometry("800x600")
        self.resizable(True, True)
        
        # Переменные
        self.file_path = tk.StringVar()
        self.output_path = tk.StringVar(value=os.path.expanduser("~/Movies/AutoKaraoke"))
        self.status = tk.StringVar(value="Готов к работе")
        self.progress = tk.DoubleVar(value=0.0)
        self.language = tk.StringVar(value="ru")
        self.include_original_vocals = tk.BooleanVar(value=False)
        self.create_visualization = tk.BooleanVar(value=True)
        self.background_video_path = tk.StringVar()
        
        # Создаем интерфейс
        self._create_widgets()
        
        # Задаём значения для выпадающего списка языков
        self.language_dropdown['values'] = [
            "ru", "en", "es", "fr", "de", "it", "ja", "ko", "pt", "zh"
        ]
        self.language_dropdown.current(0)  # По умолчанию русский
        
        logger.info("Приложение AutoKaraoke запущено")
    
    def _create_widgets(self):
        """
        Создание элементов интерфейса
        """
        # Основной фрейм с отступами
        main_frame = ttk.Frame(self, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="AutoKaraoke", font=("Arial", 24))
        title_label.pack(pady=10)
        
        # Описание
        desc_label = ttk.Label(main_frame, text="Создавайте караоке из любой музыки автоматически!")
        desc_label.pack(pady=5)
        
        # Фрейм для выбора файла
        file_frame = ttk.LabelFrame(main_frame, text="Входной файл", padding="10 10 10 10")
        file_frame.pack(fill=tk.X, pady=10)
        
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=50)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        file_button = ttk.Button(file_frame, text="Выбрать файл", command=self._select_file)
        file_button.pack(side=tk.RIGHT)
        
        # Фрейм для выбора директории сохранения
        output_frame = ttk.LabelFrame(main_frame, text="Выходная директория", padding="10 10 10 10")
        output_frame.pack(fill=tk.X, pady=10)
        
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path, width=50)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        output_button = ttk.Button(output_frame, text="Выбрать директорию", command=self._select_output)
        output_button.pack(side=tk.RIGHT)
        
        # Фрейм для настроек
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки", padding="10 10 10 10")
        settings_frame.pack(fill=tk.X, pady=10)
        
        # Язык текста
        language_label = ttk.Label(settings_frame, text="Язык:")
        language_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.language_dropdown = ttk.Combobox(settings_frame, textvariable=self.language, width=10)
        self.language_dropdown.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Включение оригинального вокала
        vocals_check = ttk.Checkbutton(settings_frame, text="Включить оригинальный вокал", 
                                       variable=self.include_original_vocals)
        vocals_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Создание визуализации
        viz_check = ttk.Checkbutton(settings_frame, text="Создать визуализацию аудио", 
                                   variable=self.create_visualization)
        viz_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Выбор фонового видео
        bg_label = ttk.Label(settings_frame, text="Фоновое видео (опционально):")
        bg_label.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        bg_entry = ttk.Entry(settings_frame, textvariable=self.background_video_path, width=30)
        bg_entry.grid(row=3, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        bg_button = ttk.Button(settings_frame, text="Выбрать", command=self._select_background)
        bg_button.grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        
        # Настройки для сетки
        settings_frame.columnconfigure(1, weight=1)
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Кнопка создания караоке
        generate_button = ttk.Button(button_frame, text="Создать караоке", command=self._start_process)
        generate_button.pack(side=tk.RIGHT, padx=5)
        
        # Статус и прогресс
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        status_label = ttk.Label(status_frame, textvariable=self.status)
        status_label.pack(anchor=tk.W, pady=5)
        
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress, length=300, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Логи
        log_frame = ttk.LabelFrame(main_frame, text="Логи", padding="10 10 10 10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD, bg='#f0f0f0')
        self.log_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text.config(yscrollcommand=scrollbar.set)
        self.log_text.configure(state='disabled')  # Запрещаем редактирование
        
        # Добавляем обработчик для перенаправления логов в текстовое поле
        self._setup_log_redirect()
    
    def _setup_log_redirect(self):
        """
        Настраивает перенаправление логов в текстовое поле
        """
        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                logging.Handler.__init__(self)
                self.text_widget = text_widget
            
            def emit(self, record):
                msg = self.format(record)
                
                def append():
                    self.text_widget.configure(state='normal')
                    self.text_widget.insert(tk.END, msg + '\\n')
                    self.text_widget.configure(state='disabled')
                    self.text_widget.see(tk.END)
                
                self.text_widget.after(0, append)
        
        text_handler = TextHandler(self.log_text)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Добавляем обработчик к корневому логгеру
        root_logger = logging.getLogger()
        root_logger.addHandler(text_handler)
    
    def _select_file(self):
        """
        Открывает диалог выбора файла и устанавливает выбранный путь
        """
        file_types = [
            ("Аудио и видео файлы", "*.mp3 *.wav *.flac *.aac *.m4a *.ogg *.mp4 *.mkv *.avi *.mov"),
            ("Аудио файлы", "*.mp3 *.wav *.flac *.aac *.m4a *.ogg"),
            ("Видео файлы", "*.mp4 *.mkv *.avi *.mov"),
            ("Все файлы", "*.*"),
        ]
        
        file_path = filedialog.askopenfilename(
            title="Выберите аудио или видео файл",
            filetypes=file_types
        )
        
        if file_path:
            self.file_path.set(file_path)
            logger.info(f"Выбран файл: {file_path}")
    
    def _select_output(self):
        """
        Открывает диалог выбора директории сохранения
        """
        output_dir = filedialog.askdirectory(
            title="Выберите директорию для сохранения караоке"
        )
        
        if output_dir:
            self.output_path.set(output_dir)
            logger.info(f"Выбрана директория для сохранения: {output_dir}")
    
    def _select_background(self):
        """
        Открывает диалог выбора фонового видео
        """
        file_types = [
            ("Видео файлы", "*.mp4 *.mkv *.avi *.mov *.webm"),
            ("Все файлы", "*.*")
        ]
        
        bg_path = filedialog.askopenfilename(
            title="Выберите фоновое видео",
            filetypes=file_types
        )
        
        if bg_path:
            self.background_video_path.set(bg_path)
            logger.info(f"Выбрано фоновое видео: {bg_path}")
    
    def _update_progress(self, value, status_text=None):
        """
        Обновляет индикатор прогресса и статус
        
        Args:
            value: значение прогресса от 0.0 до 100.0
            status_text: текст статуса (если None, оставляется текущее значение)
        """
        self.progress.set(value)
        if status_text:
            self.status.set(status_text)
        
        # Обновляем интерфейс принудительно
        self.update_idletasks()
    
    def _start_process(self):
        """
        Запускает процесс создания караоке в отдельном потоке
        """
        # Проверяем наличие входного файла
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror("Ошибка", "Выберите входной аудио или видео файл!")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("Ошибка", f"Файл не найден: {file_path}")
            return
        
        # Проверяем корректность типа файла
        if not (is_audio_file(file_path) or is_video_file(file_path)):
            messagebox.showerror("Ошибка", "Выбранный файл не является аудио или видео файлом!")
            return
        
        # Проверяем директорию для сохранения
        output_path = self.output_path.get()
        if not output_path:
            messagebox.showerror("Ошибка", "Выберите директорию для сохранения!")
            return
        
        # Создаем директорию, если она не существует
        if not os.path.exists(output_path):
            try:
                os.makedirs(output_path)
            except OSError as e:
                messagebox.showerror("Ошибка", f"Не удалось создать директорию: {str(e)}")
                return
        
        # Проверяем права на запись в директорию
        if not os.access(output_path, os.W_OK):
            messagebox.showerror("Ошибка", f"Нет прав на запись в директорию: {output_path}")
            return
        
        # Проверяем фоновое видео, если указано
        bg_video_path = self.background_video_path.get()
        if bg_video_path and not os.path.exists(bg_video_path):
            messagebox.showerror("Ошибка", f"Фоновое видео не найдено: {bg_video_path}")
            return
        
        # Запускаем обработку в отдельном потоке
        self._update_progress(0, "Запуск процесса...")
        
        thread = threading.Thread(target=self._process_file)
        thread.daemon = True
        thread.start()
    
    def _process_file(self):
        """
        Обрабатывает выбранный файл и создает караоке
        """
        try:
            file_path = self.file_path.get()
            output_dir = self.output_path.get()
            language = self.language.get()
            include_vocals = self.include_original_vocals.get()
            create_viz = self.create_visualization.get()
            bg_video_path = self.background_video_path.get() if self.background_video_path.get() else None
            
            # Определяем имя выходного файла
            file_name = os.path.basename(file_path)
            file_base_name = os.path.splitext(file_name)[0]
            file_base_name = clean_filename(file_base_name)
            output_file = os.path.join(output_dir, f"{file_base_name}_karaoke.mp4")
            
            logger.info(f"Начинаем обработку файла: {file_path}")
            self._update_progress(5, "Подготовка...")
            
            # Если файл - видео, извлекаем аудио
            audio_path = file_path
            if is_video_file(file_path):
                logger.info("Извлечение аудио из видео...")
                self._update_progress(10, "Извлечение аудио из видео...")
                audio_path = self.audio_processor.extract_audio_from_video(file_path)
            
            # Отделяем вокал от музыки
            logger.info("Отделение вокала от музыки...")
            self._update_progress(15, "Отделение вокала от музыки...")
            vocals_path, accompaniment_path = self.audio_processor.extract_vocals(audio_path)
            
            # Распознаем текст из вокала
            logger.info(f"Распознавание текста на языке: {language}...")
            self._update_progress(30, "Распознавание текста...")
            recognition_result = self.text_recognizer.recognize_speech(vocals_path, language=language)
            
            # Сохраняем текст песни
            lyrics_path = os.path.join(output_dir, f"{file_base_name}_lyrics.txt")
            self.text_recognizer.save_lyrics(recognition_result, lyrics_path)
            
            # Создаем файл синхронизации
            sync_path = os.path.join(output_dir, f"{file_base_name}_sync.lrc")
            self.text_recognizer.create_synchronization(recognition_result, sync_path)
            
            # Создаем субтитры SRT
            srt_path = os.path.join(output_dir, f"{file_base_name}_subtitles.srt")
            self.text_recognizer.create_srt_subtitles(recognition_result, srt_path)
            
            # Подготавливаем аудио для караоке
            logger.info("Подготовка аудио для караоке...")
            self._update_progress(50, "Подготовка аудио...")
            
            if include_vocals:
                # Смешиваем вокал (с уменьшенной громкостью) и аккомпанемент
                logger.info("Смешивание вокала и аккомпанемента...")
                reduced_vocals = self.audio_processor.adjust_audio_volume(vocals_path, 0.5)
                karaoke_audio = self.audio_processor.mix_audio_files(
                    accompaniment_path, reduced_vocals, volume1=1.0, volume2=0.5
                )
            else:
                # Используем только аккомпанемент
                karaoke_audio = accompaniment_path
            
            # Подготавливаем фоновое видео, если нужно
            background_video = None
            if create_viz and not bg_video_path:
                logger.info("Создание фонового видео с визуализацией аудио...")
                self._update_progress(60, "Создание визуализации аудио...")
                
                # Получаем длительность аудио
                import librosa
                duration = librosa.get_duration(path=karaoke_audio)
                
                # Создаем визуализацию
                background_video = self.karaoke_generator.create_background_video_with_audio_visualization(
                    karaoke_audio, duration
                )
            else:
                background_video = bg_video_path
            
            # Создаем караоке-видео
            logger.info("Создание караоке-видео...")
            self._update_progress(75, "Создание караоке-видео...")
            karaoke_video = self.karaoke_generator.create_karaoke_video(
                karaoke_audio, recognition_result, output_file, background_video
            )
            
            logger.info(f"Караоке-видео создано успешно: {karaoke_video}")
            self._update_progress(100, "Готово!")
            
            # Показываем сообщение об успешном завершении
            messagebox.showinfo(
                "Готово", 
                f"Караоке создано успешно!\\n\\nФайл: {karaoke_video}\\n\\n"
                f"Текст песни: {lyrics_path}\\n"
                f"Файл синхронизации: {sync_path}\\n"
                f"Субтитры: {srt_path}"
            )
            
        except Exception as e:
            logger.error(f"Ошибка при создании караоке: {str(e)}", exc_info=True)
            self._update_progress(0, "Произошла ошибка!")
            messagebox.showerror("Ошибка", f"Произошла ошибка при создании караоке:\\n{str(e)}")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
''')

