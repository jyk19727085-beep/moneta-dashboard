import streamlit as st
import base64
import requests
import datetime
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def analyze_with_moneta(raw_text):
    prompt = f"""
    당신은 Daniel 주인님을 보필하는 수석 프로비서 '모네타'입니다.
    주관적 해석이나 모호한 전망을 철저히 배제하고, 수치(Data)와 논리적 인과관계(Logic)에 기반한 '초정밀 데이터 대시보드' 형태로 구성하십시오.

    [🛠 고도화된 브리핑 원칙 (가중치 90% 반영)]
    - 정량적 데이터 우선: 보고서 내 핵심 수치(%, $ 등)와 시장 지표(지수, 환율, 금리) 간의 상관관계를 최우선으로 분석합니다.
    - 교차 검증: 메일 보고서 내용과 실시간 경제 기사, 글로벌 시장 데이터를 대조하여 신뢰도를 평가합니다.
    - 냉철한 시사점: 시장의 낙관론이나 비관론에 휩쓸리지 않고, 통계적 유의성과 과거 패턴을 바탕으로 한 객관적 시나리오를 제시합니다.
    - 효율적 구조화: 정보의 노이즈를 최소화하고, 의사결정에 직결되는 핵심 변수(Key Variables) 위주로 요약합니다.

    아래 [📅 브리핑 예시] 포맷을 단 한 치의 오차도 없이 출력하십시오.

    [데이터 브리핑: {datetime.datetime.now().strftime('%Y-%m-%d')}]
    - 핵심 지표: 
    - 데이터 분석: 
    - 연관 기사: 
    - 냉철한 시사점 (Weight 90%+): 

    [분석할 원시 데이터]
    {raw_text[:4000]}
    """
    
    # 확실한 최신 모델명으로 변경 완료
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={st.secrets['GEMINI_API_KEY']}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        resp_data = response.json()
        
        if 'candidates' in resp_data and len(resp_data['candidates']) > 0:
            return resp_data['candidates'][0]['content']['parts'][0]['text']
        elif 'error' in resp_data:
            return f"🚨 [서버 에러 감지]: {resp_data['error'].get('message', '알 수 없는 에러')}"
        else:
            return f"🚨 [응답 구조 이상]: {resp_data}"
            
    except Exception as e:
        return f"🚨 [통신 장애 감지]: {e}"

st.set_page_config(layout="wide")
st.title("📊 모네타: 초정밀 데이터 통합 분석 허브")

if st.button("신규 데이터 정밀 분석 및 알림 발송"):
    try:
        token_info = json.loads(st.secrets["TOKEN_JYK"])
        service = build('gmail', 'v1', credentials=Credentials.from_authorized_user_info(token_info))
        msgs = service.users().messages().list(userId='me', maxResults=1).execute().get('messages', [])
        
        if msgs:
            msg_data = service.users().messages().get(userId='me', id=msgs[0]['id']).execute()
            payload = msg_data.get('payload', {})
            body = ""
            
            if 'parts' in payload:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain':
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', 'ignore')
                        break
                    elif part.get('mimeType') == 'text/html' and not body:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', 'ignore')
            elif 'body' in payload and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', 'ignore')
            
            if not body:
                body = "[시스템 알림: 텍스트를 추출할 수 없는 메일입니다.]"

            result = analyze_with_moneta(body)
            st.markdown(result)
        else:
            st.warning("⚠️ 수신된 메일이 없습니다.")
    except Exception as e:
        st.error(f"🚨 메일 연동 시스템 에러 발생: {e}")
