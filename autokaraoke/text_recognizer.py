import os
import re
import json
import logging
import tempfile
import numpy as np
import whisper
from whisper.utils import get_writer
import librosa
from sklearn.metrics import pairwise_distances
from typing import Dict, List, Optional, Tuple, Union, Any

# Импорт вспомогательных функций
from autokaraoke.utils import (
    get_temp_directory,
    create_directory_if_not_exists,
    seconds_to_time,
    get_base_filename
)

logger = logging.getLogger(__name__)

class TextRecognizer:
#     \"\"\"
#     Класс для распознавания текста из аудио и создания файлов синхронизации для караоке.
#     \"\"\"
    
    def __init__(
        self,
        model_name: str = "base",
        device: str = "cpu",
        language: Optional[str] = None
    ):
#         \"\"\"
#         Инициализация распознавателя текста.
#
#         Args:
#             model_name (str): Название модели Whisper ('tiny', 'base', 'small', 'medium', 'large')
#             device (str): Устройство для запуска модели ('cpu' или 'cuda')
#             language (str, optional): Код языка для распознавания
#         \"\"\"
        self.model_name = model_name
        self.device = device
        self.language = language
        self.temp_dir = get_temp_directory()
        
        logger.info(f"Загрузка модели Whisper: {model_name}")
        try:
            self.model = whisper.load_model(model_name, device=device)
            logger.info(f"Модель Whisper {model_name} успешно загружена")
        except Exception as e:
            logger.error(f"Ошибка при загрузке модели Whisper: {str(e)}")
            raise
    
    def recognize_speech(
        self, 
        audio_path: str,
        output_dir: Optional[str] = None,
        return_timestamps: bool = True
    ) -> Dict[str, Any]:
#         \"\"\"
#         Распознает речь из аудиофайла с помощью Whisper.
#
#         Args:
#             audio_path (str): Путь к аудиофайлу
#             output_dir (str, optional): Директория для сохранения результатов
#             return_timestamps (bool): Возвращать ли временные метки для слов
#
#         Returns:
#             Dict[str, Any]: Результат распознавания с текстом и временными метками
#         \"\"\"
        logger.info(f"Распознавание речи из файла: {audio_path}")
        
        if output_dir is None:
            output_dir = os.path.join(self.temp_dir, "transcriptions")
        
        create_directory_if_not_exists(output_dir)
        
        transcribe_options = {
            "task": "transcribe",
            "verbose": True,
        }
        
        if self.language:
            transcribe_options["language"] = self.language
        
        try:
            # Загрузка аудиофайла
            logger.info("Загрузка аудио...")
            audio = whisper.load_audio(audio_path)
            audio = whisper.pad_or_trim(audio)
            
            # Распознавание речи
            logger.info("Распознавание речи...")
            result = self.model.transcribe(
                audio_path, 
                word_timestamps=return_timestamps,
                **transcribe_options
            )
            
            # Сохраняем результат в виде JSON
            base_name = get_base_filename(audio_path)
            json_output = os.path.join(output_dir, f"{base_name}_transcription.json")
            
            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=4)
            
            logger.info(f"Результат распознавания сохранен в {json_output}")
            
            # Сохраняем результат в виде текста и SRT
            txt_writer = get_writer("txt", output_dir)
            txt_writer(result, audio_path)
            
            srt_writer = get_writer("srt", output_dir)
            srt_writer(result, audio_path)
            
            return result
        
        except Exception as e:
            logger.error(f"Ошибка при распознавании речи: {str(e)}")
            raise
    
    def save_lyrics(self, result: Dict[str, Any], output_path: str) -> str:
#         \"\"\"
#         Сохраняет распознанный текст в файл.
#
#         Args:
#             result (Dict[str, Any]): Результат распознавания Whisper
#             output_path (str): Путь для сохранения текста
#
#         Returns:
#             str: Путь к сохраненному файлу с текстом
#         \"\"\"
        logger.info(f"Сохранение текста в файл: {output_path}")
        
        try:
            text = result["text"]
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            logger.info(f"Текст успешно сохранен в {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Ошибка при сохранении текста: {str(e)}")
            raise
    
    def create_synchronization(
        self,
        result: Dict[str, Any],
        output_path: str
    ) -> str:
