import json
import requests
from bs4 import BeautifulSoup
from langchain_upstage import ChatUpstage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import base64, json
from openai import OpenAI
import numpy as np
from typing import List, Dict

# 1. 공통 필요 함수 ----------------------------------------------------------------------------------------------------------------

# 이미지 파일을 base64로 인코딩하는 함수
# 이 함수는 이미지 파일을 읽고 base64로 인코딩하여 문자열로 반환합니다.
def encode_image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# 이미지에서 정보를 추출하는 함수
# 이 함수는 Upstage API를 사용하여 이미지에서 정보를 추출합니다.
def extract_information_from_image(API_KEY, file_path):
    # Encode the image
    encoded_image = encode_image_to_base64(file_path)
    
    # Define your schema (or use a pre-generated one)
    schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "document_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "키": {
                        "type": "number",
                        "description": "키 (cm)"
                    },
                    "몸무게": {
                        "type": "number",
                        "description": "몸무게 (kg)"
                    },
                    "체질량지수": {
                        "type": "number",
                        "description": "체질량지수 (kg/㎡)"
                    },
                    "허리둘레": {
                        "type": "number",
                        "description": "허리둘레 (cm)"
                    },
                    "혈압": {
                        "type": "string",
                        "description": "혈압 (수축기/이완기, mmHg)"
                    },
                    "혈색소": {
                        "type": "string",
                        "description": "빈혈 등 혈색소 (g/dL)"
                    },
                    "빈혈 소견": {
                        "type": "string",
                        "description": "정상/빈혈 의심/기타 중 체크된 항목"
                    },
                    "공복혈당": {
                        "type": "string",
                        "description": "당뇨병 공복혈당 (mg/dL)"
                    },
                    "당뇨병 소견": {
                        "type": "string",
                        "description": "정상/공복혈당장애 의심/유질환자/당뇨병 의심 중 체크된 항목"
                    },
                    "총콜레스테롤": {
                        "type": "string",
                        "description": "총콜레스테롤 (mg/dL)"
                    },
                    "고밀도콜레스테롤": {
                        "type": "string",
                        "description": "고밀도 콜레스테롤 (mg/dL)"
                    },
                    "중성지방": {
                        "type": "string",
                        "description": "중성지방 (mg/dL)"
                    },
                    "저밀도콜레스테롤": {
                        "type": "string",
                        "description": "저밀도 콜레스테롤 (mg/dL)"
                    },
                    "이상지질혈증 소견": {
                        "type": "string",
                        "description": "정상/고콜레스테롤혈증 의심/고중성지방혈증 의심/낮은 HDL 콜레스테롤 의심/유질환자 중 체크된 항목"
                    },
                    "혈청크레아티닌": {
                        "type": "string",
                        "description": "혈청 크레아티닌 (mg/dL)"
                    },
                    "eGFR": {
                        "type": "string",
                        "description": "신사구체여과율 (mL/min/1.73㎡)"
                    },
                    "신장질환 소견": {
                        "type": "string",
                        "description": "정상/신장기능 이상 의심 중 체크된 항목"
                    },
                    "AST": {
                        "type": "string",
                        "description": "AST (SGOT) (IU/L)"
                    },
                    "ALT": {
                        "type": "string",
                        "description": "ALT (SGPT) (IU/L)"
                    },
                    "감마지티피": {
                        "type": "string",
                        "description": "감마지티피 (γGTP) (IU/L)"
                    },
                    "간장질환": {
                        "type": "string",
                        "description": "정상/간기능 이상 의심 중 체크된 항목"
                    },
                    "요단백": {
                        "type": "string",
                        "description": "정상/경계/단백뇨 의심 중 체크된 항목"
                    },
                    "흉부촬영": {
                        "type": "string",
                        "description": "정상/비활동성 폐결핵/특정 질환 의심/기타 소견 중 체크된 항목"
                    },
                    "과거병력": {
                        "type": "string",
                        "description": "과거병력 (예: 없음)"
                    },
                    "약물치료병력": {
                        "type": "string",
                        "description": "약물치료병력 (예: 없음)"
                    }
                },
                "required": [
                "키",
                "몸무게",
                "체질량지수",
                "허리둘레",
                "혈압",
                "혈색소",
                "빈혈 소견",
                "공복혈당",
                "당뇨병 소견",
                "총콜레스테롤",
                "고밀도콜레스테롤",
                "중성지방",
                "저밀도콜레스테롤",
                "이상지질혈증 소견",
                "혈청크레아티닌",
                "eGFR",
                "신장질환 소견",
                "AST",
                "ALT",
                "감마지티피",
                "간장질환",
                "요단백",
                "흉부촬영",
                "과거병력",
                "약물치료병력"
                ]
            }
        }
    }
    
    # Define the API endpoint and headers
    # Create an API client
    extract_client = OpenAI(api_key=API_KEY, base_url="https://api.upstage.ai/v1/information-extraction")
    
    # Call the extraction API
    extraction_response = extract_client.chat.completions.create(
        model="information-extract",
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
        ]}],
        response_format=schema
    )
    
    # Parse the JSON result
    extracted_data = json.loads(extraction_response.choices[0].message.content)
    return extracted_data

# upstage request 오류 확인
def print_upstage_error(response):
    if 'error' in response.json().keys():
        return response.json()['error']

# 테스트 함수
def test_function(API_KEY, file_path):

    url = "https://api.upstage.ai/v1/document-digitization"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    files = {"document": open(file_path, "rb")}
    data = {"ocr": "force", "base64_encoding": "['table']", "model": "document-parse"}
    response = requests.post(url, headers=headers, files=files, data=data)

    # upstage 오류 확인
    upstage_error = print_upstage_error(response)
    if upstage_error:
        return upstage_error
    
    # 메인 기능
    contents_html = response.json()['content']['html']
    soup = BeautifulSoup(contents_html)
    text = soup.find(attrs = {'id': '20'}).text

    return text

# 개발용 예시 데이터 ------------------------------------------------------------------------------------------------------------------

API_KEY = "" # 테스트용 API 키
file_path = "./data/test_image.jpg" # 테스트용 파일 경로