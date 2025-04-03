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

API_KEY = "up_dcseVnD61Oe3olPjywOM5inoFr0Hn" # 테스트용 API 키
file_path = "./data/test_image.jpg" # 테스트용 파일 경로

extract_result = extract_information_from_image(API_KEY, file_path)
print(extract_result)
# {'키': 184, '몸무게': 98.8, '체질량지수': 29.2, '허리둘레': 88.3, '혈압': '119/ 77 mmHg', '혈색소': '13.4', '빈혈 소견': '정상', '공복혈당': '122', '당뇨병 소견': '공복혈당장애 의심', '총콜레스테롤': '188', '고밀도콜레스테롤': '70', '중성지방': '80', '저밀도콜레스테롤': '111', '이상지질혈증 소견': '정상', '혈청크레아티닌': '0.8', 'eGFR': '84', '신장질환 소견': '정상', 'AST': '25', 'ALT': '21', '감마지티피': '12', '간장질환': '정상', '요단백': '정상', '흉부촬영': '정상', '과거병력': '무', '약물치료병력': '무'}


# info_classification 함수 -> 확인해보기!!

# 1. 정상 비정상 데이터 셋팅
def classify_health_data(data):
    # 정상 범위 정의
    normal_ranges = {
        "키": (140, 200),  # cm
        "몸무게": (40, 150),  # kg
        "체질량지수": (18.5, 24.9),  # BMI
        "허리둘레": (60, 100),  # cm
        "혈압": lambda x: 90 <= int(x.split('/')[0]) <= 120 and 60 <= int(x.split('/')[1].split()[0]) <= 80,  # mmHg
        "혈색소": (12.0, 16.0),  # g/dL
        "공복혈당": (70, 100),  # mg/dL
        "총콜레스테롤": (0, 200),  # mg/dL
        "고밀도콜레스테롤": (40, 60),  # mg/dL
        "중성지방": (0, 150),  # mg/dL
        "저밀도콜레스테롤": (0, 130),  # mg/dL
        "혈청크레아티닌": (0.6, 1.2),  # mg/dL
        "AST": (0, 40),  # IU/L
        "ALT": (0, 40),  # IU/L
        "감마지티피": (0, 50),  # IU/L
    }

    # eGFR 정상 범위 계산 함수 (나이에 따라 동적 설정)
    def calculate_egfr_range(age):
        if age < 40:
            return (90, 120)  # 젊은 성인
        elif 40 <= age <= 65:
            return (60, 120)  # 중년
        else:
            return (45, 120)  # 고령

    # 결과 저장용 딕셔너리
    normal = {}
    abnormal = {}

    # 데이터 분류
    for key, value in data.items():
        if key == "eGFR":
            # 나이에 따라 eGFR 정상 범위 계산
            age = int(data.get("나이", 50))  # 기본값 50세
            egfr_range = calculate_egfr_range(age)
            is_normal = egfr_range[0] <= float(value) <= egfr_range[1]
        elif key in normal_ranges:
            range_check = normal_ranges[key]
            if callable(range_check):  # 혈압처럼 함수로 정의된 경우
                is_normal = range_check(value)
            else:  # 범위로 정의된 경우
                is_normal = range_check[0] <= float(value) <= range_check[1]
        else:
            # 기타 소견은 그대로 분류
            if value == "정상":
                is_normal = True
            else:
                is_normal = False

        # 결과 저장
        if is_normal:
            normal[key] = value
        else:
            abnormal[key] = value

    return {"정상": normal, "비정상": abnormal}


# 테스트 데이터
data = {
    '키': 184,
    '몸무게': 98.8,
    '체질량지수': 29.2,
    '허리둘레': 88.3,
    '혈압': '119/ 77 mmHg',
    '혈색소': '13.4',
    '빈혈 소견': '정상',
    '공복혈당': '122',
    '당뇨병 소견': '공복혈당장애 의심',
    '총콜레스테롤': '188',
    '고밀도콜레스테롤': '70',
    '중성지방': '80',
    '저밀도콜레스테롤': '111',
    '이상지질혈증 소견': '정상',
    '혈청크레아티닌': '0.8',
    'eGFR': '84',
    '신장질환 소견': '정상',
    'AST': '25',
    'ALT': '21',
    '감마지티피': '12',
    '간장질환': '정상',
    '요단백': '정상',
    '흉부촬영': '정상',
    '과거병력': '무',
    '약물치료병력': '무',
    '나이': 50  # 추가된 나이 데이터
}

# 함수 실행
result = classify_health_data(data)
print("정상:", result["정상"])
print("비정상:", result["비정상"])