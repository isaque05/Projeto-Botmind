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
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    GEMINI_MAX_OUTPUT_TOKENS = int(os.getenv('GEMINI_MAX_OUTPUT_TOKENS', 256))
    GEMINI_TEMPERATURE = float(os.getenv('GEMINI_TEMPERATURE', 0.7))
    GEMINI_STREAMING_ENABLED = os.getenv('GEMINI_STREAMING_ENABLED', 'true').lower() == 'true'
    GEMINI_SYSTEM_PROMPT = os.getenv('GEMINI_SYSTEM_PROMPT')
    GEMINI_SAFETY_SETTINGS_ENABLED = os.getenv('GEMINI_SAFETY_SETTINGS_ENABLED', 'true').lower() == 'true'
    GEMINI_SAFETY_CATEGORIES = os.getenv('GEMINI_SAFETY_CATEGORIES', '').split(',') if os.getenv('GEMINI_SAFETY_CATEGORIES') else []
    GEMINI_LOG_REQUESTS = os.getenv('GEMINI_LOG_REQUESTS', 'true').lower() == 'true'
    
    # Configurações de segurança
    MAX_MESSAGE_LENGTH = 2000
    MAX_HISTORY_MESSAGES = 100
    
    # Configurações de UI
    AUTO_SCROLL_ENABLED = os.getenv('AUTO_SCROLL_ENABLED', 'true').lower() == 'true'
    SOUND_NOTIFICATIONS_ENABLED = os.getenv('SOUND_NOTIFICATIONS_ENABLED', 'true').lower() == 'true'
    
    # Configurações de Log
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate_config(cls):
        """Valida as configurações da aplicação"""
        issues = []
        
        if cls.SECRET_KEY == 'your-secret-key-change-this':
            issues.append("[AVISO] SECRET_KEY não foi alterada - use uma chave segura em produção")
        
        if not cls.GEMINI_API_KEY:
            issues.append("[INFO] GEMINI_API_KEY não configurada - Gemini não estará disponível")
        elif cls.GEMINI_API_KEY == 'your_gemini_api_key_here':
            issues.append("[AVISO] GEMINI_API_KEY não foi configurada - substitua pela sua chave real")
        
        # Validar configurações do Gemini
        if cls.GEMINI_TEMPERATURE < 0 or cls.GEMINI_TEMPERATURE > 2:
            issues.append("[AVISO] GEMINI_TEMPERATURE deve estar entre 0 e 2")
        
        if cls.GEMINI_MAX_OUTPUT_TOKENS < 1 or cls.GEMINI_MAX_OUTPUT_TOKENS > 8192:
            issues.append("[AVISO] GEMINI_MAX_OUTPUT_TOKENS deve estar entre 1 e 8192")
        
        # Validar nível de log
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if cls.LOG_LEVEL not in valid_log_levels:
            issues.append(f"[AVISO] LOG_LEVEL deve ser um dos seguintes: {', '.join(valid_log_levels)}")
        
        return issues

# Instância de configuração
config = Config()
