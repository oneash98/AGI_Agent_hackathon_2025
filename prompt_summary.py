import json
import requests
from bs4 import BeautifulSoup
from langchain_upstage import ChatUpstage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import base64, json
from openai import OpenAI

# 기존 파일
import main

def return_json(API_KEY, file_path):
    # Instead of returning test data, use the real extraction function:
    return main.extract_information_from_image(API_KEY, file_path)

# 새로 정의한 함수------------------------------------------------------------------------------------------------

def return_normal_standard(age=None):  # age를 매개변수로 받음
    # 정상 범위 정의
    normal_ranges = {
        "키": (0, 300),  # cm
        "몸무게": (40, 150),  # kg
        "체질량지수": (18.5, 24.9),  # BMI
        "허리둘레": (60, 100),  # cm
        "혈압": lambda x: 90 <= int(x.split('/')[0]) <= 120 and 60 <= int(x.split('/')[1].split()[0]) <= 80,  # mmHg
        "혈색소": (7.4, 16.0),  # g/dL
        "공복혈당": (70, 100),  # mg/dL
        "총콜레스테롤": (120, 200),  # mg/dL
        "고밀도콜레스테롤": (40, 60),  # mg/dL
        "중성지방": (40, 150),  # mg/dL
        "저밀도콜레스테롤": (0, 130),  # mg/dL
        "혈청크레아티닌": (0.6, 1.2),  # mg/dL
        "AST": (0, 40),  # IU/L
        "ALT": (0, 40),  # IU/L
        "감마지티피": (8, 63),  # IU/L
        "eGFR": (60, 120) #50세 기준
    }

    # eGFR 정상 범위 계산 함수 (나이에 따라 동적 설정)
    def calculate_egfr_range(age):
        if age < 40:
            return (90, 120)  # 젊은 성인
        elif 40 <= age <= 65:
            return (60, 120)  # 중년
        else:
            return (45, 120)  # 고령자

    # age가 제공된 경우 eGFR 범위를 동적으로 추가
    if age is not None:
        normal_ranges["eGFR"] = calculate_egfr_range(age)

    return normal_ranges

def return_summary_format(): #테스트용 함수

    format = """
👋 안녕하세요, 검사 결과를 살펴봤어요. 먼저 간단하게 건강검사 결과를 요약해드릴게요.

✅ 잘 관리가 되고 있는 항목: 

📌 관리가 필요한 항목:

"""
    return format

def return_summary(API_KEY, file_path, age=None):
    # Step 1: Extract health information from the image
    health_info = return_json(API_KEY, file_path)

    # Step 2: Define the conversation for Solar LLM using the provided prompt for an easy summary
    msg = [
        {
            "role": "system",
            "content": (
                "You are Dr. 소라, a warm and friendly AI health coach.\n"
                "Your job is to gently explain a patient's health check-up results using soft and clear language.\n"
                "Focus only on what needs attention. Never use complex medical terms or diagnosis names.\n"
                "Explain in everyday language that is emotionally supportive and easy to understand.\n"
                f"Please check following standards that determines whether check-up results are normal or not: {return_normal_standard()}\n"
            )
        },
        {
            "role": "user",
            "content": (
                f"Here is the health check-up result: {json.dumps(health_info, ensure_ascii=False)}\n"
                "Please provide an easy-to-understand summary focusing on key aspects that need attention by using Korean.\n"
                f"Please provide a summary in the following format: {return_summary_format()}\n"
            )
        }
    ]
    
    # Step 3: Call the Solar LLM using the Upstage API client
    client = OpenAI(api_key=API_KEY, base_url="https://api.upstage.ai/v1")
    stream = client.chat.completions.create(
        model="solar-pro",
        messages=msg,
        stream=True
        )
    
    final_response = ""

    # Extract the summary text from the response
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            # print(chunk.choices[0].delta.content, end='')
            # Append the content to the final response
            final_response += chunk.choices[0].delta.content

    # summary_text = response.choices[0].message['content']
    return final_response

# return_summary(API_KEY, file_path, age=30)
