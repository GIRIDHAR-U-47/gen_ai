from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from collections import defaultdict, Counter
import nltk
from nltk.corpus import brown
from nltk.tokenize import word_tokenize
import re

# Download required NLTK data
try:
    nltk.data.find('corpora/brown')
except LookupError:
    nltk.download('brown')

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# ============= Trigram Model =============
class TrigramModel:
    def __init__(self):
        self.trigrams = defaultdict(Counter)
        self.train_model()
    
    def preprocess_text(self, text):
        """Preprocess text: lowercase, remove special chars, tokenize"""
        text = text.lower()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Tokenize
        tokens = word_tokenize(text)
        return tokens
    
    def train_model(self):
        """Train trigram model on Brown Corpus"""
        print("Training Trigram model on Brown Corpus...")
        
        # Get all sentences from Brown Corpus
        for sentence in brown.sents():
            # Preprocess sentence
            tokens = [word.lower() for word in sentence]
            
            # Filter out very short sentences
            if len(tokens) < 3:
                continue
            
            # Add start tokens
            tokens = ['<START>', '<START>'] + tokens + ['<END>']
            
            # Create trigrams
            for i in range(len(tokens) - 2):
                bigram = (tokens[i], tokens[i + 1])
                next_word = tokens[i + 2]
                self.trigrams[bigram][next_word] += 1
        
        print(f"Model trained! Total unique bigrams: {len(self.trigrams)}")
    
    def predict(self, text, top_n=3):
        """
        Predict next word(s) given input text
        
        Args:
            text: Input text (e.g., "the united")
            top_n: Number of predictions to return
        
        Returns:
            List of top predicted words with probabilities
        """
        tokens = self.preprocess_text(text)
        
        if len(tokens) < 2:
            return []
        
        # Get last two words to form bigram
        bigram = (tokens[-2], tokens[-1])
        
        # Check if bigram exists in training data
        if bigram not in self.trigrams:
            # Try with lowercased version
            bigram = (tokens[-2].lower(), tokens[-1].lower())
            if bigram not in self.trigrams:
                return []
        
        # Get counter for next words
        next_words = self.trigrams[bigram]
        
        # Return top N predictions
        predictions = []
        for word, count in next_words.most_common(top_n):
            if word not in ['<START>', '<END>']:
                predictions.append({
                    'word': word,
                    'frequency': count
                })
        
        return predictions[:top_n]


# Initialize model (trained once at startup)
print("Initializing FastAPI app and loading Trigram model...")
model = TrigramModel()

# ============= FastAPI Setup =============
app = FastAPI(title="Next-Word Prediction API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Request/Response models
class PredictRequest(BaseModel):
    text: str

class PredictionResult(BaseModel):
    word: str
    frequency: int

class PredictResponse(BaseModel):
    predictions: list[str]
    input_text: str

# ============= Routes =============

@app.get("/")
async def root():
    """Serve the main HTML file"""
    return FileResponse("static/index.html", media_type="text/html")

@app.post("/predict")
async def predict(request: PredictRequest):
    """
    Predict next word(s) given input text
    
    Example:
        Input: {"text": "the united"}
        Output: {"predictions": ["states", "nations", "kingdom"], "input_text": "the united"}
    """
    if not request.text or not request.text.strip():
        return {"predictions": [], "input_text": request.text}
    
    # Get predictions from model
    results = model.predict(request.text, top_n=3)
    
    # Extract just the words for the response
    predictions = [result['word'] for result in results]
    
    return {
        "predictions": predictions,
        "input_text": request.text
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "model": "trigram"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
