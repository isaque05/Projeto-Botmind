from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
from flask import Response
from chatbot import ChatBot
from database import DatabaseManager
from config import config

app = Flask(__name__)
CORS(app)

# Configurações
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['DATABASE_PATH'] = config.DATABASE_PATH

# Inicializar componentes
db_manager = DatabaseManager(config.DATABASE_PATH)

# Sincronizar GEMINI_API_KEY do ambiente para o banco antes de criar o chatbot
try:
    gemini_key = config.GEMINI_API_KEY or os.getenv('GEMINI_API_KEY')
    if gemini_key:
        db_manager.set_system_config('gemini_api_key', gemini_key)
except Exception as e:
    print(f"Erro ao sincronizar GEMINI_API_KEY: {e}")

chatbot = ChatBot(db_manager)

@app.route('/')
def index():
    """Página principal do chatbot"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint para enviar mensagens ao chatbot"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        user_id = data.get('user_id', 'anonymous')
        use_gemini = data.get('use_gemini', False)
        try:
            gemini_available = chatbot.gemini_integration.is_available() if chatbot.gemini_integration else False
        except Exception:
            gemini_available = False
        print(f"[CHAT] use_gemini={use_gemini} gemini_available={gemini_available}")
        
        if not message:
            return jsonify({'error': 'Mensagem não pode estar vazia'}), 400
        
        # Processar mensagem com o chatbot
        response = chatbot.process_message(message, user_id, use_gemini)
        
        return jsonify({
            'response': response['message'],
            'timestamp': response['timestamp'],
            'message_id': response['message_id']
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """Endpoint de streaming de resposta do Gemini via SSE"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        user_id = data.get('user_id', 'anonymous')
        use_gemini = data.get('use_gemini', False)
        if not message:
            return jsonify({'error': 'Mensagem não pode estar vazia'}), 400

        # Salvar mensagem do usuário
        user_message_id = db_manager.save_message(user_id=user_id, message=message, is_user=True)

        def event_stream():
            if use_gemini and chatbot.gemini_integration and chatbot.gemini_integration.is_available():
                # Contexto mínimo
                context = chatbot._get_conversation_context_for_gemini(user_id)
                chunks = chatbot.gemini_integration.generate_stream(message, context)
                accumulated = []
                for text in chunks:
                    if not text:
                        continue
                    accumulated.append(text)
                    yield f"data: {text}\n\n"
                # Salvar resposta completa
                full_text = ''.join(accumulated) if accumulated else ''
                if full_text:
                    db_manager.save_message(user_id=user_id, message=full_text, is_user=False, parent_message_id=user_message_id)
                    yield "event: end\n" + f"data: {{\"saved\": true}}\n\n"
                else:
                    # fallback
                    fallback = chatbot._get_default_response(message)
                    db_manager.save_message(user_id=user_id, message=fallback, is_user=False, parent_message_id=user_message_id)
                    yield "event: end\n" + f"data: {{\"saved\": true}}\n\n"
            else:
                # Sem Gemini: usar resposta padrão de uma vez
                fallback = chatbot._get_default_response(message)
                db_manager.save_message(user_id=user_id, message=fallback, is_user=False, parent_message_id=user_message_id)
                yield f"data: {fallback}\n\n"
                yield "event: end\n" + f"data: {{\"saved\": true}}\n\n"

        return Response(event_stream(), mimetype='text/event-stream')
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@app.route('/api/history/<user_id>')
def get_history(user_id):
    """Obter histórico de conversas do usuário"""
    try:
        history = db_manager.get_user_history(user_id)
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'error': f'Erro ao obter histórico: {str(e)}'}), 500

@app.route('/api/user', methods=['POST'])
def create_user():
    """Criar ou atualizar dados do usuário"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'anonymous')
        username = data.get('username', '')
        email = data.get('email', '')
        
        user_data = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'created_at': datetime.now().isoformat()
        }
        
        db_manager.create_or_update_user(user_data)
        return jsonify({'message': 'Usuário criado/atualizado com sucesso'})
        
    except Exception as e:
        return jsonify({'error': f'Erro ao criar usuário: {str(e)}'}), 500

@app.route('/api/health')
def health_check():
    """Verificar saúde da API"""
    try:
        gemini_available = chatbot.gemini_integration.is_available() if chatbot.gemini_integration else False
    except Exception:
        gemini_available = False
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if db_manager.test_connection() else 'disconnected',
        'gemini': 'available' if gemini_available else 'unavailable'
    })

@app.route('/api/gemini/status')
def gemini_status():
    """Detalhes sobre o estado da integração do Gemini"""
    try:
        info = chatbot.gemini_integration.get_model_info() if chatbot.gemini_integration else {'available': False}
    except Exception as e:
        info = {'available': False, 'error': str(e)}
    return jsonify(info)

@app.route('/api/gemini/test')
def gemini_test():
    """Faz um teste simples direto no Gemini"""
    try:
        if not chatbot.gemini_integration or not chatbot.gemini_integration.is_available():
            return jsonify({'ok': False, 'error': 'Gemini indisponível'}), 400
        resp = chatbot.gemini_integration.generate_response("Diga apenas: OK", None)
        return jsonify({'ok': True, 'response': resp})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Validar configurações
    config_issues = config.validate_config()
    if config_issues:
        print("[AVISO] Problemas de configuração encontrados:")
        for issue in config_issues:
            print(f"  {issue}")
        print()
    
    # Criar tabelas do banco de dados
    db_manager.init_database()
    
    # Executar aplicação
    print(f"[INICIANDO] ChatBot em http://{config.HOST}:{config.PORT}")
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
