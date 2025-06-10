import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import logging
from typing import Optional, Dict, Any, List

# Импорт модулей проекта
from autokaraoke.audio_processor import AudioProcessor
from autokaraoke.text_recognizer import TextRecognizer
from autokaraoke.karaoke_generator import KaraokeGenerator
from autokaraoke.utils import (
    check_ffmpeg,
    get_temp_directory,
    create_directory_if_not_exists,
    is_audio_file,
    is_video_file,
    get_file_extension
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AutoKaraoke")

class Application(tk.Tk):

   #  Главный класс приложения AutoKaraoke.


    def __init__(self):

        # Инициализация приложения.

        super().__init__()

        self.title("AutoKaraoke")
        self.geometry("800x600")
        self.minsize(800, 600)

        # Настройка внешнего вида
        self.configure(bg='#f0f0f0')
        self.option_add('*Font', 'Helvetica 11')

        # Переменные для путей файлов и опций
        self.input_path = tk.StringVar()
        self.output_directory = tk.StringVar(value=os.path.expanduser("~/Documents/AutoKaraoke"))
        self.output_filename = tk.StringVar()
        self.model_name = tk.StringVar(value="base")
        self.language = tk.StringVar(value="auto")
        self.include_vocal = tk.BooleanVar(value=False)
        self.vocal_volume = tk.DoubleVar(value=0.3)
        self.create_visualization = tk.BooleanVar(value=True)

        # Создание директории для выходных файлов
        create_directory_if_not_exists(self.output_directory.get())

        # Проверка зависимостей
        self._check_dependencies()

        # Создание UI
        self._create_widgets()

        logger.info("Приложение AutoKaraoke инициализировано")

    def _check_dependencies(self):

       #  Проверка необходимых зависимостей.

        # Проверка наличия FFmpeg
        if not check_ffmpeg():
            messagebox.showerror(
                "Ошибка зависимостей",
                "FFmpeg не найден в системе. Пожалуйста, установите FFmpeg и перезапустите приложение."
            )
            logger.error("FFmpeg не найден в системе")
            sys.exit(1)

    def _create_widgets(self):

        # Создание элементов интерфейса.

        # Главный контейнер
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        title_label = ttk.Label(
            main_frame,
            text="AutoKaraoke",
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Рамка для выбора файлов
        file_frame = ttk.LabelFrame(main_frame, text="Выбор файлов", padding="10")
        file_frame.pack(fill=tk.X, padx=5, pady=5)

        # Выбор входного файла
        input_frame = ttk.Frame(file_frame)
        input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(input_frame, text="Входной файл:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(input_frame, textvariable=self.input_path, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(input_frame, text="Обзор...", command=self._select_file).pack(side=tk.LEFT, padx=5)

        # Выбор выходной директории
        output_frame = ttk.Frame(file_frame)
        output_frame.pack(fill=tk.X, pady=5)

        ttk.Label(output_frame, text="Выходная директория:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(output_frame, textvariable=self.output_directory, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Обзор...", command=self._select_output).pack(side=tk.LEFT, padx=5)

        # Имя выходного файла
        output_name_frame = ttk.Frame(file_frame)
        output_name_frame.pack(fill=tk.X, pady=5)

        ttk.Label(output_name_frame, text="Имя выходного файла:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(output_name_frame, textvariable=self.output_filename, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Рамка для настроек
        settings_frame = ttk.LabelFrame(main_frame, text="Настройки", padding="10")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)

        # Выбор модели Whisper
        model_frame = ttk.Frame(settings_frame)
        model_frame.pack(fill=tk.X, pady=5)

        ttk.Label(model_frame, text="Модель:").pack(side=tk.LEFT, padx=5)
        models = ["tiny", "base", "small", "medium", "large"]
        model_menu = ttk.OptionMenu(model_frame, self.model_name, self.model_name.get(), *models)
        model_menu.pack(side=tk.LEFT, padx=5)

        # Выбор языка
        lang_frame = ttk.Frame(settings_frame)
        lang_frame.pack(fill=tk.X, pady=5)

        ttk.Label(lang_frame, text="Язык:").pack(side=tk.LEFT, padx=5)
        languages = ["auto", "ru", "en", "fr", "de", "es", "it", "ja", "ko", "zh", "pt", "nl"]
        lang_menu = ttk.OptionMenu(lang_frame, self.language, self.language.get(), *languages)
        lang_menu.pack(side=tk.LEFT, padx=5)

        # Включение оригинального вокала
        vocal_frame = ttk.Frame(settings_frame)
        vocal_frame.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(
            vocal_frame,
            text="Включить оригинальный вокал",
            variable=self.include_vocal,
            onvalue=True,
            offvalue=False
        ).pack(side=tk.LEFT, padx=5)

        # Регулировка громкости вокала
        volume_frame = ttk.Frame(settings_frame)
        volume_frame.pack(fill=tk.X, pady=5)

        ttk.Label(volume_frame, text="Громкость вокала:").pack(side=tk.LEFT, padx=5)
        ttk.Scale(
            volume_frame,
            from_=0.0,
            to=1.0,
            variable=self.vocal_volume,
            orient=tk.HORIZONTAL,
            length=200
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Визуализация аудио
        viz_frame = ttk.Frame(settings_frame)
        viz_frame.pack(fill=tk.X, pady=5)

        ttk.Checkbutton(
            viz_frame,
            text="Создать визуализацию аудио",
            variable=self.create_visualization,
            onvalue=True,
            offvalue=False
        ).pack(side=tk.LEFT, padx=5)

        # Индикатор прогресса
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, padx=5, pady=10)

        self.progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, pady=5)

        self.status_label = ttk.Label(progress_frame, text="Готово к созданию караоке")
        self.status_label.pack(fill=tk.X, pady=5)

        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            button_frame,
            text="Создать караоке",
            command=self._start_process,
            style="Accent.TButton"
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            button_frame,
            text="Выход",
            command=self.quit
        ).pack(side=tk.RIGHT, padx=5)

        # Создание стилей
        self._setup_styles()

    def _setup_styles(self):

        # Настройка стилей для элементов интерфейса.

        style = ttk.Style()

        # Стили для кнопок
        style.configure("TButton", padding=6)
        style.configure("Accent.TButton", background="#007bff", foreground="white")

        # Стили для полей ввода
        style.configure("TEntry", padding=5)

        # Стили для выпадающих списков
        style.configure("TOptionMenu", padding=5)

    def _select_file(self):

        # Обработчик для выбора входного файла.

        filetypes = [
            ("Аудио и видео файлы", "*.mp3 *.wav *.flac *.ogg *.mp4 *.mkv *.avi *.mov"),
            ("Аудио файлы", "*.mp3 *.wav *.flac *.ogg"),
            ("Видео файлы", "*.mp4 *.mkv *.avi *.mov"),
            ("Все файлы", "*.*")
        ]

        file_path = filedialog.askopenfilename(
            title="Выберите аудио или видео файл",
            filetypes=filetypes
        )

        if file_path:
            self.input_path.set(file_path)

            # Автоматически заполняем имя выходного файла
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.output_filename.set(f"{base_name}_karaoke.mp4")

            logger.info(f"Выбран входной файл: {file_path}")

    def _select_output(self):

        # Обработчик для выбора выходной директории.

        directory = filedialog.askdirectory(
            title="Выберите директорию для сохранения"
        )

        if directory:
            self.output_directory.set(directory)
            create_directory_if_not_exists(directory)
            logger.info(f"Выбрана выходная директория: {directory}")

    def _start_process(self):

        # Начинает процесс создания караоке в отдельном потоке.

        if not self.input_path.get():
            messagebox.showerror("Ошибка", "Выберите входной файл!")
            return

        if not os.path.exists(self.input_path.get()):
            messagebox.showerror("Ошибка", "Указанный входной файл не существует!")
            return

        if not self.output_filename.get():
            messagebox.showerror("Ошибка", "Укажите имя выходного файла!")
            return

        # Запуск обработки в отдельном потоке
        threading.Thread(target=self._process_file, daemon=True).start()

    def _process_file(self):

        # Процесс обработки файла и создания караоке-видео.

        try:
            # Обновление интерфейса
            self.status_label.config(text="Начало обработки...")
            self.progress['value'] = 0
            self.update_idletasks()
            
            input_path = self.input_path.get()
            output_dir = self.output_directory.get()
            output_filename = self.output_filename.get()
            output_path = os.path.join(output_dir, output_filename)
            
            # Создание экземпляров классов для обработки
            audio_processor = AudioProcessor()
            
            # Если выбран язык "auto", устанавливаем None для автоопределения
            language = None if self.language.get() == "auto" else self.language.get()
            text_recognizer = TextRecognizer(
                model_name=self.model_name.get(),
                language=language
            )
            
            karaoke_generator = KaraokeGenerator()
            
            # 1. Если входной файл - видео, извлекаем аудио
            self.status_label.config(text="Подготовка аудио...")
            self.progress['value'] = 10
            self.update_idletasks()
            
            audio_path = input_path
            if is_video_file(input_path):
                logger.info("Извлечение аудио из видео...")
                audio_path = audio_processor.extract_audio_from_video(input_path)
            
            # 2. Разделение аудио на вокал и музыку
            self.status_label.config(text="Отделение вокала от музыки...")
            self.progress['value'] = 20
            self.update_idletasks()
            
            logger.info("Разделение аудио на вокал и инструменты...")
            separated_audio = audio_processor.extract_vocals(audio_path)
            
            # Проверка результатов разделения
            vocals_path = separated_audio.get("vocals")
            instrumental_path = separated_audio.get("instrumental")
            
            if not vocals_path or not instrumental_path:
                raise RuntimeError("Не удалось разделить аудио на вокал и инструменты")
            
            # 3. Распознавание текста из вокала
            self.status_label.config(text="Распознавание текста песни...")
            self.progress['value'] = 40
            self.update_idletasks()
            
            logger.info("Распознавание текста из вокала...")
            result = text_recognizer.recognize_speech(vocals_path)
            
            # 4. Создание файла синхронизации
            self.status_label.config(text="Создание файла синхронизации...")
            self.progress['value'] = 60
            self.update_idletasks()
            
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            lrc_path = os.path.join(output_dir, f"{base_name}.lrc")
            srt_path = os.path.join(output_dir, f"{base_name}.srt")
            
            logger.info("Создание файлов синхронизации...")
            text_recognizer.create_synchronization(result, lrc_path)
            text_recognizer.create_srt_subtitles(result, srt_path)
            
            # 5. Подготовка аудио для караоке
            self.status_label.config(text="Подготовка аудио дорожки...")
            self.progress['value'] = 70
            self.update_idletasks()
            
            audio_for_karaoke = instrumental_path
            
            # Если нужно включить оригинальный вокал
            if self.include_vocal.get():
                logger.info("Добавление оригинального вокала с уменьшенной громкостью...")
                
                # Регулируем громкость вокала
                adjusted_vocals = audio_processor.adjust_audio_volume(
                    vocals_path, 
                    self.vocal_volume.get()
                )
                
                # Смешиваем инструментал и вокал с пониженной громкостью
                audio_for_karaoke = audio_processor.mix_audio_files(
                    instrumental_path,
                    adjusted_vocals,
                    volume_1=1.0,
                    volume_2=self.vocal_volume.get()
                )
            
            # 6. Создание караоке-видео
            self.status_label.config(text="Создание караоке-видео...")
            self.progress['value'] = 80
            self.update_idletasks()
            
            logger.info("Создание караоке-видео...")
            
            # Определяем, нужно ли создавать визуализацию
            create_visualization = self.create_visualization.get()
            
            # Создаем караоке-видео
            karaoke_video_path = karaoke_generator.create_karaoke_video(
                audio_for_karaoke,
                result,
                output_path=output_path,
                create_visualization=create_visualization
            )
            
            # Готово!
            self.status_label.config(text=f"Караоке успешно создано: {output_filename}")
            self.progress['value'] = 100
            self.update_idletasks()
            
            # Показываем сообщение об успешном завершении
            messagebox.showinfo(
                "Готово!",
                f"Караоке успешно создано и сохранено в:\\n{output_path}"
            )
            
            logger.info(f"Караоке успешно создано: {output_path}")
            
        except Exception as e:
            logger.error(f"Ошибка при создании караоке: {str(e)}", exc_info=True)
            
            # Показываем сообщение об ошибке
            messagebox.showerror(
                "Ошибка",
                f"Произошла ошибка при создании караоке:\\n{str(e)}"
            )
            
            self.status_label.config(text=f"Ошибка: {str(e)}")
            self.progress['value'] = 0
            self.update_idletasks()

def main():

    # Основная функция для запуска приложения.

    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()
