import os
import logging
import numpy as np
import librosa
from pydub import AudioSegment
import ffmpeg
import tempfile
import subprocess
from typing import Optional, Tuple, Dict, List, Union

# Импорт вспомогательных функций
from autokaraoke.utils import (
    get_temp_directory, 
    create_directory_if_not_exists,
    get_base_filename
)

logger = logging.getLogger(__name__)

class AudioProcessor:
#     \"\"\"
#     Класс для обработки аудио и отделения вокала от инструментальной части.
#     \"\"\"
#
    def __init__(self):
#         \"\"\"
#         Инициализация процессора аудио.
#         \"\"\"
        self.temp_dir = get_temp_directory()
        logger.info(f"AudioProcessor инициализирован. Временная директория: {self.temp_dir}")
    
    def extract_vocals(
        self,
        audio_path: str,
        output_dir: Optional[str] = None,
        model: str = "htdemucs",
        device: str = "cpu"
    ) -> Dict[str, str]:
#         \"\"\"
#         Отделяет вокал от инструментальной части с помощью demucs.
#
#         Args:
#             audio_path (str): Путь к аудиофайлу
#             output_dir (str, optional): Директория для сохранения результатов
#             model (str): Модель demucs для использования
#             device (str): Устройство для запуска модели ('cpu' или 'cuda')
#
#         Returns:
#             Dict[str, str]: Словарь с путями к файлам вокала и инструментальной части
#         \"\"\"
        if output_dir is None:
            output_dir = os.path.join(self.temp_dir, "separated")
        
        create_directory_if_not_exists(output_dir)
        
        logger.info(f"Отделение вокала из файла: {audio_path}")
        logger.info(f"Используется модель: {model}")
        
        # Базовое имя файла для выходных файлов
        base_filename = get_base_filename(audio_path)
        
        # Создание временного файла для вывода
        output_path = os.path.join(output_dir, base_filename)
        
        try:
            # Запуск demucs для разделения аудио
            cmd = [
                "demucs", 
                "--two-stems=vocals", 
                "-n", model,
                "-o", output_dir,
                "-d", device,
                audio_path
            ]
            
            logger.info(f"Выполнение команды: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Ошибка при отделении вокала: {result.stderr}")
                raise RuntimeError(f"Ошибка при отделении вокала: {result.stderr}")
            
            logger.info("Разделение аудио завершено успешно")
            
            # Сформируем пути к разделенным файлам
            # Demucs создает директорию с именем модели внутри output_dir, затем название песни
            model_dir = os.path.join(output_dir, model)
            track_dir = os.path.join(model_dir, base_filename)
            
            vocals_path = os.path.join(track_dir, "vocals.wav")
            no_vocals_path = os.path.join(track_dir, "no_vocals.wav")
            
            # Проверяем наличие файлов
            if not os.path.exists(vocals_path):
                logger.warning(f"Файл вокала не найден по пути {vocals_path}")
                vocals_path = None
                
            if not os.path.exists(no_vocals_path):
                # Ищем альтернативные названия файла инструментальной части
                alternatives = ["accompaniment.wav", "other.wav", "no_vocals.wav", "instrumental.wav"]
                for alt in alternatives:
                    alt_path = os.path.join(track_dir, alt)
                    if os.path.exists(alt_path):
                        no_vocals_path = alt_path
                        break
                else:
                    logger.warning(f"Файл инструментальной части не найден в {track_dir}")
                    no_vocals_path = None
            
            return {
                "vocals": vocals_path,
                "instrumental": no_vocals_path
            }
            
        except Exception as e:
            logger.error(f"Ошибка при отделении вокала: {str(e)}")
            raise
    
    def extract_audio_from_video(self, video_path: str, output_path: Optional[str] = None) -> str:
