from setuptools import setup, find_packages

setup(
    name="autokaraoke",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "demucs>=4.0.0,<5.0.0",
        "openai-whisper>=20231117",
        "moviepy>=1.0.3",
        "numpy>=1.26.0",
        "pydub>=0.25.1",
        "librosa>=0.10.0,<0.11.0",
        "pillow>=10.0.0",
        "matplotlib>=3.8.0",
        "scikit-learn>=1.3.0",
        "tk>=0.1.0",
        "requests>=2.31.0",
        "tqdm>=4.66.0",
        "ffmpeg-python>=0.2.0",
    ],
    entry_points={
        'console_scripts': [
            'autokaraoke=autokaraoke.main:main',
        ],
    },
    python_requires='>=3.9,<3.12',
    author="AutoKaraoke Team",
    author_email="info@autokaraoke.com",
    description="Automatic karaoke generator for macOS",
    keywords="karaoke, audio, video, music",
    url="https://github.com/autokaraoke/autokaraoke",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
    ],
)
