# Architecture & System Design

## Project Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        BROWSER                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │             Frontend (HTML/CSS/JS)                 │   │
│  │  ┌──────────────────────────────────────────────┐ │   │
│  │  │  Text Input: "the united"                    │ │   │
│  │  │  [____________] [Predict]                    │ │   │
│  │  └──────────────────────────────────────────────┘ │   │
│  │  ┌──────────────────────────────────────────────┐ │   │
│  │  │  fetch() POST /predict                       │ │   │
│  │  └──────────────────────────────────────────────┘ │   │
│  │  ┌──────────────────────────────────────────────┐ │   │
│  │  │  Results:                                    │ │   │
│  │  │  [states] [nations] [kingdom]                │ │   │
│  │  └──────────────────────────────────────────────┘ │   │
│  └────────────────────────────────────────────────────┘   │
│                          ↕ (HTTP)                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────────────────────────┐
        │      FastAPI Server (Python)           │
        ├───────────────────────────────────────┤
        │                                        │
        │  ┌─────────────────────────────────┐  │
        │  │     POST /predict endpoint      │  │
        │  │  - Receive: {"text": "..."}     │  │
        │  │  - Call model.predict()         │  │
        │  │  - Return: JSON response        │  │
        │  └─────────────────────────────────┘  │
        │                                        │
        │  ┌─────────────────────────────────┐  │
        │  │   Trigram Model (In-Memory)     │  │
        │  │                                 │  │
        │  │  trigrams = {                   │  │
        │  │    ("the", "united"): {         │  │
        │  │      "states": 1023,            │  │
        │  │      "nations": 487,            │  │
        │  │      "kingdom": 234,            │  │
        │  │      ...                        │  │
        │  │    }                            │  │
        │  │  }                              │  │
        │  └─────────────────────────────────┘  │
        │                                        │
        │  Training (Startup):                  │
        │  Brown Corpus → Tokenize →            │
        │  Generate Trigrams → Count →          │
        │  Store in Memory                      │
        │                                        │
        └───────────────────────────────────────┘
```

## Data Flow

### Initialization (Server Startup)
```
1. Import FastAPI, NLTK
2. Initialize TrigramModel class
   ├─ Download Brown Corpus (first time)
   ├─ Load all sentences
   ├─ Tokenize & preprocess
   ├─ Generate trigrams: (w1, w2) → w3
   ├─ Count frequencies
   └─ Store in defaultdict(Counter)
3. Start FastAPI/Uvicorn server
4. Serve index.html on GET /
```

### Prediction Request (Client → Server)
```
Client (Browser)                          Server
     │                                      │
     ├─ User types: "the united"           │
     ├─ User clicks "Predict"              │
     │                                      │
     └─ fetch() POST /predict          →   │
        {"text": "the united"}             │
                                            │
                                      ┌─────┴──────┐
                                      │ Server     │
                                      │ Processing │
                                      ├─────┬──────┘
                                            │
     ← JSON response ◄──────────────────────┤
     {"predictions": [                      │
         "states",                          │ Parse input
         "nations",                         │ Extract ("the", "united")
         "kingdom"                          │ Lookup trigrams
     ]}                                     │ Sort by frequency
                                            │ Return top 3
     │
     ├─ Display predictions
     ├─ Highlight results
     └─ Allow click to extend
