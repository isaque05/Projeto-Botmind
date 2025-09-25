import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class DatabaseManager:
    """
    Classe para gerenciar operações com o banco de dados SQLite
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados e cria as tabelas necessárias"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabela de usuários
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT UNIQUE NOT NULL,
                        username TEXT,
                        email TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Tabela de mensagens
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        message TEXT NOT NULL,
                        is_user BOOLEAN NOT NULL,
                        parent_message_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (parent_message_id) REFERENCES messages (id),
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Tabela de configurações do sistema
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_config (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        config_key TEXT UNIQUE NOT NULL,
                        config_value TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Inserir configurações padrão
                cursor.execute('''
                    INSERT OR IGNORE INTO system_config (config_key, config_value) 
                    VALUES ('gemini_api_key', NULL)
                ''')
                
                conn.commit()
                print("Banco de dados inicializado com sucesso!")
                
        except Exception as e:
            print(f"Erro ao inicializar banco de dados: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Testa a conexão com o banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except:
            return False
    
    def create_or_update_user(self, user_data: Dict) -> bool:
        """Cria ou atualiza dados do usuário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, username, email, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    user_data['user_id'],
                    user_data.get('username', ''),
                    user_data.get('email', ''),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Erro ao criar/atualizar usuário: {e}")
            return False
    
    def save_message(self, user_id: str, message: str, is_user: bool, 
                    parent_message_id: Optional[int] = None) -> Optional[int]:
        """Salva uma mensagem no banco de dados"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO messages (user_id, message, is_user, parent_message_id)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, message, is_user, parent_message_id))
                
                message_id = cursor.lastrowid
                conn.commit()
                return message_id
                
        except Exception as e:
            print(f"Erro ao salvar mensagem: {e}")
            return None
    
    def get_user_history(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Obtém histórico de mensagens do usuário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, message, is_user, created_at, parent_message_id
                    FROM messages 
                    WHERE user_id = ? 
                    ORDER BY created_at ASC
                    LIMIT ?
                ''', (user_id, limit))
                
                messages = []
                for row in cursor.fetchall():
                    messages.append({
                        'id': row['id'],
                        'message': row['message'],
                        'is_user': bool(row['is_user']),
                        'created_at': row['created_at'],
                        'parent_message_id': row['parent_message_id']
                    })
                
                return messages
                
        except Exception as e:
            print(f"Erro ao obter histórico: {e}")
            return []
    
    def get_recent_messages(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Obtém mensagens recentes do usuário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, message, is_user, created_at
                    FROM messages 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (user_id, limit))
                
                messages = []
                for row in cursor.fetchall():
                    messages.append({
                        'id': row['id'],
                        'message': row['message'],
                        'is_user': bool(row['is_user']),
                        'created_at': row['created_at']
                    })
                
                return list(reversed(messages))  # Ordenar cronologicamente
                
        except Exception as e:
            print(f"Erro ao obter mensagens recentes: {e}")
            return []
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Obtém estatísticas do usuário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Contar mensagens
                cursor.execute('''
                    SELECT COUNT(*) FROM messages WHERE user_id = ?
                ''', (user_id,))
                total_messages = cursor.fetchone()[0]
                
                # Contar mensagens do usuário
                cursor.execute('''
                    SELECT COUNT(*) FROM messages WHERE user_id = ? AND is_user = 1
                ''', (user_id,))
                user_messages = cursor.fetchone()[0]
                
                # Primeira mensagem
                cursor.execute('''
                    SELECT created_at FROM messages 
                    WHERE user_id = ? 
                    ORDER BY created_at ASC 
                    LIMIT 1
                ''', (user_id,))
                first_message = cursor.fetchone()
                
                return {
                    'total_messages': total_messages,
                    'user_messages': user_messages,
                    'bot_messages': total_messages - user_messages,
                    'first_message_date': first_message[0] if first_message else None
                }
                
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def clear_user_history(self, user_id: str) -> bool:
        """Limpa histórico de mensagens do usuário"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM messages WHERE user_id = ?', (user_id,))
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Erro ao limpar histórico: {e}")
            return False
    
    def get_system_config(self, config_key: str) -> Optional[str]:
        """Obtém configuração do sistema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT config_value FROM system_config WHERE config_key = ?
                ''', (config_key,))
                
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            print(f"Erro ao obter configuração: {e}")
            return None
    
    def set_system_config(self, config_key: str, config_value: str) -> bool:
        """Define configuração do sistema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO system_config (config_key, config_value, updated_at)
                    VALUES (?, ?, ?)
                ''', (config_key, config_value, datetime.now().isoformat()))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Erro ao definir configuração: {e}")
            return False
