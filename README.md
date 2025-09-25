# 🤖 ChatBot Inteligente com Flask e SQLite

Um chatbot moderno e interativo desenvolvido em Python com Flask, SQLite e integração futura com a API do Google Gemini. Interface inspirada no ChatGPT com design responsivo e funcionalidades avançadas.

## ✨ Características

### Backend
- **Flask** como framework web
- **SQLite** para persistência de dados
- **Classes Python** para organização do código
- **API RESTful** para comunicação frontend/backend
- **Integração com Gemini** (opcional)
- **Sistema de usuários** e histórico de conversas

### Frontend
- **Interface moderna** inspirada no ChatGPT
- **Design responsivo** para mobile e desktop
- **JavaScript vanilla** para interatividade
- **Animações suaves** e feedback visual
- **Configurações personalizáveis**
- **Sugestões de mensagens** interativas

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 1. Clone o repositório
```bash
git clone <seu-repositorio>
cd meu_chatbot
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Configure as variáveis de ambiente (opcional)
Crie um arquivo `.env` na raiz do projeto:
```env
SECRET_KEY=sua-chave-secreta-aqui
GEMINI_API_KEY=sua-chave-do-gemini-aqui
DEBUG=True
```

### 4. Execute a aplicação
```bash
python app.py
```

A aplicação estará disponível em: `http://localhost:5000`

## 🔧 Configuração do Gemini (Opcional)

Para ativar a integração com o Google Gemini:

1. Obtenha uma API key no [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Configure a variável de ambiente `GEMINI_API_KEY`
3. Reinicie a aplicação

### Configuração via interface
Você também pode configurar a API key através da interface:
1. Acesse as configurações (ícone de engrenagem)
2. Adicione sua chave do Gemini
3. A opção "Usar Gemini AI" estará disponível

## 📁 Estrutura do Projeto

```
meu_chatbot/
├── app.py                 # Aplicação Flask principal
├── chatbot.py            # Classe principal do chatbot
├── database.py           # Gerenciador do banco SQLite
├── gemini_integration.py # Integração com Gemini
├── config.py             # Configurações da aplicação
├── requirements.txt      # Dependências Python
├── templates/
│   └── index.html        # Interface HTML
├── static/
│   ├── css/
│   │   └── style.css     # Estilos CSS
│   └── js/
│       └── chat.js       # JavaScript do frontend
└── README.md
```

## 🎯 Funcionalidades

### Chat Inteligente
- Respostas contextuais baseadas em padrões
- Integração opcional com Gemini para respostas avançadas
- Histórico de conversas persistente
- Sugestões de mensagens interativas

### Interface Moderna
- Design inspirado no ChatGPT
- Animações suaves e feedback visual
- Interface responsiva para mobile
- Tema claro com cores modernas

### Gerenciamento de Dados
- Banco SQLite para persistência
- Sistema de usuários
- Histórico de mensagens
- Configurações personalizáveis

### API RESTful
- `POST /api/chat` - Enviar mensagem
- `GET /api/history/<user_id>` - Obter histórico
- `POST /api/user` - Criar/atualizar usuário
- `GET /api/health` - Status da API

## 🛠️ Desenvolvimento

### Adicionando Novas Funcionalidades

1. **Novas respostas do chatbot**: Edite o método `_load_responses()` em `chatbot.py`
2. **Novos endpoints**: Adicione rotas em `app.py`
3. **Modificações no banco**: Atualize `database.py` e execute migrações
4. **Interface**: Modifique `templates/index.html` e `static/css/style.css`

### Estrutura das Classes

#### ChatBot
- Gerencia lógica de conversação
- Integra com diferentes fontes de resposta
- Processa mensagens e gera respostas

#### DatabaseManager
- Gerencia operações com SQLite
- CRUD para usuários e mensagens
- Configurações do sistema

#### GeminiIntegration
- Integração com API do Google Gemini
- Geração de respostas avançadas
- Gerenciamento de sessões de chat

## 🔒 Segurança

- Validação de entrada de dados
- Sanitização de mensagens
- Limite de caracteres por mensagem
- Chaves de API seguras

## 📱 Responsividade

A interface é totalmente responsiva e funciona em:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (até 767px)

## 🚀 Deploy

### Produção
1. Configure variáveis de ambiente adequadas
2. Use um servidor WSGI como Gunicorn
3. Configure um proxy reverso (Nginx)
4. Use HTTPS em produção

### Docker (futuro)
```dockerfile
# Dockerfile será adicionado em versão futura
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 🆘 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação
2. Abra uma issue no GitHub
3. Consulte os logs da aplicação

## 🔮 Roadmap

### Próximas funcionalidades
- [ ] Suporte a múltiplos idiomas
- [ ] Upload de arquivos
- [ ] Temas escuro/claro
- [ ] Exportação de conversas
- [ ] Integração com mais APIs de IA
- [ ] Sistema de plugins
- [ ] Deploy com Docker

---

**Desenvolvido com ❤️ usando Python, Flask e muito café! ☕**