#         \"\"\"
#         Извлекает аудиодорожку из видеофайла.
#
#         Args:
#             video_path (str): Путь к видеофайлу
#             output_path (str, optional): Путь для сохранения аудио
#
#         Returns:
#             str: Путь к извлеченному аудиофайлу
#         \"\"\"
        if output_path is None:
            base_name = get_base_filename(video_path)
            output_path = os.path.join(self.temp_dir, f"{base_name}.wav")
        
        logger.info(f"Извлечение аудио из видео: {video_path}")
        
        try:
            (
                ffmpeg
                .input(video_path)
                .output(output_path, acodec='pcm_s16le', ar='44100')
                .overwrite_output()
                .run(quiet=True)
            )
            logger.info(f"Аудио успешно извлечено и сохранено в: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Ошибка при извлечении аудио: {str(e)}")
            raise
    
    def adjust_audio_volume(self, audio_path: str, volume_factor: float) -> str:
#         \"\"\"
#         Регулирует громкость аудиофайла.
#
#         Args:
#             audio_path (str): Путь к аудиофайлу
#             volume_factor (float): Коэффициент громкости (1.0 - без изменений)
#
#         Returns:
#             str: Путь к обработанному аудиофайлу
#         \"\"\"
        logger.info(f"Регулировка громкости для {audio_path}, коэффициент: {volume_factor}")
        
        audio = AudioSegment.from_file(audio_path)
        
        # Изменение громкости
        adjusted_audio = audio + (20 * np.log10(volume_factor))
        
        # Создание имени выходного файла
        base_name = get_base_filename(audio_path)
        output_path = os.path.join(self.temp_dir, f"{base_name}_volume_{volume_factor}.wav")
        
        # Сохранение обработанного файла
        adjusted_audio.export(output_path, format="wav")
        logger.info(f"Громкость отрегулирована, сохранено в: {output_path}")
        
        return output_path
    
    def mix_audio_files(
        self,
        audio_path_1: str,
        audio_path_2: str,
        volume_1: float = 1.0,
        volume_2: float = 1.0,
        output_path: Optional[str] = None
    ) -> str:
#         \"\"\"
#         Смешивает два аудиофайла с заданными уровнями громкости.
#
#         Args:
#             audio_path_1 (str): Путь к первому аудиофайлу
#             audio_path_2 (str): Путь ко второму аудиофайлу
#             volume_1 (float): Коэффициент громкости для первого файла
#             volume_2 (float): Коэффициент громкости для второго файла
#             output_path (str, optional): Путь для сохранения результата
#
#         Returns:
#             str: Путь к смешанному аудиофайлу
#         \"\"\"
        logger.info(f"Смешивание аудиофайлов: {audio_path_1} и {audio_path_2}")
        
        if output_path is None:
            base_name_1 = get_base_filename(audio_path_1)
            base_name_2 = get_base_filename(audio_path_2)
            output_path = os.path.join(
                self.temp_dir,
                f"{base_name_1}_{base_name_2}_mixed.wav"
            )
        
        try:
            # Загрузка аудиофайлов с помощью pydub
            audio_1 = AudioSegment.from_file(audio_path_1)
            audio_2 = AudioSegment.from_file(audio_path_2)
            
            # Регулировка громкости
            if volume_1 != 1.0:
                audio_1 = audio_1 + (20 * np.log10(volume_1))
                
            if volume_2 != 1.0:
                audio_2 = audio_2 + (20 * np.log10(volume_2))
            
            # Гарантируем, что оба файла имеют одинаковую длину
            if len(audio_1) > len(audio_2):
                audio_2 = audio_2 + AudioSegment.silent(duration=len(audio_1) - len(audio_2))
            elif len(audio_2) > len(audio_1):
                audio_1 = audio_1 + AudioSegment.silent(duration=len(audio_2) - len(audio_1))
                
            # Смешивание аудио
            mixed_audio = audio_1.overlay(audio_2)
            
            # Сохранение результата
            mixed_audio.export(output_path, format="wav")
            logger.info(f"Смешанный аудиофайл сохранен в: {output_path}")
            
            return output_path
        except Exception as e:
            logger.error(f"Ошибка при смешивании аудиофайлов: {str(e)}")
            raise
