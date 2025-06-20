import streamlit as st
import requests
import time
import json
import os

# ------------------- Page Config ------------------- #
st.set_page_config(page_title="Keyword Extractor", layout="centered")
st.title("🔍 Internal Site Keyword Extractor")

# ------------------- URL Input ------------------- #
url = st.text_input("🌐 Enter the URL of the page:")
BACKEND_HOST = os.getenv("BACKEND_HOST", "backend")

# ------------------- Auto Method Selector ------------------- #
def auto_pick_method(url: str) -> str:
    lowered = url.lower()
    if "wikipedia" in lowered:
        return "keybert"
    elif "medium" in lowered or "blog" in lowered:
        return "llm"
    elif "arxiv" in lowered or "research" in lowered:
        return "tfidf"
    else:
        return "rake"

method = "keybert"  # default
if url:
    method = auto_pick_method(url)

selected_method = st.selectbox(
    "🧠 Choose Extraction Method (Auto-selected):",
    options=["keybert", "rake", "tfidf", "llm"],
    index=["keybert", "rake", "tfidf", "llm"].index(method),
    help="You can override the auto-suggested method."
)

# ------------------- Keyword Extraction ------------------- #
if st.button("🚀 Extract Keywords"):
    if not url.strip():
        st.warning("Please enter a valid URL.")
    else:
        with st.spinner(f"Extracting keywords using `{selected_method}`..."):
            start = time.time()

            try:
                response = requests.get(
                        f"http://{BACKEND_HOST}:8000/extract_keywords",
                        params={"url": url, "method": selected_method},
                        timeout=40)
                response.raise_for_status()

                keywords = response.json().get("keywords", [])
                elapsed = round(time.time() - start, 2)

                if keywords:
                    st.success(f"✅ {len(keywords)} Keywords Extracted using `{selected_method}` in {elapsed}s")
                    st.markdown("### 🔑 Extracted Keywords:")

                    for kw in keywords:
                        st.markdown(f"<span style='color:#4b8bbe;font-size:18px;'>• {kw.strip()}</span>", unsafe_allow_html=True)

                    # JSON Download
                    st.download_button("📦 Download Keywords", json.dumps(keywords, indent=2),
                                       file_name="keywords.json", mime="application/json")
                else:
                    st.warning("No keywords found. Try a different method or check the content.")

            except requests.exceptions.Timeout:
                st.error("⏰ Request timed out. Try a lighter method or check your internet.")
            except requests.exceptions.ConnectionError:
                st.error("🚫 Backend not reachable. Is FastAPI running?")
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ HTTP Error: {e.response.status_code} - {e.response.reason}")
            except Exception as e:
                st.error(f"🔥 Unexpected error: {str(e)}")
