from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.scraper import Scraper
from app.processor import TextProcessor
from app.extractor import KeywordExtractor
from app.vectorstore import VectorStore  # Assuming this exists

import traceback

app = FastAPI(
    title="🔑 Internal Keyword Extractor API",
    description="Extracts important keywords from internal pages using NLP + LLMs",
    version="2.0.0"
)

# CORS middleware to connect with Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Optional: restrict to frontend domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
scraper = Scraper()
processor = TextProcessor()
extractor = KeywordExtractor()
vectorstore = VectorStore()  # Assuming this handles FAISS logic

@app.get("/")
def root():
    return {"message": "🚀 Keyword Extractor API is running!"}


@app.get("/extract_keywords")
async def extract_keywords_endpoint(
    url: str = Query(..., description="Page URL"),
    method: str = Query("keybert", description="Extraction method: keybert, rake, tfidf, llm")
):
    try:
        html_content = await scraper.scrape_page(url)
        text = processor.clean_html(html_content)

        # Choose method
        if method == "keybert":
            keywords = extractor.extract_keywords(text)
        elif method == "rake":
            keywords = extractor.extract_rake(text)
        elif method == "tfidf":
            keywords = extractor.extract_tfidf(text)
        elif method == "llm":
            keywords = extractor.extract_llm_keywords(text)
        else:
            raise ValueError("❌ Invalid extraction method specified.")

        # Save to vector store (index + metadata like URL)
        vectorstore.save_keywords(keywords, url)

        return JSONResponse(content={"keywords": keywords})

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"🔥 Internal Error: {str(e)}")
