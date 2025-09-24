@echo off
echo 🤖 Instalando dependencias do ChatBot...
echo.

REM Verificar se Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python nao encontrado! Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

echo ✅ Python encontrado
echo.

REM Instalar dependencias
echo 📦 Instalando dependencias...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Erro ao instalar dependencias
    pause
    exit /b 1
)

echo.
echo ✅ Dependencias instaladas com sucesso!
echo.
echo 🚀 Para executar o ChatBot, use: python run.py
echo.
pause
