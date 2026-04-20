@echo off
setlocal

cd /d "%~dp0"

echo [1/3] PyInstaller kontrol ediliyor...
python -m pip show pyinstaller >nul 2>nul
if errorlevel 1 (
    echo PyInstaller bulunamadi, yukleniyor...
    python -m pip install pyinstaller
)

echo [2/3] Eski build klasorleri temizleniyor...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "ScreenTranslator.spec" del /q "ScreenTranslator.spec"

echo [3/3] EXE olusturuluyor...
python -m PyInstaller --noconfirm --windowed --onefile --name "ScreenTranslator" main.py

if exist "dist\ScreenTranslator.exe" (
    echo.
    echo Basarili: dist\ScreenTranslator.exe olusturuldu.
    echo Bu dosyayi masaustune kisayol yapip uygulama gibi kullanabilirsin.
) else (
    echo.
    echo Hata: EXE olusturulamadi.
)

echo.
pause
