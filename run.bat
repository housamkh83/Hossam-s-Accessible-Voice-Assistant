@echo off
chcp 65001
title Hossam Fadl Kaddour
cls
echo ================================================
echo   Enhanced Multilingual Voice Assistant
echo   Programmer: Hossam Fadl Kaddour
echo ================================================
echo.

:: Check for Python installation
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed on your system
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b
    )
)

:: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

:: Check pip installation
if not exist "venv\Scripts\pip.exe" (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b
)

echo [INFO] Installing requirements...
echo [NOTE] Download time may vary depending on internet speed...

:: Upgrade pip first
python -m pip install --upgrade pip

:: Remove existing PyAudio and PortAudio installations
pip uninstall -y pyaudio portaudio

:: Install Microsoft Visual C++ Build Tools first
pip install -q wheel setuptools

:: Install PortAudio manually first
echo [INFO] Installing PortAudio...
pip install -q pipwin
pipwin install pyaudio

:: Install other required libraries with specific versions
pip install -q SpeechRecognition==3.10.0
pip install -q gTTS==2.4.0
pip install -q sounddevice==0.4.6
pip install -q soundfile==0.12.1
pip install -q numpy==1.24.3
pip install -q pygame==2.5.2
pip install -q deep-translator==1.11.4
pip install -q cffi==1.16.0
pip install -q python-bidi==0.4.2
pip install -q arabic-reshaper==3.0.0

:: Launch application
echo.
echo [INFO] Starting Enhanced Multilingual Voice Assistant...
echo [NOTE] Make sure your microphone is properly connected and set as default device
echo.
python assistant.py

:: Error handling
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] An error occurred while running the application
    echo.
    echo Common solutions for audio device errors:
    echo 1. Check if your microphone is properly connected
    echo 2. Set your microphone as the default recording device in Windows
    echo 3. Try a different USB port if using a USB microphone
    echo 4. Update your audio drivers
    echo 5. Check Windows Privacy Settings to allow microphone access
    echo.
    echo Technical details:
    echo - If you see error -9999, it means the audio device initialization failed
    echo - Check Windows Sound settings ^> Recording devices
    echo - Try running 'python -m sounddevice' to list available devices
    pause
)

:: Deactivate virtual environment
deactivate