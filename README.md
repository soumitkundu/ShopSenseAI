# ShopSense AI 🛍️

> An intelligent multimodal e-commerce recommendation bot powered by Azure AI services and GPT-4o-mini. Talk to it, speak to it, or show it a photo — it finds the right products for you.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat&logo=fastapi&logoColor=white)
![Azure](https://img.shields.io/badge/Azure-AI%20Services-0078D4?style=flat&logo=microsoftazure&logoColor=white)
![GPT-4](https://img.shields.io/badge/OpenAI-GPT--4-412991?style=flat&logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Deploy](https://img.shields.io/badge/Deploy-Azure%20App%20Service-0078D4?style=flat&logo=microsoftazure&logoColor=white)

---

## What is ShopSense AI?

ShopSense AI is a conversational product recommendation bot that understands **three types of input**:

| Modality | How it works |
|---|---|
| 💬 **Text** | Type what you're looking for in plain language |
| 🎤 **Voice** | Speak your query — it transcribes and responds with audio |
| 📸 **Image** | Upload a product photo — it analyses the visual attributes and recommends similar items |

Every query is processed through a pipeline of Azure AI services before reaching GPT-4, which generates structured, context-aware product recommendations with names, price ranges, key features, and a personalised justification for each suggestion.

---

## Live Demo

| Resource | URL |
|---|---|
| 🌐 Web App | `https://shopsenseai.azurewebsites.net` |
| 📖 API Docs | `https://shopsenseai.azurewebsites.net/docs` |
| ❤️ Health Check | `https://shopsenseai.azurewebsites.net/health` |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│          Text Input │ Voice Input │ Image Upload             │
└──────────┬──────────┴──────┬──────┴────────────┬─────────────┘
           │                 │                   │
           ▼                 ▼                   ▼
┌──────────────────┐ ┌──────────────┐ ┌───────────────────────┐
│  Azure Language  │ │  Azure Speech│ │   Azure Computer      │
│  Key phrases +   │ │  STT → text  │ │   Vision              │
│  intent extract  │ │  TTS ← audio │ │   Tags + captions     │
└────────┬─────────┘ └────────┬─────┘ └─────────────┬─────────┘
         │                    │                     │
         └────────────────────┼─────────────────────┘
                              ▼
                ┌─────────────────────────┐
                │   FastAPI Orchestrator  │
                │   Session management    │
                │   Prompt construction   │
                └────────────┬────────────┘
                             ▼
               ┌──────────────────────────┐
               │   Azure OpenAI GPT-4     │
               │   Recommendation engine  │
               └────────────┬─────────────┘
                            ▼
                ┌─────────────────────────┐
                │   Structured response   │
                │   3 products + reasons  │
                └─────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend framework** | FastAPI 0.111 + Uvicorn (Python 3.11) |
| **LLM** | Azure OpenAI — GPT-4o-mini |
| **Speech** | Azure Cognitive Services Speech SDK 1.37 |
| **Vision** | Azure AI Vision Image Analysis 1.0.0 |
| **Language** | Azure AI Text Analytics 5.3 |
| **Frontend** | HTML5 / CSS3 / Vanilla JavaScript |
| **Hosting** | Azure App Service (Linux, Python 3.11) |
| **CI/CD** | GitHub Actions + Azure Service Principal |
| **Config** | python-dotenv + Azure App Settings |

---

## Project Structure

```
ShopSenseAI/
│
├── app.py                      # FastAPI entry point — serves UI + API
├── config.py                   # Environment variable loading + validation
├── requirements.txt            # Python dependencies
├── startup.sh                  # Azure App Service startup script
│
├── bot/
│   ├── __init__.py
│   └── bot_handler.py          # Modality router (text / voice / image)
│
├── services/
│   ├── __init__.py
│   ├── openai_service.py         # GPT-4o-mini prompt construction + API calls
│   ├── speech_service.py         # Azure STT (file) + TTS (bytes)
│   ├── vision_service.py         # Azure Computer Vision image analysis
│   └── language_service.py       # Key phrase extraction + sentiment
│
├── static/
│   ├── index.html                # Main chat UI
|   ├── css/
│   |    └── style.css            # Styles (light + dark mode)
|   ├── js/
│   |    └── app.js               # Frontend logic — modality switching
│   └── webchat.html              # Azure Web Chat embedded interface
│
└── .github/
    └── workflows/
        └── main_shopsenseai.yml  # GitHub Actions CI/CD pipeline
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- An Azure account with the following resources provisioned:
  - Azure OpenAI (with a GPT-4 deployment)
  - Azure Speech Service
  - Azure Computer Vision
  - Azure Language Service

### 1. Clone the repository

```bash
git clone https://github.com/soumitkundu/ShopSenseAI.git
cd ShopSenseAI
```

### 2. Create a virtual environment

```bash
# Windows
py -3.11 -m venv .venv
.venv\Scripts\activate

# Mac / Linux
python -3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a **`.env`** file in the project root and refer to the **`example.env`** file for details

> ⚠️ I have already added the file in `.gitignore`. So that it cannot be committed to version control by mistake. 

### 5. Run locally

```bash
py app.py
```

Open your browser at:
- **Chat UI** → `http://localhost:8000`
- **API docs** → `http://localhost:8000/docs`

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serves the chat UI |
| `/chat/text` | POST | Text query → Language enrichment → GPT-4o-mini |
| `/chat/voice` | POST | WAV file → Azure STT → GPT-4o-mini + TTS response |
| `/chat/image` | POST | Image file → Computer Vision → GPT-4o-mini |
| `/tts` | POST | Text → Azure Neural TTS → WAV bytes |
| `/api/webchat-token` | GET | Exchanges Bot secret for short-lived DirectLine token |
| `/session/{id}` | DELETE | Clears conversation history for a session |
| `/health` | GET | Liveness check |

### Example — Text request

```bash
curl -X POST http://localhost:8000/chat/text \
  -H "Content-Type: application/json" \
  -d '{"session_id": "demo-001", "message": "I need wireless earbuds under Rs. 2000 for gym"}'
```

### Example — Image request

```bash
curl -X POST http://localhost:8000/chat/image \
  -F "session_id=demo-001" \
  -F "image_file=@/path/to/product.jpg"
```

### Example — Voice request

```bash
curl -X POST http://localhost:8000/chat/voice \
  -F "session_id=demo-001" \
  -F "audio_file=@/path/to/recording.wav"
```

---

## Testing Individual Services

Debug scripts are provided to test each Azure service in isolation before running the full application:

```bash
# Test Azure Language Service (key phrases + sentiment)
py debug_language.py

# Test Azure Speech Service (TTS → WAV → STT round-trip)
py debug_speech.py

# Test Azure Computer Vision (URL + bytes analysis)
py debug_vision.py

# Test full end-to-end pipeline (text + image → GPT-4)
py debug_full_pipeline.py
```

---

## Deployment

### Deployed through Azure App Service via GitHub Actions

The repository includes a complete CI/CD pipeline in `.github/workflows/main_shopsenseai.yml`.

It can be triggered once you push your changes to the `main` branch.

#### Push to main

```bash
git push origin main:main
```

The pipeline runs automatically. Watch progress in the **Actions** tab on GitHub. On success, your app is live at `https://your-app.azurewebsites.net`.

---

## How Modality Detection Works

ShopSense AI uses **explicit routing** rather than auto-detection. The user selects their input mode (Text / Voice / Image) via buttons in the UI. The frontend then calls the corresponding API endpoint directly:

```
User clicks "Voice" → currentMode = "voice" → POST /chat/voice
User clicks "Image" → currentMode = "image" → POST /chat/image
User clicks "Text"  → currentMode = "text"  → POST /chat/text
```

Each endpoint handles exactly one modality, which keeps the backend logic clean and makes individual service testing straightforward.

---

## Known Limitations

- **No live product catalogue** — right now the recommendations are based on GPT-4o-mini's training knowledge, not a real product database. Prices are estimates.
- **In-memory sessions** — conversation history is lost on app restart. Production deployments should use Azure Cache for Redis.
- **Image quality sensitivity** — Computer Vision performs best on clean product photos against neutral backgrounds.
- **STT brand name accuracy** — neural STT occasionally splits unfamiliar brand names (e.g., "ShopSense" → "Shop Sense"). This does not affect recommendation quality.

---

## Future Improvement Plans

- 🔗 **Live product API integration** — connect to a real product catalogue with RAG for factually grounded recommendations
- 💾 **Persistent sessions** — replace in-memory store with Azure Cache for Redis
- 🌍 **Multi-language support** — extend to Hindi, Tamil, Bengali using Azure Speech and Language multilingual models
- 🎯 **Custom Vision model** — fine-tune on domain-specific product categories for better image analysis accuracy
- 📊 **Analytics** — integrate Azure Application Insights for telemetry and recommendation quality tracking

---

## Azure Services Used

| Service | Purpose | Docs |
|---|---|---|
| Azure OpenAI | GPT-4 recommendation engine | [Docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/) |
| Azure Speech | STT transcription + Neural TTS | [Docs](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/) |
| Azure Computer Vision | Image Analysis 4.0 | [Docs](https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/) |
| Azure Language | Key phrase extraction | [Docs](https://learn.microsoft.com/en-us/azure/ai-services/language-service/) |
| Azure App Service | Application hosting | [Docs](https://learn.microsoft.com/en-us/azure/app-service/) |

---

## Academic Context

This project was developed as part of **SIG788 — Engineering AI Solutions** at **Deakin University** (Master of Data Science), Task — Intelligent Recommendation Bot Project.

---

## License

This project is licensed under the MIT License.

---

<p align="center">Built with Azure AI · FastAPI · GPT-4o-mini · Python 3.11</p>