```

## File Structure Detailed

```
ngram-predictor/
│
├── main.py (370 lines)
│   ├── Imports & setup
│   ├── TrigramModel class
│   │   ├── __init__()
│   │   ├── preprocess_text()
│   │   ├── train_model()
│   │   └── predict()
│   ├── FastAPI app initialization
│   ├── Pydantic models
│   │   ├── PredictRequest
│   │   ├── PredictionResult
│   │   └── PredictResponse
│   └── Route handlers
│       ├── GET / (serve HTML)
│       ├── POST /predict (predictions)
│       └── GET /health (status)
│
├── static/index.html (350 lines)
│   ├── HTML structure
│   │   ├── Head (meta, title, styles)
│   │   ├── Body
│   │   │   ├── Container div
│   │   │   ├── Title & subtitle
│   │   │   ├── Input section
│   │   │   ├── Results section
│   │   │   └── Model stats
│   │   └── Script (JavaScript)
│   ├── CSS styling
│   │   ├── Global styles
│   │   ├── Layout (flexbox/grid)
│   │   ├── Components
│   │   │   ├── Input styling
│   │   │   ├── Button styling
│   │   │   ├── Prediction cards
│   │   │   └── Loading spinner
│   │   ├── Animations
│   │   └── Responsive design
│   └── JavaScript
│       ├── DOM selectors
│       ├── Event listeners
│       ├── fetch() implementation
│       ├── Response handling
│       └── Helper functions
│
├── requirements.txt
│   ├── fastapi==0.104.1
│   ├── uvicorn==0.24.0
│   ├── pydantic==2.5.0
│   ├── nltk==3.8.1
│   └── python-multipart==0.0.6
│
├── README.md (comprehensive documentation)
├── QUICKSTART.md (30-second setup)
├── CONFIG.md (customization guide)
├── TESTING.md (test cases & examples)
├── PROJECT_SUMMARY.md (overview)
└── ARCHITECTURE.md (this file)
```

## Component Breakdown

### 1. TrigramModel Class

```python
TrigramModel
├── Attributes
│   └── trigrams: defaultdict(Counter)
│       └── Structure: {(word1, word2): Counter{word3: count, ...}}
│
├── Methods
│   ├── __init__()
│   │   └── Calls train_model()
│   │
│   ├── preprocess_text(text: str) → list[str]
│   │   ├── Lowercase
│   │   ├── Normalize whitespace
│   │   ├── Tokenize
│   │   └── Return tokens
│   │
│   ├── train_model() → None
│   │   ├── Load Brown Corpus
│   │   ├── For each sentence:
│   │   │   ├── Preprocess tokens
│   │   │   ├── Add start/end tokens
│   │   │   ├── Create trigrams
│   │   │   └── Count frequencies
│   │   └── Print statistics
│   │
│   └── predict(text: str, top_n: int) → list[dict]
│       ├── Preprocess input
│       ├── Extract bigram (last 2 words)
│       ├── Lookup in trigrams dict
│       ├── Get next words with counts
│       ├── Sort by frequency
│       └── Return top N
```

### 2. FastAPI Application

```
FastAPI App
├── Configuration
│   ├── Title: "Next-Word Prediction API"
│   └── Static files: /static
│
├── Global State
│   └── model: TrigramModel (initialized at startup)
│
├── Pydantic Models
│   ├── PredictRequest
│   │   └── text: str
│   │
│   └── PredictResponse
│       ├── predictions: list[str]
│       └── input_text: str
│
└── Route Handlers
    ├── GET / → FileResponse("static/index.html")
    │
    ├── POST /predict → PredictResponse
    │   ├── Accept: PredictRequest
    │   ├── Call: model.predict(text)
    │   ├── Format response
    │   └── Return JSON
    │
    └── GET /health → {"status": "ok", "model": "trigram"}
