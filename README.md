# 🍯 HoneyScam-India — AI Honeypot for Indian Scam Detection

[![Deployed on Google Cloud Run](https://img.shields.io/badge/Google%20Cloud%20Run-Deployed-blue?logo=google-cloud)](https://honeypot-api-639738131935.asia-south1.run.app)
[![LLM: Groq](https://img.shields.io/badge/LLM-Groq%20(Fast%20%26%20Free)-green)](https://groq.com)
[![Model: Llama 3.3](https://img.shields.io/badge/Model-Llama%203.3%2070B-orange)](https://llama.meta.com)
[![ICAN 2026](https://img.shields.io/badge/Research-ICAN%202026-purple)](https://github.com/vijayreddy2607/conference)

An AI-powered honeypot system that detects scam messages and engages scammers using 5 intelligent Indian personas, extracting intelligence while wasting scammers' time.

---

## 🧠 ML Models

The system uses a **3-stage ensemble pipeline** for scam detection. Model files (`.pth`, `.pkl`) are not included in the repo due to file size — see training instructions below to recreate them.

### Stage 1 — Overnight DistilBERT (`scam_detector_model_safe.pth`)

| Property | Value |
|----------|-------|
| **Architecture** | DistilBERT (`distilbert-base-uncased`) + Linear classifier head |
| **Task** | Binary classification: Scam vs. Legitimate |
| **Training Data** | `Dataset_5971.csv` (5,971 samples: ham/spam/smishing) + `phishing_email.csv` |
| **Test Accuracy** | **97.27%** (on 3,000 held-out samples) |
| **Precision / Recall / F1** | 97.36% / 97.27% / 97.27% |
| **Confusion Matrix** | TN=1,493 · FP=7 · FN=75 · TP=1,425 |
| **Inference Latency** | 24.3 ms/sample (CPU) |
| **Parameters** | ~66M (DistilBERT base) |

**Train:**
```bash
python train_indian_scam_model.py  # OR
python retrain_with_real_data.py
```

---

### Stage 2 — Indian-Specific DistilBERT V3 (`indian_scam_detector_v3.pth`)

| Property | Value |
|----------|-------|
| **Architecture** | DistilBERT (`distilbert-base-uncased`) fine-tuned on Indian corpus |
| **Task** | Binary classification — specialised for Indian scam patterns (Hinglish, UPI, KYC fraud, digital arrest) |
| **Training Data** | `indian_scam_dataset.csv` — **10,000 rows**, perfectly balanced (5,000 scam + 5,000 legitimate) |
| **Checkpoint Accuracy** | **98.09%** |
| **Key Advantage** | Understands India-specific language, UPI IDs, AADHAAR patterns, digital arrest scams |

**Train:**
```bash
python train_indian_scam_model.py
# Outputs: indian_scam_detector_v3.pth
```

**Datasets to download first:**
```bash
python download_datasets.py
# Downloads: indian_scam_dataset.csv, Dataset_5971.csv, phishing_email.csv
```

---

### Stage 3 — TF-IDF + Naïve Bayes Scam Type Classifier (`production_scam_detector.pkl`)

| Property | Value |
|----------|-------|
| **Architecture** | TF-IDF vectorizer + Multinomial Naïve Bayes |
| **Task** | Multi-class: classify scam into 10 sub-categories |
| **10 Scam Categories** | `bank_phishing`, `digital_arrest`, `lottery_prize`, `fake_job`, `investment`, `delivery_scam`, `marketplace_scam`, `sextortion`, `impersonation`, `credit_loan` |
| **Training Data** | Curated Indian scam labeled corpus |

**Train / Inspect:**
```bash
python production_scam_detector.py
```

---

### Metadata Analyzer (`app/ml/metadata_analyzer.py`)

Rule-based feature extractor that runs **in parallel** with the DistilBERT stages:

| Signal | How it works |
|--------|-------------|
| URL risk | Checks TLD (`.site`, `.xyz`), WHOIS patterns, brand spoofing |
| Phone clustering | Detects multiple phone numbers (scammer pattern) |
| UPI ID presence | Flags `@paytm`, `@upi` etc. |
| Urgency score | Lexicon scoring ("URGENT", "immediately", "blocked") |
| Threat score | Lexicon scoring ("arrested", "legal action", "FIR") |

**Test it:**
```bash
python app/ml/metadata_analyzer.py
```

---

### Q-Learning Reinforcement Learning Agent (`app/rl/rl_agent.py`)

| Property | Value |
|----------|-------|
| **Algorithm** | Q-Learning (tabular) |
| **State space** | 7 dimensions: `{scam_type, turn_number, intelligence_count, trust_level, urgency_level, message_length, conversation_length}` |
| **Actions (10)** | `ask_clarifying_question`, `show_compliance`, `create_obstacle`, `express_confusion`, `ask_for_proof`, `share_fake_details`, `express_fear`, `request_time`, `feign_technical_issue`, `ask_for_supervisor` |
| **Hyperparameters** | ε=0.2, α=0.1, γ=0.95 |
| **Q-table states explored** | 38 (from live production deployment) |
| **Saved model** | `rl_model.pkl` |

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/vijayreddy2607/conference.git
cd conference
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
cp .env.example .env
# Edit .env — add your GROQ_API_KEY (free at https://console.groq.com)
```

### 3. Train the Models (One-time setup)
```bash
# Download datasets
python download_datasets.py

# Train Stage 1 + Stage 2 DistilBERT
python train_indian_scam_model.py

# Train Stage 3 TF-IDF classifier
python production_scam_detector.py
```

### 4. Run the API
```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Test It
```bash
curl -X POST "http://localhost:8000/api/message" \
  -H "Content-Type: application/json" \
  -H "x-api-key: honeypot-secret-key-12345" \
  -d '{
    "sessionId": "test-001",
    "message": {
      "sender": "scammer",
      "text": "URGENT: Your SBI account blocked! Update KYC now!",
      "timestamp": "2026-03-19T10:00:00+05:30"
    }
  }'
```

---

## 🎭 The 5 Personas

| Persona | File | Character | Best For |
|---------|------|-----------|---------|
| **Uncle** | `app/agents/uncle_agent.py` | Retired govt employee, old-fashioned | Bank/KYC scams |
| **Aunty** | `app/agents/aunty_agent.py` | Housewife, trusting, emotional | Lottery/prize scams |
| **Worried** | `app/agents/worried_agent.py` | Anxious professional, nervous | Digital arrest, legal threats |
| **TechSavvy** | `app/agents/techsavvy_agent.py` | CS student, skeptical | Investment/crypto scams |
| **Student** | `app/agents/student_agent.py` | College student, gullible | Job/internship scams |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI + Python 3.11 |
| **LLM** | Groq API — Llama 3.3 70B Versatile (**free**, fast) |
| **ML Models** | DistilBERT (HuggingFace Transformers) + scikit-learn |
| **RL** | Custom Q-Learning (tabular) |
| **Deployment** | Google Cloud Run (asia-south1) |
| **Container** | Docker |

---

## 📊 Performance Summary

| Metric | Value |
|--------|-------|
| Stage 1 Accuracy | **97.27%** (tested on 3,000 samples) |
| Stage 2 Accuracy | **98.09%** (Indian-specific corpus) |
| Ensemble Accuracy | **≥98.09%** |
| Scam Categories | **10** Indian scam types |
| Avg Latency | **24.3 ms/sample** (model inference) |
| RL Actions | **10** conversation tactics |
| Personas | **5** culturally-authentic Indian characters |

---

## 📖 API Reference

**Endpoint**: `POST /api/message`  
**Auth header**: `x-api-key: honeypot-secret-key-12345`

**Request**:
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "your message here",
    "timestamp": "2026-03-19T10:00:00+05:30"
  }
}
```

**Response**:
```json
{
  "status": "success",
  "reply": "Arre beta! Which bank are you calling from? Tell me properly"
}
```

API docs: `GET /docs` (Swagger UI)

---

## 🔐 Environment Variables

```bash
API_KEY=honeypot-secret-key-12345
GROQ_API_KEY=your-groq-api-key-here     # Get free at console.groq.com
GROQ_MODEL=llama-3.3-70b-versatile
LLM_PROVIDER=groq
ENVIRONMENT=production
```

---

## 📝 License

MIT License — feel free to fork and improve!


[![Deployed on Google Cloud Run](https://img.shields.io/badge/Google%20Cloud%20Run-Deployed-blue?logo=google-cloud)](https://honeypot-api-639738131935.asia-south1.run.app)
[![LLM: Groq](https://img.shields.io/badge/LLM-Groq%20(Fast%20%26%20Free)-green)](https://groq.com)
[![Model: Llama 3.3](https://img.shields.io/badge/Model-Llama%203.3%2070B-orange)](https://llama.meta.com)

An AI-powered honeypot system that detects scam messages and engages scammers using 5 intelligent Indian personas, extracting intelligence while wasting scammers' time.

## 🚀 Live Deployment

**Production API**: `https://honeypot-api-639738131935.asia-south1.run.app`

- **API Endpoint**: `POST /api/message`
- **Health Check**: `GET /health`
- **API Docs**: `/docs`
- **Region**: `asia-south1` (India)
- **Status**: ✅ Live and operational

## 🎯 GUVI Hackathon Submission

### Quick Test
```bash
curl -X POST "https://honeypot-api-639738131935.asia-south1.run.app/api/message" \
  -H "Content-Type: application/json" \
  -H "x-api-key: honeypot-secret-key-12345" \
  -d '{
    "sessionId": "test-001",
    "message": {
      "sender": "scammer",
      "text": "URGENT: Your account has been compromised. Share OTP immediately.",
      "timestamp": "2026-02-03T18:45:00+05:30"
    }
  }'
```

### Submit to GUVI
1. Navigate to: https://hackathon.guvi.in/timeline
2. Find: "API Endpoint Submission and Testing"
3. Enter:
   - **x-api-key**: `honeypot-secret-key-12345`
   - **Honeypot API Endpoint URL**: `https://honeypot-api-639738131935.asia-south1.run.app/api/message`
4. Click: "Test Honeypot Endpoint"
5. Verify test passes ✅
6. Submit to hackathon

## 📚 Features

- **5 Intelligent Personas**: Confused Elder, Tech-Savvy Student, Busy Professional, Worried Parent, Curious Teen
- **ML-Powered Scam Detection**: 98%+ accuracy on Indian scam patterns
- **Groq LLM**: Fast, free, intelligent responses using Llama 3.3 70B
- **Intelligence Extraction**: Automatically collects scammer data (phone numbers, UPI IDs, bank details, etc.)
- **Session Management**: Handles multiple concurrent conversations
- **GUVI Compliant**: Fully compliant with GUVI hackathon API requirements

## 🛠️ Tech Stack

- **Backend**: FastAPI + Python 3.11
- **LLM**: Groq API (Llama 3.3 70B Versatile)
- **ML Model**: DistilBERT for scam detection
- **Deployment**: Google Cloud Run
- **Container**: Docker
- **Database**: SQLite (for session persistence)

## 📖 Documentation

- [Google Cloud Deployment Guide](GOOGLE_CLOUD_DEPLOYMENT.md) - Deploy your own instance
- [HuggingFace Deployment](HUGGINGFACE_DEPLOYMENT.md) - Alternative deployment
- [API Documentation](https://honeypot-api-639738131935.asia-south1.run.app/docs) - Interactive API docs

## 🔧 Local Development

### Prerequisites
- Python 3.11+
- Groq API key (free from [console.groq.com](https://console.groq.com))

### Setup
```bash
# Clone the repository
cd "/path/to/honey pot agent"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run locally
uvicorn app.main:app --reload --port 8000
```

### Test Locally
```bash
curl -X POST "http://localhost:8000/api/message" \
  -H "Content-Type: application/json" \
  -H "x-api-key: honeypot-secret-key-12345" \
  -d '{
    "sessionId": "local-test",
    "message": {
      "sender": "scammer",
      "text": "Hello, I need your bank details",
      "timestamp": "2026-02-03T18:00:00+05:30"
    }
  }'
```

## 🌐 Deploy Your Own

### Google Cloud Run (Recommended)
```bash
# Set environment variables
export GCLOUD_PROJECT_ID=your-project-id
export GROQ_API_KEY=your-groq-key
export LLM_PROVIDER=groq

# Deploy
./deploy.sh
```

See [GOOGLE_CLOUD_DEPLOYMENT.md](GOOGLE_CLOUD_DEPLOYMENT.md) for detailed instructions.

## 📊 API Response Format

**Request**:
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Hi, I'm calling from your bank",
    "timestamp": "2026-02-03T18:00:00+05:30"
  }
}
```

**Response**:
```json
{
  "status": "success",
  "reply": "Arre beta! Which bank are you calling from? Tell me properly"
}
```

## 🔐 Configuration

Key environment variables:
- `API_KEY`: Authentication for your API
- `LLM_PROVIDER`: `groq` (recommended), `openai`, `anthropic`
- `GROQ_API_KEY`: Your Groq API key
- `ENVIRONMENT`: `production` or `development`

## 📈 Performance

- **Response Time**: ~500ms average (with Groq)
- **Scam Detection Accuracy**: 98.09%
- **Uptime**: 99.9% on Google Cloud Run
- **Cost**: $0 (within free tier)

## 🏆 GUVI Hackathon Details

- **Event**: GUVI India AI Impact Buildathon
- **Deadline**: February 5, 2026
- **Team**: Individual Project
- **Status**: ✅ Ready for submission

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

This is a hackathon project. Feel free to fork and improve!

## 📮 Contact

For questions about this project, please check the [documentation](GOOGLE_CLOUD_DEPLOYMENT.md) or open an issue.
