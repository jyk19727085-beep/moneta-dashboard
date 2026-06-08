import streamlit as st
import base64
import requests
import datetime
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

def get_gmail_service_from_dict(token_info):
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = Credentials.from_authorized_user_info(token_info, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            st.error("⚠️ 클라우드 연동 토큰이 만료되었습니다. 로컬에서 토큰을 재발급받아야 합니다.")
            st.stop()
    return build('gmail', 'v1', credentials=creds)

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
    
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    try:
        models_data = requests.get(list_url).json()
        available_models = [m['name'] for m in models_data.get('models', []) 
                            if 'generateContent' in m.get('supportedGenerationMethods', [])]
        if not available_models:
            return "⚠️ 모델 스캔 실패. 클라우드 Secrets API Key 확인 필요."
        target_model = available_models[0]
    except Exception as e:
        return f"⚠️ 구글 클라우드 라우팅 실패: {e}"

    url = f"https://generativelanguage.googleapis.com/v1beta/{target_model}:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
    당신은 Daniel 주인님을 보필하는 수석 프로비서 '모네타'입니다.
    하달된 [🛠 고도화된 브리핑 원칙]에 의거하여 주관적 억측은 0%로 차단하고 오직 정량적 수치와 인과관계로만 분석서 작성을 보고하십시오.
    
    [원시 데이터 수신본]
    {raw_text[:4000]}
    
    아래의 [📅 브리핑 예시] 포맷을 단 하나의 자구 오차도 없이 출력하십시오. 포맷 외의 불필요한 인사말이나 코드 블록 기호는 절대 금지합니다.
    
    [데이터 브리핑: {today_date}]
    - 핵심 지표: (원시 데이터 내 핵심 수치 %, $ 추출 및 요약)
    - 데이터 분석: (지표들 간의 상관관계 및 통계적/과거 패턴 인과관계 매칭)
    - 연관 기사: (현재 글로벌 시장 상황과 대조하여 신뢰도 평가 요약)
    - 냉철한 시사점 (Weight 90%+): (낙관/비관론을 배제한, 자산 비중 및 리스크 관리 관점의 객관적 단기 시나리오)
    """
    
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, json=data)
        resp_json = response.json()
        if 'candidates' in resp_json:
            return resp_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return "🔄 신규 시장 데이터 분석 대기 중..."
    except Exception as e:
        return f"⚠️ 모네타 코어 통신 장애: {e}"

st.set_page_config(layout="wide")
st.title("📊 모네타 클라우드 초정밀 AI 분석 대시보드 (24/7 무인 관측 모드)")
st.write("---")

try:
    accounts = {
        "DANIEL J (주계정)": json.loads(st.secrets["TOKEN_JYK"]),
        "GMASTER (부계정)": json.loads(st.secrets["TOKEN_GMASTER"])
    }
except Exception as e:
    st.error(f"⚠️ 클라우드 시스템 보안 금고 해독 실패: {e}")
    st.stop()

for name, token_info in accounts.items():
    st.header(f"📬 {name} 분석 센터")
    try:
        service = get_gmail_service_from_dict(token_info)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=2).execute()
        messages = results.get('messages', [])
        
        if not messages:
            st.info("새로 수집된 시장 데이터가 없습니다.")
        else:
            for msg in messages:
                msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '제목 없음')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '발신자 미상')
                
                with st.expander(f"📌 최신 데이터: {subject} (발신: {sender})"):
                    st.write("🔄 *모네타 AI가 구글 클라우드망을 통해 초정밀 교차 검증 중...*")
                    body_text = get_email_body(msg_data['payload'])
                    briefing_result = analyze_with_moneta(body_text)
                    st.markdown(briefing_result)
                    
    except Exception as e:
        st.error(f"⚠️ {name} 통신 링크 해제 상태: 클라우드 금고 세팅을 완료해 주십시오.")

st.write("---")
st.success("🎯 글로벌 시장 온디맨드(On-Demand) 초정밀 관측 시스템 정상 가동 중.")