```

### 3. Frontend Architecture

```javascript
Frontend
├── HTML Structure
│   ├── Container (max 600px)
│   ├── Header (title + subtitle)
│   ├── Input Section
│   │   ├── Label
│   │   ├── Text Input (#inputText)
│   │   └── Predict Button (#predictBtn)
│   ├── Results Section (#resultsContainer)
│   └── Stats Footer
│
├── CSS Styling (5 breakpoints)
│   ├── Variables: gradients, colors, spacing
│   ├── Layout: flexbox for input, grid for predictions
│   ├── Components: cards, buttons, spinners
│   └── Responsive: mobile-first design
│
└── JavaScript (Event-Driven)
    ├── State
    │   └── DOM elements (input, button, results)
    │
    ├── Event Listeners
    │   ├── Click on predict button
    │   ├── Enter key on input
    │   └── Click on prediction cards
    │
    ├── Functions
    │   ├── predict() - Main handler
    │   ├── fetch() - Call API
    │   ├── displayResults() - Render predictions
    │   ├── showLoading() - Show spinner
    │   ├── showError() - Show error message
    │   ├── copyToInput() - Extend text
    │   └── escapeHtml() - Security
    │
    └── Error Handling
        └── Try-catch, validation, user feedback
```

## Data Structures

### Trigram Storage (In-Memory)
```python
trigrams = {
    ("the", "united"): {
        "states": 1023,      # Frequency count
        "nations": 487,
        "kingdom": 234,
        ...
    },
    ("of", "the"): {
        "states": 892,
        "united": 756,
        "government": 543,
        ...
    },
    ...  # ~100,000+ unique bigrams
}
```

**Time Complexity:**
- Lookup: O(1) - Dictionary lookup
- Prediction: O(k) where k = number of next words (typically 3-5)
- Memory: O(n) where n = number of bigrams × avg next words

### Request/Response JSON

**Request:**
```json
{
  "text": "the united"
}
```

**Response:**
```json
{
  "predictions": ["states", "nations", "kingdom"],
  "input_text": "the united"
}
```

## Training Pipeline

```
Input: Brown Corpus (57,340 sentences)
        │
        ├─ Tokenization
        │  └─ word_tokenize() per sentence
        │
        ├─ Preprocessing
        │  ├─ Lowercase all words
        │  ├─ Filter short sentences (<3 words)
        │  └─ Add <START>, <START>, <END> tokens
        │
        ├─ Trigram Generation
        │  └─ For each sentence:
        │     ├─ Create all consecutive 3-word sequences
        │     └─ Map (word1, word2) → word3
        │
        ├─ Frequency Counting
        │  └─ Counter({word3: count, ...})
        │
        └─ Storage
           └─ defaultdict(Counter)

Output: ~100K unique bigrams with frequencies
```

## Performance Characteristics

```
Operation          | Time      | Notes
───────────────────┼───────────┼──────────────────────
Model Training     | 30-60 sec | First run, ~1.1M words
Prediction         | <50 ms    | Dictionary lookup O(1)
JSON Serialization | <5 ms     | Small response payload
Total API Response | <60 ms    | Network + processing
───────────────────┼───────────┼──────────────────────
```

## Security Considerations

```
Input Validation        ✓ Required (2+ words)
Output Encoding         ✓ JSON serialization
XSS Prevention         ✓ HTML escaping in JS
SQL Injection          ✓ N/A (no database)
CORS                   ✓ Configurable in FastAPI
Rate Limiting          ○ Recommended for production
Authentication         ○ N/A (demo)
```

## Deployment Architecture

```
Development:
  Client → FastAPI Dev Server (localhost:8000)

Production (Recommended):
  Client → Reverse Proxy (Nginx)
         → Gunicorn Workers (4+)
         → FastAPI App
         → Model (In-Memory)

Docker:
  Client → Docker Container
         → Uvicorn + FastAPI App
         → Model (In-Memory)

Cloud (AWS/GCP/Heroku):
  Client → Load Balancer
         → Container Orchestration (K8s/ECS)
         → Multiple FastAPI Instances
         → Shared Model Cache
```

## Extension Points

```
├── Add More Corpora
│   └── Modify train_model() to support multiple sources
│
├── Implement Persistence
│   └── Add model.save() / model.load() methods
│
├── Add Database Logging
│   └── Log predictions to PostgreSQL/MongoDB
│
├── Implement Caching
│   └── Cache popular queries with @lru_cache
│
├── Add Confidence Scores
│   └── Calculate probability percentages
│
└── Support Multiple N-gram Sizes
    └── Create BigramModel, FourgramModel classes
```

---

For more details, see:
- [main.py](main.py) - Complete backend code
- [static/index.html](static/index.html) - Complete frontend code
- [README.md](README.md) - Full documentation