#         \"\"\"
#         Создает файл синхронизации в формате LRC для караоке.
#
#         Args:
#             result (Dict[str, Any]): Результат распознавания Whisper
#             output_path (str): Путь для сохранения файла LRC
#
#         Returns:
#             str: Путь к созданному файлу синхронизации
#         \"\"\"
        logger.info(f"Создание файла синхронизации LRC: {output_path}")
        
        try:
            # Проверяем наличие сегментов с временными метками
            if "segments" not in result:
                logger.error("Отсутствуют сегменты в результате распознавания")
                raise ValueError("Отсутствуют сегменты в результате распознавания")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                # Записываем метаданные LRC
                title = os.path.splitext(os.path.basename(output_path))[0]
                f.write(f"[ti:{title}]\\n")
                f.write(f"[ar:Unknown]\\n")
                f.write(f"[al:AutoKaraoke]\\n")
                f.write(f"[by:AutoKaraoke]\\n\\n")
                
                # Записываем синхронизацию для сегментов
                for segment in result["segments"]:
                    start_time = segment["start"]
                    text = segment["text"].strip()
                    
                    if text:
                        time_tag = seconds_to_time(start_time)
                        f.write(f"{time_tag}{text}\\n")
                    
                    # Если доступны временные метки для слов, добавляем их
                    if "words" in segment:
                        for word_data in segment["words"]:
                            word_start = word_data["start"]
                            word = word_data["word"].strip()
                            
                            if word:
                                word_time_tag = seconds_to_time(word_start)
                                f.write(f"{word_time_tag}{word} ")
                        
                        f.write("\\n")
            
            logger.info(f"Файл синхронизации LRC успешно создан: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка при создании файла синхронизации: {str(e)}")
            raise
    
    def create_srt_subtitles(self, result: Dict[str, Any], output_path: str) -> str:
#         \"\"\"
#         Создает файл субтитров в формате SRT.
#
#         Args:
#             result (Dict[str, Any]): Результат распознавания Whisper
#             output_path (str): Путь для сохранения файла SRT
#
#         Returns:
#             str: Путь к созданному файлу субтитров
#         \"\"\"
        logger.info(f"Создание файла субтитров SRT: {output_path}")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                count = 1
                
                for segment in result["segments"]:
                    start_time = segment["start"]
                    end_time = segment["end"]
                    text = segment["text"].strip()
                    
                    if text:
                        # Форматируем время в формат SRT
                        start_formatted = self._format_srt_time(start_time)
                        end_formatted = self._format_srt_time(end_time)
                        
                        # Записываем блок субтитров
                        f.write(f"{count}\\n")
                        f.write(f"{start_formatted} --> {end_formatted}\\n")
                        f.write(f"{text}\\n\\n")
                        
                        count += 1
            
            logger.info(f"Файл субтитров SRT успешно создан: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Ошибка при создании файла субтитров: {str(e)}")
            raise
    
    def _format_srt_time(self, seconds: float) -> str:
#         \"\"\"
#         Форматирует время в секундах в формат SRT (HH:MM:SS,mmm).
#
#         Args:
#             seconds (float): Время в секундах
#
#         Returns:
#             str: Отформатированное время в формате SRT
#         \"\"\"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"
    
    def import_lyrics_with_synchronization(
        self,
        lyrics_path: str,
        sync_file_path: Optional[str] = None
    ) -> Dict[str, Any]:
