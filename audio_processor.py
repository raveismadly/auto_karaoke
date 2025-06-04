# Создаем audio_processor.py
with open('audio_processor.py', 'w') as f:
    f.write('''
import os
import logging
import numpy as np
from pathlib import Path
import librosa
import soundfile as sf
from spleeter.separator import Separator
from pydub import AudioSegment

from utils import get_temp_directory, create_directory_if_not_exists

# Настройка логирования
logger = logging.getLogger(__name__)

class AudioProcessor:
    """
    Класс для обработки аудио и отделения вокала от инструментальной части
    """
    
    def __init__(self):
        """
        Инициализация аудио процессора
        """
        # Создаем сепаратор Spleeter с предобученной моделью для разделения на вокал и аккомпанемент
        self.separator = Separator('spleeter:2stems')
        self.temp_dir = get_temp_directory()
    
    def extract_vocals(self, audio_file_path):
        """
        Отделяет вокал от инструментальной части
        
        Args:
            audio_file_path: путь к аудиофайлу
            
        Returns:
            tuple: пути к файлам с вокалом и инструментальной частью
        """
        logger.info(f"Отделение вокала от музыки для файла: {audio_file_path}")
        
        # Создаем временную директорию для результатов
        file_name = os.path.basename(audio_file_path)
        file_base_name = os.path.splitext(file_name)[0]
        output_dir = os.path.join(self.temp_dir, file_base_name)
        create_directory_if_not_exists(output_dir)
        
        # Выполняем разделение
        try:
            self.separator.separate_to_file(audio_file_path, output_dir)
            
            # Пути к полученным файлам
            vocals_path = os.path.join(output_dir, file_base_name, 'vocals.wav')
            accompaniment_path = os.path.join(output_dir, file_base_name, 'accompaniment.wav')
            
            logger.info(f"Вокал сохранен в: {vocals_path}")
            logger.info(f"Инструментальная часть сохранена в: {accompaniment_path}")
            
            return vocals_path, accompaniment_path
        except Exception as e:
            logger.error(f"Ошибка при отделении вокала: {str(e)}")
            raise
    
    def extract_audio_from_video(self, video_file_path):
        """
        Извлекает аудиодорожку из видеофайла
        
        Args:
            video_file_path: путь к видеофайлу
            
        Returns:
            str: путь к извлеченному аудиофайлу
        """
        logger.info(f"Извлечение аудио из видео: {video_file_path}")
        
        file_name = os.path.basename(video_file_path)
        file_base_name = os.path.splitext(file_name)[0]
        audio_output_path = os.path.join(self.temp_dir, f"{file_base_name}_audio.wav")
        
        try:
            import moviepy.editor as mp
            video = mp.VideoFileClip(video_file_path)
            video.audio.write_audiofile(audio_output_path, codec='pcm_s16le')
            logger.info(f"Аудио извлечено и сохранено в: {audio_output_path}")
            return audio_output_path
        except Exception as e:
            logger.error(f"Ошибка при извлечении аудио из видео: {str(e)}")
            raise
    
    def adjust_audio_volume(self, audio_file_path, volume_factor=1.0):
        """
        Регулирует громкость аудиофайла
        
        Args:
            audio_file_path: путь к аудиофайлу
            volume_factor: коэффициент громкости (1.0 - без изменений)
            
        Returns:
            str: путь к новому аудиофайлу с измененной громкостью
        """
        logger.info(f"Регулировка громкости для {audio_file_path} с коэффициентом {volume_factor}")
        
        file_name = os.path.basename(audio_file_path)
        file_base_name = os.path.splitext(file_name)[0]
        output_path = os.path.join(self.temp_dir, f"{file_base_name}_adjusted.wav")
        
        try:
            audio = AudioSegment.from_file(audio_file_path)
            adjusted_audio = audio + (10 * np.log10(volume_factor) * 2)  # пересчет громкости в децибелы
            adjusted_audio.export(output_path, format='wav')
            logger.info(f"Аудио с измененной громкостью сохранено в: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Ошибка при регулировке громкости аудио: {str(e)}")
            raise
    
    def mix_audio_files(self, audio_file1, audio_file2, output_file=None, volume1=1.0, volume2=0.5):
        """
        Смешивает два аудиофайла
        
        Args:
            audio_file1: путь к первому аудиофайлу
            audio_file2: путь ко второму аудиофайлу
            output_file: путь для сохранения результата (если None, создается автоматически)
            volume1: громкость первого файла (1.0 = 100%)
            volume2: громкость второго файла (0.5 = 50%)
            
        Returns:
            str: путь к смешанному аудиофайлу
        """
        logger.info(f"Смешивание аудиофайлов: {audio_file1} и {audio_file2}")
        
        if output_file is None:
            file_name1 = os.path.basename(audio_file1)
            file_base_name1 = os.path.splitext(file_name1)[0]
            output_file = os.path.join(self.temp_dir, f"{file_base_name1}_mixed.wav")
        
        try:
            # Загружаем аудиофайлы
            sound1 = AudioSegment.from_file(audio_file1)
            sound2 = AudioSegment.from_file(audio_file2)
            
            # Регулируем громкость
            if volume1 != 1.0:
                sound1 = sound1 + (10 * np.log10(volume1) * 2)
            
            if volume2 != 1.0:
                sound2 = sound2 + (10 * np.log10(volume2) * 2)
            
            # Обрабатываем разную длину файлов
            if len(sound1) > len(sound2):
                # Дополняем второй файл тишиной
                silence = AudioSegment.silent(duration=len(sound1) - len(sound2))
                sound2 = sound2 + silence
            elif len(sound2) > len(sound1):
                # Дополняем первый файл тишиной
                silence = AudioSegment.silent(duration=len(sound2) - len(sound1))
                sound1 = sound1 + silence
            
            # Смешиваем аудио
            mixed = sound1.overlay(sound2)
            
            # Сохраняем результат
            mixed.export(output_file, format='wav')
            logger.info(f"Смешанный аудиофайл сохранен в: {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Ошибка при смешивании аудио: {str(e)}")
            raise
''')

