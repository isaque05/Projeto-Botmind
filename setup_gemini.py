#!/usr/bin/env python3
"""
Script para configurar a integração com Gemini
"""
import sys
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

def setup_gemini():
    """Configura a integração com Gemini"""
    print("🤖 Configuração do Google Gemini")
    print("=" * 40)
    
    # Solicitar API key
    api_key = input("Digite sua API key do Gemini (ou pressione Enter para pular): ").strip()
    
    if not api_key:
        print("⚠️ Configuração do Gemini pulada")
        print("💡 Você pode configurar depois editando o arquivo .env ou usando a interface")
        return
    
    try:
        from database import DatabaseManager
        from config import config
        
        # Conectar ao banco
        db_manager = DatabaseManager(config.DATABASE_PATH)
        
        # Salvar API key
        success = db_manager.set_system_config('gemini_api_key', api_key)
        
        if success:
            print("✅ API key do Gemini configurada com sucesso!")
            print("🔄 Reinicie a aplicação para ativar o Gemini")
        else:
            print("❌ Erro ao salvar API key")
            
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")

def test_gemini():
    """Testa a integração com Gemini"""
    print("\n🧪 Testando integração com Gemini...")
    
    try:
        from gemini_integration import GeminiIntegration
        from database import DatabaseManager
        from config import config
        
        # Obter API key do banco
        db_manager = DatabaseManager(config.DATABASE_PATH)
        api_key = db_manager.get_system_config('gemini_api_key')
        
        if not api_key:
            print("❌ API key não encontrada. Execute setup_gemini() primeiro.")
            return
        
        # Testar integração
        gemini = GeminiIntegration(api_key)
        
        if gemini.is_available():
            print("✅ Gemini disponível!")
            
            # Teste simples
            response = gemini.generate_response("Olá! Você está funcionando?")
            print(f"🤖 Resposta: {response['response']}")
            
        else:
            print("❌ Gemini não disponível")
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")

def main():
    """Menu principal"""
    while True:
        print("\n🔧 Menu de Configuração do Gemini")
        print("1. Configurar API key")
        print("2. Testar integração")
        print("3. Sair")
        
        choice = input("\nEscolha uma opção (1-3): ").strip()
        
        if choice == '1':
            setup_gemini()
        elif choice == '2':
            test_gemini()
        elif choice == '3':
            print("👋 Até logo!")
            break
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    main()
