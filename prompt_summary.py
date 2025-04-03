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


# 개발용 예시 데이터
test_data = """
{
"나이": 30대,
"별명": 건강한다람쥐,
"성별": 여성,
"키": 158,
"몸무게": 65.4,
"체질량지수": 26.2,
"허리둘레": 86.0,
"혈압": "135/88 mmHg",
"혈색소": "12.6",
"빈혈 소견": "정상",
"공복혈당": "108",
"당뇨병 소견": "공복혈당장애 의심",
"총콜레스테롤": "198",
"고밀도콜레스테롤": "55",
"중성지방": "140",
"저밀도콜레스테롤": "115",
"이상지질혈증 소견": "정상",
"혈청크레아티닌": "1.5",
"eGFR": "48",
"신장질환 소견": "만성 신장병 의심",
"AST": "55",
"ALT": "62",
"감마지티피": "85",
"간장질환": "지속적 간기능 이상",
"요단백": "양성(1+)",
"흉부촬영": "정상"
}
"""

def return_json_for_test(): # 테스트용 함수

    return test_data

def return_json(API_KEY, file_path):
    # Instead of returning test data, use the real extraction function:
    return main.extract_information_from_image(API_KEY, file_path)

def return_summary_for_test(): #테스트용 함수

    temp = """
👋 안녕하세요, 건강한다람쥐님! 검사 결과를 살펴봤어요. 걱정하지 마세요. 함께 차근차근 살펴보도록 해요.

📌 주요 사항: 혈당, 신장 기능, 간 기능

🔍 자세한 설명:

* 혈당: 공복 혈당이 높은 편이에요. 이는 혈당을 조절하는 데 주의가 필요함을 의미해요. 과일, 채소와 같은 건강한 탄수화물을 선택하고, 규칙적인 운동을 통해 혈당을 관리할 수 있어요.
(생략)

✅ 생활습관 팁:
(생략)

"""
    return temp

# return_summary_for_test()

def return_summary(API_KEY, file_path):
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
                "Explain in everyday language that is emotionally supportive and easy to understand."
            )
        },
        {
            "role": "user",
            "content": (
                f"Here is the health check-up result: {json.dumps(health_info, ensure_ascii=False)}\n"
                "Please provide an easy-to-understand summary focusing on key aspects that need attention."
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
            print(chunk.choices[0].delta.content, end='')
            # Append the content to the final response
            final_response += chunk.choices[0].delta.content

    # summary_text = response.choices[0].message['content']
    return final_response

return_summary(API_KEY, file_path)
