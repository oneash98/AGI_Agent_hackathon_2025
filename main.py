import os
from dotenv import load_dotenv
import requests
import streamlit as st
from bs4 import BeautifulSoup

# API KEY 가져오기 
if os.path.exists('.env'): # 로컬에서 테스트 실행
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
else: # streamlit web에서 실행
    API_KEY = st.secrets["API_KEY"]


def test_function(file_path):

    url = "https://api.upstage.ai/v1/document-digitization"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    files = {"document": open(file_path, "rb")}
    data = {"ocr": "force", "base64_encoding": "['table']", "model": "document-parse"}
    response = requests.post(url, headers=headers, files=files, data=data)
    
    contents_html = response.json()['content']['html']
    soup = BeautifulSoup(contents_html)
    text = soup.find(attrs = {'id': '20'}).text

    return text