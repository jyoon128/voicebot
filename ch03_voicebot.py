import streamlit as st
from audiorecorder import audiorecorder
# from streamlit_webrtc import webrtc_streamer

import openai
import os
from datetime import datetime
from gtts import gTTS
import base64

def STT(audio, apikey):
    filename='input.wav'
    audio.export(filename, format="wav")
    
    
    audio_file = open(filename,"rb")
    client = openai.OpenAI(api_key = apikey)
    respons = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    audio_file.close()
    
    os.remove(filename)
    return respons.text

def ask_gpt(prompt, model, apikey):
    client = openai.OpenAI(api_key=apikey)
    response=client.chat.completions.create(
        model=model,
        messages=prompt)
    gptResponse = response.choices[0].message.content
    return gptResponse

def TTS(response):
    #gTTS를 활용하여 음성파일 생성
    filename="output.mp3"
    tts=gTTS(text=response,lang="ko")
    tts.save(filename)
    
    #음원 파일 자동 재생
    with open(filename, "rb") as f:
        data = f.read()
        b64=base64.b64encode(data).decode()
        md = F"""
            <audio autoplay="True">
            <source src="data:audio/mp3;base64, {b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True,)
    #파일삭제
    os.remove(filename)

def main():
    # 기본 설정
    st.set_page_config(
        page_title="동민이의 음성 비서 프로그램",
        layout="wide"
    )

    # 제목
    st.header("음성 비서: 똑똑이 made by 김재윤")
    st.markdown("---")

    # 기본 설명
    with st.expander("똑똑이에 관하여", expanded=True):
        st.write("""
        - UI는 Streamlit을 사용했습니다.
        - STT(Speech-To-Text)는 OpenAI Whisper AI를 사용했습니다.
        - 답변은 OpenAI의 GPT 모델로 생성됩니다.
        - TTS(Text-To-Speech)는 Google Translate TTS를 사용했습니다.
        """)

    # Session state 초기화
    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if "OPEN_API" not in st.session_state:
        st.session_state["OPENAI_API"] = ""

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{
            "role": "system",
            "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in Korean."
        }]

    if "check_reset" not in st.session_state:
        st.session_state["check_reset"] = False

    # 사이드바
    with st.sidebar:
        st.session_state["OPENAI_API"] = st.text_input(
            label="OPEN API 키",
            placeholder="Enter Your API Key",
            value="",
            type="password"
        )

        st.markdown("---")
        model = st.radio(label="GPT 모델", options=["gpt-4", "gpt-3.5-turbo"])

        st.markdown("---")
        if st.button(label="초기화"):
            st.session_state["chat"] = []
            st.session_state["messages"] = [{
                "role": "system",
                "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in Korean."
            }]
            st.session_state["check_reset"] = True

    # 기능 구현 공간
    col1, col2 = st.columns(2)

    with col1:
        # 왼쪽 영역 작성 
        st. subheader("질문하기") 
        # 음성 녹음 01이콘 추가 
        audio = audiorecorder("클릭하여 녹음하기", "녹음 중...")
        if (audio.duration_seconds > 0) and (st.session_state["check_reset"] == False):
        # 북음을 실행하연? 
        # 음성 재생 
            st.audio(audio.export().read())
            question=STT(audio, st.session_state["OPENAI_API"])
            
            now=datetime.now().strftime("%H:%M")
            st.session_state["chat"]=st.session_state["chat"]+[("user",now,question)]
            
            st.session_state["messages"]=st.session_state["messages"]+[{"role":"user","content":question}]

    with col2:
        st.subheader("질문/답변")
        if (audio.duration_seconds > 0) and (st.session_state["check_reset"]==False):
            #gpt에게 답변 얻기
            response=ask_gpt(st.session_state["messages"],model,st.session_state["OPENAI_API"])
            
            st.session_state["messages"]=st.session_state["messages"]+[{"role":"system","content":response}]
            
            now=datetime.now().strftime("%H:%M")
            st.session_state["chat"]=st.session_state["chat"]+[("bot",now,response)]
            #채팅 형식으로 시각화하기
            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(f"""
                    <div style="display:flex;align-items:center;">
                    <div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">
                    {message}
                    </div>
                    <div style="font-size:0.8rem;color:gray;">{time}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")  # 줄 바꿈

                elif sender == "bot":
                    st.write(f"""
                    <div style="display:flex;align-items:center;justify-content:flex-end;">
                    <div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">
                    {message}
                    </div>
                    <div style="font-size:0.8rem;color:gray;">{time}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")  # 줄 바꿈

            
if __name__ == "__main__":
    main()
