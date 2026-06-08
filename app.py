import streamlit as st
import base64
import requests
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# [초정밀 데이터 브리핑 허브]
def analyze_with_moneta(email_content):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={st.secrets['GEMINI_API_KEY']}"
    
    # 주인님의 절대 헌법을 프롬프트에 강제 삽입
    prompt = f"""
    당신은 Daniel 주인님을 보필하는 수석 프로비서 '모네타'입니다.
    수신된 메일 본문({email_content[:3000]})을 분석하십시오.
    
    [🛠 고도화된 브리핑 원칙]
    1. 수신된 메일의 핵심 지표를 추출하고, 외부 시장 뉴스/월스트리트 반응과 교차 검증하십시오.
    2. 데이터 간의 상관관계를 통계적으로 분석하십시오.
    3. 주관적 견해를 배제하고, [📅 브리핑 예시 포맷]대로만 출력하십시오.

    [📅 브리핑 예시 포맷]
    - 핵심 지표: ...
    - 데이터 분석: ...
    - 연관 기사(교차 검증): ...
    - 냉철한 시사점 (Weight 90%+): ...
    """
    
    response = requests.post(url, headers={'Content-Type': 'application/json'}, 
                             json={"contents": [{"parts": [{"text": prompt}]}]})
    return response.json()['candidates'][0]['content']['parts'][0]['text']

# [대시보드 메인 로직]
st.title("📊 모네타: 초정밀 데이터 통합 분석 허브")
if st.button("신규 데이터 정밀 분석 및 알림 발송"):
    token_info = json.loads(st.secrets["TOKEN_JYK"])
    service = build('gmail', 'v1', credentials=Credentials.from_authorized_user_info(token_info))
    
    # 1. 메일 가져오기
    msg = service.users().messages().list(userId='me', maxResults=1).execute()['messages'][0]
    msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
    body = get_email_body(msg_data['payload'])
    
    # 2. 통합 분석 실행
    result = analyze_with_moneta(body)
    st.markdown(result)
