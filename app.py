import streamlit as st
import base64
import requests
import datetime
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def analyze_with_moneta(raw_text):
    # 주인님의 [🛠 고도화된 브리핑 원칙] 강제 적용
    prompt = f"""
    당신은 Daniel 주인님을 보필하는 수석 프로비서 '모네타'입니다. 
    주관적 의견은 0%로 배제하고, 수치(Data)와 논리적 인과관계(Logic)만 분석하여 
    아래 [📅 브리핑 포맷]에 맞춰 정확히 작성하십시오. 
    다른 인사말은 일체 생략하십시오.

    [데이터 브리핑: {datetime.datetime.now().strftime('%Y-%m-%d')}]
    - 핵심 지표: 
    - 데이터 분석: 
    - 연관 기사: 
    - 냉철한 시사점 (Weight 90%+): 

    [분석할 원시 데이터]
    {raw_text[:4000]}
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={st.secrets['GEMINI_API_KEY']}"
    response = requests.post(url, headers={'Content-Type': 'application/json'}, 
                             json={"contents": [{"parts": [{"text": prompt}]}]})
    
    resp_data = response.json()
    if 'candidates' in resp_data and resp_data['candidates']:
        return resp_data['candidates'][0]['content']['parts'][0]['text']
    return "🔄 분석 처리 중... (서버 포맷 재검증)"

st.title("📊 모네타: 초정밀 데이터 통합 분석 허브")

if st.button("신규 데이터 정밀 분석 및 알림 발송"):
    token_info = json.loads(st.secrets["TOKEN_JYK"])
    service = build('gmail', 'v1', credentials=Credentials.from_authorized_user_info(token_info))
    msgs = service.users().messages().list(userId='me', maxResults=1).execute().get('messages', [])
    
    if msgs:
        msg_data = service.users().messages().get(userId='me', id=msgs[0]['id']).execute()
        # 본문 추출 및 분석
        body = base64.urlsafe_b64decode(msg_data['payload']['body'].get('data', '')).decode('utf-8', 'ignore')
        result = analyze_with_moneta(body)
        st.markdown(result)
