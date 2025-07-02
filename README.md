# Создаем README.md с инструкциями по использованию


## macOS ARM64 (M1/M2) Setup Instructions

### Prerequisites:

1. **Install Xcode Command Line Tools**: Ensure you have Xcode command line tools installed:
   ```sh
   xcode-select --install
   ```
2. **Install Homebrew**: If not installed, install Homebrew at https://brew.sh/.
3. **Python 3.12**: Required by current project dependencies.

### Quick Setup:

Execute the following commands to set up your environment with all necessary dependencies:

```sh
cd /path/to/auto_karaoke/
./launch.sh  # Installs virtualenv, adjusts for ARM64 and installs dependencies
```

### Detailed Steps:

1. **Create Python Virtual Environment**:
    ```sh
    rm -rf venv
    python3 -m venv venv
    source venv/bin/activate
    ```

2. **Install Requirements**:
    ```sh
    pip install setuptools wheel  # Essential for package compilation
    pip install -r requirements.txt  # Ensure pip is <=25.1.1 to avoid build errors
    ```

3. **Additional Packages for ARM64/Macs**:
   If `scipy` or other wheel-incompatible packages require compilation:
   ```sh
   brew install ffmpeg pkg-config    # For audio processing
   ```

### Known Issues & Solutions:

- **Numpy/Scipy ARM64**: The provided launch script ensures correct `CFLAGS` and `LDFLAGS`. If wheels aren't available, manually installing dependencies first allows for faster subsequent builds.

- **Setuptools Issues**: Recent versions of `pip`/`setuptools` may mishandle Python 3.12's build environment. Adjust via `./launch.sh` script to pin them or switch Python versions.

### Running Locally:

After the dependencies are correctly set up, execute using:

### Dockerized Version (Optional):
For consistent environment and CI/CD pipeline compatibility, see Docker guide under `docker-compose`.

Contact maintainers at [openhands@all-hands.dev](mailto:openhands@all-hands.dev) for feature requests or questions.




## Initial Setup for macOS

To ensure the project can compile successfully on macOS (especially on M1/M2 Apple Silicon), follow these instructions:

### Install Xcode Command Line Tools

First, make sure you have Xcode Command Line Tools installed. If not already installed, run the following command in Terminal:

```bash
xcode-select --install
```

**Verify Installation:**
Run `cc --version` and `clang --version` to check whether Xcode tools are available.

### Install Homebrew and Required Packages
1. Install Homebrew (if not already installed):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

2. Install Tcl/Tk dependencies:

```bash
brew install tcl-tk
```

### Using the Launch Script for macOS

Run the provided `launch.sh` script to set up your Python environment:

```bash
./launch.sh
```

**Note**: If you encounter permissions issues, ensure that you have executed:
```bash
chmod +x launch.sh
```

### Running the Application

Ensure you are in the project root directory with all dependencies and libraries met. Launch the application using:
```bash
python3 main.py
```

If you encounter any issues, double check that all the instructions have been followed and make sure all dependencies are correctly installed.

---





## MacOS Setup Instructions

1. **Homebrew Installation**:
   - Ensure you have [Homebrew](https://brew.sh/) installed.

2. **Tkinter Setup**:
   - Install Tcl/Tk dependencies via Homebrew to integrate with Python's tkinter:
     ```bash
     brew install tcl-tk


_**Note**: Ensure you have Xcode Command Line Tools installed via Terminal:
```bash
xcode-select --install
```
This resolves CCompiler failures in macOS Python builds.



     ```

3. **Python Development Environment**:
   - If using Apple Silicon (M1/M2), ensure Python is configured to use ARM64 compatibility.

4. **Command Line Tools**:
   - Confirm Command Line Tools are installed:
     ```bash
     xcode-select --install
     ```

5. **Dependencies**:
   - Run the launch script to set up the dependencies:
     ```bash
     ./launch.sh
     ```


## Описание
AutoKaraoke - это приложение для macOS, которое позволяет автоматически создавать караоке из музыкальных файлов. Приложение отделяет вокал от музыки, распознает текст песни и создает видео караоке с синхронизированным текстом.

## Требования
- macOS 10.14 или новее
- Python 3.8 или новее
- FFmpeg (установить через Homebrew: `brew install ffmpeg`)

## Установка

1. Клонируйте репозиторий или скачайте архив с файлами
2. Создайте виртуальное окружение Python (рекомендуется):
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```

## Использование

1. Запустите приложение:
   ```
   python main.py
   ```
2. В открывшемся окне выберите аудио или видео файл для создания караоке
3. Выберите директорию для сохранения результатов
4. Настройте параметры создания караоке:
    - Язык текста песни
    - Включение/исключение оригинального вокала
    - Создание визуализации аудио
    - Использование своего фонового видео (опционально)
5. Нажмите кнопку "Создать караоке"
6. Дождитесь завершения процесса

## Результаты

После успешного создания караоке в выбранной директории будут созданы следующие файлы:
- `<название_песни>_karaoke.mp4` - видео караоке с синхронизированным текстом
- `<название_песни>_lyrics.txt` - текст песни
- `<название_песни>_sync.lrc` - файл синхронизации в формате LRC
- `<название_песни>_subtitles.srt` - субтитры в формате SRT

## Возможные проблемы

### FFmpeg не найден
Убедитесь, что FFmpeg установлен и доступен в системном PATH. Для установки на macOS используйте команду:
```
brew install ffmpeg
```

### Ошибка при распознавании текста
Если текст распознается неточно, попробуйте:
1. Выбрать другой язык в настройках
2. Изменить модель распознавания в файле main.py (строка 35) с "small" на "medium" или "large" для улучшения точности распознавания

### Ошибка "RuntimeError: GPU unavailable"
Приложение работает на CPU, если GPU недоступен. Это нормальное поведение, но обработка будет занимать больше времени.

## Структура проекта

- `main.py` - основной файл с GUI интерфейсом на Tkinter
- `audio_processor.py` - модуль для отделения вокала от музыки
- `text_recognizer.py` - модуль для распознавания текста
- `karaoke_generator.py` - модуль для создания караоке видео
- `utils.py` - вспомогательные функции
- `requirements.txt` - файл с зависимостями

## Лицензия

Это приложение распространяется под лицензией MIT.
