# Configuration & Customization Guide

## Model Parameters

Edit `main.py` to customize the Trigram model:

### Number of Predictions
```python
# In the /predict endpoint
results = model.predict(request.text, top_n=5)  # Change 3 to desired number
```

### Trigram Minimum Frequency
Add frequency filtering in the `predict()` method:
```python
# Filter out rare predictions (occur less than N times)
MIN_FREQUENCY = 2
predictions = [
    p for p in next_words.most_common(top_n) 
    if p[1] >= MIN_FREQUENCY
]
```

## Server Configuration

### Change Port
```bash
# Use port 8001 instead of 8000
uvicorn main:app --reload --port 8001
```

### Enable CORS (for frontend access from different origin)
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: restrict this!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Performance Tuning

### 1. Reduce Training Time (Use Smaller Sample)
```python
# In train_model(), process only first N sentences:
sentence_count = 0
for sentence in brown.sents():
    if sentence_count >= 10000:  # Limit to 10k sentences
        break
    # ... rest of training code
    sentence_count += 1
```

### 2. Increase Predictions Speed
- Model already runs in-memory ✓
- Predictions take <50ms ✓
- No further optimization needed for typical use

## Different Corpus Sources

### Use a Different NLTK Corpus
```python
# Instead of brown.sents(), use:
from nltk.corpus import gutenberg
# or
from nltk.corpus import inaugural
# or
from nltk.corpus import movie_reviews
```

### Train on Custom Text
```python
def train_from_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    tokens = word_tokenize(text.lower())
    tokens = ['<START>', '<START>'] + tokens + ['<END>']
    
    for i in range(len(tokens) - 2):
        bigram = (tokens[i], tokens[i+1])
        next_word = tokens[i+2]
        self.trigrams[bigram][next_word] += 1
```

## Frontend Customization

### Change Color Scheme
Edit `static/index.html` CSS:
```css
/* Change primary gradient color */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
/* To something like: */
background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
```

### Add Custom Predictions Limit
In JavaScript section:
```javascript
// Change top 3 to top 5
const top_n = 5;
```

### Modify Input Validation
```javascript
// Change minimum words requirement from 2 to 3
if (words.length < 3) {
    showError('Please enter at least 3 words');
}
```

## Advanced Features

### Add Confidence Scores
Modify the response:
```python
@app.post("/predict")
async def predict(request: PredictRequest):
    results = model.predict(request.text, top_n=3)
    
    # Add confidence calculation
    total_freq = sum(r['frequency'] for r in results)
    predictions_with_confidence = []
    
    for result in results:
        confidence = (result['frequency'] / total_freq) * 100
        predictions_with_confidence.append({
            'word': result['word'],
            'confidence': round(confidence, 2)
        })
    
    return {
        "predictions": [p['word'] for p in predictions_with_confidence],
        "confidence": [p['confidence'] for p in predictions_with_confidence],
        "input_text": request.text
    }
```

### Add Fallback Predictions
If bigram not found, predict based on single word:
```python
def predict(self, text, top_n=3):
    tokens = self.preprocess_text(text)
    
    # Try trigram first
    if len(tokens) >= 2:
        bigram = (tokens[-2], tokens[-1])
        if bigram in self.trigrams:
            next_words = self.trigrams[bigram]
            return [{'word': w, 'frequency': c} 
                   for w, c in next_words.most_common(top_n)]
    
    # Fallback to unigram (single word)
    if len(tokens) >= 1:
        unigram = (tokens[-1],)
        if unigram in self.unigrams:
            next_words = self.unigrams[unigram]
            return [{'word': w, 'frequency': c} 
                   for w, c in next_words.most_common(top_n)]
    
    return []
```

### Add Caching for Popular Queries
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_predict(self, text, top_n=3):
    return self.predict(text, top_n)
```

### Add Request Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/predict")
async def predict(request: PredictRequest):
    logger.info(f"Prediction request: {request.text}")
    # ... rest of code
```

## Database Integration (Optional)

Store predictions and user queries:
```python
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class PredictionLog(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True)
    input_text = Column(String)
    predictions = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

# In your endpoint:
@app.post("/predict")
async def predict(request: PredictRequest, db: Session = Depends(get_db)):
    predictions = model.predict(request.text)
    
    # Log to database
    log = PredictionLog(
        input_text=request.text,
        predictions=",".join(predictions)
    )
    db.add(log)
    db.commit()
    
    return {"predictions": predictions}
```

## Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t ngram-predictor .
docker run -p 8000:8000 ngram-predictor
```

## Production Deployment

### Gunicorn (Recommended)
```bash
pip install gunicorn

# Run with 4 workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Environment Variables
Create `.env`:
```
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=info
DEBUG=false
```

Load in `main.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()
port = int(os.getenv('PORT', 8000))
```

---

See [README.md](README.md) for more information.
