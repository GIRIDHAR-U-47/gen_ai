# Quick Start Guide

## 30-Second Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Server
```bash
python main.py
```

Expected output:
```
Initializing FastAPI app and loading Trigram model...
Training Trigram model on Brown Corpus...
Model trained! Total unique bigrams: XXXXX
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 3. Open Browser
Navigate to: **http://localhost:8000**

## Testing the API

### Using the Web UI
1. Type: "the united"
2. Click "Predict"
3. See: ["states", "nations", "kingdom"] (or similar)

### Using curl
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"the united\"}"
```

Response:
```json
{
  "predictions": ["states", "nations", "kingdom"],
  "input_text": "the united"
}
```

## Keyboard Shortcuts
- **Enter key** while typing → Predict
- **Click predictions** → Add to input for chaining

## Common Test Cases

| Input | Expected Output (approx) |
|-------|--------------------------|
| "of the" | states, united, government |
| "united states" | government, congress, system |
| "in the" | united, us, american |
| "new york" | times, state, city |

---

**⏳ First run takes 30-60 seconds to train the model. Subsequent runs are instant!**
