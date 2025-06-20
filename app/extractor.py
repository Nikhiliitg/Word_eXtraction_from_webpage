from keybert import KeyBERT
from sklearn.feature_extraction.text import TfidfVectorizer
from rake_nltk import Rake
from transformers import pipeline
import torch


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
        prompt = (
            "You are a keyword extraction expert. Read the following content and extract 5 to 10 important keywords. "
            "Return them as a comma-separated list:\n\n"
            f"{text[:1000]}"  # limit prompt to avoid hitting max token limit
        )
        result = self.llm_model(prompt, max_length=100, min_length=10, do_sample=False)
        return [kw.strip() for kw in result[0]["generated_text"].split(",")]
