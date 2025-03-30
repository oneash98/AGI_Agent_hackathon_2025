import streamlit as st
from main import test_function
import os
from datetime import datetime
from dotenv import load_dotenv


if 'API_KEY' not in st.session_state: # API key 담을 변수 설정
	if os.path.exists('.env'): 	# 로컬에서 테스트 실행 시 API KEY 가져오기 
		load_dotenv()
		st.session_state.API_KEY = os.getenv("API_KEY")
	else: # 스트림릿 웹에서 실행 시
		st.session_state.API_KEY = ""
	
if 'masked_API_KEY' not in st.session_state:
	st.session_state.masked_API_KEY = ""

# 웹 탭 꾸미기
st.set_page_config(
    page_title="제목 추천받아요",
)

# UI 구현
st.title("뭐라고 적을까요")
st.subheader('뭐라고 적을까요 2')
st.markdown('뭐라고 적을까요 3')

# API 키 설정
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


# 파일 업로드
uploaded_file = st.file_uploader("파일을 선택하세요", type=['pdf', 'png', 'jpeg'])

if uploaded_file:
	# 파일 저장
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
    
	# API 호출
	text = test_function(st.session_state.API_KEY, file_path)
	st.markdown(text)