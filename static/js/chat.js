class ChatBot {
    constructor() {
        this.userId = this.generateUserId();
        this.isLoading = false;
        this.autoScroll = true;
        this.soundEnabled = true;
        
        this.initializeElements();
        this.bindEvents();
        this.loadSettings();
        this.initializeChat();
    }
    
    generateUserId() {
        // Gerar ID único para o usuário
        return 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    initializeElements() {
        // Elementos do DOM
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.charCount = document.getElementById('charCount');
        this.useGeminiCheckbox = document.getElementById('useGemini');
        this.settingsModal = document.getElementById('settingsModal');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        
        // Botões
        this.newChatBtn = document.getElementById('newChatBtn');
        this.settingsBtn = document.getElementById('settingsBtn');
        this.closeSettingsBtn = document.getElementById('closeSettings');
        this.saveSettingsBtn = document.getElementById('saveSettings');
        this.cancelSettingsBtn = document.getElementById('cancelSettings');
        
        // Configurações
        this.usernameInput = document.getElementById('username');
        this.emailInput = document.getElementById('email');
        this.autoScrollCheckbox = document.getElementById('autoScroll');
        this.soundEnabledCheckbox = document.getElementById('soundEnabled');
    }
    
    bindEvents() {
        // Envio de mensagem
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Contador de caracteres
        this.messageInput.addEventListener('input', () => this.updateCharCount());
        
        // Botões de sugestão
        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const message = e.currentTarget.getAttribute('data-message');
                this.messageInput.value = message;
                this.updateCharCount();
                this.sendMessage();
            });
        });
        
        // Modal de configurações
        this.settingsBtn.addEventListener('click', () => this.showSettings());
        this.closeSettingsBtn.addEventListener('click', () => this.hideSettings());
        this.cancelSettingsBtn.addEventListener('click', () => this.hideSettings());
        this.saveSettingsBtn.addEventListener('click', () => this.saveSettings());
        
        // Nova conversa
        this.newChatBtn.addEventListener('click', () => this.startNewChat());
        
        // Fechar modal clicando fora
        this.settingsModal.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) {
                this.hideSettings();
            }
        });
        
        // Auto-resize do textarea
        this.messageInput.addEventListener('input', () => this.autoResizeTextarea());
    }
    
    initializeChat() {
        // Carregar histórico se existir
        this.loadChatHistory();
        
        // Configurar auto-scroll
        this.setupAutoScroll();
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isLoading) return;
        
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.updateCharCount();
        this.autoResizeTextarea();
        
        try {
            if (this.useGeminiCheckbox.checked) {
                // No streaming não exibimos overlay para ver o texto se formando
                this.sendBtn.disabled = true;
                await this.sendStreaming(message);
                this.sendBtn.disabled = false;
            } else {
                this.showLoading();
                const response = await this.sendToBackend(message);
                this.addMessage(response.response, 'bot');
                await this.saveUserSettings();
                this.hideLoading();
            }
        } catch (error) {
            console.error('Erro ao enviar mensagem:', error);
            this.addMessage('Desculpe, ocorreu um erro. Tente novamente.', 'bot');
            // Garantir que o overlay não fique travado em erros no modo não-streaming
            try { this.hideLoading(); } catch (_) {}
        }
    }

    async sendStreaming(message) {
        // Cria uma mensagem vazia do bot e vai preenchendo em tempo real
        const placeholderDiv = document.createElement('div');
        placeholderDiv.className = 'message bot';
        const timestamp = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
        placeholderDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content"><span class="stream-text"></span>
                <div class="message-time">${timestamp}</div>
            </div>`;
        this.chatMessages.appendChild(placeholderDiv);
        const streamSpan = placeholderDiv.querySelector('.stream-text');
        if (this.autoScroll) this.scrollToBottom();

        const payload = {
            message: message,
            user_id: this.userId,
            use_gemini: true
        };

        const resp = await fetch('/api/chat/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!resp.ok) throw new Error('Falha ao iniciar streaming');

        const reader = resp.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const parts = buffer.split('\n\n');
            buffer = parts.pop();
            for (const part of parts) {
                if (!part.startsWith('data:') && !part.startsWith('event:')) continue;
                if (part.startsWith('event: end')) {
                    // fim do stream
                    continue;
                }
                if (part.startsWith('data:')) {
                    const text = part.slice(5).trimStart();
                    streamSpan.textContent += text;
                    if (this.autoScroll) this.scrollToBottom();
                }
            }
        }
    }
    
    async sendToBackend(message) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                user_id: this.userId,
                use_gemini: this.useGeminiCheckbox.checked
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    addMessage(content, sender) {
        // Remover mensagem de boas-vindas se existir
        const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        // Criar elemento da mensagem
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const timestamp = new Date().toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const avatar = sender === 'user' ? 'U' : '🤖';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                ${this.formatMessage(content)}
                <div class="message-time">${timestamp}</div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        
        // Auto-scroll
        if (this.autoScroll) {
            this.scrollToBottom();
        }
        
        // Som de notificação
        if (this.soundEnabled && sender === 'bot') {
            this.playNotificationSound();
        }
    }
    
    formatMessage(content) {
        // Formatação básica de markdown
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }
    
    updateCharCount() {
        const count = this.messageInput.value.length;
        this.charCount.textContent = `${count}/2000`;
        
        // Ativar/desativar botão de envio
        this.sendBtn.disabled = count === 0 || count > 2000;
        
        // Mudar cor do contador
        if (count > 1800) {
            this.charCount.style.color = '#ff6b6b';
        } else if (count > 1500) {
            this.charCount.style.color = '#f59e0b';
        } else {
            this.charCount.style.color = '#a0aec0';
        }
    }
    
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    showLoading() {
        this.isLoading = true;
        this.loadingOverlay.classList.add('show');
        this.sendBtn.disabled = true;
    }
    
    hideLoading() {
        this.isLoading = false;
        this.loadingOverlay.classList.remove('show');
        this.updateCharCount();
    }
    
    showSettings() {
        this.settingsModal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
    
    hideSettings() {
        this.settingsModal.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
    
    saveSettings() {
        const settings = {
            username: this.usernameInput.value,
            email: this.emailInput.value,
            autoScroll: this.autoScrollCheckbox.checked,
            soundEnabled: this.soundEnabledCheckbox.checked
        };
        
        localStorage.setItem('chatbot_settings', JSON.stringify(settings));
        
        // Aplicar configurações
        this.autoScroll = settings.autoScroll;
        this.soundEnabled = settings.soundEnabled;
        
        this.hideSettings();
        this.showNotification('Configurações salvas!');
    }
    
    loadSettings() {
        const savedSettings = localStorage.getItem('chatbot_settings');
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            
            this.usernameInput.value = settings.username || '';
            this.emailInput.value = settings.email || '';
            this.autoScrollCheckbox.checked = settings.autoScroll !== false;
            this.soundEnabledCheckbox.checked = settings.soundEnabled !== false;
            
            this.autoScroll = settings.autoScroll !== false;
            this.soundEnabled = settings.soundEnabled !== false;
        }
    }
    
    async saveUserSettings() {
        const username = this.usernameInput.value.trim();
        const email = this.emailInput.value.trim();
        
        if (username || email) {
            try {
                await fetch('/api/user', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_id: this.userId,
                        username: username,
                        email: email
                    })
                });
            } catch (error) {
                console.error('Erro ao salvar configurações do usuário:', error);
            }
        }
    }
    
    async loadChatHistory() {
        try {
            const response = await fetch(`/api/history/${this.userId}`);
            if (response.ok) {
                const data = await response.json();
                if (data.history && data.history.length > 0) {
                    this.displayChatHistory(data.history);
                }
            }
        } catch (error) {
            console.error('Erro ao carregar histórico:', error);
        }
    }
    
    displayChatHistory(history) {
        // Remover mensagem de boas-vindas
        const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }
        
        // Adicionar mensagens do histórico
        history.forEach(msg => {
            this.addMessage(msg.message, msg.is_user ? 'user' : 'bot');
        });
    }
    
    startNewChat() {
        // Limpar mensagens
        this.chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-content">
                    <div class="welcome-icon">
                        <i class="fas fa-robot"></i>
                    </div>
                    <h2>Nova conversa iniciada!</h2>
                    <p>Como posso ajudá-lo hoje?</p>
                    <div class="suggestions">
                        <button class="suggestion-btn" data-message="Como você funciona?">
                            <i class="fas fa-question-circle"></i>
                            Como você funciona?
                        </button>
                        <button class="suggestion-btn" data-message="Me conte uma curiosidade">
                            <i class="fas fa-lightbulb"></i>
                            Me conte uma curiosidade
                        </button>
                        <button class="suggestion-btn" data-message="Como posso usar o Gemini?">
                            <i class="fas fa-brain"></i>
                            Como posso usar o Gemini?
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Rebind eventos dos botões de sugestão
        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const message = e.currentTarget.getAttribute('data-message');
                this.messageInput.value = message;
                this.updateCharCount();
                this.sendMessage();
            });
        });
        
        // Gerar novo ID de usuário
        this.userId = this.generateUserId();
        
        this.showNotification('Nova conversa iniciada!');
    }
    
    setupAutoScroll() {
        this.chatMessages.addEventListener('scroll', () => {
            const isAtBottom = this.chatMessages.scrollTop + this.chatMessages.clientHeight >= this.chatMessages.scrollHeight - 10;
            this.autoScroll = isAtBottom;
        });
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    playNotificationSound() {
        // Criar som de notificação simples
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
        
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.2);
    }
    
    showNotification(message) {
        // Criar notificação temporária
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--primary-color);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: var(--shadow-lg);
            z-index: 3000;
            animation: slideInRight 0.3s ease;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// Adicionar estilos para animações
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
`;
document.head.appendChild(style);

// Inicializar chatbot quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    new ChatBot();
});
