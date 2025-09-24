#!/bin/bash

echo "🤖 Instalando dependências do ChatBot..."
echo

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python não encontrado! Instale Python 3.8+ primeiro."
    exit 1
fi

echo "✅ Python encontrado"
echo

# Instalar dependências
echo "📦 Instalando dependências..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências"
    exit 1
fi

echo
echo "✅ Dependências instaladas com sucesso!"
echo
echo "🚀 Para executar o ChatBot, use: python3 run.py"
echo
