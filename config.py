"""
Arquivo de configuração do ChatBot
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    """Configurações base da aplicação"""
    
    # Configurações do Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Configurações do banco de dados
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'chatbot.db')
    
    # Configurações do servidor
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Configurações do Gemini
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Configurações de segurança
    MAX_MESSAGE_LENGTH = 2000
    MAX_HISTORY_MESSAGES = 100
    
    # Configurações de UI
    AUTO_SCROLL_ENABLED = True
    SOUND_NOTIFICATIONS_ENABLED = True
    
    @classmethod
    def validate_config(cls):
        """Valida as configurações da aplicação"""
        issues = []
        
        if cls.SECRET_KEY == 'your-secret-key-change-this':
            issues.append("⚠️ SECRET_KEY não foi alterada - use uma chave segura em produção")
        
        if not cls.GEMINI_API_KEY:
            issues.append("ℹ️ GEMINI_API_KEY não configurada - Gemini não estará disponível")
        
        return issues

# Instância de configuração
config = Config()
