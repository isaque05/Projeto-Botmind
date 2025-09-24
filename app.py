from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from datetime import datetime
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
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if db_manager.test_connection() else 'disconnected'
    })

if __name__ == '__main__':
    # Validar configurações
    config_issues = config.validate_config()
    if config_issues:
        print("⚠️ Problemas de configuração encontrados:")
        for issue in config_issues:
            print(f"  {issue}")
        print()
    
    # Criar tabelas do banco de dados
    db_manager.init_database()
    
    # Executar aplicação
    print(f"🚀 Iniciando ChatBot em http://{config.HOST}:{config.PORT}")
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
