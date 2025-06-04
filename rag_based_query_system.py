from openai import OpenAI
import numpy as np
from typing import List, Dict
import json
import faiss
import pandas as pd

# RAG를 이용하여 질문에 대한 답변 생성하는 클래스
class HealthRAGSystem:
    def __init__(self, api_key: str, faiss_index_path: str, metadata_csv: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.upstage.ai/v1" # 업스테이지 Solar API
        )        
        
        self.health_status = None # 추후 환자 데이터 저장 변수
        # ─────────── 벡터 검색 세팅 ───────────
        # 미리 생성해 둔 FAISS 인덱스
        self.index = faiss.read_index(faiss_index_path)
        # 가이드라인 데이터
        self.guidelines_df = pd.read_csv(metadata_csv)

    # 환자 건강 상태 정보 로드
    def load_health_status(self, health_status: Dict):
        """Load the patient's health status"""
        self.health_status = health_status

    # def preprocess_query(self, query: str) -> str:
    #     """Optional query preprocessing"""
    #     # For now, just return the original query
    #     # You can add keyword extraction or other preprocessing here
    #     return query

    # 텍스트 임베딩
    def get_embeddings(self, text: str) -> np.ndarray:
        """Get embeddings using Solar API"""
        response = self.client.embeddings.create(
            model="embedding-query",  # 임베딩용 모델
            input=text
        )
        return np.array(response.data[0].embedding) # 넘파이 배열로 변환

    # 관련있는 의료 지침 retrieve
    def retrieve_relevant_snippets(self, query: str, top_k: int = 3) -> List[str]:
        # 질문 임베딩
        query_embedding = self.get_embeddings(query)
        # FAISS 검색을 위해 float32 2차원 배열
        query_embedding = np.array([query_embedding]).astype("float32")
        # top k 검색
        distances, indices = self.index.search(query_embedding, top_k)
        # 인덱스 -> 텍스트 변환
        relevant_snippets = []
        for idx in indices[0]:
            snippet = self.guidelines_df.iloc[idx]['chunk_text']
            relevant_snippets.append(snippet)
        
        return relevant_snippets

    # LLM 프롬프트 생성
    def construct_prompt(self, query: str, relevant_snippets: List[str]) -> str:
        """Construct the prompt for the LLM"""
        prompt = f"""[사용자의 건강 검진 결과]를 염두에 두면서 [관련 의료 지침]을 바탕으로 [사용자 질문]에 대한 상세하고 이해하기 쉬운 설명을 제공해주세요. 지침의 범위를 벗어난 질문에는 답변하지 마세요. 
        #사용자의 건강 검진 결과:{json.dumps(self.health_status, indent=2, ensure_ascii=False)}

        #관련 의료 지침:
        """
        for i, snippet in enumerate(relevant_snippets, 1): # 지침 나열
            prompt += f"{i}. {snippet}\n"

        prompt += f"\n#사용자 질문: {query}\n"
        
        return prompt

    # 최종 답변 생성
    def generate_response(self, query: str) -> str:
        """Generate final response using Solar LLM"""
        # 질문 전처리
        processed_query = self.preprocess_query(query)
        
        # 관련 지식 검색
        relevant_snippets = self.retrieve_relevant_snippets(processed_query)
        
        # 프롬프트 생성
        prompt = self.construct_prompt(processed_query, relevant_snippets)
        
        # LLM 답변 생성
        response = self.client.chat.completions.create(
            model="solar-pro",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content

# 실행 함수
def main(api_key: str, health_status: Dict, user_query: str):
    """
    Main function to run the HealthRAGSystem with provided parameters
    
    Args:
        api_key: API key for the OpenAI client
        health_status: Dictionary containing patient health data
        user_query: User's health-related question
    
    Returns:
        Response from the RAG system
    """
    # 시스템 초기화
    rag_system = HealthRAGSystem(
        api_key=api_key,
        faiss_index_path="data/every_faiss_index.bin",
        metadata_csv="data/RAG_every.csv"
    )
    
    # 건강 상태 로드
    rag_system.load_health_status(health_status)
    
    # 답변 생성
    response = rag_system.generate_response(user_query)
    print("Response:", response)
    return response

# if __name__ == "__main__":
#     # Example parameters (commented out - would be provided as actual parameters)
#     """
#     Example health_status:
#     {
#         "생년월일": "780203-3",
#         "검진일": "2025년 5월 5일",
#         "검진종합소견": "고혈압 및 당뇨병 전단계 소견",
#         "키": 175,
#         "몸무게": 86.2,
#         "체질량지수": 28.2,
#         "허리둘레": 92.0,
#         "혈압": "145/95 mmHg",
#         "혈색소": "14.2",
#         "빈혈 소견": "정상",
#         "공복혈당": "128",
#         "당뇨병 소견": "공복혈당장애 의심",
#         "총콜레스테롤": "220",
#         "고밀도콜레스테롤": "38",
#         "중성지방": "180",
#         "저밀도콜레스테롤": "148",
#         "이상지질혈증 소견": "이상지질혈증 의심",
#         "혈청크레아티닌": "1.1",
#         "eGFR": "79",
#         "신장질환 소견": "정상",
#         "AST": "35",
#         "ALT": "38",
#         "감마지티피": "60",
#         "간장질환": "경계성 간기능 이상",
#         "요단백": "미량",
#         "흉부촬영": "정상"
#     }
    
#     Example user_query: "고혈압에 좋은 음식이 따로 있나요?"
#     """
    
#     # Sample usage - uncomment and modify as needed
#     # health_data = {...}  # Replace with actual health data
#     # api_key = "your_api_key"
#     # question = "your health question"
#     # main(api_key, health_data, question) 