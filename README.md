# 🛡️ Jarvis AI — Sophisticated Digital Intelligence

[![Powered by Groq](https://img.shields.io/badge/Powered%20by-Groq-orange?style=for-the-badge)](https://groq.com)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Framework-black?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Jarvis AI** is a high-performance, mature, and scholarly digital companion. Powered by the **Groq LLaMA 3.3 70B** model, it offers ultra-fast inference and sophisticated interaction capabilities, combined with a premium glassmorphic interface.

---

## ✨ Key Features

### 🧠 Advanced Intelligence
- **Natural Language Processing**: High-context conversations using LLaMA 3.3 70B.
- **RAG (Retrieval Augmented Generation)**: Connect your local knowledge base. Drop `.pdf`, `.txt`, `.md`, or `.json` files into the `knowledge/` folder, and Jarvis will learn from them instantly.
- **Smart Memory**: Persistent storage of past interactions with TF-IDF-based context retrieval for long-term continuity.
- **Neural Intent Detection**: Real-time classification of user requests into system commands or conversational queries.

### 🎙️ Multi-Modal Interaction
- **Voice Recognition**: Hands-free operation with integrated Speech-to-Text.
- **Neural TTS**: Sophisticated, scholarly vocal response tuned for a professional "Jarvis" persona.
- **Premium HUD**: Interactive glassmorphic UI with real-time status monitoring and animated AI orb.

### ⚙️ System Mastery
- **Application Control**: Open/Close local apps (Notepad, Chrome, VS Code, etc.).
- **Media Mastery**: Volume control (up/down/mute) and YouTube integration.
- **OS Operations**: Real-time system diagnostics (CPU, RAM, Battery), screenshots, and power management (Shutdown/Restart).
- **Web Synthesis**: Seamless Google searches and URL navigation.

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.8+**
- **Groq API Key**: Get a free key at [console.groq.com](https://console.groq.com) (No credit card required).

### 2. Installation
Clone the repository and install the dependencies:
```bash
# Clone the repository
git clone https://github.com/yourusername/jarvis-ai.git
cd jarvis-ai

# Install requirements
pip install -r requirements.txt
```

### 3. Configuration
Set your Groq API key in your environment variables or directly in `assistant.py`:
```python
# assistant.py
GROQ_API_KEY = "your_gsk_key_here"
```

### 4. Launch
Start the backend server:
```bash
python assistant.py
```
Then, simply open `index.html` in your modern browser (Chrome/Edge recommended for Voice features).

---

## 📁 Project Structure

```text
.
├── assistant.py          # Flask Backend & AI Logic
├── index.html            # Premium Frontend UI
├── knowledge/            # RAG Knowledge Base (Drop files here)
├── nova_memory.json      # Persistent Conversation Memory
├── requirements.txt      # Python Dependencies
└── README.md             # Project Documentation
```

---

## 🛠️ Tech Stack

- **Inference**: [Groq Cloud](https://groq.com) (LLaMA 3.3 70B Versatile)
- **Backend**: Python, Flask, Flask-CORS
- **ML/NLP**: Scikit-Learn (TF-IDF), TextBlob
- **System**: Psutil, PyAutoGUI, Subprocess
- **Frontend**: HTML5, CSS3 (Glassmorphism), Vanilla JavaScript, Marked.js (Markdown Rendering)

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to enhance Jarvis's capabilities.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <i>"Always at your service, sir."</i>
</p>
