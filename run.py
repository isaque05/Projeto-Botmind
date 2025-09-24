#!/usr/bin/env python3
"""
Script de inicialização do ChatBot
"""
import sys
import os
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Função principal de inicialização"""
    print("🤖 Iniciando ChatBot Inteligente...")
    print("=" * 50)
    
    try:
        # Importar e executar a aplicação
        from app import app, db_manager, config
        
        # Validar configurações
        config_issues = config.validate_config()
        if config_issues:
            print("⚠️ Avisos de configuração:")
            for issue in config_issues:
                print(f"  {issue}")
            print()
        
        # Verificar banco de dados
        if db_manager.test_connection():
            print("✅ Banco de dados conectado")
        else:
            print("❌ Erro na conexão com banco de dados")
            return
        
        # Inicializar banco se necessário
        db_manager.init_database()
        print("✅ Banco de dados inicializado")
        
        # Mostrar informações da aplicação
        print(f"🌐 Servidor: http://{config.HOST}:{config.PORT}")
        print(f"🔧 Modo: {'Desenvolvimento' if config.DEBUG else 'Produção'}")
        print(f"🤖 Gemini: {'Ativado' if config.GEMINI_API_KEY else 'Desativado'}")
        print("=" * 50)
        print("✨ ChatBot pronto! Acesse o navegador para começar a conversar.")
        print("💡 Dica: Use Ctrl+C para parar o servidor")
        print()
        
        # Executar aplicação
        app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
        
    except KeyboardInterrupt:
        print("\n👋 ChatBot encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar ChatBot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
