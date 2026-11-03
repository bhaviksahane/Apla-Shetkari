# Apla Shetkari (आपला शेतकरी) – AI Helper for Farmers
> **"Smart Farming, Better Future."**

An AI-powered web application designed to empower Indian farmers with instant agricultural guidance, scientific crop recommendations, disease diagnosis, and farming solutions through an interactive multilingual AI assistant.

Built with **Python Flask**, **SQLite**, **HTML5/CSS3/JavaScript**, and **Google Gemini AI**.

---

## 🌾 Project Highlights

- **Multilingual Support**: Fully fluent in **English**, **Hindi (हिंदी)**, and **Marathi (मराठी)** with audio speech-to-text input.
- **Experienced Agricultural Advisor Persona**: Modeled after Krishi Vigyan Kendra (KVK) and ICAR extension scientists—considers Indian soil types (Regur/Black cotton, Alluvial, Red, Laterite), cropping seasons (Kharif, Rabi, Zaid), and local agro-climatic conditions.
- **Precision Crop Recommendations**: Evaluates farmer's State, District, Soil Type, Land Area, Sowing Season, and Water Source to generate detailed crop advisory cards (sowing window, water schedules, cultivation tips, duration, and yield estimates).
- **Safe Farming Protocols**: Follows Integrated Pest Management (IPM); prevents arbitrary chemical dosages; advises consulting local agricultural officers for severe plant outbreaks.
- **User Authentication & Dashboard**: Secure registration, login (via Mobile Number or Email), password hashing with Werkzeug, persistent chat history in SQLite, and saved recommendation sessions.
- **Responsive Agriculture Theme**: Modern green, mint, white, and harvest gold design with agriculture iconography, mobile drawer navigation, card hover animations, and typing indicators.

---

## 🛠️ Technology Stack

| Layer | Technology | Description |
|---|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+) | Custom responsive layout, CSS variables, mobile menu, speech recognition |
| **Icons & Fonts** | FontAwesome 6, Google Fonts | Outfit, Plus Jakarta Sans, Noto Sans Devanagari |
| **Backend** | Python 3, Flask Framework | Modular routing, session management, input validation, rate limiting |
| **Database** | SQLite3 (`instance/database.db`) | Relational schema: `users`, `chat_history`, `crop_recommendations` |
| **AI Integration** | Google Gemini API | `gemini-2.5-flash` / `gemini-1.5-flash` via REST API |
| **Security** | Werkzeug Security | Salted password hashing, parameterized SQL queries, env isolation |

---

## 📁 Project Folder Structure

```
apla_shetkari/
│
├── app.py                     # Main Flask application & route controllers
├── config.py                  # Application configuration & env loader
├── database.py                # SQLite connection pool & parameterized queries
├── ai_service.py              # Gemini AI API integration & agricultural prompts
├── test_app.py                # Automated unit & integration test suite
├── requirements.txt           # Python dependencies
├── .env                       # Local environment variables (API keys, secrets)
├── .env.example               # Template for environment configuration
├── README.md                  # Detailed documentation & setup guide
│
├── templates/
│   ├── base.html              # Base layout with navbar, language selector & footer
│   ├── index.html             # Homepage with hero, 6 feature cards & agri tips
│   ├── login.html             # Farmer login (Mobile/Email + Password toggle)
│   ├── register.html          # Registration form with state & district fields
│   ├── dashboard.html         # User dashboard with stats, chat history & saved recs
│   ├── chatbot.html           # Interactive AI Chatbot with speech input & chips
│   ├── crop_recommendation.html # Crop recommendation form & card display
│   └── about.html             # About Us, mission, tech stack & academic overview
│
├── static/
│   ├── css/
│   │   └── style.css          # Agriculture theme, responsive layouts & animations
│   ├── js/
│   │   └── script.js          # Client interactions, multilingual UI, Speech API
│   └── images/
│       └── logo.svg           # Custom branded vector logo & favicon
│
└── instance/
    └── database.db            # SQLite database file (auto-created on startup)
```

---

## 🚀 Step-by-Step Setup & Installation

### Prerequisites
- **Python 3.10+** installed on your system.
- An internet connection for Google Gemini AI.

