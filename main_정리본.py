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

# extract_information_from_image(API_KEY, file_path)

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

# 2. 검사 결과 요약을 위한 함수 ----------------------------------------------------------------------------------------------------------------

def return_json_for_test(): # 테스트용 함수

    return test_data

def return_json(API_KEY, file_path):
    # Instead of returning test data, use the real extraction function:
    return extract_information_from_image(API_KEY, file_path)

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

def return_summary(API_KEY, health_info):
    # Step 1: Define the conversation for Solar LLM using the provided prompt for an easy summary
    messages = [
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
    
    # Step 2: Call the Solar LLM using the Upstage API client
    client = OpenAI(api_key=API_KEY, base_url="https://api.upstage.ai/v1")
    response = client.chat.completions.create(
        model="solar-pro",
        messages=messages
    )
    
    # Extract the summary text from the response
    summary_text = response.choices[0].message['content']
    return summary_text

# Example usage
API_KEY = "your_api_key"
file_path = "path_to_your_file"
health_info = extract_information_from_image(API_KEY, file_path)  # Call the function first
summary = return_summary(API_KEY, health_info)  # Pass the result as a parameter
print(summary)

# 3. 진료과 추천 ----------------------------------------------------------------------------------------------------------------

# 진료과 추천 함수 (임시)
def suggest_specialty(API_KEY, input_data):
    llm = ChatUpstage(api_key=API_KEY, model="solar-pro")
    
    prompt_template = """
당신은 의료 인공지능 챗봇 MAGIC입니다. 
환자의 건강검진 결과를 분석해, 다음 세 가지 진료과 중 가장 적절한 곳을 1곳 추천하거나, 추천하지 않음:

1. 가정의학과
2. 내과
3. 혈액내과
4. 해당없음

추천 기준
가정의학과: 체중 증가, 경미하거나 경계성 위험 소견, 단일 건강문제가 의심될 때, 다양한 질환이 있으나 복합적이지 않은 경우
내과: 고혈압, 당뇨 등 명확한 질병 진단이 있는 경우, 여러 질환이 복합적으로 존재하는 경우 (예: 고지혈증 + 고혈압 등), 가정의학과에서 다루기 어려운 복잡도일 경우

혈액내과: 혈색소 수치가 낮거나 높은 경우 (빈혈 또는 적혈구 증가 등), 백혈구, 혈소판 수치 이상, 기타 혈액 이상 소견이 있을 때

추가 지침
간결하고 명확한 요약과 함께 진료과를 추천할 것
동일 환자에게 복합적으로 여러 질환이 발견되어도, 혹은 판단이 애매한 경우라도 위 기준을 토대로 가장 적합한 과를 반드시 하나만 추천할 것
검진 결과가 모두 정상이라면 "추천_진료과"를 "해당없음"으로 출력할 것 
예시 출력과 같이 JSON 형식으로 출력할 것

예시: 체중 증가, 혈색소 수치 정상, 공복 혈당 약간 높음 (경계 수준)
예시 출력:
{
	"간략한_요약": "체중 증가와 경계 수준의 혈당은 비교적 경미한 소견이며, 단일 문제 위주로 접근 가능하므로 가정의학과가 적합합니다.",
	"추천_진료과": "가정의학과"
}
    """
    final_prompt = PromptTemplate.from_template(prompt_template)
    output_parser = StrOutputParser()

    chain = final_prompt | llm | output_parser
    response = chain.invoke({"input_data": input_data})
    
    return response

# 4. RAG 바탕 의료 comment----------------------------------------------------------------------------------------------------------------

class HealthRAGSystem:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.upstage.ai/v1"
        )
        self.health_status = None
        self.guidelines_db = []  # This would be your vector database of medical guidelines
        
    def load_health_status(self, health_status: Dict):
        """Load the patient's health status"""
        self.health_status = health_status

    def preprocess_query(self, query: str) -> str:
        """Optional query preprocessing"""
        # For now, just return the original query
        # You can add keyword extraction or other preprocessing here
        return query

    def get_embeddings(self, text: str) -> np.ndarray:
        """Get embeddings using Solar API"""
        response = self.client.embeddings.create(
            model="embedding-query",  # Use appropriate embedding model
            input=text
        )
        return np.array(response.data[0].embedding)

    def retrieve_relevant_snippets(self, query: str, top_k: int = 3) -> List[str]:
        """Retrieve relevant guideline snippets using vector similarity"""
        query_embedding = self.get_embeddings(query)
        
        # Calculate similarities with all guidelines
        similarities = []
        for guideline in self.guidelines_db:
            guideline_embedding = self.get_embeddings(guideline)
            similarity = np.dot(query_embedding, guideline_embedding)
            similarities.append((similarity, guideline))
        
        # Sort by similarity and get top k
        similarities.sort(reverse=True)
        return [snippet for _, snippet in similarities[:top_k]]

    def construct_prompt(self, query: str, relevant_snippets: List[str]) -> str:
        """Construct the prompt for the LLM"""
        prompt = f"""[사용자의 건강 검진 결과]를 염두에 두면서 [관련 의료 지침]을 바탕으로 [사용자 질문]에 대한 상세하고 이해하기 쉬운 설명을 제공해주세요. 지침의 범위를 벗어난 질문에는 답변하지 마세요. 
        #사용자의 건강 검진 결과:{json.dumps(self.health_status, indent=2, ensure_ascii=False)}

        #관련 의료 지침:
        """
        for i, snippet in enumerate(relevant_snippets, 1):
            prompt += f"{i}. {snippet}\n"

        prompt += f"\n#사용자 질문: {query}\n"
        
        return prompt

    def generate_response(self, query: str) -> str:
        """Generate final response using Solar LLM"""
        # Preprocess query
        processed_query = self.preprocess_query(query)
        
        # Retrieve relevant snippets
        relevant_snippets = self.retrieve_relevant_snippets(processed_query)
        
        # Construct prompt
        prompt = self.construct_prompt(processed_query, relevant_snippets)
        
        # Generate response using Solar
        response = self.client.chat.completions.create(
            model="solar-pro",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content