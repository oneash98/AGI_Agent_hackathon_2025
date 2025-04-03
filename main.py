import json
import requests
from bs4 import BeautifulSoup
from langchain_upstage import ChatUpstage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import base64, json
from openai import OpenAI
from scipy.spatial import KDTree
import numpy as np

def encode_image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def return_json(API_KEY, file_path, result_queue):
    schema_client = OpenAI(api_key=API_KEY, base_url="https://api.upstage.ai/v1/information-extraction/schema-generation")
    # Encode the image
    encoded_image = encode_image_to_base64(file_path)
    
    schema_response = schema_client.chat.completions.create(
        model="information-extract",
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
        ]}],
    )
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
    
    # --- Step 2: Extract Information ---
    extract_client = OpenAI(api_key=API_KEY, base_url="https://api.upstage.ai/v1/information-extraction")
    extraction_response = extract_client.chat.completions.create(
        model="information-extract",
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
        ]}],
        response_format=schema  # Use the auto-generated schema
    )

    # --- Step 3: Print or process the result ---
    extracted_data = json.loads(extraction_response.choices[0].message.content)
    result_queue.put(("health_info", extracted_data))
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


def return_summary_for_test():

    temp = "요약"

    return temp


def return_simple_explanation(API_KEY, health_info, result_queue):
    # Step 1 Define the conversation for Solar LLM using the provided prompt for an easy summary
    messages = [
        {
            "role": "system",
            "content": (
                """You are MAGIC, a Korean, warm and friendly AI health coach.
                Your job is to gently explain a patient's health check-up results using friendly language.
                Focus only on what needs attention. Never use complex medical terms or diagnosis names.
                Explain in everyday language that is emotionally supportive and easy to understand.
                Use emojis to make the explanation more friendly and engaging.

                Input:

                Doctor's health check-up summary (written in Korean)
                Patient nickname (e.g., 슬기로운고양이)
                Age group (e.g., 30대), Gender (e.g., 여성)
                Output Format:
                {
                    👋 Greeting & Empathy (1 short paragraph)
                    Greet the patient using their nickname. Briefly mention you’ve read their results and will explain gently.

                    📌 Health Summary (2–3 sentences max)
                    Summarize the main areas that need attention. Keep it short and focused.

                    🔍 Detailed Explanation (up to 3 areas)
                    For each issue:

                    What was found (in natural words)
                    Why it matters (soft explanation)
                    How to help the body (adjust food, exercise, or habits)
                    Use lifestyle examples that are appropriate to age/gender.
                    ✅ Lifestyle Tips (2–3 total)
                    MUST Consider patient's age and sex
                    Offer kind and simple suggestions on food, movement, or daily routines.

                    Examples should suit the patient’s profile (age and sex):
                    Young woman → 떡볶이, 마라탕, 홈트
                    Older woman → 반찬, 산책, 요가
                    Young man → 치킨, 라면, 헬스
                    Older man → 등산, 유산소 운동
                    💬 Friendly Encouragement
                    End with comforting words to support the patient and encourage action.
                }
                """
            )
        },
        {
            "role": "user",
            "content": (
                #f"Patient's nickname: {health_info['별명']}\n   "
                #f"Patient's age group: {health_info['나이']}\n"
                #f"Patient's gender: {health_info['성별']}\n"
                f"Health check-up result: {json.dumps(health_info, ensure_ascii=False)}\n"
                #f"Brief summary of the health check-up result: {summary_professional}\n"

                "Please provide an easy-to-understand summary focusing on key aspects that need attention."
            )
        }
    ]
    
    try:
        # Step 2: Call the Solar LLM using the Upstage API client
        client = OpenAI(api_key=API_KEY, base_url="https://api.upstage.ai/v1")
        response = client.chat.completions.create(
            model="solar-pro",
            messages=messages
        )
        
        # Step 3: Extract the summary text from the response
        summary_text = response.choices[0].message.content
        result_queue.put(("simple_explanation", summary_text))
        return summary_text
    
    except Exception as e:
        # Return a fallback message if the API call fails
        print(f"Error in return_summary: {str(e)}")
        error_message = "죄송합니다. 요약 정보를 가져오는 중 오류가 발생했습니다. 다시 시도해주세요."
        result_queue.put(("explanation_error", error_message))
        return error_message


