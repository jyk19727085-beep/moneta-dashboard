import streamlit as st
import base64
import requests
import datetime
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_email_body(payload):
    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain':
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
    return ""

def analyze_with_moneta(raw_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={st.secrets['GEMINI_API_KEY']}"
    
    # [🛠 고도화된 브리핑 원칙 하드코딩]
    prompt = f"""
    당신은 Daniel 주인님을 보필하는 수석 프로비서 '모네타'입니다. 
    아래 [📅 브리핑 예시] 포맷을 단 한 치의 오차도 없이 출력하십시오. 
    주관적 의견은 0%로 소거하고 수치와 통계적 근거만 제시하십시오.

    [데이터 브리핑: {datetime.datetime.now().strftime('%Y-%m-%d')}]
    - 핵심 지표: 
    - 데이터 분석: 
    - 연관 기사: 
    - 냉철한 시사점 (Weight 90%+): 

    [분석 데이터]
    {raw_text[:4000]}
    """
    
    response = requests.post(url, headers={'Content-Type': 'application/json'}, 
                             json={"contents": [{"parts": [{"text": prompt}]}]})
    
    resp_data = response.json()
    # [안전장치: 'candidates' 응답 키 정밀 검증]
    if 'candidates' in resp_data and resp_data['candidates']:
        return resp_data['candidates'][0]['content']['parts'][0]['text']
    else:
        return "🔄 시스템 통신 원활하지 않음. 데이터 포맷 확인 중."

st.title("📊 모네타: 초정밀 데이터 통합 분석 허브")

if st.button("신규 데이터 정밀 분석 및 알림 발송"):
    token_info = json.loads(st.secrets["TOKEN_JYK"])
    service = build('gmail', 'v1', credentials=Credentials.from_authorized_user_info(token_info))
    msgs = service.users().messages().list(userId='me', maxResults=1).execute().get('messages', [])
    
    if msgs:
        msg_data = service.users().messages().get(userId='me', id=msgs[0]['id']).execute()
        body = get_email_body(msg_data.get('payload', {}))
        result = analyze_with_moneta(body)
        st.markdown(result)
