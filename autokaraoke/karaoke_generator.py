import os
import logging
import numpy as np
import tempfile
from typing import Dict, List, Optional, Tuple, Union, Any
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    VideoClip, 
    AudioFileClip, 
    VideoFileClip,
    TextClip, 
    CompositeVideoClip, 
    ColorClip,
    clips_array
)
import matplotlib.pyplot as plt

# Импорт вспомогательных функций
from autokaraoke.utils import (
    get_temp_directory,
    create_directory_if_not_exists,
    clean_filename,
    get_base_filename
)

logger = logging.getLogger(__name__)

class KaraokeGenerator:
#     \"\"\"
#     Класс для создания караоке-видео с синхронизированным текстом.
#     \"\"\"
    
    def __init__(
        self,
        font_path: Optional[str] = None,
        font_size: int = 36,
        text_color: str = "white",
        highlight_color: str = "yellow",
        output_dir: Optional[str] = None
    ):
#         \"\"\"
#         Инициализация генератора караоке.
#
#         Args:
#             font_path (str, optional): Путь к файлу шрифта
#             font_size (int): Размер шрифта
#             text_color (str): Цвет обычного текста
#             highlight_color (str): Цвет выделенного текста
#             output_dir (str, optional): Директория для выходных файлов
#         \"\"\"
        self.font_size = font_size
        self.text_color = text_color
        self.highlight_color = highlight_color
        
        if output_dir is None:
            self.output_dir = os.path.join(get_temp_directory(), "karaoke")
        else:
            self.output_dir = output_dir
            
        create_directory_if_not_exists(self.output_dir)
        
        # Использование системного шрифта, если не указан специфический
        if font_path is None:
            # Пытаемся использовать стандартный шрифт
            system_fonts = [
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
                "/System/Library/Fonts/Arial.ttf",      # Другой вариант для macOS
                "/Library/Fonts/Arial.ttf",             # Еще один вариант для macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                "C:\\Windows\\Fonts\\arial.ttf"         # Windows
            ]
            
            for font in system_fonts:
                if os.path.exists(font):
                    self.font_path = font
                    break
            else:
                # Если не нашли системный шрифт, используем дефолтный из PIL
                self.font_path = None
                logger.warning("Не удалось найти системный шрифт. Будет использоваться шрифт по умолчанию.")
        else:
            self.font_path = font_path
        
        logger.info(f"KaraokeGenerator инициализирован. Шрифт: {self.font_path}, размер: {font_size}")
    
    def generate_lyrics_frames(
        self, 
        recognition_result: Dict[str, Any],
        width: int = 1280,
        height: int = 720,
        background_color: Tuple[int, int, int] = (0, 0, 0)
    ) -> Dict[float, np.ndarray]:
#         \"\"\"
#         Генерирует кадры с текстом для караоке.
#
#         Args:
#             recognition_result (Dict[str, Any]): Результат распознавания текста
#             width (int): Ширина кадра
#             height (int): Высота кадра
#             background_color (Tuple[int, int, int]): Цвет фона (RGB)
#
#         Returns:
#             Dict[float, np.ndarray]: Словарь, где ключи - временные метки, значения - кадры
#         \"\"\"
        logger.info("Генерация кадров с текстом для караоке")
        
        frames = {}
        
        if "segments" not in recognition_result or not recognition_result["segments"]:
            logger.warning("В результатах распознавания отсутствуют сегменты с текстом")
            return frames
        
        try:
            # Сортируем сегменты по времени начала
            segments = sorted(recognition_result["segments"], key=lambda s: s["start"])
            
            for i, segment in enumerate(segments):
                start_time = segment["start"]
                text = segment["text"].strip()
                
                if "words" in segment and segment["words"]:
                    # Если есть отдельные слова с таймингами
                    words = segment["words"]
                    
                    for j, word_data in enumerate(words):
                        word_time = word_data["start"]
                        word = word_data["word"].strip()
                        
                        # Создаем новый кадр с выделенным текущим словом
                        frame = self._create_text_frame(
                            segments,
                            i,  # индекс текущего сегмента
                            j if j < len(words) else -1,  # индекс текущего слова или -1
                            width,
                            height,
                            background_color
                        )
                        
                        frames[word_time] = frame
                
                else:
                    # Если нет отдельных слов, создаем кадр для всего сегмента
                    frame = self._create_text_frame(
                        segments,
                        i,  # индекс текущего сегмента
                        -1,  # нет выделенного слова
                        width,
                        height,
                        background_color
                    )
                    
                    frames[start_time] = frame
            
            logger.info(f"Сгенерировано {len(frames)} кадров")
            return frames
            
        except Exception as e:
            logger.error(f"Ошибка при генерации кадров с текстом: {str(e)}")
            raise
    
    def _create_text_frame(
        self,
        segments: List[Dict[str, Any]],
        current_segment_index: int,
        current_word_index: int,
        width: int,
        height: int,
        background_color: Tuple[int, int, int]
    ) -> np.ndarray:
