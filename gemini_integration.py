"""
Módulo para integração futura com a API do Google Gemini
"""
import os
from typing import Optional, Dict, Any
import google.generativeai as genai
from datetime import datetime

class GeminiIntegration:
    """
    Classe para integração com a API do Google Gemini
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        self.chat_session = None
        
        if self.api_key:
            self.initialize_gemini()
    
    def initialize_gemini(self):
        """Inicializa a conexão com a API do Gemini"""
        try:
            from config import config
            
            genai.configure(api_key=self.api_key)
            # Usar configurações do arquivo .env
            self.model = genai.GenerativeModel(config.GEMINI_MODEL)
            print(f"[OK] Gemini API inicializada com sucesso! Modelo: {config.GEMINI_MODEL}")
        except Exception as e:
            print(f"[ERRO] Erro ao inicializar Gemini API: {e}")
            self.model = None
    
    def generate_response(self, message: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Gera resposta usando a API do Gemini
        
        Args:
            message: Mensagem do usuário
            context: Contexto adicional da conversa
            
        Returns:
            Dict com resposta e metadados
        """
        if not self.model:
            return {
                'response': 'Desculpe, a integração com Gemini não está disponível no momento.',
                'error': 'Gemini API não inicializada',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Instrução de idioma: garantir respostas em pt-BR
            language_instruction = (
                "Responda em português brasileiro. Seja conciso mas natural. "
                "Máximo 2-3 frases. Vá direto ao ponto. Use emojis se apropriado. "
                "Seja amigável e útil."
            )

            # Preparar prompt com contexto se disponível
            if context:
                prompt = (
                    f"{language_instruction}\n\n"
                    f"Contexto da conversa (resuma se necessário):\n{context}\n\n"
                    f"Mensagem do usuário: {message}"
                )
            else:
                prompt = f"{language_instruction}\n\nMensagem do usuário: {message}"
            
            # Usar configurações do .env
            from config import config
            
            # Gerar resposta com configurações otimizadas
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'max_output_tokens': 50,  # Limitar a 50 tokens para respostas curtas
                    'temperature': 0.3,  # Criatividade moderada para respostas naturais
                    'top_p': 0.7,  # Focar nas respostas mais prováveis
                    'top_k': 10   # Limitar opções de vocabulário
                }
            )
            
            # Limpar e formatar o texto da resposta
            clean_text = self._clean_response_text(response.text)
            
            return {
                'response': clean_text,
                'timestamp': datetime.now().isoformat(),
                'model': getattr(self.model, 'model_name', os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')),
                'success': True
            }
            
        except Exception as e:
            error_msg = str(e)
            
            # Tratar erros específicos
            if 'quota' in error_msg.lower() or '429' in error_msg:
                return {
                    'response': 'Desculpe, o limite diário de requisições foi excedido. Tente novamente amanhã ou considere usar um plano pago.',
                    'error': 'Quota exceeded',
                    'timestamp': datetime.now().isoformat(),
                    'success': False
                }
            elif 'api key' in error_msg.lower() or 'invalid' in error_msg.lower():
                return {
                    'response': 'Erro de configuração da API. Verifique se a chave da API está correta.',
                    'error': 'Invalid API key',
                    'timestamp': datetime.now().isoformat(),
                    'success': False
                }
            else:
                return {
                    'response': f'Desculpe, ocorreu um erro ao processar sua mensagem: {error_msg}',
                    'error': error_msg,
                    'timestamp': datetime.now().isoformat(),
                    'success': False
                }
    
    def start_chat_session(self, system_prompt: Optional[str] = None):
        """
        Inicia uma nova sessão de chat com o Gemini
        
        Args:
            system_prompt: Prompt do sistema para definir comportamento
        """
        if not self.model:
            return False
        
        try:
            # Prompt padrão para forçar pt-BR
            default_system = (
                "Você é um assistente que SEMPRE responde em português do Brasil (pt-BR). "
                "Use tom claro e natural brasileiro."
            )
            use_prompt = system_prompt or default_system
            self.chat_session = self.model.start_chat(history=[])
            # Enviar prompt do sistema como primeira mensagem
            self.chat_session.send_message(use_prompt)
            
            return True
        except Exception as e:
            print(f"Erro ao iniciar sessão de chat: {e}")
            return False
    
    def send_message_to_session(self, message: str) -> Dict[str, Any]:
        """
        Envia mensagem para a sessão de chat ativa
        
        Args:
            message: Mensagem do usuário
            
        Returns:
            Dict com resposta e metadados
        """
        if not self.chat_session:
            return self.generate_response(message)
        
        try:
            response = self.chat_session.send_message(message)
            
            return {
                'response': response.text,
                'timestamp': datetime.now().isoformat(),
                'model': 'gemini-pro',
                'success': True,
                'session_active': True
            }
            
        except Exception as e:
            return {
                'response': f'Erro na sessão de chat: {str(e)}',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'success': False
            }
    
    def get_chat_history(self) -> list:
        """Obtém histórico da sessão de chat atual"""
        if not self.chat_session:
            return []
        
        try:
            return self.chat_session.history
        except Exception as e:
            print(f"Erro ao obter histórico: {e}")
            return []
    
    def clear_chat_session(self):
        """Limpa a sessão de chat atual"""
        self.chat_session = None
    
    def _clean_response_text(self, text: str) -> str:
        """Limpa e formata o texto da resposta"""
        import re
        
        # Remover caracteres de controle e espaços excessivos
        text = re.sub(r'\s+', ' ', text)
        
        # Corrigir espaçamento antes de pontuação
        text = re.sub(r'\s+([.!?])', r'\1', text)
        
        # Corrigir espaçamento após pontuação
        text = re.sub(r'([.!?])([A-Za-z])', r'\1 \2', text)
        
        # Remover asteriscos duplos e formatação markdown desnecessária
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        
        # Remover quebras de linha desnecessárias
        text = re.sub(r'\n+', ' ', text)
        
        # Corrigir espaçamento antes de vírgulas e dois pontos
        text = re.sub(r'\s+([,;:])', r'\1', text)
        text = re.sub(r'([,;:])([A-Za-z])', r'\1 \2', text)
        
        # Remover pontos duplos e caracteres estranhos
        text = re.sub(r'\.+', '.', text)
        text = re.sub(r'\?+', '?', text)
        text = re.sub(r'!+', '!', text)
        
        # Limpar espaços no início e fim
        text = text.strip()
        
        # Garantir que frases terminem com pontuação
        if text and not text.endswith(('.', '!', '?', ':', ';')):
            text += '.'
        
        return text
    
    def is_available(self) -> bool:
        """Verifica se a integração com Gemini está disponível"""
        return self.model is not None and self.api_key is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obtém informações sobre o modelo Gemini"""
        if not self.model:
            return {'available': False}
        
        from config import config
        
        return {
            'available': True,
            'model_name': config.GEMINI_MODEL,
            'api_key_set': bool(self.api_key),
            'chat_session_active': self.chat_session is not None,
            'max_output_tokens': config.GEMINI_MAX_OUTPUT_TOKENS,
            'temperature': config.GEMINI_TEMPERATURE,
            'streaming_enabled': config.GEMINI_STREAMING_ENABLED
        }

    def generate_stream(self, message: str, context: Optional[str] = None):
        """
        Gera resposta em streaming (yield de trechos de texto) usando a API do Gemini
        """
        if not self.model:
            yield ''
            return
        # Instrução fixa para pt-BR
        language_instruction = (
            "Você é um assistente que SEMPRE responde em português do Brasil (pt-BR). "
            "Use vocabulário e convenções brasileiras."
        )
        if context:
            prompt = (
                f"{language_instruction}\n\n"
                f"Contexto da conversa (resuma se necessário):\n{context}\n\n"
                f"Mensagem do usuário: {message}"
            )
        else:
            prompt = f"{language_instruction}\n\nMensagem do usuário: {message}"
        try:
            from config import config
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    'max_output_tokens': 50,  # Limitar a 50 tokens para respostas curtas
                    'temperature': 0.3,  # Criatividade moderada para respostas naturais
                    'top_p': 0.7,  # Focar nas respostas mais prováveis
                    'top_k': 10   # Limitar opções de vocabulário
                },
                stream=True
            )
            for chunk in response:
                try:
                    if hasattr(chunk, 'text') and chunk.text:
                        # Limpar e formatar o texto do chunk
                        clean_text = self._clean_response_text(chunk.text)
                        yield clean_text
                except Exception:
                    continue
        except Exception as e:
            error_msg = str(e)
            
            # Tratar erros específicos
            if 'quota' in error_msg.lower() or '429' in error_msg:
                yield "Desculpe, o limite diário de requisições foi excedido. Tente novamente amanhã."
            elif 'api key' in error_msg.lower() or 'invalid' in error_msg.lower():
                yield "Erro de configuração da API. Verifique se a chave está correta."
            else:
                yield f"Erro ao processar mensagem: {error_msg}"

# Função para configurar Gemini no chatbot principal
def setup_gemini_in_chatbot(chatbot_instance, api_key: Optional[str] = None):
    """
    Configura a integração Gemini no chatbot principal
    
    Args:
        chatbot_instance: Instância do ChatBot
        api_key: Chave da API do Gemini (opcional)
    """
    try:
        gemini = GeminiIntegration(api_key)
        if gemini.is_available():
            chatbot_instance.set_gemini_integration(gemini)
            print("[OK] Integração Gemini configurada com sucesso!")
            return True
        else:
            print("[AVISO] Gemini não disponível - usando respostas padrão")
            return False
    except Exception as e:
        print(f"[ERRO] Erro ao configurar Gemini: {e}")
        return False

# Exemplo de uso
if __name__ == "__main__":
    # Teste da integração
    gemini = GeminiIntegration()
    
    if gemini.is_available():
        print("Testando integração com Gemini...")
        response = gemini.generate_response("Olá! Como você funciona?")
        print(f"Resposta: {response['response']}")
    else:
        print("Gemini não disponível. Configure a variável GEMINI_API_KEY.")
