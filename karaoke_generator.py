import os
import logging
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tempfile
from pathlib import Path
import moviepy.editor as mp
from moviepy.editor import TextClip, ColorClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
import matplotlib.pyplot as plt

from utils import get_temp_directory, create_directory_if_not_exists, clean_filename

# Настройка логирования
logger = logging.getLogger(__name__)

class KaraokeGenerator:
    """
    Класс для создания караоке-видео с синхронизированным текстом
    """
    
    def __init__(self):
        """
        Инициализация генератора караоке
        """
        self.temp_dir = get_temp_directory()
        
        # Настройка шрифтов
        # Пытаемся найти подходящие шрифты для macOS
        self.fonts = {
            'main': '/System/Library/Fonts/Supplemental/Arial.ttf',
            'bold': '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
        }
        
        # Проверяем наличие шрифтов, если не найдены - используем стандартные
        if not os.path.exists(self.fonts['main']):
            self.fonts['main'] = None  # Будет использоваться шрифт по умолчанию
        if not os.path.exists(self.fonts['bold']):
            self.fonts['bold'] = None  # Будет использоваться шрифт по умолчанию
            
        # Настройка стилей
        self.styles = {
            'normal_color': 'white',
            'highlight_color': 'yellow',
            'bg_color': (0, 0, 0, 128),  # Полупрозрачный черный
            'fontsize': 40,
            'stroke_width': 1.5
        }
    
    def generate_lyrics_frames(self, recognition_result, duration, fps=24, output_format='png'):
        """
        Генерирует кадры с текстом для караоке
        
        Args:
            recognition_result: результат распознавания с синхронизацией
            duration: длительность видео в секундах
            fps: частота кадров
            output_format: формат изображений
            
        Returns:
            str: директория с сгенерированными кадрами
        """
        logger.info("Генерация кадров с текстом для караоке")
        
        # Создаем директорию для кадров
        frames_dir = os.path.join(self.temp_dir, "karaoke_frames")
        create_directory_if_not_exists(frames_dir)
        
        # Расчет общего количества кадров
        total_frames = int(duration * fps)
        
        # Извлекаем сегменты и их времена
        segments = recognition_result['segments']
        
        # Для каждого кадра определяем, какой текст нужно показать и как его подсветить
        for frame_idx in range(total_frames):
            current_time = frame_idx / fps
            
            # Находим текущий сегмент
            current_segment = None
            for segment in segments:
                if segment['start'] <= current_time < segment['end']:
                    current_segment = segment
                    break
            
            # Если нет актуального сегмента, пропускаем кадр (будет пустым)
            if not current_segment:
                continue
                
            # Генерируем изображение с текстом
            img = self._create_text_frame(current_segment, current_time, 1280, 720)
            
            # Сохраняем кадр
            frame_path = os.path.join(frames_dir, f"frame_{frame_idx:05d}.{output_format}")
            img.save(frame_path)
        
        logger.info(f"Сгенерировано {total_frames} кадров с текстом")
        return frames_dir
    
    def _create_text_frame(self, segment, current_time, width, height):
        """
        Создает кадр с текстом
        
        Args:
            segment: текущий сегмент текста
            current_time: текущее время
            width: ширина кадра
            height: высота кадра
            
        Returns:
            PIL.Image: созданное изображение с текстом
        """
        # Создаем пустое изображение с прозрачным фоном
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Определяем размер шрифта и его параметры
        try:
            font = ImageFont.truetype(self.fonts['main'], self.styles['fontsize'])
            font_bold = ImageFont.truetype(self.fonts['bold'], self.styles['fontsize'])
        except (IOError, OSError):
            # Если шрифт не найден, используем шрифт по умолчанию
            font = ImageFont.load_default()
            font_bold = ImageFont.load_default()
        
        # Получаем текст и его позицию
        text = segment['text']
        
        # Определяем размер текста
        try:
            text_width, text_height = draw.textsize(text, font=font)
        except:
            # В более новых версиях PIL
            text_width = draw.textlength(text, font=font)
            text_height = self.styles['fontsize'] * 1.5
        
        # Центрируем текст
        x = (width - text_width) // 2
        y = height - text_height - 40  # Позиция текста снизу с отступом
        
        # Рисуем фон для текста
        padding = 20
        draw.rectangle(
            [(x - padding, y - padding), (x + text_width + padding, y + text_height + padding)], 
            fill=self.styles['bg_color']
        )
        
        # Рисуем текст
        draw.text((x, y), text, fill=self.styles['normal_color'], font=font, stroke_width=self.styles['stroke_width'], stroke_fill='black')
        
        return img
    
    def create_karaoke_video(self, audio_file, recognition_result, output_path=None, background_video=None):
        """
        Создает караоке-видео с синхронизированным текстом
        
        Args:
            audio_file: путь к аудиофайлу
            recognition_result: результат распознавания с синхронизацией
            output_path: путь для сохранения видео (если None, создается автоматически)
            background_video: путь к фоновому видео (если есть)
            
        Returns:
            str: путь к созданному караоке-видео
        """
        logger.info("Создание караоке-видео")
        
        if output_path is None:
            audio_name = os.path.basename(audio_file)
            audio_base_name = os.path.splitext(audio_name)[0]
            output_path = os.path.join(self.temp_dir, f"{audio_base_name}_karaoke.mp4")
            
        try:
            # Загружаем аудио
            audio_clip = mp.AudioFileClip(audio_file)
            duration = audio_clip.duration
            
            # Функция для генерации текста в нужное время
            def make_text_clip(segment):
                start_time = segment['start']
                end_time = segment['end']
                text = segment['text']
                
                font_size = self.styles['fontsize']
                
                # Создаем текстовый клип
                text_clip = TextClip(
                    text, 
                    fontsize=font_size, 
                    color=self.styles['normal_color'],
                    bg_color=self.styles['bg_color'],
                    stroke_color='black',
                    stroke_width=1,
                    font=self.fonts['main'] if self.fonts['main'] else 'Arial'
                )
                
                # Центрируем текст и помещаем его внизу
                text_clip = text_clip.set_position(('center', 0.85), relative=True)
                
                # Устанавливаем время отображения клипа
                text_clip = text_clip.set_start(start_time).set_end(end_time)
                
                return text_clip
            
            # Создаем список всех текстовых клипов
            text_clips = []
            for segment in recognition_result['segments']:
                text_clips.append(make_text_clip(segment))
            
            # Создаем основной видеоклип
            if background_video and os.path.exists(background_video):
                logger.info(f"Используем фоновое видео: {background_video}")
                bg_clip = mp.VideoFileClip(background_video)
                
                # Если длительность видео меньше аудио, зацикливаем его
                if bg_clip.duration < duration:
                    bg_clip = bg_clip.loop(duration=duration)
                # Если длительность видео больше аудио, обрезаем его
                else:
                    bg_clip = bg_clip.subclip(0, duration)
                
                main_clip = bg_clip
            else:
                logger.info("Создаем фоновое видео с градиентом")
                # Создаем градиентный фон
                def make_gradient_frame(t):
                    # Создаем градиент от темно-синего к черному
                    img = np.zeros((720, 1280, 3), dtype=np.uint8)
                    for i in range(720):
                        factor = i / 720
                        blue = int(25 * (1 - factor))
                        img[i, :] = [0, 0, blue]
                    return img
                
                main_clip = mp.VideoClip(make_gradient_frame, duration=duration)
            
            # Собираем итоговое видео
            final_clip = CompositeVideoClip([main_clip] + text_clips)
            
            # Добавляем аудио
            final_clip = final_clip.set_audio(audio_clip)
            
            # Сохраняем видео
            final_clip.write_videofile(
                output_path, 
                fps=24, 
                codec='libx264', 
                audio_codec='aac',
                temp_audiofile=os.path.join(self.temp_dir, "temp_audio.m4a"),
                remove_temp=True
            )
            
            logger.info(f"Караоке-видео сохранено в: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка при создании караоке-видео: {str(e)}")
            raise
    
    def create_background_video_with_audio_visualization(self, audio_file, duration, output_path=None):
        """
        Создает фоновое видео с визуализацией аудио (спектрограммой)
        
        Args:
            audio_file: путь к аудиофайлу
            duration: длительность видео в секундах
            output_path: путь для сохранения видео (если None, создается автоматически)
            
        Returns:
            str: путь к созданному видео с визуализацией
        """
        logger.info(f"Создание фонового видео с визуализацией для аудио: {audio_file}")
        
        if output_path is None:
            audio_name = os.path.basename(audio_file)
            audio_base_name = os.path.splitext(audio_name)[0]
            output_path = os.path.join(self.temp_dir, f"{audio_base_name}_visualization.mp4")
        
        try:
            # Загружаем аудиофайл и получаем данные
            y, sr = librosa.load(audio_file)
            
            # Вычисляем STFT (короткое преобразование Фурье)
            D = librosa.stft(y)
            S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
            
            # Длительность одного кадра спектрограммы
            hop_length = 512  # значение по умолчанию в librosa.stft
            
            # Создаем функцию для генерации кадров визуализации
            def make_frame(t):
                # Конвертируем время в индекс кадра спектрограммы
                frame_idx = int(t * sr / hop_length)
                if frame_idx >= S_db.shape[1]:
                    frame_idx = S_db.shape[1] - 1
                    
                # Создаем изображение
                plt.figure(figsize=(12.8, 7.2), dpi=100, facecolor='black')
                plt.axis('off')
                
                # Рисуем текущий срез спектрограммы
                spectrum = S_db[:, frame_idx]
                plt.plot(spectrum, color='cyan', linewidth=2)
                plt.fill_between(range(len(spectrum)), spectrum, -80, color='blue', alpha=0.6)
                
                # Установка пределов
                plt.ylim(-80, 0)
                plt.tight_layout(pad=0)
                
                # Конвертация в изображение
                fig = plt.gcf()
                fig.canvas.draw()
                img = np.array(fig.canvas.renderer.buffer_rgba())
                plt.close()
                
                return img
            
            # Создаем видеоклип с визуализацией
            viz_clip = mp.VideoClip(make_frame, duration=duration)
            
            # Добавляем аудио
            audio_clip = mp.AudioFileClip(audio_file)
            viz_clip = viz_clip.set_audio(audio_clip)
            
            # Сохраняем видео
            viz_clip.write_videofile(
                output_path, 
                fps=24, 
                codec='libx264', 
                audio_codec='aac',
                temp_audiofile=os.path.join(self.temp_dir, "temp_audio.m4a"),
                remove_temp=True
            )
            
            logger.info(f"Фоновое видео с визуализацией сохранено в: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка при создании видео с визуализацией: {str(e)}")
            raise
''')

