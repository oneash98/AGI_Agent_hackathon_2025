import base64, json
from openai import OpenAI

# --- Step 0: Setup ---
API_KEY = "up_GuigAOl5bgZmOGMDD3YzlJ5DRSk4Q"          # Your Upstage API key
IMAGE_PATH = "D:/STUDY/2025-1/AGI agent Hackerthon/김당고_당뇨전단계_일반건강검진 결과통보서(건강검진 실시기준)_페이지_2.jpg"  # Path to your medical record image

def encode_image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# --- Step 1: Generate Schema ---
schema_client = OpenAI(api_key=API_KEY, base_url="https://api.upstage.ai/v1/information-extraction/schema-generation")
encoded_image = encode_image_to_base64(IMAGE_PATH)

schema_response = schema_client.chat.completions.create(
    model="information-extract",
    messages=[{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
    ]}],
)

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
print(extracted_data)
