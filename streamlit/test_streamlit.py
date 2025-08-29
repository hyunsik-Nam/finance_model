import streamlit as st
import requests
import json
import time
import os

backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")

st.title("Hello  🚀")
st.write("간단한 챗봇입니다")


# 채팅 기록을 세션 상태에 저장
if "messages" not in st.session_state:
    st.session_state.messages = []

# 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # API 호출로 봇 응답 받기
    with st.chat_message("assistant"):
        # Streamlit의 내장 spinner 사용
        with st.spinner("work ..."):
            try:
                response = requests.post(f"{backend_url}/api/v1/test/chat", 
                               params={"msg": prompt}, 
                               stream=True)

                if response.status_code == 200:
                    full_response = ""
                    message_placeholder = st.empty()
                    
                    # 스트림 데이터를 실시간으로 받아서 표시
                    for line in response.iter_lines(decode_unicode=True):
                        if line:
                            if line.startswith('data: '):
                                json_str = line[6:]  # 'data: ' 제거
                                
                                # 스트림 종료 신호 확인
                                if json_str.strip() == '[DONE]':
                                    break
                                    
                                try:
                                    data = json.loads(json_str)
                                    # 에러 처리
                                    if "error" in data:
                                        full_response = f"에러: {data['error']}"
                                        break
                                    
                                    content = data.get("content", "")
                                    print(content)
                                    full_response += content
                                    message_placeholder.markdown(full_response + "▌")
                                    time.sleep(0.01)  # 약간의 지연 추가
                                except json.JSONDecodeError:
                                    continue
                    
                    # 최종 응답에서 커서 제거
                    message_placeholder.markdown(full_response)
                    bot_response = full_response
                else:
                    st.error(f"API 오류: {response.status_code}")
                    bot_response = f"API 오류: {response.status_code}"
            except Exception as e:
                st.error(f"API 호출 실패: {str(e)}")
                bot_response = f"API 호출 실패: {str(e)}"
        
        st.session_state.messages.append({"role": "assistant", "content": bot_response})
