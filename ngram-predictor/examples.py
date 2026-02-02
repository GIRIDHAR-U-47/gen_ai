#!/usr/bin/env python3
"""
Example Script: Using the Next-Word Prediction API

This script demonstrates how to interact with the prediction API
in various ways.

Usage:
    python examples.py
"""

import requests
import json
import time
from typing import List, Dict

# API Configuration
API_BASE_URL = "http://localhost:8000"
PREDICT_ENDPOINT = f"{API_BASE_URL}/predict"
HEALTH_ENDPOINT = f"{API_BASE_URL}/health"

class PredictionClient:
    """Client for interacting with the prediction API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict:
        """Check if the API is running"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Health check failed: {e}")
            print(f"Is the server running? Try: python main.py")
            return None
    
    def predict(self, text: str) -> Dict:
        """Get predictions for given text"""
        try:
            response = self.session.post(
                f"{self.base_url}/predict",
                json={"text": text}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"❌ Prediction failed: {e}")
            return None
    
    def predict_multiple(self, texts: List[str]) -> List[Dict]:
        """Get predictions for multiple inputs"""
        results = []
        for text in texts:
            result = self.predict(text)
            if result:
                results.append(result)
            time.sleep(0.1)  # Small delay to avoid overwhelming server
        return results
    
    def chain_predictions(self, initial_text: str, depth: int = 3) -> List[str]:
        """Chain predictions: use result as next input"""
        sequence = initial_text.split()
        print(f"\n🔗 Chaining predictions (depth={depth}):")
        print(f"Start: {' '.join(sequence)}")
        
        for i in range(depth):
            result = self.predict(' '.join(sequence[-2:]))
            if not result or not result['predictions']:
                print(f"  └─ No predictions found")
                break
            
            next_word = result['predictions'][0]
            sequence.append(next_word)
            print(f"  ├─ Step {i+1}: {' '.join(sequence[-3:])}")
        
        return sequence
    
    def find_alternatives(self, text: str) -> None:
        """Show all top 3 predictions"""
        result = self.predict(text)
        if not result:
            return
        
        print(f"\n📊 Predictions for: '{result['input_text']}'")
        if result['predictions']:
            for i, word in enumerate(result['predictions'], 1):
                print(f"  {i}. {word}")
        else:
            print("  (No predictions found)")


def example_1_basic():
    """Example 1: Basic usage"""
    print("\n" + "="*50)
    print("Example 1: Basic Prediction")
    print("="*50)
    
    client = PredictionClient()
    result = client.predict("the united")
    
    if result:
        print(f"Input: {result['input_text']}")
        print(f"Predictions: {result['predictions']}")


def example_2_multiple():
    """Example 2: Multiple predictions"""
    print("\n" + "="*50)
    print("Example 2: Multiple Predictions")
    print("="*50)
    
    client = PredictionClient()
    test_cases = [
        "of the",
        "united states",
        "in the",
        "new york",
        "the fact"
    ]
    
    results = client.predict_multiple(test_cases)
    
    print(f"\nTested {len(results)} inputs:\n")
    for result in results:
        print(f"  '{result['input_text']}' → {result['predictions']}")


def example_3_chaining():
    """Example 3: Chain predictions"""
    print("\n" + "="*50)
    print("Example 3: Chaining Predictions")
    print("="*50)
    
    client = PredictionClient()
    sequence = client.chain_predictions("the united", depth=3)
    print(f"\nFinal sequence: {' '.join(sequence)}")


def example_4_error_handling():
    """Example 4: Error handling"""
    print("\n" + "="*50)
    print("Example 4: Error Handling")
    print("="*50)
    
    client = PredictionClient()
    
    print("\n1️⃣  Testing empty input:")
    result = client.predict("")
    print(f"   Result: {result}")
    
    print("\n2️⃣  Testing single word:")
    result = client.predict("hello")
    print(f"   Result: {result}")
    
    print("\n3️⃣  Testing gibberish:")
    result = client.predict("qwerty asdfgh")
    print(f"   Predictions: {result['predictions']}")


def example_5_alternatives():
    """Example 5: Show top 3 alternatives"""
    print("\n" + "="*50)
    print("Example 5: Exploring Alternatives")
    print("="*50)
    
    client = PredictionClient()
    phrases = ["of the", "united states", "new york"]
    
    for phrase in phrases:
        client.find_alternatives(phrase)


def example_6_performance():
    """Example 6: Performance testing"""
    print("\n" + "="*50)
    print("Example 6: Performance Testing")
    print("="*50)
    
    client = PredictionClient()
    
    # Warmup
    client.predict("the united")
    
    # Measure
    start = time.time()
    iterations = 10
    
    for i in range(iterations):
        client.predict("the united")
    
    elapsed = time.time() - start
    avg_time = (elapsed / iterations) * 1000
    
    print(f"\nResults:")
    print(f"  Total time: {elapsed:.3f}s")
    print(f"  Iterations: {iterations}")
    print(f"  Average: {avg_time:.2f}ms per request")
    print(f"  Throughput: {1000/avg_time:.0f} requests/second")


def example_7_all_predictions():
    """Example 7: Get all predictions for comparison"""
    print("\n" + "="*50)
    print("Example 7: Comparing Predictions")
    print("="*50)
    
    client = PredictionClient()
    
    phrases = {
        "of the": "Very common preposition pattern",
        "united states": "Country name",
        "in the": "Location phrase",
        "new york": "City name",
    }
    
    print("\nPhrase | Predictions")
    print("-" * 60)
    
    for phrase, description in phrases.items():
        result = client.predict(phrase)
        if result:
            preds = ", ".join(result['predictions'])
            print(f"{phrase:15} → {preds}")


def main():
    """Run all examples"""
    print("\n" + "🎯 Next-Word Prediction API - Example Usage" + "\n")
    
    # Check if server is running
    client = PredictionClient()
    health = client.health_check()
    
    if not health:
        print("\n⚠️  Server is not running!")
        print("Start it with: python main.py")
        return
    
    print(f"✅ Server is running: {health}")
    
    # Run examples
    try:
        example_1_basic()
        example_2_multiple()
        example_3_chaining()
        example_4_error_handling()
        example_5_alternatives()
        example_6_performance()
        example_7_all_predictions()
        
        print("\n" + "="*50)
        print("✅ All examples completed!")
        print("="*50)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