### 1. Clone or Open the Project
Open your terminal / command prompt in the project directory:
```bash
cd "c:\Users\KOMAL\OneDrive\Desktop\shetkari"
```

### 2. (Optional) Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (`.env`)
1. Obtain a free Google Gemini API key from [Google AI Studio](https://aistudio.google.com/).
2. Open the `.env` file in the project folder and paste your key:
```env
SECRET_KEY=apla-shetkari-farmer-smart-app-secret-key-2025
GEMINI_API_KEY=AIzaSy...your_actual_key_here
FLASK_ENV=development
PORT=5000
```
*(Note: If no API key is added, the app starts normally and displays clear configuration guidance whenever an AI query is triggered.)*

### 5. Run the Application
```bash
python app.py
```

Open your browser and navigate to:
**`http://127.0.0.1:5000`**

---

## 🧪 Running Automated Tests

Run the built-in test suite to verify all database operations, authentication flows, route endpoints, and AI parsers:
```bash
python test_app.py
```
Expected output:
```
Ran 7 tests in 0.606s
OK
```

---

## 💬 Sample Questions to Test the AI Assistant

Click on the suggested question chips or type/speak into the chatbot:

1. **Which crop should I grow in black soil?**
   *(काळी कापसाची मातीत कोणते पीक चांगले येईल?)*
2. **What fertilizer is suitable for wheat?**
   *(गव्हाच्या पिकासाठी योग्य खत व्यवस्थापन कोणते?)*
3. **My tomato plants have yellow leaves. What should I do?**
   *(माझ्या टोमॅटोच्या झाडांची पाने पिवळी पडली आहेत. काय उपाय करावा?)*
4. **How can I increase the productivity of my farm?**
   *(शेतातील उत्पादन वाढवण्यासाठी काय करावे?)*
5. **What is the best season to grow cotton?**
   *(कापूस लागवडीसाठी कोणता हंगाम आणि महिना योग्य आहे?)*
6. **How much water does sugarcane require?**
   *(ऊस पिकाला किती पाणी लागते आणि ठिबक सिंचन कसे करावे?)*
7. **How can I control pests in soybean crops?**
   *(सोयाबीन पिकावरील खोडकिडा आणि अळीचे नियंत्रण कसे करावे?)*

---

## 🎓 College Presentation & Demonstration Guide

When demonstrating this project for professors, recruiters, or viva examiners:

1. **Homepage Demonstration (`/`)**:
   - Highlight the Indian agriculture aesthetic (green/gold palette, responsive cards).
   - Show the 6 core agricultural feature cards and the seasonal tips ticker.
   - Switch language between **English**, **हिन्दी**, and **मराठी**.

2. **User Registration & Login (`/register`, `/login`)**:
   - Register a farmer with Mobile Number, Name, State, and District.
   - Point out password hashing with Werkzeug security utilities.
   - Log in using either the registered Mobile Number or Email.

3. **AI Chatbot (`/chat`)**:
   - Click a suggested question chip (e.g. *"What fertilizer is suitable for wheat?"*).
   - Switch the chatbot language to **मराठी** and ask in Marathi to showcase authentic Devanagari regional answers.
   - Demonstrate the **Microphone Voice Input** button (Speech-to-Text).
   - Demonstrate the **Copy Advice** and **Clear Chat** features.

4. **Crop Recommendation System (`/crop-recommendation`)**:
   - Select State (e.g. *Maharashtra*), District (e.g. *Nashik*), Soil Type (*Black Cotton Soil*), Sowing Season (*Kharif*), and Water Availability (*Moderate / Drip*).
   - Click **Generate Crop Recommendations**.
   - Show the generated cards with Sowing Windows, Growing Duration, Water Needs, and Cultivation Tips.

5. **Farmer Dashboard (`/dashboard`)**:
   - Show the personalized greeting, questions asked counter, saved crop recommendations, and profile management tab.

6. **Database Integrity (`instance/database.db`)**:
   - Demonstrate the 3 relational tables (`users`, `chat_history`, `crop_recommendations`) using parameterized queries to prevent SQL injection.

---

## 📜 License & Acknowledgements
- Developed for Indian farmers and academic demonstration.
- Inspired by the initiatives of the **Ministry of Agriculture & Farmers Welfare**, **ICAR**, and **Krishi Vigyan Kendras (KVK)** across India.
