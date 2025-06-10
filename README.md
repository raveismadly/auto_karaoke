## Возможности

- 🎵 **Автоматическое отделение вокала от музыки** с помощью Demucs
- 🎤 **Распознавание текста песни** с использованием OpenAI Whisper
- 📹 **Создание караоке-видео** с синхронизированным текстом
- 🌍 **Поддержка разных языков** (русский, английский и многие другие)
- 📊 **Визуализация аудио** для создания фонового видео
- ⚙️ **Гибкие настройки** (громкость вокала, язык, параметры отображения)

## Системные требования

- macOS 10.15 (Catalina) или новее
- Python 3.9 или новее (но ниже 3.12)
- 4 ГБ свободной оперативной памяти
- FFmpeg

## Установка

### Автоматическая установка (рекомендуется)

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/autokaraoke/autokaraoke.git
   cd autokaraoke
   ```

2. Запустите скрипт установки:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

### Установка с помощью Make

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/autokaraoke/autokaraoke.git
   cd autokaraoke
   ```

2. Установите через Makefile:
   ```bash
   make install
   ```

3. Запустите приложение:
   ```bash
   make run
   ```

### Ручная установка

1. Установите Homebrew (если еще не установлен):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Установите FFmpeg:
   ```bash
   brew install ffmpeg
   ```

3. Создайте виртуальное окружение:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Установите зависимости:
   ```bash
   pip install -e .
   ```

## Использование

1. Запустите приложение:
   ```bash
   source venv/bin/activate
   autokaraoke
   ```

2. В открывшемся интерфейсе:
   - Выберите аудио или видео файл
   - Укажите директорию для сохранения результатов
   - Настройте параметры (модель распознавания, язык, включение вокала)
   - Нажмите "Создать караоке"

3. После завершения обработки караоке-видео будет сохранено в указанной директории.

## Решение проблем

### Проблемы с FFmpeg

Если возникают ошибки связанные с FFmpeg:
```bash
brew reinstall ffmpeg
```

### Проблемы с установкой Demucs

Если при установке Demucs возникают ошибки:
```bash
pip install torch==2.0.1 torchaudio==2.0.2
pip install demucs
```

### Ошибка MemoryError

Если возникает ошибка о нехватке памяти:
- Закройте другие приложения для освобождения RAM
- Используйте модель меньшего размера (tiny или base вместо small/medium/large)

### Проблемы с библиотекой tk

Если возникает ошибка `_tkinter.TclError: no display name and no $DISPLAY environment variable`:
```bash
brew install python-tk
```

## Структура проекта

```
autokaraoke/
├── __init__.py
├── main.py              # Основной файл с GUI
├── audio_processor.py   # Модуль для обработки аудио
├── text_recognizer.py   # Модуль для распознавания текста
├── karaoke_generator.py # Модуль для создания караоке
└── utils.py             # Вспомогательные функции
```

## Лицензия