#         \"\"\"
#         Создает один кадр с текстом.
#
#         Args:
#             segments (List[Dict]): Список сегментов
#             current_segment_index (int): Индекс текущего сегмента
#             current_word_index (int): Индекс текущего слова
#             width (int): Ширина кадра
#             height (int): Высота кадра
#             background_color (Tuple[int, int, int]): Цвет фона (RGB)
#
#         Returns:
#             np.ndarray: Массив изображения кадра
#         \"\"\"
        # Создаем пустое изображение
        image = Image.new('RGB', (width, height), color=background_color)
        draw = ImageDraw.Draw(image)
        
        # Загружаем шрифт
        if self.font_path:
            try:
                font = ImageFont.truetype(self.font_path, self.font_size)
            except Exception:
                font = ImageFont.load_default()
        else:
            font = ImageFont.load_default()
        
        # Определяем положение текста
        y_position = height // 2 - self.font_size
        
        # Показываем текущий сегмент и 1-2 следующих
        num_segments = len(segments)
        segments_to_show = []
        
        # Текущий сегмент
        if 0 <= current_segment_index < num_segments:
            segments_to_show.append({
                "text": segments[current_segment_index]["text"],
                "is_current": True,
                "current_word_index": current_word_index
            })
        
        # 1-2 следующих сегмента
        for i in range(1, 3):
            next_index = current_segment_index + i
            if next_index < num_segments:
                segments_to_show.append({
                    "text": segments[next_index]["text"],
                    "is_current": False,
                    "current_word_index": -1
                })
        
        # Отрисовываем каждый сегмент
        for i, segment_info in enumerate(segments_to_show):
            text = segment_info["text"].strip()
            is_current = segment_info["is_current"]
            segment_y = y_position + i * (self.font_size + 10)
            
            if is_current and segment_info["current_word_index"] >= 0:
                # Если есть выделенное слово, разделяем текст на слова
                words = text.split()
                
                if 0 <= segment_info["current_word_index"] < len(words):
                    # Отображаем слова с выделением текущего
                    x_position = width // 2
                    total_width = sum(draw.textlength(w + " ", font=font) for w in words)
                    start_x = x_position - total_width / 2
                    
                    for j, word in enumerate(words):
                        # Определяем цвет слова
                        if j == segment_info["current_word_index"]:
                            word_color = self.highlight_color
                        else:
                            word_color = self.text_color
                        
                        # Рисуем слово
                        draw.text((start_x, segment_y), word, fill=word_color, font=font)
                        
                        # Обновляем позицию для следующего слова
                        start_x += draw.textlength(word + " ", font=font)
                else:
                    # Если индекс слова вне диапазона, показываем весь текст
                    text_width = draw.textlength(text, font=font)
                    draw.text(
                        (width // 2 - text_width // 2, segment_y),
                        text,
                        fill=self.text_color,
                        font=font
                    )
            else:
                # Отображаем весь текст сегмента
                text_width = draw.textlength(text, font=font)
                text_color = self.highlight_color if is_current else self.text_color
                draw.text(
                    (width // 2 - text_width // 2, segment_y),
                    text,
                    fill=text_color,
                    font=font
                )
        
        # Преобразуем изображение в numpy массив
        return np.array(image)
    
    def create_karaoke_video(
        self,
        audio_path: str,
        recognition_result: Dict[str, Any],
        output_path: Optional[str] = None,
        width: int = 1280,
        height: int = 720,
        fps: int = 24,
        background_video_path: Optional[str] = None,
        create_visualization: bool = False
    ) -> str:
#         \"\"\"
#         Создает караоке-видео с синхронизированным текстом.
#
#         Args:
#             audio_path (str): Путь к аудиофайлу
#             recognition_result (Dict[str, Any]): Результат распознавания текста
#             output_path (str, optional): Путь для сохранения видео
#             width (int): Ширина видео
#             height (int): Высота видео
#             fps (int): Количество кадров в секунду
#             background_video_path (str, optional): Путь к фоновому видео
#             create_visualization (bool): Создать визуализацию аудио
#
#         Returns:
#             str: Путь к созданному видео
#         \"\"\"
        logger.info("Создание караоке-видео")
        
        if output_path is None:
            base_name = get_base_filename(audio_path)
            output_path = os.path.join(self.output_dir, f"{base_name}_karaoke.mp4")
        
        try:
            # Загружаем аудио
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            
            # Генерация кадров с текстом
            frames_dict = self.generate_lyrics_frames(
                recognition_result,
                width=width,
                height=height
            )
            
            # Создаем временные метки и соответствующие им кадры
            times = sorted(frames_dict.keys())
            frames = [frames_dict[t] for t in times]
            
            # Добавляем начальный кадр, если первая метка не с нуля
            if not times or times[0] > 0:
                # Создаем пустой начальный кадр
                initial_frame = self._create_text_frame(
                    segments=recognition_result.get("segments", []),
                    current_segment_index=-1,  # Нет активного сегмента
                    current_word_index=-1,     # Нет активного слова
                    width=width,
                    height=height,
                    background_color=(0, 0, 0)
                )
                times.insert(0, 0.0)
                frames.insert(0, initial_frame)
            
            # Функция для получения кадра в нужный момент времени
            def make_frame(t):
                # Найти индекс ближайшей временной метки, не превышающей текущее время
                idx = 0
                while idx < len(times) - 1 and times[idx + 1] <= t:
                    idx += 1
                
                return frames[idx]
            
            # Создаем видеоклип с текстом
            text_clip = VideoClip(make_frame, duration=duration)
            
            # Подготовка финального видео
            if background_video_path and os.path.exists(background_video_path):
                # Используем предоставленное фоновое видео
                logger.info(f"Используем фоновое видео: {background_video_path}")
                background_clip = VideoFileClip(background_video_path)
                
                # Обрезаем или зацикливаем видео до нужной длительности
                if background_clip.duration < duration:
                    logger.info(f"Фоновое видео короче аудио. Зацикливаем видео.")
                    background_clip = background_clip.loop(duration=duration)
                else:
                    background_clip = background_clip.subclip(0, duration)
                
                # Изменяем размер фонового видео до нужных размеров
                background_clip = background_clip.resize((width, height))
                
                # Накладываем текст на фоновое видео
                final_clip = CompositeVideoClip([background_clip, text_clip.set_opacity(0.9)])
            
            elif create_visualization:
                # Создаем визуализацию аудио как фон
                logger.info("Создание фонового видео с визуализацией аудио")
                background_path = self.create_background_video_with_audio_visualization(
                    audio_path,
                    width=width,
                    height=height,
                    fps=fps,
                    duration=duration
                )
                background_clip = VideoFileClip(background_path)
                
                # Накладываем текст на фон с визуализацией
                final_clip = CompositeVideoClip([background_clip, text_clip.set_opacity(0.9)])
            
            else:
                # Используем простой черный фон
                logger.info("Создание видео с черным фоном")
                final_clip = text_clip
            
            # Добавляем аудио к видео
            final_clip = final_clip.set_audio(audio_clip)
            
            # Сохраняем видео
            logger.info(f"Сохранение караоке-видео в файл: {output_path}")
            final_clip.write_videofile(
                output_path, 
                codec="libx264", 
                audio_codec="aac",
                fps=fps,
                preset="medium",
                threads=2
            )
            
            # Закрываем клипы
            final_clip.close()
            if 'background_clip' in locals():
                background_clip.close()
            text_clip.close()
            audio_clip.close()
            
            logger.info(f"Караоке-видео успешно создано: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка при создании караоке-видео: {str(e)}")
            raise
    
    def create_background_video_with_audio_visualization(
        self,
        audio_path: str,
        output_path: Optional[str] = None,
        width: int = 1280,
        height: int = 720,
        fps: int = 24,
        duration: Optional[float] = None
    ) -> str:
#         \"\"\"
#         Создает фоновое видео с визуализацией аудио.
#
#         Args:
#             audio_path (str): Путь к аудиофайлу
#             output_path (str, optional): Путь для сохранения видео
#             width (int): Ширина видео
#             height (int): Высота видео
#             fps (int): Количество кадров в секунду
#             duration (float, optional): Длительность видео
#
#         Returns:
#             str: Путь к созданному видео
#         \"\"\"
        logger.info(f"Создание фонового видео с визуализацией для аудио: {audio_path}")
        
        if output_path is None:
            base_name = get_base_filename(audio_path)
            output_path = os.path.join(self.output_dir, f"{base_name}_visualization.mp4")
        
        try:
            # Загружаем аудио и получаем данные
            audio_clip = AudioFileClip(audio_path)
            
            if duration is None:
                duration = audio_clip.duration
            
            # Частота дискретизации аудио
            sample_rate = 44100
            
            # Функция для визуализации аудио
            def audio_visualization_frame(t):
                # Определяем временной срез для текущего момента
                start_sample = int((t - 0.1) * sample_rate) if t > 0.1 else 0
                end_sample = int((t + 0.1) * sample_rate)
                
                # Получаем часть аудиоданных
                audio_data = audio_clip.to_soundarray(fps=sample_rate)
                
                if start_sample >= len(audio_data):
                    start_sample = len(audio_data) - 1
                if end_sample >= len(audio_data):
                    end_sample = len(audio_data) - 1
                
                audio_segment = audio_data[start_sample:end_sample]
                
                if len(audio_segment.shape) > 1:
                    # Если стерео, берем среднее значение каналов
                    audio_segment = audio_segment.mean(axis=1)
                
                # Создаем изображение для визуализации
                fig, ax = plt.figure(figsize=(width/100, height/100), dpi=100, facecolor='black'), plt.Axes(plt.figure(), [0., 0., 1., 1.])
                plt.close(fig)
                fig.add_axes(ax)
                
                # Визуализация спектра
                spectrum = np.abs(np.fft.fft(audio_segment))
                freqs = np.fft.fftfreq(len(spectrum), 1/sample_rate)
                spectrum = spectrum[:len(spectrum)//2]
                freqs = freqs[:len(freqs)//2]
                
                # Нормализация
                spectrum = spectrum / np.max(spectrum) if np.max(spectrum) > 0 else spectrum
                
                # Визуализируем только значимую часть спектра
                max_freq_idx = min(len(freqs), 1000)  # Ограничение для визуализации
                
                # Градиент цветов от синего к красному
                colors = plt.cm.viridis(np.linspace(0, 1, len(spectrum[:max_freq_idx])))
                
                ax.bar(
                    range(len(spectrum[:max_freq_idx])), 
                    spectrum[:max_freq_idx], 
                    color=colors,
                    width=1.0
                )
                ax.axis('off')
                
                # Изменяем фигуру в массив изображения
                fig.canvas.draw()
                img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
                img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
                
                plt.close(fig)
                
                return img
            
            # Создаем видеоклип с визуализацией
            visualization_clip = VideoClip(audio_visualization_frame, duration=duration)
            
            # Добавляем аудио к визуализации
            visualization_clip = visualization_clip.set_audio(audio_clip)
            
            # Сохраняем видео
            logger.info(f"Сохранение фонового видео с визуализацией: {output_path}")
            visualization_clip.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                fps=fps,
                preset="medium",
                threads=2
            )
            
            visualization_clip.close()
            audio_clip.close()
            
            logger.info(f"Фоновое видео с визуализацией успешно создано: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка при создании фонового видео с визуализацией: {str(e)}")
            raise
