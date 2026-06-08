import streamlit as st
import base64
import requests
import datetime
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# [가장 먼저 정의되어야 하는 함수]
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
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={st.secrets['GEMINI_API_KEY']}"
    
    prompt = f"""
    당신은 Daniel 주인님을 보필하는 수석 프로비서 '모네타'입니다.
    [🛠 고도화된 브리핑 원칙]에 따라 다음 포맷으로 분석하십시오.
    
    [데이터 브리핑: {today_date}]
    - 핵심 지표: (수치/지표 요약)
    - 데이터 분석: (상관관계 및 통계적 일치 확률)
    - 연관 기사: (시장 동향 및 기관 반응)
    - 냉철한 시사점 (Weight 90%+): (리스크 관리 및 단기 시나리오)
    
    [원시 데이터]
    {raw_text[:4000]}
    """
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"🔄 분석 중 오류 발생: {e}"

# [메인 실행부]
st.set_page_config(layout="wide")
st.title("📊 모네타: 초정밀 데이터 브리핑 대시보드")

if st.button("신규 데이터 정밀 분석 및 알림 발송"):
    token_info = json.loads(st.secrets["TOKEN_JYK"])
    service = build('gmail', 'v1', credentials=Credentials.from_authorized_user_info(token_info))
    msg = service.users().messages().list(userId='me', maxResults=1).execute()['messages'][0]
    msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
    
    # 여기서 get_email_body가 확실히 호출됩니다.
    body = get_email_body(msg_data['payload'])
    result = analyze_with_moneta(body)
    st.markdown(result)
