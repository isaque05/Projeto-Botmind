import random
import json
from datetime import datetime
from typing import Dict, List, Optional
from database import DatabaseManager
from gemini_integration import GeminiIntegration

class ChatBot:
    """
    Classe principal do chatbot que gerencia a lógica de conversação
    e integração com diferentes fontes de resposta
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.responses = self._load_responses()
        self.gemini_integration = None
        self._initialize_gemini()
        
    def _load_responses(self) -> Dict[str, List[str]]:
        """Carrega respostas padrão do chatbot"""
        return {
            'greeting': [
                "Olá! Como posso ajudá-lo hoje?",
                "Oi! Estou aqui para conversar com você!",
                "Olá! Que bom te ver por aqui!"
            ],
            'how_works': [
                "Sou um chatbot inteligente que pode conversar sobre diversos tópicos. Posso responder perguntas, contar curiosidades e até mesmo usar IA avançada quando necessário!",
                "Funciono através de processamento de linguagem natural e posso me conectar com APIs como o Gemini para respostas mais sofisticadas.",
                "Sou programado para entender contexto e manter conversas naturais. Use a opção 'Usar Gemini AI' para respostas mais avançadas!"
            ],
            'curiosity': [
                "Você sabia que o cérebro humano tem cerca de 86 bilhões de neurônios?",
                "Curiosidade: A língua de uma girafa pode medir até 50 centímetros!",
                "Interessante: O coração de uma baleia azul é tão grande que um humano poderia nadar através de suas artérias!",
                "Fato curioso: O mel nunca estraga - arqueólogos encontraram mel comestível em tumbas egípcias de 3000 anos!"
            ],
            'gemini_info': [
                "O Gemini é uma IA avançada do Google que pode gerar respostas mais sofisticadas e contextualizadas. Quando ativado, suas perguntas serão processadas por essa IA para respostas mais detalhadas.",
                "Para usar o Gemini, marque a opção 'Usar Gemini AI' antes de enviar sua mensagem. Isso permitirá respostas mais inteligentes e contextualizadas!",
                "O Gemini pode ajudar com análises complexas, explicações detalhadas e respostas mais criativas. Experimente ativá-lo para uma experiência mais avançada!"
            ],
            'default': [
                "Interessante! Pode me contar mais sobre isso?",
                "Entendo. Como posso ajudá-lo melhor?",
                "Que legal! Tem mais alguma coisa que gostaria de saber?",
                "Obrigado por compartilhar! O que mais posso fazer por você?"
            ]
        }
    
    def process_message(self, message: str, user_id: str, use_gemini: bool = False) -> Dict:
        """
        Processa uma mensagem do usuário e retorna uma resposta
        
        Args:
            message: Mensagem do usuário
            user_id: ID do usuário
            use_gemini: Se deve usar integração com Gemini
            
        Returns:
            Dict com resposta, timestamp e ID da mensagem
        """
        try:
            # Salvar mensagem do usuário
            user_message_id = self.db_manager.save_message(
                user_id=user_id,
                message=message,
                is_user=True
            )
            
            # Gerar resposta
            if use_gemini and self.gemini_integration and self.gemini_integration.is_available():
                print("[GEMINI] Chamando Gemini para gerar resposta...")
                response_text = self._get_gemini_response(message, user_id)
            else:
                if use_gemini:
                    print("[GEMINI] Gemini não disponível, usando resposta padrão")
                response_text = self._get_default_response(message)
            
            # Salvar resposta do bot
            bot_message_id = self.db_manager.save_message(
                user_id=user_id,
                message=response_text,
                is_user=False,
                parent_message_id=user_message_id
            )
            
            return {
                'message': response_text,
                'timestamp': datetime.now().isoformat(),
                'message_id': bot_message_id
            }
            
        except Exception as e:
            error_response = "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente!"
            return {
                'message': error_response,
                'timestamp': datetime.now().isoformat(),
                'message_id': None
            }
    
    def _get_default_response(self, message: str) -> str:
        """Gera resposta padrão baseada na mensagem"""
        message_lower = message.lower()
        
        # Detectar intenções
        if any(word in message_lower for word in ['olá', 'oi', 'hello', 'hi']):
            return random.choice(self.responses['greeting'])
        
        elif any(word in message_lower for word in ['como', 'funciona', 'funcionar']):
            return random.choice(self.responses['how_works'])
        
        elif any(word in message_lower for word in ['curiosidade', 'curioso', 'sabia', 'fato']):
            return random.choice(self.responses['curiosity'])
        
        elif any(word in message_lower for word in ['gemini', 'ia', 'inteligência']) and 'conte' not in message_lower and 'piada' not in message_lower:
            return random.choice(self.responses['gemini_info'])
        
        else:
            return random.choice(self.responses['default'])
    
    def _initialize_gemini(self):
        """Inicializa integração com Gemini se disponível"""
        try:
            # Tentar obter chave da API do banco de dados
            api_key = self.db_manager.get_system_config('gemini_api_key')
            
            if api_key:
                self.gemini_integration = GeminiIntegration(api_key)
                if self.gemini_integration.is_available():
                    print("[OK] Integração Gemini ativada!")
                else:
                    print("[AVISO] Gemini configurado mas não disponível")
            else:
                print("[INFO] Gemini não configurado - usando respostas padrão")
                
        except Exception as e:
            print(f"[ERRO] Erro ao inicializar Gemini: {e}")
            self.gemini_integration = None
    
    def _get_gemini_response(self, message: str, user_id: str = 'current_user') -> str:
        """
        Gera resposta usando integração com Gemini
        """
        if not self.gemini_integration or not self.gemini_integration.is_available():
            print("[GEMINI] Fallback para resposta padrão - Gemini não disponível")
            return self._get_default_response(message)
        
        try:
            # Obter contexto da conversa recente
            context = self._get_conversation_context_for_gemini(user_id)
            print(f"[GEMINI] Contexto da conversa obtido: {len(context)} caracteres")
            
            # Gerar resposta com Gemini
            response = self.gemini_integration.generate_response(message, context)
            
            if response.get('success', False):
                return response['response']
            else:
                print(f"[GEMINI] Fallback para resposta padrão - Gemini falhou: {response.get('error', 'Erro desconhecido')}")
                # Se for erro de quota, mostrar mensagem específica
                if 'quota' in response.get('error', '').lower() or '429' in response.get('error', ''):
                    return "Desculpe, o limite diário de requisições foi excedido. Tente novamente amanhã ou considere usar um plano pago."
                return self._get_default_response(message)
                
        except Exception as e:
            print(f"Erro ao usar Gemini: {e}")
            return self._get_default_response(message)
    
    def _get_conversation_context_for_gemini(self, user_id: str = 'current_user') -> str:
        """Obtém contexto da conversa para o Gemini"""
        try:
            # Pegar as últimas 6 mensagens para dar contexto ao Gemini
            recent_messages = self.db_manager.get_recent_messages(user_id, 6)
            if not recent_messages:
                return ""
            
            # Construir contexto da conversa
            context_parts = []
            for msg in recent_messages[-6:]:  # Pegar apenas as últimas 6 mensagens
                role = "Usuário" if msg['is_user'] else "Assistente"
                context_parts.append(f"{role}: {msg['message']}")
            
            return "\n".join(context_parts)
        except Exception as e:
            print(f"[GEMINI] Erro ao obter contexto: {e}")
            return ""
    
    def set_gemini_integration(self, gemini_client):
        """Define o cliente Gemini para integração futura"""
        self.gemini_integration = gemini_client
    
    def get_conversation_context(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Obtém contexto da conversa recente"""
        return self.db_manager.get_recent_messages(user_id, limit)
