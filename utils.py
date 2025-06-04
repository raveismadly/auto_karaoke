# Создаем utils.py
with open('utils.py', 'w') as f:
    f.write('''
import os
import re
import logging
import tempfile
import subprocess
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directory_if_not_exists(directory_path):
    """
    Создаёт директорию, если она не существует
    
    Args:
        directory_path: путь к директории
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logger.info(f"Создана директория: {directory_path}")

def clean_filename(filename):
    """
    Очищает имя файла от недопустимых символов
    
    Args:
        filename: исходное имя файла
        
    Returns:
        Очищенное имя файла
    """
    # Удаляем недопустимые символы
    cleaned = re.sub(r'[\\\\/*?:"<>|]', "", filename)
    # Удаляем множественные пробелы
    cleaned = re.sub(r'\\s+', " ", cleaned).strip()
    return cleaned

def get_temp_directory():
    """
    Получает путь к временной директории
    
    Returns:
        Путь к временной директории
    """
    temp_dir = tempfile.gettempdir()
    karaoke_temp_dir = os.path.join(temp_dir, "autokaraoke")
    create_directory_if_not_exists(karaoke_temp_dir)
    return karaoke_temp_dir

def check_ffmpeg():
    """
    Проверяет наличие ffmpeg в системе
    
    Returns:
        bool: True если ffmpeg установлен, иначе False
    """
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        logger.info("FFmpeg найден в системе")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.error("FFmpeg не найден! Установите FFmpeg для работы с приложением")
        return False

def time_to_seconds(time_str):
    """
    Преобразует строку времени формата MM:SS или HH:MM:SS в секунды
    
    Args:
        time_str: строка времени
        
    Returns:
        float: время в секундах
    """
    parts = time_str.split(':')
    if len(parts) == 2:  # MM:SS
        return int(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:  # HH:MM:SS
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    else:
        return float(time_str)  # Предполагаем, что это уже секунды

def seconds_to_time(seconds):
    """
    Преобразует секунды в строку времени формата MM:SS.ms
    
    Args:
        seconds: время в секундах
        
    Returns:
        str: строка времени
    """
    minutes = int(seconds // 60)
    seconds_remainder = seconds % 60
    return f"{minutes:02d}:{seconds_remainder:05.2f}"

def get_file_extension(file_path):
    """
    Получает расширение файла
    
    Args:
        file_path: путь к файлу
        
    Returns:
        str: расширение файла без точки
    """
    return os.path.splitext(file_path)[1][1:].lower()

def is_audio_file(file_path):
    """
    Проверяет, является ли файл аудиофайлом по расширению
    
    Args:
        file_path: путь к файлу
        
    Returns:
        bool: True если это аудиофайл, иначе False
    """
    audio_extensions = {'mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg'}
    return get_file_extension(file_path) in audio_extensions

def is_video_file(file_path):
    """
    Проверяет, является ли файл видеофайлом по расширению
    
    Args:
        file_path: путь к файлу
        
    Returns:
        bool: True если это видеофайл, иначе False
    """
    video_extensions = {'mp4', 'mkv', 'avi', 'mov', 'wmv', 'webm'}
    return get_file_extension(file_path) in video_extensions
''')

print("Created utils.py")