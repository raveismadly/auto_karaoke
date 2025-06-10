import os
import re
import logging
import tempfile
import subprocess
import pathlib
from typing import Optional, Tuple, Union

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directory_if_not_exists(directory_path: str) -> None:
    \"\"\"
    Создает директорию, если она не существует.
    
    Args:
        directory_path (str): Путь к директории
    \"\"\"
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logger.info(f"Создана директория: {directory_path}")

def clean_filename(filename: str) -> str:
    \"\"\"
    Очищает имя файла от недопустимых символов.
    
    Args:
        filename (str): Исходное имя файла
        
    Returns:
        str: Очищенное имя файла
    \"\"\"
    # Заменяем недопустимые символы на подчеркивание
    clean_name = re.sub(r'[\\\\/*?:"<>|]', "_", filename)
    return clean_name

def get_temp_directory() -> str:
    \"\"\"
    Возвращает путь к временной директории.
    
    Returns:
        str: Путь к временной директории
    \"\"\"
    temp_dir = os.path.join(tempfile.gettempdir(), "autokaraoke")
    create_directory_if_not_exists(temp_dir)
    return temp_dir

def check_ffmpeg() -> bool:
    \"\"\"
    Проверяет наличие FFmpeg в системе.
    
    Returns:
        bool: True, если FFmpeg установлен, иначе False
    \"\"\"
    try:
        subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=True
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def time_to_seconds(time_str: str) -> float:
    \"\"\"
    Конвертирует время из формата [MM:SS.ms] в секунды.
    
    Args:
        time_str (str): Строка времени в формате [MM:SS.ms]
        
    Returns:
        float: Время в секундах
    \"\"\"
    time_str = time_str.strip('[]')
    parts = time_str.split(':')
    
    if len(parts) == 2:
        minutes, seconds = parts
        return float(minutes) * 60 + float(seconds)
    else:
        return float(time_str)

def seconds_to_time(seconds: float, include_brackets: bool = True) -> str:
    \"\"\"
    Конвертирует секунды в формат [MM:SS.ms].
    
    Args:
        seconds (float): Время в секундах
        include_brackets (bool): Включать ли скобки в результат
        
    Returns:
        str: Время в формате [MM:SS.ms]
    \"\"\"
    minutes = int(seconds // 60)
    seconds_remainder = seconds % 60
    
    time_str = f"{minutes:02d}:{seconds_remainder:06.3f}"
    
    if include_brackets:
        return f"[{time_str}]"
    return time_str

def get_file_extension(file_path: str) -> str:
#     \"\"\"
#     Получает расширение файла.
#
#     Args:
#         file_path (str): Путь к файлу
#
#     Returns:
#         str: Расширение файла (с точкой)
#     \"\"\"
    return pathlib.Path(file_path).suffix.lower()

def is_audio_file(file_path: str) -> bool:
#     \"\"\"
#     Проверяет, является ли файл аудиофайлом.
#
#     Args:
#         file_path (str): Путь к файлу
#
#     Returns:
#         bool: True, если файл является аудиофайлом, иначе False
#     \"\"\"
    audio_extensions = ['.mp3', '.wav', '.flac', '.ogg', '.aac', '.m4a']
    return get_file_extension(file_path) in audio_extensions

def is_video_file(file_path: str) -> bool:
#     \"\"\"
#     Проверяет, является ли файл видеофайлом.
#
#     Args:
#         file_path (str): Путь к файлу
#
#     Returns:
#         bool: True, если файл является видеофайлом, иначе False
#     \"\"\"
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.webm']
    return get_file_extension(file_path) in video_extensions

def get_base_filename(file_path: str) -> str:
#     \"\"\"
#     Получает базовое имя файла без расширения.
#
#     Args:
#         file_path (str): Путь к файлу
#
#     Returns:
#         str: Базовое имя файла
#     \"\"\"
    return os.path.splitext(os.path.basename(file_path))[0]
