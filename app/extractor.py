from keybert import KeyBERT
from sklearn.feature_extraction.text import TfidfVectorizer
from rake_nltk import Rake
from transformers import pipeline
import torch
import re


class KeywordExtractor:
    def __init__(self):
        self.kw_model = KeyBERT()
        self.llm_model = pipeline(
            "text2text-generation",
            model="google/flan-t5-small",  # Lighter model
            device=-1  # Force CPU
        )

    def extract_keywords(self, text, top_n=5):
        keywords = self.kw_model.extract_keywords(
            text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=top_n
        )
        return [kw[0] for kw in keywords]

    def extract_rake(self, text):
        r = Rake()
        r.extract_keywords_from_text(text)
        return r.get_ranked_phrases()

    def extract_tfidf(self, text, top_n=10):
        vectorizer = TfidfVectorizer(stop_words="english", max_features=top_n)
        X = vectorizer.fit_transform([text])
        return vectorizer.get_feature_names_out().tolist()

    def extract_llm_keywords(self, text):
    # Give it a wider window to find more keywords
    # Skip the first 100 (usually "SpaceX - Wikipedia") and take 1500 chars
        clean_text = text[100:1600] 

        prompt = (
            "Instructions: List exactly 5 important keywords from the text below. "
            "Focus on companies, people, and technology. "
            "Format: keyword1, keyword2, keyword3, keyword4, keyword5. "
            f"Text: {clean_text}"
        )
        
        result = self.llm_model(
            prompt, 
            max_new_tokens=100, # Increased to allow more words
            do_sample=True, 
            temperature=0.7,     # Add a bit of 'creativity'
            repetition_penalty=1.5 # Lowered from 3.0 so it's less aggressive
        )
        
        raw_output = result[0]["generated_text"]
        
        # Simple split and clean
        keywords = [k.strip() for k in raw_output.split(',') if len(k.strip()) > 2]
        
        # Final filter: Remove generic Wikipedia words
        junk_words = ["wikipedia", "content", "sidebar", "menu", "article"]
        final_keywords = [k for k in keywords if k.lower() not in junk_words]
        
        return final_keywords[:6]