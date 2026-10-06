# 🏥 MediScan AI — AI-Based Medical Report Analysis System

> **Disclaimer:** MediScan AI is an educational and informational tool. It does not provide medical diagnosis, treatment, or prescriptions. Always consult a qualified healthcare professional for medical decisions.

---

## 📋 Project Description

MediScan AI is a full-stack Python web application that allows users to upload medical reports (PDF, JPG, PNG), extract and analyze the data, and receive plain-language explanations using AI. Built as a college Python project demonstrating real-world application of core Python, data science, and web development concepts.

---

## ✨ Features

- 🔐 **User Authentication** — Secure registration, login, and session management
- 📤 **File Upload** — PDF, PNG, JPG, JPEG with drag-and-drop support
- 📄 **Text Extraction** — PyMuPDF for PDFs, EasyOCR for scanned images
- 🔍 **Medical Data Extraction** — Regular expressions to identify test names, values, units, and reference ranges
- 🤖 **AI Analysis** — Gemini, OpenAI, or Groq API for intelligent report explanation
- 📊 **Data Visualization** — Matplotlib charts for test results and report comparison
- 📈 **Data Analysis** — Pandas and NumPy for statistical analysis
- ⚖️ **Report Comparison** — Compare test values between two reports
- 💬 **Interactive Q&A** — Ask questions about your report
- 📥 **Download Summary** — Export PDF or text summary
- 🧪 **Demo Mode** — Load sample data without uploading real documents
- 📱 **Responsive Design** — Works on desktop and mobile

---

## 🛠️ Technology Stack

| Category | Technology |
|---|---|
| Backend | Python 3, Flask, Flask-Login, Flask-SQLAlchemy |
| Database | SQLite, SQLAlchemy ORM |
| Data Analysis | Pandas, NumPy |
| Visualization | Matplotlib |
| PDF Processing | PyMuPDF (fitz) |
| OCR | EasyOCR (optional), Tesseract (optional) |
| Image Processing | Pillow |
| AI API | Google Gemini / OpenAI / Groq |
| Auth | Werkzeug (password hashing), Flask sessions |
| Config | python-dotenv |
| PDF Export | ReportLab |

---

## 📁 Project Structure

```
mediscan_ai/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (DO NOT commit)
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
│
├── models/
│   ├── __init__.py
│   └── database.py             # SQLAlchemy models (User, Report, TestResult, History)
│
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # Login, Register, Logout
│   ├── dashboard.py            # Dashboard, Profile, About
│   ├── reports.py              # Upload, View, Delete, Download, Demo, Compare
│   └── api.py                  # AJAX endpoints (Ask AI, Status)
│
├── services/
│   ├── __init__.py
│   ├── document_processor.py   # PDF/Image text extraction
│   ├── document_classifier.py  # Document type classification
│   ├── medical_extractor.py    # Regex-based test data extraction
│   ├── data_analyzer.py        # Pandas/NumPy analysis
│   ├── visualizer.py           # Matplotlib chart generation
│   ├── ai_service.py           # AI API integration
│   └── demo_data.py            # Sample medical data
│
├── templates/
│   ├── base.html               # Base template
│   ├── layout.html             # Sidebar macro
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── upload.html
│   ├── reports.html
│   ├── report_detail.html
│   ├── compare.html
│   ├── profile.html
│   ├── about.html
│   └── error.html
│
├── static/
│   ├── css/style.css           # Main stylesheet
│   ├── js/app.js               # JavaScript
│   └── generated_charts/       # Auto-generated chart images
│
├── uploads/                    # Uploaded documents (gitignored)
└── instance/
    └── mediscan.db             # SQLite database (gitignored)
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.9 or higher
- pip

### 1. Navigate to Project

```bash
cd mediscan_ai
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Optional OCR Dependencies

For scanned document OCR support:

#### Option A: EasyOCR (recommended, no system install needed)
```bash
pip install easyocr
```

#### Option B: Tesseract OCR (system install required)
- **Windows:** Download from https://github.com/UB-Mannheim/tesseract/wiki
- **Ubuntu/Debian:** `sudo apt install tesseract-ocr`
- **macOS:** `brew install tesseract`

Then install Python binding:
```bash
pip install pytesseract
```

### 5. Configure Environment Variables

```bash
# Copy the example file
copy .env.example .env   # Windows
cp .env.example .env     # Linux/macOS

# Edit .env with your settings
```

Required `.env` settings:

