// server.js
require('dotenv').config();
const express = require('express');
const axios = require('axios');
const path = require('path');

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public'))); // serve index.html em /

// configs
const PORT = process.env.PORT || 3000;
const MODEL = process.env.MODEL || 'gemini-2.5-flash';
const GEMINI_ENDPOINT = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent`;
const API_KEY = process.env.GEMINI_API_KEY;
if (!API_KEY) {
  console.error('ERRO: configure GEMINI_API_KEY no .env');
  process.exit(1);
}

// helper: extrai texto da resposta (tenta lidar com formatos comuns)
function extractText(data) {
  if (!data) return '';
  // caso "candidates" (doc oficial)
  if (Array.isArray(data.candidates) && data.candidates.length) {
    return data.candidates.map(cand => {
      if (cand.content && Array.isArray(cand.content)) {
        return cand.content.map(con => {
          if (Array.isArray(con.parts)) return con.parts.map(p => p.text || '').join('');
          if (con.text) return con.text;
          return '';
        }).join('\n');
      }
      return JSON.stringify(cand);
    }).join('\n\n');
  }
  // fallback: stringify (útil para debug)
  return JSON.stringify(data).slice(0, 2000);
}

// endpoint que o front-end chama
app.post('/api/chat', async (req, res) => {
  try {
    const userMessage = req.body.message;
    if (!userMessage) return res.status(400).json({ error: 'message is required' });

    const body = {
      contents: [
        {
          role: 'user',
          parts: [{ text: userMessage }]
        }
      ]
    };

    const resp = await axios.post(GEMINI_ENDPOINT, body, {
      headers: {
        'Content-Type': 'application/json',
        'x-goog-api-key': API_KEY
      },
      timeout: 30000
    });

    const replyText = extractText(resp.data);
    return res.json({ reply: replyText });
  } catch (err) {
    console.error('Erro Gemini:', err.response?.data || err.message);
    return res.status(500).json({ error: 'Erro ao chamar Gemini', detail: err.response?.data || err.message });
  }
});

app.listen(PORT, () => console.log(`Servidor rodando em http://localhost:${PORT}`));
