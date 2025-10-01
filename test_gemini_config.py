#!/usr/bin/env python3
"""
Script para testar a configuração do Gemini
"""
import sys
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

def test_env_file():
    """Testa se o arquivo .env existe e tem as configurações necessárias"""
    print("🔍 Verificando arquivo .env...")
    
    try:
        from dotenv import load_dotenv
        import os
        
        # Carregar variáveis de ambiente
        load_dotenv()
        
        # Verificar configurações essenciais
        required_vars = [
            'GEMINI_API_KEY',
            'GEMINI_MODEL',
            'GEMINI_MAX_OUTPUT_TOKENS',
            'GEMINI_TEMPERATURE',
            'GEMINI_STREAMING_ENABLED'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Variáveis ausentes: {', '.join(missing_vars)}")
            return False
        
        print("✅ Arquivo .env carregado com sucesso!")
        print(f"   Modelo: {os.getenv('GEMINI_MODEL')}")
        print(f"   Max Tokens: {os.getenv('GEMINI_MAX_OUTPUT_TOKENS')}")
        print(f"   Temperature: {os.getenv('GEMINI_TEMPERATURE')}")
        print(f"   Streaming: {os.getenv('GEMINI_STREAMING_ENABLED')}")
        
        return True
        
    except ImportError:
        print("❌ python-dotenv não instalado. Execute: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Erro ao carregar .env: {e}")
        return False

def test_config_class():
    """Testa se a classe Config está funcionando"""
    print("\n🔍 Testando classe Config...")
    
    try:
        from config import config
        
        print("✅ Classe Config carregada com sucesso!")
        print(f"   Gemini Model: {config.GEMINI_MODEL}")
        print(f"   Max Output Tokens: {config.GEMINI_MAX_OUTPUT_TOKENS}")
        print(f"   Temperature: {config.GEMINI_TEMPERATURE}")
        print(f"   Streaming Enabled: {config.GEMINI_STREAMING_ENABLED}")
        
        # Validar configurações
        issues = config.validate_config()
        if issues:
            print("\n⚠️ Problemas encontrados:")
            for issue in issues:
                print(f"   {issue}")
        else:
            print("✅ Todas as configurações estão válidas!")
        
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ Erro ao testar Config: {e}")
        return False

def test_gemini_integration():
    """Testa se a integração com Gemini está funcionando"""
    print("\n🔍 Testando integração Gemini...")
    
    try:
        from gemini_integration import GeminiIntegration
        
        # Criar instância (sem API key para teste)
        gemini = GeminiIntegration()
        
        print("✅ Classe GeminiIntegration carregada com sucesso!")
        
        # Verificar se API key está configurada
        if gemini.api_key and gemini.api_key != 'your_gemini_api_key_here':
            print("✅ API key configurada!")
            
            # Testar inicialização
            if gemini.is_available():
                print("✅ Gemini disponível!")
                
                # Teste simples
                response = gemini.generate_response("Teste de conexão")
                if response.get('success'):
                    print("✅ Teste de resposta bem-sucedido!")
                    print(f"   Resposta: {response['response'][:100]}...")
                else:
                    print(f"⚠️ Erro na resposta: {response.get('error', 'Erro desconhecido')}")
            else:
                print("❌ Gemini não disponível")
        else:
            print("⚠️ API key não configurada ou usando valor padrão")
            print("   Configure GEMINI_API_KEY no arquivo .env")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar Gemini: {e}")
        return False

def main():
    """Função principal"""
    print("🤖 Teste de Configuração do Gemini")
    print("=" * 50)
    
    tests = [
        ("Arquivo .env", test_env_file),
        ("Classe Config", test_config_class),
        ("Integração Gemini", test_gemini_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado em {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(results)} testes passaram")
    
    if passed == len(results):
        print("\n🎉 Todos os testes passaram! Sua configuração está pronta!")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique as configurações acima.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
