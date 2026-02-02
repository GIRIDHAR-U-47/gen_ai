# Testing & Examples

## Running the Application

### Step 1: Install Dependencies
```bash
cd ngram-predictor
pip install -r requirements.txt
```

### Step 2: Start Server
```bash
python main.py
```

Expected console output:
```
Initializing FastAPI app and loading Trigram model...
Training Trigram model on Brown Corpus...
Model trained! Total unique bigrams: XXXXX
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Step 3: Access Application
Open browser: **http://localhost:8000**

---

## Test Cases & Expected Outputs

### Test Case 1: "of the"
**Input:**
```json
{"text": "of the"}
```

**Expected Predictions (examples):**
```json
{
  "predictions": ["states", "united", "government"],
  "input_text": "of the"
}
```

### Test Case 2: "united states"
**Input:**
```json
{"text": "united states"}
```

**Expected Predictions (examples):**
```json
{
  "predictions": ["government", "of", "and"],
  "input_text": "united states"
}
```

### Test Case 3: "in the"
**Input:**
```json
{"text": "in the"}
```

**Expected Predictions (examples):**
```json
{
  "predictions": ["united", "united", "american"],
  "input_text": "in the"
}
```

### Test Case 4: "new york"
**Input:**
```json
{"text": "new york"}
```

**Expected Predictions (examples):**
```json
{
  "predictions": ["times", "state", "city"],
  "input_text": "new york"
}
```

### Test Case 5: "the fact"
**Input:**
```json
{"text": "the fact"}
```

**Expected Predictions (examples):**
```json
{
  "predictions": ["that", "is", "that"],
  "input_text": "the fact"
}
```

### Test Case 6: "mr. president"
**Input:**
```json
{"text": "mr. president"}
```

**Expected Predictions (examples):**
```json
{
  "predictions": ["and", "has", "will"],
  "input_text": "mr. president"
}
```

---

## Using cURL for Testing

### Example 1: Basic Prediction
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"the united\"}"
```

### Example 2: Using jq to Format Output
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"the united\"}" | jq .
```

### Example 3: Save Output to File
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"the united\"}" > prediction_output.json
```

### Example 4: Test Error Handling (short input)
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"the\"}"
```

Expected Response:
```json
{
  "predictions": [],
  "input_text": "the"
}
```

---

## Using Python Requests for Testing

### Example 1: Simple Prediction
```python
import requests
import json

response = requests.post(
    "http://localhost:8000/predict",
    json={"text": "the united"}
)

print(json.dumps(response.json(), indent=2))
```

Output:
```json
{
  "predictions": ["states", "nations", "kingdom"],
  "input_text": "the united"
}
```

### Example 2: Multiple Predictions
```python
import requests

test_cases = [
    "of the",
    "united states",
    "in the",
    "new york",
    "the fact"
]

for text in test_cases:
    response = requests.post(
        "http://localhost:8000/predict",
        json={"text": text}
    )
    data = response.json()
    print(f"Input: {data['input_text']}")
    print(f"Predictions: {data['predictions']}")
    print()
```

### Example 3: Test API Health
```python
import requests

response = requests.get("http://localhost:8000/health")
print(response.json())
# Output: {"status": "ok", "model": "trigram"}
```

---

## Web UI Testing

### Step 1: Open Browser
Navigate to: **http://localhost:8000**

### Step 2: Test Input & Predict
1. Type in text box: "the united"
2. Click "Predict" button
3. Observe top 3 predictions displayed
4. Click on a prediction to extend the input
5. Click "Predict" again to chain predictions

### Step 3: Test Keyboard Shortcuts
1. Type: "of the"
2. Press **Enter** key
3. Verify predictions appear (no need to click button)

### Step 4: Test Error Cases
1. Type: "xyz" (single word) → See: "Please enter at least 2 words"
2. Leave empty → See: "Please enter some text"
3. Type gibberish like "qwerty asdfgh" → See: "No predictions found"

---

## Performance Testing

### Test Prediction Speed
```python
import requests
import time

# Warm up
requests.post("http://localhost:8000/predict", json={"text": "the united"})

# Time 100 predictions
start = time.time()
for i in range(100):
    requests.post("http://localhost:8000/predict", json={"text": "the united"})
end = time.time()

avg_time = (end - start) / 100
print(f"Average prediction time: {avg_time*1000:.2f}ms")
# Expected: <50ms per prediction
```

### Test Model Training Time
```python
import time
# Check console output for:
# "Training Trigram model on Brown Corpus..."
# "Model trained! Total unique bigrams: XXXXX"
# Measure time between these messages
# Expected: 30-60 seconds on first run
```

---

## Common Prediction Outputs

| Input Text | Top Predictions | Notes |
|-----------|-----------------|-------|
| "of the" | states, united, government | Very common pattern |
| "united states" | government, of, and | Second part of common phrase |
| "in the" | united, american, united | Descriptive phrases |
| "new york" | times, state, city | Proper noun context |
| "mr. ," | chairman, president, director | Titles in formal text |
| "the fact" | that, is, that | Connector phrases |
| "and the" | united, new, most | Common conjunctions |
| "to the" | united, united, president | Prepositions |
| "such as" | the, political, a | Comparative phrases |
| "is the" | united, most, following | Descriptive contexts |

---

## Troubleshooting Guide

### Issue: "No predictions found"
**Cause**: Bigram not in training data
**Solution**: Try common English phrases (e.g., "of the", "in the")

### Issue: Server won't start
**Cause**: Port 8000 already in use
**Solution**: 
```bash
# Use different port
uvicorn main:app --reload --port 8001
```

### Issue: "Module not found" errors
**Cause**: Dependencies not installed
**Solution**:
```bash
pip install -r requirements.txt
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

### Issue: Model training takes forever
**Cause**: First run needs to download/process corpus
**Solution**: Wait 30-60 seconds. Subsequent runs are instant.

### Issue: API returns empty predictions
**Possible Cause 1**: Input text is too short (need 2+ words)
**Possible Cause 2**: Word combination not in Brown Corpus

**Solution**: Try different word combinations or check if phrase is common in English text

---

## Validation Checklist

- [ ] Server starts without errors
- [ ] Web UI loads at http://localhost:8000
- [ ] Can type in text input box
- [ ] Predict button works with mouse click
- [ ] Enter key triggers prediction
- [ ] Valid inputs return 3 predictions
- [ ] Invalid inputs show error message
- [ ] Click prediction extends input
- [ ] API returns correct JSON format
- [ ] Health check endpoint works
- [ ] Model trains on startup
- [ ] Predictions appear in <1 second

---

## Next Steps for Development

1. **Add more corpus sources** - Try Gutenberg, Inaugural, etc.
2. **Implement confidence scores** - Return probability percentages
3. **Add request logging** - Track popular queries
4. **Build admin dashboard** - View statistics and logs
5. **Deploy to cloud** - AWS/Heroku/GCP
6. **Mobile app** - React Native or Flutter
7. **Support N-gram options** - Let users choose 2-gram vs 3-gram vs 4-gram

---

For more information, see:
- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - 30-second setup
- [CONFIG.md](CONFIG.md) - Advanced configuration
