from flask import Blueprint, jsonify, request
from src.models.message import Message, db
import uuid
import time

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat/send', methods=['POST'])
def send_message():
    """Enviar mensagem para o chatbot"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not user_message:
            return jsonify({'error': 'Mensagem não pode estar vazia'}), 400
        
        # Salvar mensagem do usuário
        user_msg = Message(
            content=user_message,
            is_user=True,
            session_id=session_id
        )
        db.session.add(user_msg)
        
        # Simular resposta do bot (aqui será integrada a API do Gemini)
        bot_response = generate_bot_response(user_message)
        
        # Salvar resposta do bot
        bot_msg = Message(
            content=bot_response,
            is_user=False,
            session_id=session_id
        )
        db.session.add(bot_msg)
        db.session.commit()
        
        return jsonify({
            'user_message': user_msg.to_dict(),
            'bot_response': bot_msg.to_dict(),
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/chat/history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    """Obter histórico de mensagens de uma sessão"""
    try:
        messages = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp).all()
        return jsonify([msg.to_dict() for msg in messages])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/chat/sessions', methods=['GET'])
def get_sessions():
    """Obter todas as sessões de chat"""
    try:
        sessions = db.session.query(Message.session_id).distinct().all()
        session_list = []
        
        for session in sessions:
            session_id = session[0]
            last_message = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp.desc()).first()
            message_count = Message.query.filter_by(session_id=session_id).count()
            
            session_list.append({
                'session_id': session_id,
                'last_message': last_message.content[:50] + '...' if len(last_message.content) > 50 else last_message.content,
                'last_timestamp': last_message.timestamp.isoformat(),
                'message_count': message_count
            })
        
        return jsonify(session_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/chat/clear/<session_id>', methods=['DELETE'])
def clear_session(session_id):
    """Limpar histórico de uma sessão específica"""
    try:
        Message.query.filter_by(session_id=session_id).delete()
        db.session.commit()
        return jsonify({'message': 'Sessão limpa com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_bot_response(user_message):
    """
    Função temporária para simular resposta do bot.
    Aqui será integrada a API do Gemini posteriormente.
    """
    # Simular tempo de processamento
    time.sleep(0.5)
    
    # Respostas pré-definidas para demonstração
    responses = {
        'oi': 'Olá! Eu sou o BotMind, seu assistente inteligente. Como posso ajudá-lo hoje?',
        'olá': 'Olá! Eu sou o BotMind, seu assistente inteligente. Como posso ajudá-lo hoje?',
        'como você está': 'Estou funcionando perfeitamente! Pronto para ajudá-lo com suas dúvidas.',
        'qual seu nome': 'Meu nome é BotMind, sou um chatbot inteligente criado para ajudá-lo.',
        'obrigado': 'De nada! Fico feliz em poder ajudar. Há mais alguma coisa que posso fazer por você?',
        'tchau': 'Até logo! Foi um prazer conversar com você. Volte sempre que precisar!',
        'bye': 'Até logo! Foi um prazer conversar com você. Volte sempre que precisar!'
    }
    
    # Verificar se há uma resposta específica
    user_lower = user_message.lower().strip()
    if user_lower in responses:
        return responses[user_lower]
    
    # Resposta padrão inteligente
    if '?' in user_message:
        return f"Essa é uma pergunta interessante sobre '{user_message}'. No momento estou em modo de demonstração, mas em breve serei integrado com a API do Gemini para fornecer respostas mais inteligentes e contextuais!"
    else:
        return f"Entendi que você mencionou '{user_message}'. Estou processando sua mensagem e em breve, com a integração do Gemini, poderei fornecer respostas mais elaboradas e úteis!"
