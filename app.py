import streamlit as st
import base64
import requests
import datetime
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

def send_notification_email(subject, body):
    """분석 완료 시 주인님의 Gmail로 즉시 알림을 발송하는 무인 통신 모듈"""
    try:
        # 주계정(JYK)을 알림 발송용으로 활용
        token_info = json.loads(st.secrets["TOKEN_JYK"])
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        service = build('gmail', 'v1', credentials=creds)
        
        message = {
            'raw': base64.urlsafe_b64encode(f"To: me\r\nSubject: {subject}\r\n\r\n{body}".encode()).decode()
        }
        service.users().messages().send(userId='me', body=message).execute()
    except Exception:
        pass # 알림 발송 실패 시에도 대시보드 구동에는 영향 없도록 설정

def analyze_with_moneta(raw_text):
    """주인님의 [🛠 고도화된 브리핑 원칙]을 강제 적용하는 초정밀 분석 엔진"""
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    당신은 Daniel 주인님을 보필하는 수석 프로비서 '모네타'입니다.
    주인님의 [🛠 고도화된 브리핑 원칙]에 의거하여, 아래 포맷을 한 치의 오차도 없이 출력하십시오.
    
    [원시 데이터]
    {raw_text[:4000]}
    
    [데이터 브리핑: {today_date}]
    - 핵심 지표: (보고서 내 핵심 수치 및 시장 지표 요약)
    - 데이터 분석: (지표들 간 상관관계 및 과거 패턴 통계적 일치 확률)
    - 연관 기사: (글로벌 시장 상황 대조 및 기관 반응 요약)
    - 냉철한 시사점 (Weight 90%+): (리스크 관리 및 객관적 단기 시나리오)
    """
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception:
        return "🔄 분석 실패: 시스템 재가동 대기 중..."

st.set_page_config(layout="wide")
st.title("📊 모네타: 초정밀 데이터 브리핑 대시보드")

# [자동 분석 및 알림 트리거]
if st.button("신규 데이터 정밀 분석 및 알림 발송"):
    accounts = {"주계정": json.loads(st.secrets["TOKEN_JYK"])}
    for name, token_info in accounts.items():
        service = build('gmail', 'v1', credentials=Credentials.from_authorized_user_info(token_info))
        msg = service.users().messages().list(userId='me', maxResults=1).execute()['messages'][0]
        body = get_email_body(service.users().messages().get(userId='me', id=msg['id']).execute()['payload'])
        
        result = analyze_with_moneta(body)
        st.markdown(result)
        
        # 분석 완료 후 주인님께 자동 알림 발송
        send_notification_email("모네타: 신규 데이터 정밀 분석 완료", "오늘의 시장 데이터 분석이 완료되었습니다. 대시보드에서 냉철한 시사점을 확인하십시오.")
