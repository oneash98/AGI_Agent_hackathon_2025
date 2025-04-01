import requests
from bs4 import BeautifulSoup
from langchain_upstage import ChatUpstage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

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


def return_summary_for_test(): #테스트용 함수

    temp = """
👋 안녕하세요, 건강한다람쥐님! 검사 결과를 살펴봤어요. 걱정하지 마세요. 함께 차근차근 살펴보도록 해요.

📌 주요 사항: 혈당, 신장 기능, 간 기능

🔍 자세한 설명:

* 혈당: 공복 혈당이 높은 편이에요. 이는 혈당을 조절하는 데 주의가 필요함을 의미해요. 과일, 채소와 같은 건강한 탄수화물을 선택하고, 규칙적인 운동을 통해 혈당을 관리할 수 있어요.
* 신장 기능: 신장 기능이 다소 저하된 상태에요. 충분한 수분 섭취와 염분 섭취를 줄이는 것이 도움이 될 수 있어요. 또한, 정기적인 검진을 통해 신장 기능을 모니터링하는 것이 중요해요.
* 간 기능: 간 기능이 지속적으로 이상해요. 알코올 섭취를 제한하고, 건강한 식단을 유지하며, 정기적인 검진을 통해 간 기능을 모니터링하는 것이 중요해요.

✅ 생활습관 팁:

* 건강한 식단: 신선한 채소와 과일, 통곡물, 단백질이 풍부한 식품을 섭취하도록 노력하세요.
* 규칙적인 운동: 주당 150분 이상의 중등도 유산소 운동을 목표로 하세요.
* 정기적인 검진: 정기적인 검진을 통해 건강 상태를 모니터링하고, 필요한 경우 적절한 조치를 취할 수 있도록 하세요.

💬 안심하고 행동하세요! 지금부터 조금씩 생활습관을 개선하면, 더 건강해질 수 있어요. 함께 노력해봐요!
"""
    return temp

# 진료과 추천 함수 (임시)
def suggest_specialty(API_KEY, input_data):
    llm = ChatUpstage(api_key=API_KEY, model="solar-pro")
    
    prompt_template = """
    환자 정보를 보고, 내과, 외과 중 적절한 진료과를 하나만 추천해주세요. 단답형으로 출력하세요.
    
    {input_data}
    
    """
    final_prompt = PromptTemplate.from_template(prompt_template)
    output_parser = StrOutputParser()

    chain = final_prompt | llm | output_parser
    response = chain.invoke({"input_data": input_data})
    
    return response