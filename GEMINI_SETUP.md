# 🤖 Configuração do Google Gemini

Este guia explica como configurar a integração com o Google Gemini no seu chatbot.

## 📋 Pré-requisitos

1. **Conta Google**: Você precisa de uma conta Google ativa
2. **API Key do Gemini**: Obtenha sua chave de API gratuita

## 🔑 Como obter a API Key do Gemini

1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada

## ⚙️ Configuração

### 1. Arquivo .env

O projeto já inclui um arquivo `.env` com todas as configurações necessárias. Você só precisa:

1. **Abrir o arquivo `.env`**
2. **Substituir `your_gemini_api_key_here` pela sua chave real**
3. **Ajustar outras configurações conforme necessário**

### 2. Configurações Disponíveis

```env
# Chave da API (OBRIGATÓRIA)
GEMINI_API_KEY=sua_chave_aqui

# Modelo do Gemini
GEMINI_MODEL=gemini-1.5-flash  # ou gemini-1.5-pro, gemini-1.0-pro

# Configurações de geração
GEMINI_MAX_OUTPUT_TOKENS=256   # Máximo de tokens na resposta
GEMINI_TEMPERATURE=0.7         # Criatividade (0.0 a 2.0)

# Streaming de respostas
GEMINI_STREAMING_ENABLED=true  # Respostas em tempo real

# Configurações de segurança
GEMINI_SAFETY_SETTINGS_ENABLED=true
```

### 3. Modelos Disponíveis

| Modelo | Descrição | Velocidade | Qualidade |
|--------|-----------|------------|-----------|
| `gemini-1.5-flash` | Mais rápido, ideal para chat | ⚡⚡⚡ | ⭐⭐⭐ |
| `gemini-1.5-pro` | Mais preciso, melhor qualidade | ⚡⚡ | ⭐⭐⭐⭐ |
| `gemini-1.0-pro` | Versão anterior, estável | ⚡ | ⭐⭐⭐ |

## 🚀 Testando a Configuração

### Método 1: Script de Teste
```bash
python setup_gemini.py
```

### Método 2: Teste Manual
```python
from gemini_integration import GeminiIntegration

# Testar integração
gemini = GeminiIntegration()
if gemini.is_available():
    response = gemini.generate_response("Olá! Como você está?")
    print(response['response'])
else:
    print("Gemini não configurado corretamente")
```

## 🔧 Configurações Avançadas

### Personalizar Prompt do Sistema
```env
GEMINI_SYSTEM_PROMPT=Você é um assistente especializado em programação Python...
```

### Configurar Segurança
```env
# Filtrar conteúdo inadequado
GEMINI_SAFETY_CATEGORIES=HARM_CATEGORY_HARASSMENT,HARM_CATEGORY_HATE_SPEECH
```

### Ajustar Performance
```env
# Para respostas mais rápidas
GEMINI_MAX_OUTPUT_TOKENS=128
GEMINI_TEMPERATURE=0.3

# Para respostas mais criativas
GEMINI_MAX_OUTPUT_TOKENS=512
GEMINI_TEMPERATURE=1.0
```

## 🐛 Solução de Problemas

### Erro: "API key not found"
- ✅ Verifique se a chave está no arquivo `.env`
- ✅ Confirme que não há espaços extras na chave
- ✅ Reinicie a aplicação após alterar o `.env`

### Erro: "Model not found"
- ✅ Verifique se o modelo está correto no `.env`
- ✅ Use apenas modelos suportados: `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-1.0-pro`

### Respostas muito lentas
- ✅ Use `gemini-1.5-flash` em vez de `gemini-1.5-pro`
- ✅ Reduza `GEMINI_MAX_OUTPUT_TOKENS`
- ✅ Ative `GEMINI_STREAMING_ENABLED=true`

### Respostas em inglês
- ✅ O sistema já está configurado para português brasileiro
- ✅ Se necessário, ajuste `GEMINI_SYSTEM_PROMPT`

## 📊 Monitoramento

### Logs de Requisições
```env
GEMINI_LOG_REQUESTS=true
LOG_LEVEL=DEBUG
```

### Verificar Status
```python
from gemini_integration import GeminiIntegration

gemini = GeminiIntegration()
info = gemini.get_model_info()
print(f"Modelo: {info['model_name']}")
print(f"Disponível: {info['available']}")
print(f"Streaming: {info['streaming_enabled']}")
```

## 🔒 Segurança

- ⚠️ **NUNCA** commite o arquivo `.env` com chaves reais
- ✅ Use `.env.example` como template
- ✅ Mantenha sua API key privada
- ✅ Monitore o uso da API no Google AI Studio

## 💡 Dicas de Uso

1. **Para desenvolvimento**: Use `gemini-1.5-flash` com `GEMINI_TEMPERATURE=0.7`
2. **Para produção**: Use `gemini-1.5-pro` com `GEMINI_TEMPERATURE=0.3`
3. **Para chat interativo**: Ative `GEMINI_STREAMING_ENABLED=true`
4. **Para respostas consistentes**: Use `GEMINI_TEMPERATURE=0.1`

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs da aplicação
2. Teste com `python setup_gemini.py`
3. Confirme se a API key está ativa no Google AI Studio
4. Verifique se há créditos disponíveis na sua conta

---

**🎉 Pronto!** Seu chatbot agora está configurado para usar o Google Gemini com todas as configurações personalizáveis via arquivo `.env`.
