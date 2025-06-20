import re
from bs4 import BeautifulSoup

class TextProcessor:
    def __init__(self):
        pass

    def clean_html(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def parse_text(self, text):
        # Simple parsing: split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return sentences