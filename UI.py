import streamlit as st
import streamlit.components.v1 as components
from streamlit_pdf_viewer import pdf_viewer
from streamlit_geolocation import streamlit_geolocation
from main import test_function
import os
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image



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
    st.session_state.summary_text = ""




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
	text = test_function(st.session_state.API_KEY, file_path) 
	
	# 세션 상태에 결과 저장
	st.session_state.summary_text = text
	st.session_state.has_result = True
	st.session_state.viewer_visible = False # 파일 뷰어 끄기

# 파일 저장 함수
def save_file(uploaded_file):
	if not os.path.exists('uploaded_files'):
		os.makedirs('uploaded_files')

	current_time = datetime.now()
	current_time = current_time.isoformat().replace(":", "").replace("-", "").replace(".", "")	
	temp = uploaded_file.name.split('.')
	file_name = temp[0]
	file_extension = temp[-1]
	file_name = "".join([file_name, '_', str(current_time), '.', file_extension])
	file_path = os.path.join('uploaded_files', file_name)
	with open(file_path, 'wb') as f:
		f.write(uploaded_file.getbuffer())

	return file_path

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
    page_title="제목 추천받아요",
)

# 사이드바 
with st.sidebar:

	def on_submit(): # API key submit 버튼 클릭 시
		st.session_state.API_KEY = st.session_state.temp_key # api key
		# api key 마스킹
		temp_chars = list(st.session_state.API_KEY)
		for i in range(len(temp_chars[4:-1])):
			temp_chars[i+4] = "*"
		st.session_state.masked_API_KEY = "".join(temp_chars)

		st.session_state.temp_key = ""
	
	# API key 입력 form
	with st.form("api_key_form", clear_on_submit=False):
		intput_API_KEY = st.text_input(
			label = f"Upstage API Key: {st.session_state.masked_API_KEY}",
			placeholder = "Upstage API Key를 입력하세요",
			key = "temp_key",
		)

		btn_api_key_submit = st.form_submit_button("Submit", on_click=on_submit)


st.title("뭐라고 적을까요")
st.subheader('뭐라고 적을까요 2')
st.markdown('뭐라고 적을까요 3')


# 파일 업로드 칸
container_file = st.container()
with container_file:
	uploaded_file = st.file_uploader("파일을 선택하세요", type=['pdf', 'png', 'jpeg'])

	# 실행 버튼
	btn_run = st.button("시작", on_click=initial_run)
	
	# 파일 업로드 시 파일 첫 페이지 표시
	if uploaded_file: 
		if uploaded_file != st.session_state.last_uploaded_file: # 상태 변경
			st.session_state.viewer_visible = True
			st.session_state.last_uploaded_file = uploaded_file
			st.session_state.has_result = False

		if st.session_state.viewer_visible: 
			if uploaded_file.type == "application/pdf": # pdf 파일일 경우
				temp = uploaded_file.getvalue()
				viewer = pdf_viewer(input=temp, pages_to_render=[1])
			else: # 이미지 파일일 경우
				image = Image.open(uploaded_file)
				viewer = st.image(image, use_container_width=True)

# 결과 표시 칸
container_result = st.container()

if 'has_result' in st.session_state and st.session_state.has_result:
	# 결과 표시
	with container_result:
		# 요약 결과
		st.subheader("요약 결과")
		st.markdown(st.session_state.summary_text) 

		# 병원 추천
		st.subheader("추천 병원") # 추천 병원
		place_name1 = "신촌연세병원"
		place_name2 = "신촌세브란스"

		st.button(place_name1, on_click=show_map, args=(place_name1,))
		st.markdown(f"""
		**주소:** "서울특별시 마포구 서강로 110, 지2층~6층 (신수동)"  
		**전화번호:** "02-337-7582"  
		**홈페이지:** "http://www.scys.co.kr"
		""")

		st.button(place_name2, on_click=show_map, args=(place_name2,))
		st.markdown(f"""
		**주소:** "서울특별시 서대문구 연세로 50-1, (신촌동)"  
		**전화번호:** "02-2228-0114"  
		**홈페이지:** "http://www.yuhs.or.kr"
		""")

# 지도 표시 칸
container_map = st.container()





# st.title("GPS 기능을 사용하여 나의 현 위치 확인")

# # 사용자 위치 가져오기
# location = streamlit_geolocation()

# # 위치 정보 출력
# if location:
#     st.write(f"위도: {location['latitude']}")
#     st.write(f"경도: {location['longitude']}")
#     st.write(f"정확도: {location['accuracy']}m")
# else:
#     st.write("위치를 가져오는 중입니다. 버튼을 눌러 승인하세요.")



########## CSS ###########
# style = """
# <style>
#     button {
#         background: none!important;
#         border: none;
#         padding: 0!important;
#         color: black !important;
#         text-decoration: none;
#         cursor: pointer;
#         border: none !important;
#     }
#     button:hover {
#         text-decoration: none;
#         color: black !important;
#     }
#     button:focus {
#         outline: none !important;
#         box-shadow: none !important;
#         color: black !important;
#     }
# </style>
# """
# st.markdown(style, unsafe_allow_html=True)