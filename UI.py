import streamlit as st
import streamlit.components.v1 as components
from streamlit_pdf_viewer import pdf_viewer
from streamlit_geolocation import streamlit_geolocation
from main import return_json_for_test, return_summary_for_test, suggest_specialty
import os
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image
import pandas as pd
import numpy as np
from scipy.spatial import KDTree

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 2rem;
    }
    
    /* Headers */
    .title-text {
        color: #1E88E5;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
    }
    
    .subtitle-text {
        color: #424242;
        font-size: 1.5rem !important;
        font-weight: 500 !important;
        margin-bottom: 1rem !important;
    }
    
    /* Cards */
    .stCard {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background-color: white;
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 8px;
        padding: 0.5rem 2rem;
        background-color: #1E88E5;
        color: white;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: #1565C0;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* File uploader */
    .uploadedFile {
        border: 2px dashed #1E88E5;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #F5F5F5;
    }
    
    /* Results container */
    .results-container {
        background-color: #FAFAFA;
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 2rem;
    }
    
    /* Hospital cards */
    .hospital-card {
        background-color: white;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Map container */
    .map-container {
        border-radius: 10px;
        overflow: hidden;
        margin-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

########## 세션 상태 초기화 ###########

# 업스테이지 api
if 'API_KEY' not in st.session_state: # API key 담을 변수 설정
	if os.path.exists('.env'): 	# 로컬에서 테스트 실행 시 API KEY 가져오기 
		load_dotenv()
		st.session_state.API_KEY = os.getenv("API_KEY")
	else: # 스트림릿 웹에서 실행 시
		st.session_state.API_KEY = ""

if 'masked_API_KEY' not in st.session_state:
	st.session_state.masked_API_KEY = ""

# 구글맵 api
if os.path.exists('.env'): 	# 로컬에서 테스트 실행 시 
	load_dotenv()
	GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
else: # 스트림릿 웹에서 실행 시
	GOOGLE_MAPS_API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
	

if 'viewer_visible' not in st.session_state: # 파일 뷰어 상태 설정
	st.session_state.viewer_visible = False

if 'last_uploaded_file' not in st.session_state:
	st.session_state.last_uploaded_file = None

if 'has_result' not in st.session_state: # 결과 상태 설정
    st.session_state.has_result = False
    st.session_state.summary = ""

if 'health_info' not in st.session_state: # 건강 정보 (JSON) 상태 설정
	st.session_state.health_info = None

if 'specialty' not in st.session_state: # 추천 진료과 상태 
	st.session_state.specialty = None

df_clinics = pd.read_pickle('data/clinics_info.pkl') # 병원 정보 데이터



########## functions ###########

# 건강검진 파일 업로드 후 실행 함수
def initial_run():
	if not uploaded_file: # 파일 없을 경우
		with container_file:
			st.markdown("파일을 업로드해주세요")
		return None

	# 실행
	file_path = save_file(uploaded_file) # 파일 저장 및 파일 경로 return
    
	# API 호출
	health_info = return_json_for_test() # 건강 정보 추출 (JSON)
	summary = return_summary_for_test() # 요약 정보
	specialty = suggest_specialty(st.session_state.API_KEY, health_info) # 진료과 추천
	
	# 세션 상태에 결과 저장
	st.session_state.health_info = health_info
	st.session_state.summary = summary
	st.session_state.has_result = True
	st.session_state.viewer_visible = False # 파일 뷰어 끄기
	st.session_state.specialty = specialty

# 파일 저장 함수
def save_file(uploaded_file):
	if not os.path.exists('uploaded_files'):
		os.makedirs('uploaded_files')

	# current_time = datetime.now()
	# current_time = current_time.isoformat().replace(":", "").replace("-", "").replace(".", "")	
	# temp = uploaded_file.name.split('.')
	# file_name = temp[0]
	# file_extension = temp[-1]
	# file_name = "".join([file_name, '_', str(current_time), '.', file_extension])
	file_name = uploaded_file.name
	file_path = os.path.join('uploaded_files', file_name)
	with open(file_path, 'wb') as f:
		f.write(uploaded_file.getbuffer())

	return file_path

# 병원 찾기 함수
def search_clinics(specialty, k=3):
	if user_location['latitude'] == None:
		with container_result:
			st.markdown('위치 정보가 필요합니다. 사이드바의 위치 정보 활용 버튼을 클릭해주세요.')

		return None
	
	# 위치 정보
	latitude = user_location['latitude']
	longitude = user_location['longitude']

	clinics = get_nearest_clinics(longitude, latitude, specialty, k) # 병원 정보
	with container_result: # 병원 정보 출력
		for i, row in clinics.iterrows():
			st.button(row['요양기관명'], on_click=show_map, args=({row['요양기관명']},)) # 병원 이름 클릭 시 지도 표시
			st.markdown(f"""
			**주소:** {row['주소']}  
			**전화번호:** {row['전화번호']}  
			**홈페이지:** {row['병원홈페이지']}
			""")

# 가까운 병원 찾기
def get_nearest_clinics(longitude, latitude, specialty, k):
	df = df_clinics[df_clinics['진료과'] == specialty]
	coords = df[['좌표(X)', '좌표(Y)']].values
	tree = KDTree(coords)

	target = np.array([longitude, latitude])
	distance, indicies = tree.query(target, k=k)

	return df.iloc[indicies]


# 지도 표시 함수
def show_map(place_name):
	map_url = f"""
	<iframe 
	    src="https://www.google.com/maps/embed/v1/place?key={GOOGLE_MAPS_API_KEY}&q={place_name}&language=ko" 
	    width="600" 
	    height="450" 
	    style="border:0;" 
	    allowfullscreen="" 
	    loading="lazy">
	</iframe>
	"""
	with container_map:
		components.html(map_url, height=500)



########## UI ###########

# 웹 탭 꾸미기
st.set_page_config(
    page_title="AI 건강검진 분석 도우미",
    page_icon="🏥",
    layout="wide"
)

# 사이드바 
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    
    def on_submit():
        st.session_state.API_KEY = st.session_state.temp_key
        temp_chars = list(st.session_state.API_KEY)
        for i in range(len(temp_chars[4:-1])):
            temp_chars[i+4] = "*"
        st.session_state.masked_API_KEY = "".join(temp_chars)
        st.session_state.temp_key = ""
    
    # API key 입력 form
    with st.form("api_key_form", clear_on_submit=False):
        st.markdown("#### 🔑 API Key 설정")
        intput_API_KEY = st.text_input(
            label = f"현재 API Key: {st.session_state.masked_API_KEY}",
            placeholder = "Upstage API Key를 입력하세요",
            key = "temp_key",
            type="password"
        )
        btn_api_key_submit = st.form_submit_button("저장", on_click=on_submit)

    st.markdown("---")
    st.markdown("#### 📍 위치 정보")
    st.markdown("근처 병원 찾기를 위해 위치 정보 제공이 필요합니다.")
    user_location = streamlit_geolocation()

# Main content
st.markdown('<h1 class="title-text">AI 건강검진 분석 도우미 🏥</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">건강검진 결과를 AI가 분석하여 맞춤형 정보를 제공해드립니다</p>', unsafe_allow_html=True)

# 파일 업로드 섹션
with st.container():
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("건강검진 결과 파일을 업로드해주세요 (PDF)", type=['pdf'])
    
    if uploaded_file:
        st.success("파일이 성공적으로 업로드되었습니다!")
        
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        btn_run = st.button("분석 시작 🔍", on_click=initial_run, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 결과 표시 섹션
if st.session_state.has_result:
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    
    # 요약 정보
    st.markdown("### 📋 검진 결과 요약")
    st.info(st.session_state.summary)
    
    # 추천 진료과
    if st.session_state.specialty:
        st.markdown("### 👨‍⚕️ 추천 진료과")
        st.success(f"추천 진료과: {st.session_state.specialty}")
        
        # 주변 병원 찾기
        st.markdown("### 🏥 주변 병원 찾기")
        if st.button("주변 병원 검색"):
            search_clinics(st.session_state.specialty)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 지도 표시 컨테이너
container_map = st.container()
with container_map:
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    # Map will be displayed here when a hospital is selected
    st.markdown('</div>', unsafe_allow_html=True)

# 파일 뷰어 컨테이너
container_file = st.container()
container_result = st.container()