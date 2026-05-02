import re
from bs4 import BeautifulSoup

class TextProcessor:
    def __init__(self):
        pass

    # def clean_html(self, html_content):
    #     soup = BeautifulSoup(html_content, 'html.parser')
    #     text = soup.get_text()
    #     text = re.sub(r'\s+', ' ', text).strip()
    #     return text
    def clean_html(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. REMOVE NOISE: Delete tags that never contain useful keywords
        for element in soup(["nav", "footer", "header", "script", "style", "aside", "noscript"]):
            element.decompose()

        # 2. TARGET CONTENT: On many sites, the real text is in <main> or <article>
        # If those exist, just use them. Otherwise, use body.
        main_content = soup.find("main") or soup.find("article") or soup.find("body")
        
        text = main_content.get_text(separator=' ', strip=True)
        return text

    def parse_text(self, text):
        # Simple parsing: split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return sentences