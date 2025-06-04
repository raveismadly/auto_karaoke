# Создаем text_recognizer.py
with open('text_recognizer.py', 'w') as f:
    f.write('''
import os
import re
import json
import logging
import whisper
import numpy as np
from pathlib import Path
import librosa
from sklearn.metrics.pairwise import cosine_similarity

from utils import get_temp_directory, create_directory_if_not_exists, seconds_to_time

# Настройка логирования
logger = logging.getLogger(__name__)

class TextRecognizer:
    """
    Класс для распознавания текста из аудио и создания синхронизации для караоке
    """
    
    def __init__(self, model_name="small"):
        """
        Инициализация распознавателя текста
        
        Args:
            model_name: название модели Whisper ('tiny', 'base', 'small', 'medium', 'large')
        """
        logger.info(f"Инициализация модели Whisper: {model_name}")
        try:
            self.model = whisper.load_model(model_name)
            logger.info(f"Модель {model_name} успешно загружена")
        except Exception as e:
            logger.error(f"Ошибка при загрузке модели Whisper: {str(e)}")
            raise
            
        self.temp_dir = get_temp_directory()
        
    def recognize_speech(self, audio_file_path, language="ru"):
        """
        Распознает речь из аудиофайла и возвращает текст
        
        Args:
            audio_file_path: путь к аудиофайлу
            language: код языка, по умолчанию "ru" (русский)
            
        Returns:
            dict: результат распознавания, включая текст и временные метки
        """
        logger.info(f"Распознавание речи из файла: {audio_file_path}, язык: {language}")
        
        try:
            # Распознавание с помощью Whisper
            result = self.model.transcribe(audio_file_path, language=language, word_timestamps=True)
            logger.info("Распознавание речи успешно выполнено")
            return result
        except Exception as e:
            logger.error(f"Ошибка при распознавании речи: {str(e)}")
            raise
    
    def save_lyrics(self, recognition_result, output_path=None):
        """
        Сохраняет текст песни в файл
        
        Args:
            recognition_result: результат распознавания Whisper
            output_path: путь для сохранения файла (если None, создается автоматически)
            
        Returns:
            str: путь к сохраненному файлу с текстом
        """
        if output_path is None:
            output_path = os.path.join(self.temp_dir, "lyrics.txt")
            
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(recognition_result['text'])
            logger.info(f"Текст песни сохранен в: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Ошибка при сохранении текста: {str(e)}")
            raise
    
    def create_synchronization(self, recognition_result, output_path=None):
        """
        Создает файл синхронизации для караоке в формате LRC
        
        Args:
            recognition_result: результат распознавания Whisper
            output_path: путь для сохранения файла (если None, создается автоматически)
            
        Returns:
            str: путь к сохраненному LRC файлу
        """
        if output_path is None:
            output_path = os.path.join(self.temp_dir, "synchro.lrc")
            
        try:
            logger.info("Создание файла синхронизации для караоке")
            
            # Создаем LRC формат - [MM:SS.xx] <слово или фраза>
            lrc_lines = []
            
            if 'segments' in recognition_result:
                for segment in recognition_result['segments']:
                    start_time = segment['start']
                    text = segment.get('text', '').strip()
                    
                    if text:
                        time_str = seconds_to_time(start_time)
                        lrc_line = f"[{time_str}] {text}"
                        lrc_lines.append(lrc_line)
            
            # Если доступны метки слов, используем их для более точной синхронизации
            if hasattr(recognition_result, 'word_segments') and recognition_result.word_segments:
                lrc_lines = []
                for word_segment in recognition_result.word_segments:
                    start_time = word_segment['start']
                    word = word_segment.get('word', '').strip()
                    
                    if word:
                        time_str = seconds_to_time(start_time)
                        lrc_line = f"[{time_str}] {word}"
                        lrc_lines.append(lrc_line)
            
            # Записываем результат в файл
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\\n".join(lrc_lines))
                
            logger.info(f"Файл синхронизации сохранен в: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Ошибка при создании файла синхронизации: {str(e)}")
            raise
    
    def create_srt_subtitles(self, recognition_result, output_path=None):
        """
        Создает субтитры в формате SRT
        
        Args:
            recognition_result: результат распознавания Whisper
            output_path: путь для сохранения файла (если None, создается автоматически)
            
        Returns:
            str: путь к сохраненному SRT файлу
        """
        if output_path is None:
            output_path = os.path.join(self.temp_dir, "subtitles.srt")
            
        try:
            logger.info("Создание субтитров в формате SRT")
            
            srt_lines = []
            subtitle_index = 1
            
            if 'segments' in recognition_result:
                for segment in recognition_result['segments']:
                    start_time = segment['start']
                    end_time = segment['end']
                    text = segment.get('text', '').strip()
                    
                    if text:
                        # Формат SRT: [номер]\n[начало] --> [конец]\n[текст]\n\n
                        start_srt = self._format_srt_time(start_time)
                        end_srt = self._format_srt_time(end_time)
                        
                        srt_lines.append(str(subtitle_index))
                        srt_lines.append(f"{start_srt} --> {end_srt}")
                        srt_lines.append(text)
                        srt_lines.append("")  # Пустая строка для разделения субтитров
                        
                        subtitle_index += 1
            
            # Записываем результат в файл
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\\n".join(srt_lines))
                
            logger.info(f"Файл субтитров SRT сохранен в: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Ошибка при создании файла субтитров SRT: {str(e)}")
            raise
    
    def _format_srt_time(self, seconds):
        """
        Форматирует время в секундах в формат SRT: HH:MM:SS,mmm
        
        Args:
            seconds: время в секундах
            
        Returns:
            str: время в формате SRT
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds_remainder = seconds % 60
        milliseconds = int((seconds_remainder - int(seconds_remainder)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(seconds_remainder):02d},{milliseconds:03d}"
    
    def import_lyrics_with_synchronization(self, lyrics_file_path):
        """
        Импортирует текст с готовой синхронизацией (LRC формат)
        
        Args:
            lyrics_file_path: путь к файлу LRC
            
        Returns:
            dict: словарь с текстом и временными метками
        """
        logger.info(f"Импорт синхронизированного текста из: {lyrics_file_path}")
        
        try:
            with open(lyrics_file_path, 'r', encoding='utf-8') as f:
                lrc_content = f.read()
                
            # Паттерн для LRC формата: [MM:SS.xx] текст
            pattern = r'\\[(\\d+):(\\d+\\.?\\d*)\\]\\s*(.+)'
            matches = re.findall(pattern, lrc_content)
            
            result = {
                'segments': []
            }
            
            for match in matches:
                minutes = int(match[0])
                seconds = float(match[1])
                text = match[2].strip()
                
                time_seconds = minutes * 60 + seconds
                
                # Добавляем сегмент
                result['segments'].append({
                    'start': time_seconds,
                    'text': text
                })
                
            # Рассчитываем конечные времена для сегментов
            for i in range(len(result['segments']) - 1):
                result['segments'][i]['end'] = result['segments'][i+1]['start']
                
            # Последний сегмент получает конечное время с небольшим отступом
            if result['segments']:
                last_segment = result['segments'][-1]
                last_segment['end'] = last_segment['start'] + 5.0  # По умолчанию 5 секунд
                
            logger.info(f"Импортировано {len(result['segments'])} сегментов текста с временными метками")
            return result
        except Exception as e:
            logger.error(f"Ошибка при импорте синхронизированного текста: {str(e)}")
            raise
''')

