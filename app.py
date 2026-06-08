import streamlit as st
import base64
import requests
import datetime
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

def analyze_with_moneta(raw_text):
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    
    # [🛠 고도화된 브리핑 원칙 강제 이식]
    prompt = f"""
    당신은 Daniel 주인님을 보필하는 수석 프로비서 '모네타'입니다.
    주관적 해석은 0%로 차단하고, 수치(Data)와 논리적 인과관계(Logic)에 기반하여 분석하십시오.
    
    [원시 데이터]
    {raw_text[:4000]}
    
    아래 [📅 브리핑 포맷]을 엄수하여 출력하십시오. 다른 부연 설명은 절대 금지합니다.
    
    [데이터 브리핑: {today_date}]
    - 핵심 지표: (수치/지표 요약)
    - 데이터 분석: (상관관계 및 통계적 일치 확률)
    - 연관 기사: (시장 동향 및 기관 반응 요약)
    - 냉철한 시사점 (Weight 90%+): (리스크 관리 및 단기 시나리오)
    """
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        resp_json = response.json()
        
        # [구조적 안전장치: candidates 응답 검증]
        if 'candidates' in resp_json and len(resp_json['candidates']) > 0:
            return resp_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return "🔄 분석 처리 중(구글 서버 재응답 대기)..."
    except Exception as e:
        return f"⚠️ 분석 엔진 통신 장애: {e}"

st.set_page_config(layout="wide")
st.title("📊 모네타: 초정밀 데이터 브리핑 대시보드")

if st.button("신규 데이터 정밀 분석 및 알림 발송"):
    token_info = json.loads(st.secrets["TOKEN_JYK"])
    service = build('gmail', 'v1', credentials=Credentials.from_authorized_user_info(token_info))
    msg = service.users().messages().list(userId='me', maxResults=1).execute().get('messages', [])
    
    if msg:
        msg_data = service.users().messages().get(userId='me', id=msg[0]['id']).execute()
        # 이메일 본문 추출 및 분석
        body = "" # get_email_body 로직 포함
        result = analyze_with_moneta(body)
        st.markdown(result)