#         \"\"\"
#         Импортирует готовые файлы текста и синхронизации.
#
#         Args:
#             lyrics_path (str): Путь к файлу с текстом
#             sync_file_path (str, optional): Путь к файлу синхронизации (LRC или SRT)
#
#         Returns:
#             Dict[str, Any]: Структура данных с текстом и временными метками
#         \"\"\"
        logger.info(f"Импорт текста из файла: {lyrics_path}")
        
        try:
            # Чтение файла с текстом
            with open(lyrics_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            result = {"text": text, "segments": []}
            
            # Если предоставлен файл синхронизации, импортируем его
            if sync_file_path and os.path.exists(sync_file_path):
                logger.info(f"Импорт синхронизации из файла: {sync_file_path}")
                
                ext = os.path.splitext(sync_file_path)[1].lower()
                
                if ext == '.lrc':
                    # Импорт LRC
                    with open(sync_file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    segments = []
                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith('[ti:') or line.startswith('[ar:'):
                            continue
                        
                        # Ищем временные метки в формате [MM:SS.ms]
                        time_tags = re.findall(r'\\[(\\d+:\\d+\\.\\d+)\\]', line)
                        text_parts = re.split(r'\\[\\d+:\\d+\\.\\d+\\]', line)
                        
                        if time_tags and len(text_parts) > 1:
                            for i, time_tag in enumerate(time_tags):
                                if i + 1 < len(text_parts):
                                    time_sec = self._time_to_seconds(time_tag)
                                    text_part = text_parts[i + 1].strip()
                                    
                                    if text_part:
                                        segment = {
                                            "start": time_sec,
                                            "text": text_part
                                        }
                                        segments.append(segment)
                    
                    # Сортируем сегменты по времени начала
                    segments.sort(key=lambda s: s["start"])
                    
                    # Вычисляем время окончания для каждого сегмента
                    for i in range(len(segments) - 1):
                        segments[i]["end"] = segments[i + 1]["start"]
                    
                    # Для последнего сегмента время окончания на 5 секунд позже времени начала
                    if segments:
                        segments[-1]["end"] = segments[-1]["start"] + 5.0
                    
                    result["segments"] = segments
                
                elif ext == '.srt':
                    # Импорт SRT
                    with open(sync_file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Разделяем на блоки субтитров
                    srt_blocks = re.split(r'\\d+\\n', content)
                    segments = []
                    
                    for block in srt_blocks:
                        block = block.strip()
                        if not block:
                            continue
                        
                        # Ищем временные метки в формате HH:MM:SS,mmm --> HH:MM:SS,mmm
                        time_match = re.search(
                            r'(\\d{2}:\\d{2}:\\d{2},\\d{3}) --> (\\d{2}:\\d{2}:\\d{2},\\d{3})',
                            block
                        )
                        
                        if time_match:
                            start_time = self._srt_time_to_seconds(time_match.group(1))
                            end_time = self._srt_time_to_seconds(time_match.group(2))
                            
                            # Извлекаем текст, следующий за временными метками
                            text_part = block[time_match.end():].strip()
                            
                            if text_part:
                                segment = {
                                    "start": start_time,
                                    "end": end_time,
                                    "text": text_part
                                }
                                segments.append(segment)
                    
                    result["segments"] = segments
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при импорте текста и синхронизации: {str(e)}")
            raise
    
    def _time_to_seconds(self, time_str: str) -> float:
#         \"\"\"
#         Преобразует время из формата MM:SS.ms в секунды.
#
#         Args:
#             time_str (str): Время в формате MM:SS.ms
#
#         Returns:
#             float: Время в секундах
#         \"\"\"
        parts = time_str.split(':')
        
        if len(parts) == 2:
            minutes, seconds = parts
            return float(minutes) * 60 + float(seconds)
        elif len(parts) == 3:
            hours, minutes, seconds = parts
            return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        else:
            return float(time_str)
    
    def _srt_time_to_seconds(self, time_str: str) -> float:
#         \"\"\"
#         Преобразует время из формата SRT (HH:MM:SS,mmm) в секунды.
#
#         Args:
#             time_str (str): Время в формате HH:MM:SS,mmm
#
#         Returns:
#             float: Время в секундах
#         \"\"\"
        # Заменяем запятую на точку для правильного преобразования миллисекунд
        time_str = time_str.replace(',', '.')
        hours, minutes, seconds = time_str.split(':')
        
        return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