```env
SECRET_KEY=your-secret-key-change-this-in-production
AI_PROVIDER=gemini          # gemini, openai, or groq
AI_API_KEY=your_api_key     # Optional - app works without it
```

### 6. Initialize Database

The database is created automatically when you first run the app.

### 7. Run the Application

```bash
python app.py
```

Open your browser at: **http://127.0.0.1:5000**

---

## 🤖 Configuring AI API

The application works WITHOUT an AI API key using demo/mock mode.

### Google Gemini (Recommended — Free Tier Available)
1. Go to https://aistudio.google.com/app/apikey
2. Create an API key
3. Add to `.env`:
```env
AI_PROVIDER=gemini
AI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash
```

### OpenAI
1. Go to https://platform.openai.com/api-keys
2. Create an API key
3. Add to `.env`:
```env
AI_PROVIDER=openai
AI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
```

### Groq (Free Tier Available)
1. Go to https://console.groq.com
2. Create an API key
3. Add to `.env`:
```env
AI_PROVIDER=groq
AI_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-8b-instant
```

---

## 🧪 Demo Instructions

1. Register a new account at `/register`
2. Log in at `/login`
3. Click **"Try CBC Demo"** or **"Try Biochem Demo"** in the sidebar
4. View the automatically analyzed demo report
5. Try asking questions in the Q&A section
6. Try the report comparison feature with two demo reports

---

## 🎓 Python Syllabus Concepts Demonstrated

### Unit I: Core Python
| Concept | Where |
|---|---|
| Functions | All service modules, routes |
| Strings | `medical_extractor.py`, `document_classifier.py` |
| Loops | All services (for, while) |
| Branching | All modules (if/elif/else) |
| File I/O | `document_processor.py`, `visualizer.py` |
| Modules | All `.py` files |
| Lists | `medical_extractor.py` — COMMON_UNITS, test results |
| Tuples | `medical_extractor.py` — COMMON_UNITS tuple, function return types |
| Sets | `document_classifier.py` — keyword sets |
| Dictionaries | `ai_service.py`, `document_classifier.py`, config |
| Mutable objects | Lists, dicts throughout |

### Unit II: OOP & Advanced
| Concept | Where |
|---|---|
| OOP / Classes | `MedicalDataAnalyzer`, `AIService`, SQLAlchemy models |
| Encapsulation | Private methods (`_parse_match`, `_call_gemini`) |
| Data structures | Pandas DataFrame, lists of dicts |
| Regular Expressions | `medical_extractor.py` — full module |
| Networking / API | `ai_service.py` — HTTP requests |
| Multithreading | `document_processor.py`, `reports.py` — concurrent.futures |

### Unit III: NumPy & Matplotlib
| Concept | Where |
|---|---|
| NumPy arrays | `data_analyzer.py` — `np.array()`, `np.mean()` etc. |
| Numerical calc | `data_analyzer.py` — min, max, mean, std, median |
| Matplotlib | `visualizer.py` — bar charts, donut charts, comparison charts |
| Graphs | Generated and saved to `static/generated_charts/` |

### Unit IV: Pandas, Flask, Image Processing
| Concept | Where |
|---|---|
| Pandas | `data_analyzer.py` — DataFrame, merge, groupby, filter |
| Data alignment | `compare_reports()` — pd.merge inner join |
| Aggregation | `value_counts()`, grouped statistics |
| Statistical analysis | `get_numeric_summary()` |
| Image processing | `document_processor.py` — Pillow preprocessing |
| Flask | `app.py`, all routes — web framework |

---

## ⚠️ Known Limitations

1. **OCR Accuracy**: OCR may not be 100% accurate for handwritten or poor quality documents
2. **Regex Extraction**: Very non-standard report formats may not extract all test values
3. **AI API Rate Limits**: Free tier API keys have usage limits
4. **Large Files**: Very large PDFs (100+ pages) may take longer to process
5. **EasyOCR First Load**: Downloads model (~200MB) on first use — takes time

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` in your venv |
| App won't start | Check Python version (`python --version` ≥ 3.9) |
| No AI analysis | Add `AI_API_KEY` to `.env` — app works without it in demo mode |
| OCR not working | Install EasyOCR: `pip install easyocr` |
| Chart not showing | Check `static/generated_charts/` directory exists |
| Database error | Delete `instance/mediscan.db` and restart to recreate |
| PyMuPDF error | `pip install PyMuPDF` |

---

## 📜 License

This project is created for educational purposes as part of a Python programming course.
