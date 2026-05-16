---
title: Indian Tourist
emoji: 🇮🇳
colorFrom: orange
colorTo: green
sdk: docker
pinned: false
---

# 🏛️ Discover India: Premium AI Travel Concierge

Discover India is a state-of-the-art travel recommendation engine designed to showcase the soul of Bharat through a sophisticated, high-end digital experience. Powered by **Groq & Llama 3**, it provides bespoke travel plans with real-time visual discovery.

## ✨ Features

- **🧠 Intelligent Curation**: Uses Llama 3 via Groq's high-speed inference engine to generate 4 diverse, high-quality recommendations per search.
- **🖼️ Real-time Visuals**: Integrated with the **Pexels API** to fetch unique, high-definition photography for every destination.
- **💎 Premium UI**: A modern "Glassmorphism" interface featuring sleek dark modes, gold accents, and fluid animations.
- **📱 Fully Responsive**: Optimized for a seamless experience across mobile, tablet, and desktop devices.
- **🗺️ Expanded Coverage**: Includes exotic destinations like Ladakh, Sikkim, and Meghalaya, with specialized filters for Luxury, Adventure, and Spirituality.

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **AI Engine**: Groq Cloud (Llama 3 70B)
- **Imagery**: Pexels Search API
- **Frontend**: Vanilla HTML5, CSS3 (Custom Design System), JavaScript (ES6+)
- **Deployment**: Docker on Hugging Face Spaces

## 🚀 Setup & Installation

### Prerequisites
- Python 3.9+
- Groq API Key
- Pexels API Key

### Local Development
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file and add your keys:
   ```env
   GROQ_API_KEY=your_key_here
   PEXELS_API_KEY=your_key_here
   ```
4. Run the application:
   ```bash
   python app.py
   ```

## 🔒 Security Note
This project uses environment variables for sensitive API keys. When deploying to Hugging Face, ensure `GROQ_API_KEY` and `PEXELS_API_KEY` are added to the **Repository Secrets** in the Space settings.

---
*Handcrafted with ♥ for the sophisticated traveler.*
