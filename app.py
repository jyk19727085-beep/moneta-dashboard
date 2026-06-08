import streamlit as st
import base64
import requests
import datetime
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# [절대 정의: 함수 호출 순서 고정]
def get_email_body(payload):
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
            elif part['mimeType'] == 'text/html':
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
    elif 'body' in payload and 'data' in payload['body']:
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    return ""

def analyze_with_moneta(raw_text):
    # 주인님의 절대 헌법 [🛠 고도화된 브리핑 원칙] 이식 완료
    prompt = f"""
    당신은 Daniel 주인님을 보필하는 수석 프로비서 '모네타'입니다.
    주관적 견해는 0%로 배제하고, 수치(Data)와 논리(Logic)로만 분석하십시오.
    
    [데이터 브리핑: {datetime.datetime.now().strftime('%Y-%m-%d')}]
    핵심 지표: (수치/지표/상관관계 분석)
    데이터 분석: (통계적 일치 확률 및 과거 패턴)
    연관 기사: (시장 동향 및 기관 반응)
    냉철한 시사점 (Weight 90%+): (리스크 관리 및 단기 시나리오)
    
    [데이터 소스]
    {raw_text[:4000]}
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={st.secrets['GEMINI_API_KEY']}"
    response = requests.post(url, headers={'Content-Type': 'application/json'}, 
                             json={"contents": [{"parts": [{"text": prompt}]}]})
    return response.json()['candidates'][0]['content']['parts'][0]['text']

# [메인 분석 허브]
st.title("📊 모네타: 초정밀 데이터 통합 분석 허브")
if st.button("신규 데이터 정밀 분석 및 알림 발송"):
    token_info = json.loads(st.secrets["TOKEN_JYK"])
    service = build('gmail', 'v1', credentials=Credentials.from_authorized_user_info(token_info))
    
    # 메일 리스트 확인
    msgs = service.users().messages().list(userId='me', maxResults=1).execute().get('messages', [])
    if msgs:
        msg_data = service.users().messages().get(userId='me', id=msgs[0]['id']).execute()
        # [구조 고정] 함수 선언 이후 호출
        body = get_email_body(msg_data['payload'])
        result = analyze_with_moneta(body)
        st.markdown(result)
