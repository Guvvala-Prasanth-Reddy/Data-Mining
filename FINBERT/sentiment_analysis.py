import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

class LongTextSentimentAnalyzer:
    def __init__(self, model_name="yiyanghkust/finbert-tone", device=None):
        """
        Initialize FinBERT sentiment analysis for long texts
        
        Args:
            model_name (str): Hugging Face model identifier
            device (str, optional): Device to run model on (cuda/cpu)
        """
        # Auto-detect device if not specified
        if device is None:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device)
        self.device = device
        
        # Mapping FinBERT labels to more intuitive names
        self.label_map = {
            'Positive': 'positive', 
            'Negative': 'negative', 
            'Neutral': 'neutral'
        }

    def chunk_text(self, text, max_length=512, overlap=128):
        """
        Chunk long text into overlapping segments
        
        Args:
            text (str): Input text to chunk
            max_length (int): Maximum token length per chunk
            overlap (int): Number of tokens to overlap between chunks
        
        Returns:
            List of text chunks
        """
        # Tokenize without adding special tokens initially
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        
        chunks = []
        for start in range(0, len(tokens), max_length - overlap):
            # Take chunk with a sliding window
            chunk_tokens = tokens[start:start + max_length]
            
            # Add special tokens
            chunk_tokens = [self.tokenizer.cls_token_id] + chunk_tokens + [self.tokenizer.sep_token_id]
            
            # Decode chunk
            chunk = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk)
        
        return chunks

    def analyze_sentiment(self, text, aggregation='weighted'):
        """
        Analyze sentiment for long text
        
        Args:
            text (str): Input text to analyze
            aggregation (str): Method of aggregating chunk sentiments 
                               ('weighted', 'average', 'max')
        
        Returns:
            Dict of sentiment scores
        """
        # Handle very short texts
        if len(text) < 50:
            return {
                'positive': 0.0, 
                'negative': 0.0, 
                'neutral': 1.0,
                'overall_sentiment': 'neutral'
            }
        
        # Chunk the text
        chunks = self.chunk_text(text)
        
        # Prepare for sentiment analysis
        chunk_results = []
        chunk_lengths = []
        
        for chunk in chunks:
            # Tokenize chunk
            inputs = self.tokenizer(
                chunk, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512
            ).to(self.device)
            
            # Predict sentiment
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=1)
                predictions = probabilities.cpu().numpy()[0]
            
            chunk_results.append(predictions)
            chunk_lengths.append(len(chunk))
        
        # Aggregate results
        chunk_results = np.array(chunk_results)
        chunk_lengths = np.array(chunk_lengths)
        
        if aggregation == 'weighted':
            # Weight by chunk length
            weights = chunk_lengths / np.sum(chunk_lengths)
            sentiments = np.average(chunk_results, axis=0, weights=weights)
        elif aggregation == 'max':
            # Take max of each sentiment
            sentiments = np.max(chunk_results, axis=0)
        else:  # average
            sentiments = np.mean(chunk_results, axis=0)
        
        # Prepare final result
        result = {
            'positive': sentiments[0],
            'negative': sentiments[1], 
            'neutral': sentiments[2]
        }
        
        # Determine overall sentiment
        max_sentiment = max(result, key=result.get)
        result['overall_sentiment'] = max_sentiment
        
        return result

    def classify_sentiment(self, text):
        """
        Classify overall sentiment
        
        Args:
            text (str): Input text to classify
        
        Returns:
            str: Overall sentiment classification
        """
        sentiment_result = self.analyze_sentiment(text)
        return sentiment_result['overall_sentiment']

# Example usage
def main():
    # Initialize the sentiment analyzer
    analyzer = LongTextSentimentAnalyzer()
    
    # Example long text
    long_text = """
    Your long financial text goes here. The analyzer can handle 
    multiple paragraphs and lengthy documents about financial topics.
    """
    
    # Analyze sentiment
    sentiment = analyzer.analyze_sentiment(long_text)
    print("Sentiment Breakdown:")
    for key, value in sentiment.items():
        print(f"{key}: {value:.4f}")
    
    # Quick classification
    classification = analyzer.classify_sentiment(long_text)
    print(f"\nOverall Sentiment: {classification}")

if __name__ == "__main__":
    main()