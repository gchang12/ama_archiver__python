#!/usr/bin/python3
"""
"""
from bs4 import BeautifulSoup

question_text = "Why do androids dream of electric sheep?"
answer_text = "Ask PK Dick."

text = \
f"""
    <div class='usertext-body may-blank-within md-container'>
        <p>Nothing to see here, folks. This is skipped.</p>
    </div>
    <div class='usertext-body may-blank-within md-container'>
        <p>{question_text}</p>
    </div>
    <div class='usertext-body may-blank-within md-container'>
        <p>{answer_text}</p>
    </div>
""".strip()


if __name__ == '__main__':
    soup = BeautifulSoup(text, 'html.parser')
    stuff = []
    for div in soup.find_all("div"):
        print(div.text)
