#!/usr/bin/env python3
"""
Advanced AI Engine - Step 6: Machine Learning & AI Integration
Integrates multiple AI models for enhanced document and photo analysis
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import numpy as np
import pandas as pd

# AI/ML imports
try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    from sentence_transformers import SentenceTransformer
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch/Transformers not available. Some features will be limited.")

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Warning: spaCy not available. NLP features will be limited.")

try:
    import cv2
    import PIL.Image
    from PIL import Image
    CV_AVAILABLE = True
except ImportError:
    CV_AVAILABLE = False
    print("Warning: OpenCV/PIL not available. Computer vision features will be limited.")

# Local imports
import sys
sys.path.append(str(Path(__file__).parent.parent / 'rag'))
from rag_search import RAGSearchEngine

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedAIEngine:
    """
    Advanced AI Engine integrating multiple AI models for enhanced analysis
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Advanced AI Engine"""
        self.config = self._load_config(config_path)
        self.models = {}
        self.rag_engine = None
        self._initialize_models()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "models": {
                "text_classification": "distilbert-base-uncased",
                "sentiment_analysis": "cardiffnlp/twitter-roberta-base-sentiment-latest",
                "named_entity_recognition": "dbmdz/bert-large-cased-finetuned-conll03-english",
                "summarization": "facebook/bart-large-cnn",
                "question_answering": "deepset/roberta-base-squad2",
                "image_captioning": "Salesforce/blip-image-captioning-large",
                "zero_shot_classification": "facebook/bart-large-mnli"
            },
            "spacy_model": "en_core_web_sm",
            "embedding_model": "all-MiniLM-L6-v2",
            "max_text_length": 512,
            "confidence_threshold": 0.7
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                logger.info(f"Loaded configuration from {config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def _initialize_models(self):
        """Initialize AI models based on configuration"""
        logger.info("Initializing AI models...")
        
        if TORCH_AVAILABLE:
            try:
                # Text classification
                self.models['text_classifier'] = pipeline(
                    "text-classification",
                    model=self.config['models']['text_classification'],
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info("✓ Text classification model loaded")
                
                # Sentiment analysis
                self.models['sentiment_analyzer'] = pipeline(
                    "sentiment-analysis",
                    model=self.config['models']['sentiment_analysis'],
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info("✓ Sentiment analysis model loaded")
                
                # Named entity recognition
                self.models['ner'] = pipeline(
                    "ner",
                    model=self.config['models']['named_entity_recognition'],
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info("✓ Named entity recognition model loaded")
                
                # Summarization
                self.models['summarizer'] = pipeline(
                    "summarization",
                    model=self.config['models']['summarization'],
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info("✓ Summarization model loaded")
                
                # Question answering
                self.models['qa'] = pipeline(
                    "question-answering",
                    model=self.config['models']['question_answering'],
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info("✓ Question answering model loaded")
                
                # Zero-shot classification
                self.models['zero_shot'] = pipeline(
                    "zero-shot-classification",
                    model=self.config['models']['zero_shot_classification'],
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info("✓ Zero-shot classification model loaded")
                
            except Exception as e:
                logger.error(f"Failed to initialize some models: {e}")
        
        if SPACY_AVAILABLE:
            try:
                # Load spaCy model
                self.models['spacy_nlp'] = spacy.load(self.config['spacy_model'])
                logger.info(f"✓ spaCy model '{self.config['spacy_model']}' loaded")
            except Exception as e:
                logger.warning(f"Failed to load spaCy model: {e}")
        
        # Initialize sentence transformer for embeddings
        try:
            self.models['sentence_transformer'] = SentenceTransformer(
                self.config['embedding_model']
            )
            logger.info(f"✓ Sentence transformer '{self.config['embedding_model']}' loaded")
        except Exception as e:
            logger.error(f"Failed to load sentence transformer: {e}")
        
        logger.info(f"AI Engine initialized with {len(self.models)} models")
    
    def analyze_document(self, text: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Perform comprehensive document analysis using multiple AI models
        """
        if not text or len(text.strip()) == 0:
            return {"error": "Empty or invalid text provided"}
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "text_length": len(text),
            "analysis": {}
        }
        
        # Truncate text if too long
        if len(text) > self.config['max_text_length']:
            text = text[:self.config['max_text_length']]
            results["text_truncated"] = True
        
        try:
            # Text classification
            if 'text_classifier' in self.models:
                classification = self.models['text_classifier'](text)
                results["analysis"]["classification"] = classification
            
            # Sentiment analysis
            if 'sentiment_analyzer' in self.models:
                sentiment = self.models['sentiment_analyzer'](text)
                results["analysis"]["sentiment"] = sentiment
            
            # Named entity recognition
            if 'ner' in self.models:
                entities = self.models['ner'](text)
                results["analysis"]["entities"] = entities
            
            # Text summarization
            if 'summarizer' in self.models:
                summary = self.models['summarizer'](text, max_length=130, min_length=30)
                results["analysis"]["summary"] = summary
            
            # Advanced NLP with spaCy
            if 'spacy_nlp' in self.models:
                doc = self.models['spacy_nlp'](text)
                nlp_analysis = {
                    "tokens": len(doc),
                    "sentences": len(list(doc.sents)),
                    "noun_chunks": [chunk.text for chunk in doc.noun_chunks],
                    "key_phrases": [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and token.is_alpha],
                    "language": doc.lang_,
                    "pos_tags": {token.text: token.pos_ for token in doc[:20]}  # First 20 tokens
                }
                results["analysis"]["nlp"] = nlp_analysis
            
            # Generate embeddings
            if 'sentence_transformer' in self.models:
                embedding = self.models['sentence_transformer'].encode(text)
                results["analysis"]["embedding_dimension"] = len(embedding)
                results["analysis"]["embedding_sample"] = embedding[:10].tolist()  # First 10 dimensions
            
            # Add metadata if provided
            if metadata:
                results["metadata"] = metadata
                
        except Exception as e:
            logger.error(f"Error during document analysis: {e}")
            results["error"] = str(e)
        
        return results
    
    def classify_content(self, text: str, candidate_labels: List[str]) -> Dict[str, Any]:
        """
        Perform zero-shot classification of content
        """
        if 'zero_shot' not in self.models:
            return {"error": "Zero-shot classification model not available"}
        
        try:
            result = self.models['zero_shot'](text, candidate_labels)
            return {
                "labels": result["labels"],
                "scores": result["scores"],
                "top_label": result["labels"][0],
                "confidence": result["scores"][0]
            }
        except Exception as e:
            logger.error(f"Error during zero-shot classification: {e}")
            return {"error": str(e)}
    
    def answer_question(self, question: str, context: str) -> Dict[str, Any]:
        """
        Answer questions based on provided context
        """
        if 'qa' not in self.models:
            return {"error": "Question answering model not available"}
        
        try:
            result = self.models['qa'](question=question, context=context)
            return {
                "answer": result["answer"],
                "confidence": result["score"],
                "start": result["start"],
                "end": result["end"]
            }
        except Exception as e:
            logger.error(f"Error during question answering: {e}")
            return {"error": str(e)}
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze images using computer vision models
        """
        if not CV_AVAILABLE:
            return {"error": "Computer vision libraries not available"}
        
        if not Path(image_path).exists():
            return {"error": f"Image file not found: {image_path}"}
        
        try:
            # Load image
            image = Image.open(image_path)
            results = {
                "timestamp": datetime.now().isoformat(),
                "image_path": image_path,
                "image_size": image.size,
                "image_mode": image.mode,
                "analysis": {}
            }
            
            # Basic image analysis
            if image.mode == 'RGB':
                # Convert to numpy array for OpenCV analysis
                img_array = np.array(image)
                
                # Color analysis
                colors = img_array.mean(axis=(0, 1))
                results["analysis"]["color_profile"] = {
                    "red": float(colors[0]),
                    "green": float(colors[1]),
                    "blue": float(colors[2])
                }
                
                # Brightness and contrast
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                results["analysis"]["brightness"] = float(gray.mean())
                results["analysis"]["contrast"] = float(gray.std())
                
                # Edge detection
                edges = cv2.Canny(gray, 100, 200)
                results["analysis"]["edge_density"] = float(edges.sum() / edges.size)
            
            # Image captioning (if model available)
            if 'image_captioner' in self.models:
                try:
                    caption = self.models['image_captioner'](image)
                    results["analysis"]["caption"] = caption
                except Exception as e:
                    logger.warning(f"Image captioning failed: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error during image analysis: {e}")
            return {"error": str(e)}
    
    def batch_analyze_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple documents in batch
        """
        results = []
        total = len(documents)
        
        for i, doc in enumerate(documents):
            logger.info(f"Analyzing document {i+1}/{total}")
            
            if 'text' in doc:
                analysis = self.analyze_document(doc['text'], doc.get('metadata'))
                results.append({
                    "document_id": doc.get('id', i),
                    "analysis": analysis
                })
            else:
                results.append({
                    "document_id": doc.get('id', i),
                    "error": "No text content found"
                })
        
        return results
    
    def generate_insights(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate insights from multiple document analyses
        """
        if not analyses:
            return {"error": "No analyses provided"}
        
        insights = {
            "total_documents": len(analyses),
            "timestamp": datetime.now().isoformat(),
            "insights": {}
        }
        
        try:
            # Aggregate sentiment scores
            sentiments = []
            classifications = []
            entity_types = {}
            
            for analysis in analyses:
                if 'analysis' in analysis and 'sentiment' in analysis['analysis']:
                    sentiment = analysis['analysis']['sentiment']
                    if isinstance(sentiment, list) and len(sentiment) > 0:
                        sentiments.append(sentiment[0])
                
                if 'analysis' in analysis and 'classification' in analysis['analysis']:
                    classification = analysis['analysis']['classification']
                    if isinstance(classification, list) and len(classification) > 0:
                        classifications.append(classification[0])
                
                if 'analysis' in analysis and 'entities' in analysis['analysis']:
                    entities = analysis['analysis']['entities']
                    for entity in entities:
                        entity_type = entity.get('entity_group', 'UNKNOWN')
                        entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
            
            # Sentiment insights
            if sentiments:
                positive_count = sum(1 for s in sentiments if s.get('label', '').lower() in ['positive', 'pos'])
                negative_count = sum(1 for s in sentiments if s.get('label', '').lower() in ['negative', 'neg'])
                neutral_count = len(sentiments) - positive_count - negative_count
                
                insights["insights"]["sentiment_distribution"] = {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count,
                    "total": len(sentiments)
                }
            
            # Classification insights
            if classifications:
                class_counts = {}
                for cls in classifications:
                    label = cls.get('label', 'unknown')
                    class_counts[label] = class_counts.get(label, 0) + 1
                
                insights["insights"]["classification_distribution"] = class_counts
            
            # Entity insights
            if entity_types:
                insights["insights"]["entity_distribution"] = entity_types
            
            # Text length statistics
            text_lengths = [a.get('text_length', 0) for a in analyses if 'text_length' in a]
            if text_lengths:
                insights["insights"]["text_statistics"] = {
                    "average_length": sum(text_lengths) / len(text_lengths),
                    "min_length": min(text_lengths),
                    "max_length": max(text_lengths),
                    "total_text": sum(text_lengths)
                }
                
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            insights["error"] = str(e)
        
        return insights
    
    def export_analysis(self, analysis_results: List[Dict[str, Any]], output_path: str):
        """
        Export analysis results to JSON file
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_results, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Analysis results exported to {output_file}")
            return {"success": True, "output_path": str(output_file)}
            
        except Exception as e:
            logger.error(f"Error exporting analysis: {e}")
            return {"error": str(e)}

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced AI Engine for document and image analysis")
    parser.add_argument("--action", choices=["analyze", "classify", "qa", "batch", "insights"], 
                       required=True, help="Action to perform")
    parser.add_argument("--input", required=True, help="Input file or text")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--labels", nargs="+", help="Candidate labels for classification")
    parser.add_argument("--question", help="Question for QA")
    parser.add_argument("--context", help="Context for QA")
    
    args = parser.parse_args()
    
    # Initialize AI engine
    engine = AdvancedAIEngine(args.config)
    
    if args.action == "analyze":
        if Path(args.input).exists():
            # Input is a file
            with open(args.input, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            # Input is text
            text = args.input
        
        result = engine.analyze_document(text)
        print(json.dumps(result, indent=2))
        
        if args.output:
            engine.export_analysis([result], args.output)
    
    elif args.action == "classify":
        if not args.labels:
            print("Error: --labels required for classification")
            return
        
        if Path(args.input).exists():
            with open(args.input, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            text = args.input
        
        result = engine.classify_content(text, args.labels)
        print(json.dumps(result, indent=2))
    
    elif args.action == "qa":
        if not args.question or not args.context:
            print("Error: --question and --context required for QA")
            return
        
        result = engine.answer_question(args.question, args.context)
        print(json.dumps(result, indent=2))
    
    elif args.action == "batch":
        if not Path(args.input).exists():
            print("Error: Input must be a file for batch processing")
            return
        
        with open(args.input, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        results = engine.batch_analyze_documents(documents)
        print(json.dumps(results, indent=2))
        
        if args.output:
            engine.export_analysis(results, args.output)
    
    elif args.action == "insights":
        if not Path(args.input).exists():
            print("Error: Input must be a file for insights generation")
            return
        
        with open(args.input, 'r', encoding='utf-8') as f:
            analyses = json.load(f)
        
        insights = engine.generate_insights(analyses)
        print(json.dumps(insights, indent=2))
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(insights, f, indent=2, ensure_ascii=False, default=str)

if __name__ == "__main__":
    main()