# 진료과 추천 함수 (추천 사유와 추천 진료과 반환)
def suggest_specialty(API_KEY, health_info, summary, result_queue):
    llm = ChatUpstage(api_key=API_KEY, model="solar-pro")
    
    prompt_template = """
    당신은 의료 인공지능 챗봇 MAGIC입니다. 
    환자의 <건강검진 결과>와 <요약 정보>를 분석해, 다음 진료과 중 가장 적절한 곳을 1곳 추천하거나, 추천하지 않음:
    
    - 가정의학과
    - 내과
    - 혈액내과
    - 소화기내과
    - 내분비내과
    - 심장내과
    - 신장내과
    - 해당없음
    
    추천 기준
    * 해당없음: 모든 것이 정상인 경우 추천한다.
    * 가정의학과: 체중 증가, 경미하거나 경계성 위험 소견, 단일 건강문제가 의심될 때, 다양한 질환이 있으나 복합적이지 않은 경우
    * 내과: 
    	- 혈액내과: 혈색소 수치가 낮거나 높은 경우 (빈혈 또는 적혈구 증가 등), 백혈구, 혈소판 수치 이상, 기타 혈액 이상 소견이 있을 때
    	- 신장내과: 신장기능에 문제가 있는 경우 (GFR 낮음, 크레아닌 상승 등)
    	- 심장내과: 고혈압인 경우 우선, 또는 혈압에 문제가 있는 경우 (수축기 혈압 또는 이완기 혈압 높음, 수축기 혈압과 이완기 혈압 차이가 큼)
    	- 내분비내과: 혈당에 이상이 있는 경우, 혹은 이상지질혈증과 혈당에 경계성 의심소견이 있는 경우, 여러 내분비 질환이 복합적으로 존재하는 경우 (예: 당뇨 + 고지혈증 + 고혈압 등), 가정의학과에서 다루기 어려운 복잡도일 경우
    	- 소화기내과: 간기능에 문제가 있는 경우 (ALT, AST, 지티피 상승 등)
    	- 내과: 질환의 의심되지만, 앞선 질환들이 아닌 경우.
    
    추가 지침
    간결하고 명확한 요약과 함께 진료과를 추천할 것
    동일 환자에게 복합적으로 여러 질환이 발견되어도, 혹은 판단이 애매한 경우라도 위 기준을 토대로 가장 적합한 과를 반드시 하나만 추천할 것
    검진 결과가 모두 정상이라면 "추천_진료과"를 "해당없음"으로 출력할 것 
    예시 출력과 같이 JSON 형식으로 출력할 것
    
    예시: 체중 증가, 혈색소 수치 정상, 공복 혈당 약간 높음 (경계 수준)
    예시 출력:
    {{
    	"추천_사유": "체중 증가와 경계 수준의 혈당은 비교적 경미한 소견이며, 단일 문제 위주로 접근 가능하므로 가정의학과가 적합합니다.",
    	"추천_진료과": "가정의학과"
    }}
    
    <건강검진 결과>:
    {health_info}

    <요약 정보>:
    {summary}
    """
    final_prompt = PromptTemplate.from_template(prompt_template)
    output_parser = StrOutputParser()

    chain = final_prompt | llm | output_parser
    response = chain.invoke({"health_info": health_info, "summary": summary})

    temp = json.loads(response)
    reason = temp['추천_사유']
    specialty = temp['추천_진료과']
    
    result_queue.put(("reason", reason))
    result_queue.put(("specialty", specialty))
    return reason, specialty



# 가까운 병원 찾기
def get_nearest_clinics(clinics_info, longitude, latitude, specialty, k):
    if specialty in ('가정의학과', '내과'):
        df = clinics_info[clinics_info['진료과'] == specialty]
    else:
        df = clinics_info[clinics_info[specialty] == 1]
    
    coords = df[['좌표(X)', '좌표(Y)']].values
    tree = KDTree(coords)
    target = np.array([longitude, latitude])
    distance, indicies = tree.query(target, k=k)
    
    return df.iloc[indicies] # df 반환 -> UI 파일에서 화면에 표시
