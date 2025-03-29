import streamlit as st
from operator import itemgetter
from main import test_function
import os
from datetime import datetime

# 웹 탭 꾸미기
st.set_page_config(
    page_title="제목 추천받아요",
)


# UI 구현
st.title("뭐라고 적을까요")
st.subheader('뭐라고 적을까요 2')
st.markdown('뭐라고 적을까요 3')

# 파일 업로드
uploaded_file = st.file_uploader("파일을 선택하세요", type=['pdf', 'png', 'jpeg'])

if uploaded_file:
	# 파일 저장
	if not os.path.exists('uploaded_files'):
		os.makedirs('uploaded_files')

	current_time = datetime.now()
	current_time = current_time.isoformat().replace(":", "").replace("-", "").replace(".", "")
	print(current_time)
	temp = uploaded_file.name.split('.')
	file_name = temp[0]
	file_extension = temp[-1]
	file_name = "".join([file_name, '_', str(current_time), '.', file_extension])
	file_path = os.path.join('uploaded_files', file_name)
	with open(file_path, 'wb') as f:
		f.write(uploaded_file.getbuffer())
    
	# API 호출
	text = test_function(file_path)
	st.markdown(text)
