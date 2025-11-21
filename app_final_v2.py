import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import base64
import json
import plotly.graph_objects as go
from googleapiclient.discovery import build
import numpy as np
import time
import math
import os
from PIL import Image
import io
import streamlit as st

# --- 0. API KEY 설정 ---
DEFAULT_OPENAI_KEY = st.secrets.get("OPENAI_API_KEY", "")
DEFAULT_YOUTUBE_KEY = st.secrets.get("YOUTUBE_API_KEY", "")

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="YouTube Diet | 알고리즘 처방전",
    layout="wide",
    page_icon="source/favicon.ico" if os.path.exists("source/favicon.ico") else "🥗",
    initial_sidebar_state="expanded"
)

# --- 2. 통합 디자인 시스템 (CSS) ---
st.markdown("""
<style>
    /* =============================================
       0. GLOBAL RESET & THEME (SUBTLE WHITE)
       ============================================= */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800;900&display=swap');
    
    div[data-testid="stTextInput"] label:contains('OpenAI API Key'),
    div[data-testid="stTextInput"] label:contains('YouTube API Key') {
        display: none !important;
    }
    div[data-testid="stTextInput"] input[type="password"] {
        display: none !important;
    }
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(
            135deg,
            #EDEAFF 0%,
            #DDE4FF 40%,
            #F1E9FF 100%
        ) !important;
        color: #222222 !important;
    }


    p, h1, h2, h3, h4, h5, h6, span, div, label, li {
        color: #222222 !important;
    }
    
    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    .hero-wrapper .block-container {
        max-width: 100vw !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    /* Streamlit 글로벌 구조에서 hero가 갇히지 않게 확장 */
    .hero-wrapper {
        width: 100vw !important;
        margin-left: calc(50% - 50vw) !important;
    }

    
    .section-spacer {
        height: 100px;
        width: 100%;
    }
    
    /* =============================================
       1. HERO SECTION & ANIMATIONS
       ============================================= */
    .hero-container {
        position: relative;
        width: 100vw !important;     /* 화면 전체 가로 */
        height: 100vh !important;    /* 화면 전체 세로 */
        
        margin: 0 !important;
        padding: 0 !important;

        left: 0 !important;
        right: 0 !important;

        overflow: hidden;

        display: flex;
        align-items: center;
        justify-content: center;

        background-size: cover !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
    }
    
    .hero-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg,rgba(255,255,255,0.33) 0%,rgba(255,255,255,0.17) 50%,rgba(255,255,255,0.05) 100%);
        z-index: 1;
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
        max-width: 1200px;
        width: 100%;
        padding: 0 40px;
        text-align: right;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        justify-content: center;
        height: 100%;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translate3d(0, 30px, 0); }
        to { opacity: 1; transform: translate3d(0, 0, 0); }
    }
    
    .animate-on-load {
        opacity: 0;
        animation: fadeInUp 0.8s ease-out forwards;
    }
    
    /* HERO TITLE */
    .hero-title {
        font-size: 5.5rem !important;
        font-weight: 450 !important; /* 기존보다 조금 얇게 */
        line-height: 1.05;
        margin-bottom: 1.5rem;
        letter-spacing: -2px;

        /* 블랙→퍼플 고급 그라데이션 */
        background: linear-gradient(
            135deg,
            #111111 0%,
            #0A0414 30%,
            #2A144A 50%,
            #0A0414 80%,
            #5B3A9E 100%
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
            
        text-shadow:
            0 0 4px rgba(255, 255, 255, 0.08),
            0 0 8px rgba(255, 255, 255, 0.05),
            1px 1px 3px rgba(0,0,0,0.25);

        opacity: 0;
        animation: fadeInUp 0.8s ease-out forwards;
        animation-delay: 0.2s; /* Title 먼저 */
    }



    /* HERO SUBTITLE */
    .hero-subtitle {
        font-size: 2.5rem !important;
        font-weight: 300;
        line-height: 1.35;
        max-width: 800px;
        margin-bottom: 3rem;
        letter-spacing: -0.5px;

        /* 블랙→퍼플의 은은한 그라데이션 */
        background: linear-gradient(
            135deg,
            #111111 0%,
            #1A1425 40%,
            #332A4A 100%
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;

        /* Subtitle은 glow를 더 부드럽게 */
        text-shadow:
            0 0 4px rgba(255, 255, 255, 0.18),
            0 0 8px rgba(255, 255, 255, 0.12),
            1px 1px 3px rgba(0,0,0,0.25);

        opacity: 0;
        animation: fadeInUp 0.8s ease-out forwards;
        animation-delay: 1.0s; /* Subtitle은 1초 뒤 */
    }


    
    /* =============================================
    2. CARDS & LAYOUT — Glassmorphism Light Version
    ============================================= */
    .glass-card {
        background: rgba(255, 255, 255, 0.35) !important;  /* solution-card 동일 */
        backdrop-filter: blur(18px) !important;
        -webkit-backdrop-filter: blur(18px) !important;

        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 24px;

        padding: 30px !important;     /* solution-card의 padding */
        margin-bottom: 30px;

        height: 100%;
        min-height: 320px;            /* 통일 — 카드 안정적 균형 */

        display: flex;
        flex-direction: column;
        justify-content: center;      /* solution card 기준 */
        align-items: center;          /* 중앙 정렬 */
        text-align: center;           /* 중앙 텍스트 */

        box-shadow: 0 10px 30px rgba(0,0,0,0.04);
        transition: transform 0.3s ease, 
                    box-shadow 0.3s ease, 
                    border-color 0.3s ease;
    }

    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(139, 92, 246, 0.18);
        border-color: rgba(139, 92, 246, 0.5);
    }

    /* 솔루션 카드 규격 통일 */
    .solution-card-container {
        background: rgba(255, 255, 255, 0.35) !important;   /* 동일한 밀도 */
        backdrop-filter: blur(18px) !important;
        -webkit-backdrop-filter: blur(18px) !important;

        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.25);

        height: 100%;
        min-height: 320px;

        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;

        padding: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.04);

        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .solution-card-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(139,92,246,0.18);
        border-color: rgba(139,92,246,0.5);
    }

    
    .section-title {
        font-size: 2.2rem !important;
        font-weight: 450 !important;
        margin: 0 0 30px 0;
        text-align: center;
        padding: 30px !important;

        /* ✔ 진한 보라 → 거의 검정의 고급 그라데이션 */
        background: linear-gradient(
            135deg,
            #111111 0%,      /* 거의 검정 */
            #1C0037 30%,     /* 보라가 섞인 진보라 */
            #3B007A 70%,     /* 강한 보라 */
            #2A003F 100%     /* 암보라 */
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    
    .section-subtitle {
        font-size: 1.3rem !important;
        text-align: center;
        margin-bottom: 60px;

        /* ✔ 진회색 → 거의 검정 그라데이션 */
        background: linear-gradient(
            145deg,
            #555555 0%,     /* 진회색 */
            #3A3A3A 35%,    /* 어두운 그레이 */
            #1E1E1E 75%,    /* 딥 그레이 */
            #0E0E0E 100%    /* 거의 검정 */
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* =============================================
    3. WIDGETS & SURVEY CARDS (Updated Version)
    ============================================= */

    /* 공통: column을 flex column으로 유지 */
    div[data-testid="column"] {
        display: flex;
        flex-direction: column;
    }

    /* 설문조사 카드 공통 스타일 */
    div[data-testid="stRadio"], 
    div[data-testid="stCheckbox"],
    div[class*="stSelectbox"],
    div[class*="stMultiSelect"],
    div[data-testid="stSlider"] {

        /* ✔ Glass-Light 불투명한 흰색 */
        background: rgba(255, 255, 255, 0.35) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;

        border: 1px solid rgba(255,255,255,0.25);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 24px;

        width: 280px !important;
        min-height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: flex-start !important;
        flex: 1 !important;

        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }

    /* 라벨 텍스트 스타일 */
    .stRadio label p, 
    .stSlider label p, 
    .stSelectbox label p, 
    .stMultiSelect label p,
    .stTextInput label p,
    .stTextArea label p {
        font-size: 1rem !important;
        font-weight: 500 !important;
        color: #111111 !important;
        margin-bottom: 15px;
    }

    /* 입력창 스타일 */
    .stTextInput input, .stTextArea textarea {
        background-color: rgba(255,255,255,0.85) !important;
        border: 1px solid #D1D5DB !important;
        color: #111111 !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }

    /* 포커스 스타일 */
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2) !important;
    }

    /* 슬라이더 색상 */
    div[data-testid="stSlider"] > div > div > div > div {
        background-color: #8B5CF6 !important;
    }

    /* 공통 버튼 스타일 */
    .stButton > button {
        border-radius: 30px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: none !important;
        background: linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%) !important;
        color: #fff !important;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(139, 92, 246, 0.4) !important;
    }

    /* Primary 버튼 스타일 */
    button[kind="primary"] {
        background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%) !important;
        padding: 16px 32px !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        display: block !important;
        margin: 0 auto !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4) !important;
    }
    
    /* 화면이 1200px 이하로 줄어들면 두 개씩 */
    @media (max-width: 1200px) {
        div[data-testid="stRadio"],
        div[data-testid="stCheckbox"],
        div[class*="stSelectbox"],
        div[class*="stMultiSelect"],
        div[data-testid="stSlider"] {
            width: 45% !important;
        }
    }

    /* 화면이 900px 이하 → 두 카드가 겹치기 전에 아래로 내려감 */
    @media (max-width: 900px) {
        div[data-testid="stRadio"],
        div[data-testid="stCheckbox"],
        div[class*="stSelectbox"],
        div[class*="stMultiSelect"],
        div[data-testid="stSlider"] {
            width: 100% !important;
        }
    }
    
    /* =============================================
       4. STEP INDICATOR & HEADER
       ============================================= */
    .step-container {
        display: flex;
        justify-content: space-between;
        margin: 60px auto 80px auto;
        max-width: 1000px;
        position: relative;
    }
    
    .step-item {
        text-align: center;
        z-index: 2;
        flex: 1;
        position: relative;
    }
    
    .step-circle {
        width: 50px;
        height: 50px;
        background: #FFFFFF;
        border-radius: 50%;
        margin: 0 auto 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 1.4rem !important;
        border: 2px solid #E5E7EB;
        color: #9CA3AF !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .step-item.active .step-circle,
    .step-item.completed .step-circle {
        background: #8B5CF6;
        border-color: transparent;
        color: white !important;
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
    }
    
    .step-label {
        font-size: 0.9rem !important;
        color: #9CA3AF !important;
        font-weight: 450 !important;
    }
    
    .step-item.active .step-label {
        color: #8B5CF6 !important;
    }
    
    .step-line {
        position: absolute;
        top: 25px;
        left: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(90deg, #8B5CF6 0%, #4C1D95 50%, #000000 100%);
        z-index: 1;
    }
    
    /* [수정 5] Step 헤더 스타일 (이미지+텍스트 나란히) */
    .step-header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin-bottom: 40px;
        background: transparent;
        padding: 20px;
    }
    
    .step-header-title {
        font-size: 2rem !important;
        font-weight: 450 !important;
        margin: 0;
        color: #111;
    }

    /* [수정 4] Step 3 Loading Overlay */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(5px);
        z-index: 9999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E5E7EB;
    }
    
    section[data-testid="stSidebar"] h1 {
        color: #8B5CF6 !important;
    }

    .glass-box {
        background: rgba(255, 255, 255, 0.35);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
            
    .loading-progress {
        width: 300px;
        height: 12px;
        background: rgba(255,255,255,0.3);
        border-radius: 6px;
        overflow: hidden;
        margin-top: 20px;
    }
    .loading-progress-fill {
        height: 100%;
        width: 0%;
        background: #8B5CF6;
        border-radius: 6px;
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 데이터 거버넌스 ---
STANDARD_DATA = {
    "Carbs (탄수화물)": ["충격적인 결말 포함 1분 쇼츠", "웃음참기 챌린지 실패", "뇌 빼고 보기 좋은 킬링타임", "틱톡 댄스 챌린지", "연예인 열애설 디스패치", "개그 콩트 몰아보기", "사이다 썰 애니메이션", "먹방 ASMR", "게임 하이라이트", "일상 브이로그", "리액션 영상", "숏폼 드라마"],
    "Protein (단백질)": ["파이썬 코딩 테스트 풀이", "컴활 1급 필기 요약", "재무제표 분석 강의", "부동산 경매 월세", "직장인 엑셀 실무", "반도체 산업 전망", "토익 공부법", "인공지능 논문 리뷰", "경제 뉴스 해설", "주식 투자 전략", "창업 성공 사례", "마케팅 트렌드"],
    "Fats (지방)": ["빗소리 10시간", "수면 유도 델타파", "장작 타는 소리 ASMR", "가사 없는 지브리 피아노", "숲속 물소리 명상", "불멍 영상 4K", "로파이(Lofi) 비트", "싱잉볼 소리", "백색소음", "파도소리", "카페 배경음", "명상 가이드"],
    "Vitamins (비타민)": ["니체의 철학 해설", "현대 미술 난해한 이유", "양자역학 이중 슬릿", "채식주의 윤리 토론", "제3세계 영화 비평", "우주의 기원 빅뱅", "인간의 자유의지", "클래식 음악 역사", "문화 다양성", "환경 다큐멘터리", "역사 다큐", "TED 강연"]
}

# --- 4. 헬퍼 함수들 ---
def load_image(path):
    full_path = f"source/{path}"
    if os.path.exists(full_path):
        return Image.open(full_path)
    return None

def load_svg_content(path):
    full_path = f"source/{path}"
    if os.path.exists(full_path):
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None
    return None

def get_base64_of_bin_file(bin_file):
    full_path = f"source/{bin_file}"
    if os.path.exists(full_path):
        with open(full_path, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

def get_embedding(text, client):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def filter_invalid_titles(titles):
    invalid_patterns = [
        "YouTube", "YouTube Music", "YouTube Kids", "YouTube 스튜디오",
        "YouTube Premium", "YouTube TV", "YouTube Shorts",
        "홈", "Shorts", "구독", "나중에 볼 동영상", "좋아요 표시한 동영상",
        "재생목록", "오프라인 저장", "다운로드", "구매 항목", "영화",
        "실시간", "게임", "스포츠", "학습", "팟캐스트",
        "설정", "신고 기록", "고객센터", "의견 보내기", "정보",
        "보도자료", "저작권", "문의하기", "크리에이터", "광고", "개발자",
        "약관", "개인정보처리방침", "정책 및 안전", "YouTube 작동 원리",
        "새로운 기능 테스트", "더보기", "간략히",
        "구독", "구독중", "알림", "모두", "맞춤설정", "없음",
        "좋아요", "싫어요", "공유", "오프라인 저장", "클립", "저장",
        "신고", "스크립트 표시", "댓글",
        "조회수", "업로드", "실시간 스트리밍", "최근 업로드",
        "인기 업로드", "처음부터 재생", "믹스", "관련 동영상",
        "탐색", "라이브러리", "기록", "내 동영상", "시청 기록",
        "B tv", "tv"
    ]
    
    filtered_titles = []
    for title in titles:
        if len(title) < 5 or len(title) > 200:
            continue
        
        is_invalid = False
        title_lower = title.lower()
        for pattern in invalid_patterns:
            if pattern.lower() in title_lower and len(title) < 20:
                is_invalid = True
                break
        
        if 'http' in title_lower or 'www.' in title_lower:
            is_invalid = True
            
        if title.strip().isdigit():
            is_invalid = True
            
        if not is_invalid:
            filtered_titles.append(title)
    
    return filtered_titles

def apply_context_weights(base_scores, user_context):
    weighted_scores = base_scores.copy()
    
    # 1. 시청 시간대별 가중치 (기존 유지)
    watch_time_weights = {
        "잠들기 전": {"Carbs": 0.9, "Protein": 0.8, "Fats": 1.3, "Vitamins": 1.0},
        "식사하면서": {"Carbs": 1.3, "Protein": 0.7, "Fats": 0.9, "Vitamins": 1.1}, # 밥친구는 보통 예능
        "이동 중": {"Carbs": 1.2, "Protein": 1.0, "Fats": 0.8, "Vitamins": 1.0},
        "일/공부 중": {"Carbs": 0.6, "Protein": 1.1, "Fats": 1.3, "Vitamins": 1.0} # 노동요(Fats)
    }
    
    watch_time = user_context.get('watch_time', "식사하면서")
    time_weight = watch_time_weights.get(watch_time, {})
    
    for nutrient in weighted_scores:
        weighted_scores[nutrient] *= time_weight.get(nutrient, 1.0)
    
    # 2. [수정] 쇼츠 과다 시청 여부 (shorts_heavy) 반영
    # 쇼츠를 많이 본다고 답했으면, Carbs(재미) 성향이 높다고 판단하여 가중치 부여
    if user_context.get('shorts_heavy', False):
        weighted_scores['Carbs'] *= 1.2
        weighted_scores['Protein'] *= 0.9  # 숏폼러들은 긴 호흡의 학습을 힘들어하는 경향 보정

    # 3. [수정] 프리미엄 유저 (is_premium) 반영
    # 프리미엄 유저는 '백그라운드 재생'으로 음악(Fats) 점수가 과하게 잡혔을 수 있음.
    # 이미 앞단(벡터계산)에서 보정했지만, 여기서 한 번 더 밸런스를 잡아줌.
    if user_context.get('is_premium', False):
        # 음악 청취로 인한 Fats 거품을 살짝 걷어냄 (정상화)
        weighted_scores['Fats'] *= 0.9
    
    # 4. 백분율 재계산
    total = sum(weighted_scores.values())
    if total > 0:
        for nutrient in weighted_scores:
            weighted_scores[nutrient] = int((weighted_scores[nutrient] / total) * 100)
            
    return weighted_scores

def calculate_entropy_score(scores):
    """
    [수정된 로직] 
    기존 엔트로피 방식 대신 '이상적인 비율(25%)과의 거리'를 계산합니다.
    편식이 심할수록 점수가 급격히 낮아집니다.
    """
    # 1. 값들을 리스트로 변환
    values = list(scores.values())
    total = sum(values)
    
    if total == 0: return 0
    
    # 2. 백분율로 정규화 (합을 100%로 맞춤)
    percents = [(v / total) * 100 for v in values]
    
    # 3. 이상적인 비율 (4개 항목이니 각각 25%)
    ideal = 25.0
    
    # 4. 편차(Distance) 계산: |내 점수 - 25| 의 합계
    # 예: 53%라면 |53 - 25| = 28만큼 벌점
    diffs = [abs(p - ideal) for p in percents]
    total_diff = sum(diffs)
    
    # 5. 점수 환산
    # 이론상 최악의 경우(100, 0, 0, 0)일 때 편차 합은 150입니다.
    # (|75| + |-25| + |-25| + |-25| = 150)
    # 따라서 150을 기준으로 감점합니다.
    
    penalty = (total_diff / 150.0) * 100
    final_score = 100 - penalty
    
    return int(max(0, final_score))

def diagnose_pattern(weighted_scores, user_context):
    # 가장 높은 점수의 영양소 찾기
    max_nutrient = max(weighted_scores, key=weighted_scores.get)
    max_value = weighted_scores[max_nutrient]
    
    # 진단명 사전
    diagnoses = {
        "Carbs": {
            "high": "숏폼 도파민 중독증", 
            "medium": "알고리즘 표류 증후군", 
            "context": {
                "잠들기 전": "야간 자극 과다 증후군", 
                "식사하면서": "먹방 의존증"
            }
        },
        "Protein": {
            "high": "정보 과부하 증후군", 
            "medium": "학습 강박증", 
            "context": {
                "일/공부 중": "워커홀릭 정보 섭취증"
            }
        },
        "Fats": {
            "high": "디지털 수면제 의존증", 
            "medium": "현실 도피 증후군", 
            "context": {
                "잠들기 전": "수면 유도 과의존증"
            }
        },
        "Vitamins": {
            "high": "정보 편식 개선 중", 
            "medium": "균형 잡힌 디지털 식단", 
            "context": {}
        }
    }
    
    watch_time = user_context.get('watch_time')
    
    # 점수 레벨 판별
    if max_value > 55: level = "high"
    elif max_value > 35: level = "medium"
    else: return "디지털 영양 불균형"
    
    # [수정됨] 숏폼 과다 시청자 -> '만성...' 대신 기존 '숏폼 도파민 중독증'으로 이름 통합
    # (쇼츠 많이 봄 체크 시, 점수 상관없이 이 진단명 우선 적용)
    if max_nutrient == "Carbs" and user_context.get('shorts_heavy', False):
        return "숏폼 도파민 중독증"

    # 컨텍스트 기반 특수 진단 (시간대별 습관 반영)
    # 예: 잠들기 전 + 재미 위주 = 야간 자극 과다 증후군
    if watch_time in diagnoses[max_nutrient].get("context", {}):
        return diagnoses[max_nutrient]["context"][watch_time]
        
    # 기본 진단 반환 (점수 레벨에 따름)
    return diagnoses[max_nutrient].get(level, "디지털 편식증")

def generate_personalized_recommendations(weighted_scores, user_context):
    recommendations = []

    if not weighted_scores: return []
    
    min_nutrient = min(weighted_scores, key=weighted_scores.get)
    max_nutrient = max(weighted_scores, key=weighted_scores.get)
    
    nutrient_korean = {"Carbs": "재미/오락", "Protein": "지식/학습", "Fats": "휴식/힐링", "Vitamins": "다양성/시야확장"}
    nutrient_content = {
        "Carbs": ["코미디 쇼", "게임 방송", "예능 프로그램", "챌린지 영상"],
        "Protein": ["온라인 강의", "TED 강연", "다큐멘터리", "전문가 인터뷰"],
        "Fats": ["ASMR", "명상 가이드", "자연 영상", "수면 음악"],
        "Vitamins": ["외국 문화", "예술 작품", "철학 강의", "새로운 취미"]
    }
    
    if weighted_scores[min_nutrient] < 15:
        recommendations.append(f"💊 {nutrient_korean[min_nutrient]} 콘텐츠가 매우 부족합니다. {', '.join(nutrient_content[min_nutrient][:2])} 같은 영상을 추가해보세요.")
    if weighted_scores[max_nutrient] > 50:
        recommendations.append(f"⚠️ {nutrient_korean[max_nutrient]} 콘텐츠에 과도하게 편중되어 있습니다.")
    
    watch_time = user_context.get('watch_time')
    if watch_time == "잠들기 전" and weighted_scores["Carbs"] > 30:
        recommendations.append("🌙 잠들기 전 자극적인 콘텐츠는 수면을 방해할 수 있습니다.")
    
    try:
        daily_val = str(user_context.get('daily_hours', 2))
        import re
        nums = re.findall(r'\d+', daily_val)
        daily_hours = int(nums[0]) if nums else 0
        
        if daily_hours >= 4:
            recommendations.append(f"⏰ 하루 {daily_hours}시간 시청은 눈 건강에 해롭습니다. 디지털 디톡스가 필요합니다.")
    except:
        pass

    if not recommendations:
        recommendations.append("✨")
    
    return recommendations[:3]

# --- [헬퍼 1] 쇼츠 여부 판별 ---
def is_likely_shorts(title):
    """제목에 #Shorts가 있거나, 짐작가는 패턴이 있으면 True"""
    t = title.lower()
    if "#shorts" in t or "#쇼츠" in t or "shorts" in t:
        return True
    return False

# --- [헬퍼 2] 룰 기반 점수 보정 (치트키) ---
def apply_keyword_boost(title, is_premium=False):
    """
    AI가 헷갈려하는 영상들을 강제로 올바른 영양소로 분류합니다.
    """
    title_lower = title.lower()

    # 1. [재미/오락]
    carbs_keywords = [
        "예능", "코미디", "개그", "웃음", "레전드", "ㅋㅋ", "ㅎㅎ", 
        "몰카", "참기", "챌린지", "게임", "game", "매드무비", "하이라이트", 
        "리액션", "먹방", "쇼츠", "shorts", "무한도전", "런닝맨", "유퀴즈", # 유퀴즈는 예능 성격도 있음
        "침착맨", "엔터", "스케치", "콩트"
    ]

    # [지방] 휴식/힐링 (음악, ASMR 등)
    fats_keywords = [
        "playlist", "플레이리스트", "essential", "jazz", "lullaby", "asmr", 
        "빗소리", "백색소음", "meditation", "요가", "산책", "vlog", "브이로그",
        "pop", "song", "music", "노래", "감성", "lo-fi", "lofi", "piano", "classic", "클래식"
    ]
    
    # [단백질] 지식/학습 (뉴스, 강연 등)
    protein_keywords = [
        "교수", "박사", "강연", "ted", "특강", "다큐", "documentary", 
        "뉴스", "news", "경제", "주식", "재테크", "역사", "history", 
        "과학", "science", "우주", "기술", "ai", "개발", "코딩", 
        "영어", "회화", "공부", "스터디", "독서", "책", "인문학", "철학",
        "지식", "상식", "이동진", "슈카", "유퀴즈", "알쓸", "ebs", "bbc"
    ]
    
    # [비타민] 다양성/예술
    vitamin_keywords = [
        "여행", "travel", "세계", "문화", "미술", "전시", "영화", "movie", 
        "리뷰", "해석", "비하인드", "창작", "메이킹", "diy", "취미"
    ]

    # [Carbs] 재미
    if any(k in title_lower for k in carbs_keywords):
        return "Carbs", 2.0 # 재미는 확실하게 잡아줘야 함
    
    # 1. 음악/힐링 키워드 발견 시
    if any(k in title_lower for k in fats_keywords):
        if is_premium:
            # 프리미엄 유저는 "배경음악"일 확률이 높으므로 점수 반영 비중을 낮춤 (0.5)
            return "Fats", 0.8 
        else:
            # 일반 유저는 "일부러 찾아 듣는 힐링"이므로 점수 높임 (3.0)
            return "Fats", 1.5
            
    if any(k in title_lower for k in protein_keywords):
        return "Protein", 2.0
    if any(k in title_lower for k in vitamin_keywords):
        return "Vitamins", 1.8
        
    return None, 1.0

# --- [메인] 벡터 점수 계산 (수정됨: user_context 추가) ---
def calculate_vector_scores(user_texts, client, user_context=None):

    # 사용자 설정 가져오기
    is_premium = False
    if user_context:
        is_premium = user_context.get('is_premium', False)
    
    # 1. 기준점 임베딩 (기존과 동일)
    nutrients_anchor = {
        "Carbs": "funny comedy entertainment game show prank variety short dopamine", 
        "Protein": "education knowledge science history news documentary learning philosophy lecture", 
        "Fats": "relaxation healing music nature asmr meditation sleep comfort peace vlog", 
        "Vitamins": "art culture travel creativity diversity new hobby perspective global" 
    }
    
    anchor_embeddings = {}
    for k, v in nutrients_anchor.items():
        try:
            res = client.embeddings.create(input=v, model="text-embedding-3-small")
            anchor_embeddings[k] = np.array(res.data[0].embedding)
        except:
            anchor_embeddings[k] = np.zeros(1536)

    scores = {"Carbs": 0.0, "Protein": 0.0, "Fats": 0.0, "Vitamins": 0.0}
    
    # 2. 텍스트 분석
    for text in user_texts:
        if not text.strip(): continue
        
        # [A] 쇼츠 디버프
        weight = 0.4 if is_likely_shorts(text) else 1.0
        
        # [B] 키워드 룰 (is_premium 정보 전달!)
        forced_cat, boost = apply_keyword_boost(text, is_premium)
        
        if forced_cat:
            scores[forced_cat] += (1.0 * boost * weight)
            continue 
        
        # [C] AI 벡터 계산 (기존과 동일)
        try:
            res = client.embeddings.create(input=text, model="text-embedding-3-small")
            user_vec = np.array(res.data[0].embedding)
            
            best_cat = None
            max_sim = -1.0
            norm_u = np.linalg.norm(user_vec)
            
            for k, anchor_vec in anchor_embeddings.items():
                norm_a = np.linalg.norm(anchor_vec)
                if norm_u > 0 and norm_a > 0:
                    sim = np.dot(user_vec, anchor_vec) / (norm_u * norm_a)
                    if sim > max_sim:
                        max_sim = sim
                        best_cat = k
            
            if best_cat:
                scores[best_cat] += (1.0 * weight)
        except:
            continue

    # 정규화
    total = sum(scores.values())
    if total == 0: return {k: 0 for k in scores}
    return {k: int((v / total) * 100) for k, v in scores.items()}

def search_youtube_videos(keyword, api_key):
    if not keyword or not keyword.strip():
        return []
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        search_response = youtube.search().list(q=keyword, part='snippet', maxResults=3, type='video', regionCode='KR', relevanceLanguage='ko').execute()
        videos = []
        for item in search_response.get('items', []):
            if 'id' in item and 'videoId' in item['id']:
                videos.append({
                    'title': item['snippet']['title'],
                    'thumbnail': item['snippet']['thumbnails']['high']['url'],
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                    'channel': item['snippet']['channelTitle']
                })
        return videos
    except Exception as e:
        st.error(f"YouTube API Error: {e}") # [수정 9] 에러 발생 시 사용자에게 알림
        return []

def create_radar_chart(scores):
    categories = ['탄수화물(재미)', '단백질(지식)', '지방(휴식)', '비타민(다양성)']
    values = [scores.get('Carbs', 0), scores.get('Protein', 0), scores.get('Fats', 0), scores.get('Vitamins', 0)]
    values += values[:1]
    categories += categories[:1]
    
    fig = go.Figure()
    balanced = [25, 25, 25, 25, 25]
    fig.add_trace(go.Scatterpolar(r=balanced, theta=categories, fill='toself', name='균형 식단', line=dict(color='#ccc', dash='dash'), fillcolor='rgba(200, 200, 200, 0.1)'))
    fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name='내 식단', line=dict(color='#8B5CF6', width=3), fillcolor='rgba(139, 92, 246, 0.3)'))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor='rgba(0,0,0,0.1)', gridwidth=1, tickfont=dict(color='#666')), angularaxis=dict(gridcolor='rgba(0,0,0,0.1)', tickfont=dict(color='#222', size=14))),
        showlegend=True, margin=dict(t=20, b=20, l=40, r=40), height=400, font=dict(size=14, color='#222'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', legend=dict(font=dict(color='#222'))
    )
    return fig

def create_gauge_chart(score):
    if score < 40: bar_color, status = "#FF6B6B", "위험"
    elif score < 70: bar_color, status = "#FFD93D", "주의"
    else: bar_color, status = "#6BCF7F", "건강"
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta", value = score,
        domain = {'x': [0, 1], 'y': [0, 1]}, 
        title = {'text': f"뇌 건강 지수: {status}", 'font': {'size': 20, 'color': '#222'}},
        delta = {'reference': 70, 'increasing': {'color': "#6BCF7F"}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#666"},
            'bar': {'color': bar_color, 'thickness': 0.8},
            'bgcolor': "rgba(0,0,0,0.05)", 'borderwidth': 2, 'bordercolor': "#ccc",
            'steps': [{'range': [0, 40], 'color': 'rgba(255, 107, 107, 0.1)'}, {'range': [40, 70], 'color': 'rgba(255, 217, 61, 0.1)'}, {'range': [70, 100], 'color': 'rgba(107, 207, 127, 0.1)'}],
            'threshold': {'line': {'color': "#666", 'width': 4}, 'thickness': 0.75, 'value': 70}
        }
    ))
    fig.update_layout(height=300, margin=dict(t=50, b=10, l=30, r=30), font=dict(size=16, color='#222'), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

# [수정 5] 헤더 생성 헬퍼 함수 (이미지 옆에 텍스트 배치)
def render_step_header(title, image_filename):
    b64_img = get_base64_of_bin_file(f"steps/{image_filename}")
    if b64_img:
        img_tag = f'<img src="data:image/png;base64,{b64_img}" style="width:100px; height:100px; object-fit:contain;">'
    else:
        img_tag = ''
        
    st.markdown(f"""
    <div class="step-header-container">
        {img_tag}
        <h2 class="step-header-title">{title}</h2>
    </div>
    """, unsafe_allow_html=True)

import base64
import os

# 1. 이미지를 HTML에 넣기 위해 Base64로 변환하는 도구 함수
def img_to_base64(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

# 2. 보내주신 진단명 -> 이미지 경로 매핑 함수
def get_diagnosis_image_path(diagnosis_name: str) -> str:
    """진단명 문자열을 받아서 해당 캐릭터 PNG 경로를 반환."""
    mapping = {
        "숏폼 도파민 중독증": "characters/diagnosis_shortform_dopamine.png",
        "알고리즘 표류 증후군": "characters/diagnosis_algorithm_drift.png",
        "야간 자극 과다 증후군": "characters/diagnosis_night_overstim.png",
        "먹방 의존증": "characters/diagnosis_mukbang_dependence.png",
        "정보 과부하 증후군": "characters/diagnosis_info_overload.png",
        "학습 강박증": "characters/diagnosis_learning_obsession.png",
        "워커홀릭 정보 섭취증": "characters/diagnosis_workaholic_intake.png",
        "디지털 수면제 의존증": "characters/diagnosis_digital_sleep_aid.png",
        "현실 도피 증후군": "characters/diagnosis_reality_escape.png",
        "수면 유도 과의존증": "characters/diagnosis_sleep_induction.png",
        "정보 편식 개선 중": "characters/diagnosis_improving_diet.png",
        "균형 잡힌 디지털 식단": "characters/diagnosis_balanced_diet.png",
        "디지털 영양 불균형": "characters/diagnosis_imbalance.png",
        "디지털 편식증": "characters/diagnosis_picky_eating.png",
    }
    # 혹시 예상치 못한 진단명이 들어온 경우를 대비해 기본 캐릭터 지정
    # (주의: characters 폴더에 diagnosis_default.png 파일이 있어야 오류가 안 납니다)
    return mapping.get(diagnosis_name, "characters/diagnosis_default.png")

def scroll_to_top():
    js = '''
    <script>
        var body = window.parent.document.querySelector(".main");
        console.log(body);
        body.scrollTop = 0;
    </script>
    '''
    components.html(js, height=0)

# --- 5. Session State 초기화 ---
if 'current_tab' not in st.session_state: st.session_state.current_tab = 'Introduction'
if 'step' not in st.session_state: st.session_state.step = 1
if 'survey_complete' not in st.session_state: st.session_state.survey_complete = False
if 'user_context' not in st.session_state: st.session_state.user_context = {}

# --- 6. 사이드바 네비게이션 ---
with st.sidebar:
    st.markdown("# YouTube Diet")
    st.markdown("### 당신의 알고리즘 처방전")
    st.markdown("---")
    
    if st.button("Introduction | 소개", key="sidebar_intro", help="서비스 소개"):
        st.session_state.current_tab = 'Introduction'
        st.rerun()
    
    if st.button("Analyzation | 분석", key="sidebar_analyze", help="영양 분석 시작"):
        st.session_state.current_tab = 'Analyzation'
        st.rerun()
    
    st.markdown("---")
    st.markdown("""
    <small style='color: #666;'>
    © 2024 Youtube Diet Project<br>
    Made with ❤️ by Soomin
    </small>
    """, unsafe_allow_html=True)

# --- 7. Introduction 탭 (최종 완성: 간격 조정 & 잘림 수정 & 문구 반영) ---
if st.session_state.current_tab == 'Introduction':
    
    # 1. Hero Section
    hero_bg = get_base64_of_bin_file("hero/hero_banner.png")

    st.markdown(f"""
    <div class="hero-wrapper">
        <div class="hero-container" style="background-image: url('data:image/png;base64,{hero_bg}');">
            <div class="hero-overlay"></div>
            <div class="hero-content animate-on-load">
                <h1 class="hero-title" style="font-size: 3.5rem; font-weight: 800; letter-spacing: -1px;">Youtube-Diet</h1>
                <p class="hero-subtitle" style="font-size: 1.4rem; margin-top: 10px;">
                    당신의 알고리즘 처방전 <span style="-webkit-text-fill-color: initial; background: none;">💊</span>
                </p>
                <p style="margin-top: 15px; font-size: 1.0rem; opacity: 0.8; font-weight: 300;">
                    AI-Powered Information Dietitian
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

    # 2. Catchphrase & Problem Definition
    st.markdown("""
    <div class="glass-card animate-on-load" style="text-align: center; padding: 50px 20px; margin-bottom: 50px;">
        <h2 class="section-title" style="margin-top: 0; font-size: 2.2rem; line-height: 1.4; letter-spacing: -0.5px;">
            당신의 알고리즘 식단,<br>
            진짜 '당신'의 선택인가요?
        </h2>
        <p class="section-subtitle" style="font-size: 1.15rem; margin-top: 25px; line-height: 1.8; color: #555;">
            매일 섭취하는 유튜브 콘텐츠가 당신의 사고를 지배합니다.<br>
            당신의 유튜브 습관, <strong style="color: #8B5CF6;">영양 분석</strong>이 필요합니다.
        </p>
    </div>
    
    <div style="text-align: center; margin-bottom: 40px;" class="animate-on-load">
        <h2 class="section-title">
            <span style="-webkit-text-fill-color: initial; background: none;">🚨</span> 현대인의 디지털 편식 문제
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    def card_block(path, title, desc):
        try:
            b64 = get_base64_of_bin_file(f"card/{path}")
            img_html = f'<img src="data:image/png;base64,{b64}" style="width:100%; border-radius:15px; margin-bottom:15px; object-fit: cover; height: 180px;">'
        except:
            img_html = ''
        return f"""
        <div class="glass-card animate-on-load" style="height: 100%;">
            {img_html}
            <h3 style="margin-bottom:10px; font-size: 1.2rem;">{title}</h3>
            <p style="color:#666; font-size: 0.95rem; line-height: 1.5;">{desc}</p>
        </div>
        """
    
    with col1: st.markdown(card_block("filterbubble.png", "필터 버블 (Filter Bubble)", "비슷한 정보만 반복 노출되어 사고가 편향되는 현상입니다."), unsafe_allow_html=True)
    with col2: st.markdown(card_block("dopamine.png", "도파민 중독 (Dopamine)", "짧고 자극적인 숏폼 콘텐츠에 뇌가 중독되어 집중력이 저하됩니다."), unsafe_allow_html=True)
    with col3: st.markdown(card_block("imbalance.png", "정보 불균형 (Imbalance)", "재미 위주의 편식으로 인해 지적 성장과 다양한 시각이 결핍됩니다."), unsafe_allow_html=True)
    
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

    # 3. Technical Validation (Cluster Map & Matrix)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;" class="animate-on-load">
        <h2 class="section-title">
            <span style="-webkit-text-fill-color: initial; background: none;">🔬</span> 우리의 진단 로직
        </h2>
        <p class="section-subtitle">단순히 AI에게 "분석해줘"라고 묻는 것이 아닌, <b>의미론적 벡터 분석</b>을 통해 정량 지표를 산출합니다.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1.2, 1])
    
    with c1:
        cluster_img = get_base64_of_bin_file("cluster.png")
        if cluster_img:
            st.markdown(f"""
            <div class="glass-card animate-on-load" style="padding: 10px; overflow: hidden; border: 1px solid #eee;">
                <img src="data:image/png;base64,{cluster_img}" style="width: 100%; object-fit: contain; border-radius: 10px;">
                <div style="padding: 12px; text-align: center;">
                    <p style="font-size: 0.9rem; color: #333; font-weight: bold; margin: 0;">[Figure 1] PCA Cluster Verification</p>
                    <p style="font-size: 0.8rem; color: #666; margin-top: 5px;">4대 정보 영양소(Carbs, Protein, Fats, Vitamins)의<br>벡터 공간상 군집화 검증 완료</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Cluster Map 이미지를 준비 중입니다.")

    with c2:
        def get_icon_img(name):
            b64 = get_base64_of_bin_file(f"icons/icon_{name}.svg")
            if b64:
                return f'<img src="data:image/svg+xml;base64,{b64}" style="width: 24px; height: 24px; vertical-align: middle; margin-right: 8px;">'
            return "" 

        icon_carbs = get_icon_img("carbs")
        icon_protein = get_icon_img("protein")
        icon_fats = get_icon_img("fats")
        icon_vitamins = get_icon_img("vitamins")

        st.markdown(f"""
        <div class="glass-card animate-on-load" style="height: 100%; display: flex; flex-direction: column; justify-content: center; padding: 25px;">
            <h3 style="color: #333; margin-bottom: 15px; border-bottom: 2px solid #8B5CF6; padding-bottom: 10px; display: inline-block;">
                <span style="-webkit-text-fill-color: initial; background: none;">🧬</span> 인지 부하 매트릭스
            </h3>
            <p style="color: #555; font-size: 0.95rem; margin-bottom: 20px; line-height: 1.5;">
                콘텐츠를 <b>[인지 부하 x 정보 효용]</b> 기준으로 재해석하여<br>
                4가지 필수 정보 영양소로 정의했습니다.
            </p>
            <ul style="list-style: none; padding: 0; margin: 0;">
                <li style="margin-bottom: 18px;">
                    <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        {icon_carbs}
                        <strong style="color: #333; font-size: 1.0rem;">탄수화물 (재미/오락)</strong>
                    </div>
                    <div style="font-size: 0.85rem; color: #666; padding-left: 32px;">
                        즉각적인 도파민 충전 (Shorts, 예능)
                    </div>
                </li>
                <li style="margin-bottom: 18px;">
                    <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        {icon_protein}
                        <strong style="color: #333; font-size: 1.0rem;">단백질 (지식/학습)</strong>
                    </div>
                    <div style="font-size: 0.85rem; color: #666; padding-left: 32px;">
                        지적 근육 성장 (강연, 뉴스, 경제)
                    </div>
                </li>
                <li style="margin-bottom: 18px;">
                    <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        {icon_fats}
                        <strong style="color: #333; font-size: 1.0rem;">지방 (휴식/힐링)</strong>
                    </div>
                    <div style="font-size: 0.85rem; color: #666; padding-left: 32px;">
                        필수 휴식 에너지 (ASMR, BGM)
                    </div>
                </li>
                <li>
                    <div style="display: flex; align-items: center; margin-bottom: 4px;">
                        {icon_vitamins}
                        <strong style="color: #333; font-size: 1.0rem;">비타민 (다양성)</strong>
                    </div>
                    <div style="font-size: 0.85rem; color: #666; padding-left: 32px;">
                        새로운 시야와 영감 (예술, 여행)
                    </div>
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

    # 4. Solution Process
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;" class="animate-on-load">
        <h2 class="section-title">
            <span style="-webkit-text-fill-color: initial; background: none;">➡️</span> 솔루션 과정
        </h2>
        <p class="section-subtitle">단<b>3분</b>으로 당신의 유튜브 알고리즘을 최초로 분석해보세요.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    def solution_card(img_file, step, label):
        try:
            b64 = get_base64_of_bin_file(f"steps/{img_file}")
            img_tag = f'<img src="data:image/png;base64,{b64}" style="width:100%; margin-bottom:15px;">' if b64 else ''
        except:
            img_tag = ''
        
        return f"""
        <div class="glass-card animate-on-load solution-card-container" style="text-align: center; padding: 15px;">
            {img_tag}
            <h4 style="color:#8B5CF6; margin-bottom:5px; font-size:1.5rem;">{step}</h4>
            <p style="font-size:1.3rem; color:#333; margin:0; font-weight:bold;">{label}</p>
        </div>
        """
    
    with col1: st.markdown(solution_card("step1_survey.png", "STEP 1", "습관 진단"), unsafe_allow_html=True)
    with col2: st.markdown(solution_card("step2_collect.png", "STEP 2", "피드 수집"), unsafe_allow_html=True)
    with col3: st.markdown(solution_card("step3_analysis.png", "STEP 3", "벡터 분석"), unsafe_allow_html=True)
    with col4: st.markdown(solution_card("step4_diagnosis.png", "STEP 4", "균형 평가"), unsafe_allow_html=True)
    with col5: st.markdown(solution_card("step5_prescription.png", "STEP 5", "영상 처방"), unsafe_allow_html=True)
    
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

    # 5. Usage Guide (잘림 수정 및 디자인 개선)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;" class="animate-on-load">
        <h2 class="section-title">
            <span style="-webkit-text-fill-color: initial; background: none;">💡</span> 사용 방법
        </h2>
        <p class="section-subtitle">가장 편한 방법으로 당신의 기록을 분석해보세요.</p>
    </div>
    """, unsafe_allow_html=True)
    
    guide_c1, guide_c2 = st.columns(2)
    
    with guide_c1:
        # [수정] overflow 문제 해결 (padding과 margin 조정)
        st.markdown("""
        <div class="glass-card animate-on-load" style="height: 100%; position: relative; overflow: visible; padding-top: 30px;">
            <div style="position: absolute; top: -12px; right: 10px; background: #8B5CF6; color: white; padding: 6px 16px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; box-shadow: 0 4px 6px rgba(139, 92, 246, 0.2);">
                추천
            </div>
            <h3 style="color: #333; margin-bottom: 15px; font-size: 1.1rem;">📝 방법 1: 텍스트 복사</h3>
            <p style="color: #555; font-size: 0.95rem; line-height: 1.6;">
                1. YouTube 홈페이지 접속<br>
                2. <code style="color: #E11D48; background: #FFE4E6; padding: 2px 5px; border-radius: 4px;">Ctrl + A</code> (전체선택) → <code style="color: #E11D48; background: #FFE4E6; padding: 2px 5px; border-radius: 4px;">Ctrl + C</code> (복사)<br>
                3. 입력란에 붙여넣기 (스크롤을 내려 많이 복사할수록 정확도 UP!)
            </p>
            <div style="margin-top: 20px; padding: 12px; background: rgba(139, 92, 246, 0.08); border-radius: 8px; color: #6D28D9; font-size: 0.9rem;">
                <strong>⚡ 장점:</strong> 가장 빠르고, 쇼츠 영상까지 정확하게 인식합니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with guide_c2:
        st.markdown("""
        <div class="glass-card animate-on-load" style="height: 100%; padding-top: 30px;">
            <h3 style="color: #333; margin-bottom: 15px; font-size: 1.1rem;">🖼️ 방법 2: 스크린샷 업로드</h3>
            <p style="color: #555; font-size: 0.95rem; line-height: 1.6;">
                1. YouTube 홈 화면이나 시청 기록 캡처<br>
                2. 이미지 파일 업로드 (여러 장 가능)<br>
                3. AI(Vision)가 화면 구조와 텍스트를 자동 분석
            </p>
            <div style="margin-top: 20px; padding: 12px; background: rgba(59, 130, 246, 0.08); border-radius: 8px; color: #2563EB; font-size: 0.9rem;">
                <strong>👁️ 장점:</strong> 모바일 화면 등 텍스트 복사가 어려울 때 유용합니다.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)

    # 6. Call to Action (간격 조정 완료)
    st.markdown("""
    <div style="margin-top:80px; text-align:center;" class="animate-on-load">
        <h2 class="section-title">정보 다이어트의 필요성</h2>
        <p class="section-subtitle">
            우리가 먹는 음식이 몸을 만들듯, 보는 콘텐츠가 생각을 만듭니다.<br>
            건강한 디지털 라이프를 위해, 지금 시작하세요.
        </p>
        <!-- [수정] 간격 확보 -->
        <div style="margin-top: 40px; margin-bottom: 40px; font-size: 0.95rem; color: #888; background: rgba(0,0,0,0.03); display: inline-block; padding: 10px 20px; border-radius: 20px;">
            🔒 모든 분석 데이터는 휘발성으로 처리되며 저장되지 않습니다.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    _, btn_col, _ = st.columns([3, 2, 3])
    with btn_col:
        if st.button("🚀 내 유튜브 식단 분석하러 가기", type="primary", key="go_to_analysis_btn_intro", use_container_width=True):
            st.session_state.current_tab = 'Analyzation'
            scroll_to_top()
            st.rerun()

# --- 8. Analyzation 탭 ---
elif st.session_state.current_tab == 'Analyzation':
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Step Navigator
    steps = ["설문", "수집", "분석", "진단", "처방"]
    current_step_idx = st.session_state.step
    
    progress_html = '<div class="step-container"><div class="step-line"></div>'
    for i, label in enumerate(steps, 1):
        status = "active" if i <= current_step_idx else ""
        if i < current_step_idx: status = "completed"
        progress_html += f'<div class="step-item {status}"><div class="step-circle">{i}</div><div class="step-label">{label}</div></div>'
    progress_html += '</div>'
    
    st.markdown(progress_html, unsafe_allow_html=True)
    
    # ==========================================
    # STEP 1: 설문조사 (알고리즘 보정 질문 추가)
    # ==========================================
    if st.session_state.step == 1:
        render_step_header("STEP 1. 시청 습관 진단", "step1_survey.png")
        st.markdown('<p class="section-subtitle">정확한 AI 분석을 위해 평소 습관을 알려주세요</p>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
# --- [Col 1] 시간/환경 패턴 ---
        with col1:
            st.markdown("#### ⌚ 시간 패턴")
            watch_time = st.radio(
                "주로 언제 시청하시나요?", 
                ["잠들기 전", "식사하면서", "이동 중", "일/공부 중"],
                help="선택한 시간대에 따라 '휴식' 또는 '학습' 점수의 가중치가 달라집니다.\n(예: 잠들기 전 → 자극적인 영상 감점, 휴식 영상 가점)"
            )
            daily_hours = st.slider(
                "하루 평균 시청 시간", 0, 12, 2, format="%d시간",
                help="4시간 이상일 경우 '디지털 디톡스' 관련 조언이 추가될 수 있습니다."
            )
            
        # --- [Col 2] 콘텐츠 성향 ---
        with col2:
            st.markdown("#### 📺 시청 환경 체크")
            
            with st.container(border=False):
                is_premium = st.checkbox(
                    "유튜브 프리미엄(Music) 구독 여부", 
                    help="체크 시, 음악/플레이리스트 영상을 '배경음악'으로 간주하여 알고리즘 편향을 방지합니다. (휴식 점수 과다 측정 방지)"
                )
                shorts_heavy = st.checkbox(
                    "쇼츠(Shorts)를 가장 많이 보는 편", 
                    help="체크 시, '재미/오락(도파민)' 점수에 가중치가 부여되며, 숏폼 중독 관련 진단 확률이 높아집니다."
                )            
                active_search = st.radio(
                    "영상 선택 방식", 
                    ["알고리즘 추천", "반반", "직접 검색"],
                    help="'알고리즘 추천' 선택 시 수동적인 시청 패턴으로 간주하여 진단에 참고합니다."
                )
        
        # --- [Col 3] 목표 및 의지 ---
        with col3:
            st.markdown("#### 📌 목표")
            goal = st.multiselect(
                "유튜브를 보는 주된 목적", 
                ["재미/오락", "학습/성장", "휴식/힐링", "정보/뉴스"], 
                default=[],
                help="본인의 의도와 실제 시청 패턴(데이터)의 차이를 분석하기 위한 참고 자료입니다."
            )
            change_will = st.checkbox(
                "알고리즘 개선 의향이 있다", 
                value=True,
                help="체크 해제 시, 강한 변화보다는 현상 유지 위주의 부드러운 조언을 제공합니다."
            )
        
        st.markdown("---")
        
        _, btn_col, _ = st.columns([3, 2, 3])
        with btn_col:
            if st.button("설문 조사 완료 ➡️", type="primary", use_container_width=True):
                # [데이터 저장] 설문 결과를 세션 상태에 저장 (나중에 분석 로직에서 꺼내 씀)
                st.session_state.user_context = {
                    "watch_time": watch_time,
                    "daily_hours": daily_hours,
                    "is_premium": is_premium,     # [New] 음악 보정용
                    "shorts_heavy": shorts_heavy, # [New] 쇼츠 보정용
                    "active_search": active_search,
                    "goal": goal,
                    "change_will": change_will
                }
                st.session_state.step = 2
                scroll_to_top()
                st.rerun()
    
    # STEP 2: 데이터 입력 (이미지 or 텍스트)
    # ==========================================
    elif st.session_state.step == 2:
        render_step_header("STEP 2. 유튜브 피드 데이터 수집", "step2_collect.png")
        
        with st.expander("📖 사용 방법 가이드", expanded=True):
            st.markdown("""
            ### 두 가지 방법 중 하나를 선택하세요:
            **방법 1: 텍스트 복사 (⚡ 추천)**
            1. YouTube 홈페이지 접속
            2. `Ctrl+A` (전체선택) → `Ctrl+C` (복사)
            3. 아래 텍스트 입력란에 붙여넣기
            
            **방법 2: 스크린샷 업로드**
            1. YouTube 홈 화면 스크린샷 캡처
            2. 여러 장 업로드 가능
            """)
        
        tab_txt, tab_img = st.tabs(["텍스트 입력 (추천)", "스크린샷 업로드"])
        
        # 데이터 저장소 초기화 (이전 데이터 잔류 방지)
        if 'user_input_data' not in st.session_state:
            st.session_state.user_input_data = []
        if 'raw_text_for_vector' not in st.session_state:
            st.session_state.raw_text_for_vector = []

        # -------------------------------------------------------
        # [Tab 1] 텍스트 직접 입력 (GPT 정제 로직 적용)
        # -------------------------------------------------------
        with tab_txt:
            # 💡 안내 이미지
            example_img2 = load_image("screen_example2.png")
            if example_img2:
                _, img_col_txt, _ = st.columns([1, 3, 1])
                with img_col_txt:
                    st.image(example_img2, caption="예시화면) 화면의 모든 정보를 복사해 주세요.")
                st.info("*💡 Ctrl+A로 전체 선택 후, 아래로 스크롤을 내려 더 많이 복사하면 정확도가 올라갑니다.*")

            # 💬 텍스트 입력창
            user_text = st.text_area("입력", label_visibility="collapsed",
                height=300,
                placeholder="여기에 유튜브 홈 화면 전체 텍스트를 붙여넣으세요!"
            )

        # -------------------------------------------------------
        # [Tab 2] 스크린샷 업로드
        # -------------------------------------------------------
        with tab_img:
            example_img = load_image("screen_example.png")
            if example_img:
                _, img_col, _ = st.columns([1, 3, 1])
                with img_col:
                    st.image(example_img, caption="예시화면) 스크린샷 업로드")
            
            st.info("*💡 최소 20개 이상의 영상이 나오도록 여러 장을 올려주세요.*")
            
            uploaded_files = st.file_uploader("이미지 파일 업로드", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        
        st.markdown("---")
        
        # API 키 입력 (하단 배치)
        col1, col2 = st.columns(2)
        with col1:
            openai_key = st.text_input("OpenAI API Key", value=DEFAULT_OPENAI_KEY, type="password", help="GPT-4 Vision API를 사용합니다")
        with col2:
            youtube_key = st.text_input("YouTube API Key", value=DEFAULT_YOUTUBE_KEY, type="password", help="처방 영상 검색에 사용됩니다")
        
        _, btn_col, _ = st.columns([3, 2, 3])
        
        # -------------------------------------------------------
        # [분석 시작 버튼] 로직 통합
        # -------------------------------------------------------
        with btn_col:
            if st.button("AI 분석 시작 ➡️", type="primary", use_container_width=True):
                # 1. 입력 데이터 확인
                has_text = len(user_text) > 50
                has_image = uploaded_files is not None and len(uploaded_files) > 0
                
                if not (has_text or has_image):
                    st.error("⚠️ 분석할 데이터가 없습니다! 텍스트를 붙여넣거나 이미지를 업로드해주세요.")
                elif not openai_key or not youtube_key:
                    st.error("⚠️ API Key를 모두 입력해주세요!")
                else:
                    # API 키 세션 저장
                    st.session_state.openai_key = openai_key
                    st.session_state.youtube_key = youtube_key
                    
                    # 데이터 처리 시작
                    final_titles = []
                    user_input_payload = []
                    
                    # [Case A] 텍스트 입력 처리 (GPT 정제)
                    if has_text:
                        progress_msg = st.empty()
                        progress_msg.info("📜 텍스트 구조를 분석하여 제목만 추출하는 중... (쇼츠 구간 식별)")
                        
                        try:
                            client = OpenAI(api_key=openai_key)
                            cleaning_prompt = """
                            You are a YouTube Page Text Cleaner.
                            The user has pasted the raw text dump from YouTube Home/History.
                            
                            Task:
                            1. Extract ONLY the video titles. Remove 'Views', 'Time', 'Channel Name', 'Menu items'.
                            2. **CRITICAL:** Identify the 'Shorts' section. If a title belongs to the Shorts section (usually appears after the word 'Shorts' or has no duration/timestamp), **APPEND '[Shorts]' to the end of the title.**
                            (Example: "Funny Cat Video [Shorts]", "How to cook steak")
                            
                            Return the titles as a simple list separated by commas.
                            """
                            
                            response = client.chat.completions.create(
                                model="gpt-4o",
                                messages=[
                                    {"role": "system", "content": cleaning_prompt},
                                    {"role": "user", "content": user_text[:20000]} # 너무 긴 텍스트는 자름
                                ],
                                max_tokens=2000
                            )
                            
                            cleaned_text = response.choices[0].message.content
                            titles_from_text = [
                                t.strip() for t in cleaned_text.replace("[", "").replace("]", "").replace('"', '').split(',') 
                                if len(t.strip()) > 1
                            ]
                            final_titles.extend(titles_from_text)
                            user_input_payload.append({"type": "text", "text": f"Cleaned Text: {cleaned_text}"})
                            
                        except Exception as e:
                            st.error(f"텍스트 분석 실패: {e}")
                            st.stop()

                    # [Case B] 이미지 입력 처리
                    if has_image:
                        for img_file in uploaded_files:
                            b64 = encode_image(img_file)
                            user_input_payload.append({
                                "type": "image_url", 
                                "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                            })
                    
                    # 데이터 세션 저장
                    st.session_state.user_input_data = user_input_payload
                    st.session_state.raw_text_for_vector = final_titles # 텍스트에서 나온 건 미리 저장
                    
                    # 완료 메시지 및 이동
                    shorts_count = sum(1 for t in final_titles if "Shorts" in t)
                    st.success(f"✅ 데이터 준비 완료! (텍스트 영상 {len(final_titles)}개, 쇼츠 {shorts_count}개 감지)")
                    time.sleep(1)
                    
                    st.session_state.step = 3
                    scroll_to_top()
                    st.rerun()


# ==========================================
    # STEP 3: AI 분석 및 진단 생성 (추천 로직 오류 완벽 수정본)
    # ==========================================
    elif st.session_state.step == 3:

        # 1. 진행률 표시
        progress = st.progress(0, text="분석 준비 중...")
        client = OpenAI(api_key=st.session_state.openai_key)

        # ----------------------------------
        # 단계 1: 이미지 텍스트 추출 (OCR)
        # ----------------------------------
        progress.progress(10, text="이미지에서 텍스트 추출 중...")
        time.sleep(0.5)

        extracted_titles_from_images = []

        if any(item["type"] == "image_url" for item in st.session_state.user_input_data):
            time.sleep(1)
            progress.progress(30, text="이미지 화면 구조 분석 중 (쇼츠 식별)...")

            image_payload = [
                item for item in st.session_state.user_input_data
                if item["type"] == "image_url"
            ]

            if image_payload:
                extract_prompt = """
                You are an advanced AI OCR assistant specialized in YouTube UI analysis.
                
                Task:
                1. Read the screen screenshots and extract ALL video titles accurately.
                2. Do NOT pick only keywords. Extract the FULL title sentences.
                3. Ignore UI texts like 'Home', 'Shorts', 'Subscriptions', 'Views', 'Time'.
                
                CRITICAL - Shorts Detection:
                - If a video is under a header explicitly named "Shorts",
                - OR if the thumbnail has a vertical aspect ratio (9:16) AND has the red "Shorts" logo,
                - THEN append "[Shorts]" to the end of the title.
                - OTHERWISE, do NOT append "[Shorts]".
                
                Output Format:
                Return a simple list of strings separated by commas.
                Example: "How to cook steak, Funny Cat [Shorts], Global Economy News, ..."
                """
                try:
                    ext_response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are an AI that extracts text from UI screenshots."},
                            {"role": "user", "content": image_payload + [{"type": "text", "text": extract_prompt}]}
                        ],
                        temperature=0.0,
                        max_tokens=1000
                    )
                    extracted_titles_str = ext_response.choices[0].message.content
                    
                    extracted_titles_from_images = (
                        extracted_titles_str.replace("[", "")
                        .replace("]", "")
                        .replace('"', '')
                        .split(',')
                    )
                except Exception as e:
                    st.error(f"이미지 분석 실패: {e}")

        # ----------------------------------
        # 단계 2: 벡터 연산 및 점수 계산
        # ----------------------------------
        progress.progress(50, text="벡터 공간에서 영양소 계산 중...")
        time.sleep(0.7)

        all_titles = extracted_titles_from_images + st.session_state.raw_text_for_vector
        all_titles = list(set([t.strip() for t in all_titles if len(t.strip()) > 1]))

        if not all_titles:
            st.error("분석할 데이터가 없습니다!")
            st.stop()

        base_scores = calculate_vector_scores(all_titles, client, st.session_state.user_context)
        weighted_scores = apply_context_weights(base_scores, st.session_state.user_context)
        diversity_score = calculate_entropy_score(weighted_scores) 
        diagnosis_name = diagnose_pattern(weighted_scores, st.session_state.user_context)

        # ----------------------------------
        # 단계 3: AI 진단서 및 처방 생성
        # ----------------------------------
        progress.progress(80, text="AI 닥터가 맞춤형 처방을 작성 중...")
        time.sleep(0.7)

        context = st.session_state.user_context
        
        # [핵심 로직 추가] 파이썬이 부족한/과잉 영양소를 미리 계산
        if not weighted_scores:
             weighted_scores = {"Carbs": 25, "Protein": 25, "Fats": 25, "Vitamins": 25}

        min_nutrient = min(weighted_scores, key=weighted_scores.get) # 채워야 할 것
        max_nutrient = max(weighted_scores, key=weighted_scores.get) # 줄여야 할 것
        
        nutrient_map = {
            "Carbs": "Fun/Entertainment (Comedy, Variety)",
            "Protein": "Knowledge/Learning (Lecture, News)",
            "Fats": "Rest/Healing (ASMR, Music)",
            "Vitamins": "Diversity/Art (Travel, Culture)"
        }
        
        # [프롬프트 수정] 계산된 min/max 정보를 GPT에게 강력하게 주입
        system_prompt = f"""
        You are a YouTube content analysis expert. Generate a diagnosis about the user's YouTube viewing habits.

        [Analysis Data]
        - Diagnosis Name: {diagnosis_name}
        - **EXCESS Nutrient (Too much):** {nutrient_map[max_nutrient]}
        - **LACKING Nutrient (Need more):** {nutrient_map[min_nutrient]}

        CRITICAL INSTRUCTIONS:
        1. **OUTPUT LANGUAGE: MUST BE KOREAN (한국어).**
        2. **Prescription Goal:** The user consumes too much '{max_nutrient}'. Prescribe content related to '{min_nutrient}' to balance the diet.
        3. **Search Query Rule:** In 'youtube_search_query', suggest video topics for '{min_nutrient}'. DO NOT recommend '{max_nutrient}'.
        4. **Word Ban:** Do NOT use words '비타민', '단백질', '탄수화물', '지방' in keyword/query.

        Task:
        1. 'Prescription Keyword': Catchy keyword for the *LACKING* nutrient.
        2. 'Summary': Diagnosis summary. Mention excess/lack.
        3. 'YouTube Search Query': Specific topics for the *LACKING* nutrient.

        IMPORTANT: You MUST return the result in the following JSON format. Do not change the keys.
        {{
            "prescription_keyword": "A short, metaphorical title in Korean for the user (e.g., 'Mental Detox', 'Art Vitamin')",
            "summary_text": "Diagnosis summary in Korean",
            "youtube_search_query": "A CONCRETE search query in Korean for YouTube. (e.g., 'Funny cat videos', 'Travel vlog', 'ASMR rain sounds'). This must be different from prescription_keyword."
        }}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "system", "content": system_prompt}],
                response_format={"type": "json_object"},
                temperature=0.0,
                max_tokens=500
            )
            gpt_result = json.loads(response.choices[0].message.content)

            # --- [여기가 추가된 안전장치입니다] ---
            raw_search_query = gpt_result.get('youtube_search_query', '')
            raw_keyword = gpt_result.get('prescription_keyword', '')

            # 검색어가 비어있거나, 키워드와 너무 똑같으면 '추천' 단어를 붙여서 검색되게 보정
            if not raw_search_query or raw_search_query == raw_keyword:
                search_query = f"{raw_keyword} 추천 영상"
            else:
                search_query = raw_search_query
            # ----------------------------------

            try:
                recommended_videos = search_youtube_videos(search_query, st.session_state.youtube_key)
            except Exception as vid_err:
                recommended_videos = []

            # 파이썬 가이드 생성 (이것도 파이썬 로직이므로 GPT와 결과가 일치하게 됨)
            python_recommendations = generate_personalized_recommendations(weighted_scores, st.session_state.user_context)

            result = {
                'diagnosis_name': diagnosis_name,
                'scores': weighted_scores,
                'diversity_score': diversity_score,
                'summary_text': gpt_result.get('summary_text', '진단 내용을 불러오지 못했습니다.'),
                'prescription_keyword': gpt_result.get('prescription_keyword', '디지털 밸런스'),
                'youtube_search_query': search_query, 
                'recommended_videos': recommended_videos,
                'recommendations': python_recommendations
            }

            st.session_state.result = result

        except Exception as e:
            st.error(f"AI 진단 생성 중 오류 발생: {e}")
            st.stop()

        progress.progress(100, text="✔ 분석 완료!")
        time.sleep(0.5)

        st.session_state.step = 4
        st.rerun()


    #STEP 4: 진단 결과 표시
# ==========================================
    elif st.session_state.step == 4:
        import html
        import os
        import base64
        
        render_step_header("STEP 4. 영양 불균형 진단", "step4_diagnosis.png")
        res = st.session_state.result

        # 1. 진단명 이미지 및 데이터 준비
        diagnosis_name = res['diagnosis_name']
        char_path = get_diagnosis_image_path(diagnosis_name)
        char_b64 = get_base64_of_bin_file(char_path)
        
        # 이미지 태그 생성 (없으면 빈 문자열)
        img_tag_html = ""
        if char_b64:
            img_tag_html = f'<img src="data:image/png;base64,{char_b64}" style="width:250px; max-width:100%; margin-right:0px; margin-bottom:20px; border-radius:15px;">'

        # 2. [핵심 수정] 진단명 카드 HTML 생성
        # 주의: f-string 내부의 HTML 태그들을 왼쪽 벽(line start)에 붙여서 
        # Markdown이 이를 '코드 블록'으로 오해하지 않도록 합니다.
        diagnosis_card_html = f"""
<div class="glass-card" style="border-color: #8B5CF6; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px; margin-bottom: 30px; text-align: center;">
    {img_tag_html}
    <div>
        <span style="background: rgba(139,92,246,0.15); color: #8B5CF6; padding: 6px 18px; border-radius: 20px; font-size: 0.9rem; font-weight: 800; margin-bottom: 10px; display: inline-block;">
            진단명
        </span>
        <h1 style="font-size: 2.2rem; margin: 10px 0 0 0; line-height: 1.2; background: linear-gradient(135deg, #3A0CA3, #8B5CF6, #111); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;">
            {diagnosis_name}
        </h1>
    </div>
</div>
"""
        # 들여쓰기 없는 HTML 변수를 출력
        st.markdown(diagnosis_card_html, unsafe_allow_html=True)


        # =============================
        # 두 컬럼 레이아웃
        # =============================
        col1, col2 = st.columns([1, 1])

        # ---------------------------------------
        # 📌 LEFT COLUMN — Radar Chart + Nutrients
        # ---------------------------------------
        with col1:
            st.markdown("### 📊 영양 밸런스 분석")

            # 차트 렌더링
            st.plotly_chart(create_radar_chart(res['scores']), use_container_width=True)

            # [핵심 수정] 4개의 박스를 -> 1개의 박스로 통합
            nutrients_info = {
                "Carbs": ("탄수화물", "재미/오락", "#FF6B6B", res['scores']['Carbs']),
                "Protein": ("단백질", "지식/학습", "#4ECDC4", res['scores']['Protein']),
                "Fats": ("지방", "휴식/힐링", "#45B7D1", res['scores']['Fats']),
                "Vitamins": ("비타민", "다양성/시야", "#96CEB4", res['scores']['Vitamins'])
            }
            
            # 내부 내용을 담을 문자열 초기화
            nutrients_inner_html = ""
            
            for key, (kr, desc, color, val) in nutrients_info.items():
                # 주의: 아래 f-string 안의 HTML 태그들은 왼쪽 벽에 딱 붙어 있어야 합니다.
                nutrients_inner_html += f"""
<div style="margin-bottom: 12px;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
        <span style="font-size:0.95rem; font-weight:bold; color:#333;">
            {kr} <span style="font-size:0.8rem; color:#888; font-weight:normal;">({desc})</span>
        </span>
        <span style="font-size:1.0rem; font-weight:bold; color:{color};">{val}%</span>
    </div>
    <div style="width:100%; background:rgba(0,0,0,0.05); border-radius:10px; height:8px;">
        <div style="width:{val}%; background:{color}; border-radius:10px; height:8px;"></div>
    </div>
</div>
"""
            
            # 최종적으로 하나의 Glass Card 안에 묶어서 출력
            combined_nutrients_html = f"""
<div class="glass-card" style="padding: 25px; margin-bottom: 20px;">
    <h5 style="margin: 0 0 15px 0; color:#555;">세부 영양소 점수</h5>
    {nutrients_inner_html}
</div>
"""
            st.markdown(combined_nutrients_html, unsafe_allow_html=True)

        # ---------------------------------------
        # 📌 RIGHT COLUMN — Gauge + Badges + Summary
        # ---------------------------------------
        with col2:
            st.markdown("### 🧠 뇌 건강 지수")

            # 게이지 차트
            st.plotly_chart(create_gauge_chart(res['diversity_score']), use_container_width=True)

            # 뱃지 표시 로직
            badges_earned = []
            if 30 < res['scores']['Carbs'] < 40:
                badges_earned.append(("source/badges/badge_balance.png", "균형왕"))
            if res['scores']['Protein'] > 30:
                badges_earned.append(("source/badges/badge_study.png", "학습왕"))
            if res['scores']['Fats'] > 30:
                badges_earned.append(("source/badges/badge_rest.png", "휴식왕"))
            if res['scores']['Vitamins'] > 30:
                badges_earned.append(("source/badges/badge_diversity.png", "다양성왕"))
            
            if badges_earned:
                badge_cols = st.columns(4) # 한 줄에 4개까지
                for idx, (badge_path, name) in enumerate(badges_earned):
                    with badge_cols[idx % 4]: # 컬럼 인덱스 안전장치
                        # load_image 대신 os.path.exists로 직접 확인하여 출력
                        if os.path.exists(badge_path):
                            st.image(badge_path, width=60)
                            st.caption(f"**{name}**")
                        else:
                            st.warning(f"No img: {name}")
            else:
                st.info("획득한 배지가 없습니다. (조건 미달)")
  
            # [핵심 수정] 진단 소견 텍스트 사라짐 방지
            # 1. html.escape로 특수문자(<, >) 처리
            # 2. \n을 <br>로 변환
            raw_summary = res.get('summary_text', "진단 소견 데이터가 없습니다.")
            if raw_summary:
                safe_summary = html.escape(raw_summary).replace('\n', '<br>')
            else:
                safe_summary = "진단 내용을 불러오지 못했습니다."

            # 역시 들여쓰기 없는 HTML 변수 사용
            summary_card_html = f"""
<div class="glass-card" style="margin-top:20px; padding:20px;">
    <h4 style="color:#8B5CF6; margin-bottom:10px;">👨‍⚕️ 진단 소견</h4>
    <p style="font-size:1rem; line-height:1.6; color:#444;">
        {safe_summary}
    </p>
</div>
"""
            st.markdown(summary_card_html, unsafe_allow_html=True)

        st.markdown("---")

        _, btn_col, _ = st.columns([3, 2, 3])
        with btn_col:
            if st.button("처방전 받으러 가기 ➡️", type="primary"):
                st.session_state.step = 5
                scroll_to_top()
                st.rerun()

    
    # STEP 5: 맞춤형 콘텐츠 처방 (최종 최적화)
    # ==========================================
    elif st.session_state.step == 5:
        render_step_header("STEP 5. 맞춤형 콘텐츠 처방", "step5_prescription.png")
        res = st.session_state.result
        
        # 화면에는 '멋진 키워드'를 보여줌 (UX)
        st.markdown(f"### 📺 맞춤 처방: {res['prescription_keyword']}")
        
        # -------------------------------------------------------
        # [수정] 영상 데이터 로딩 최적화
        # 1. STEP 3에서 이미 검색해둔 영상이 있으면 그걸 씁니다 (API 절약)
        # 2. 없다면, '구체적인 검색어(search_query)'로 다시 검색합니다.
        # -------------------------------------------------------
        videos = res.get('recommended_videos', [])
        
        # 검색에 사용할 쿼리 (구체적인 것 우선)
        search_query = res.get('youtube_search_query', res.get('prescription_keyword', '힐링 영상'))
        
        if not videos:
             # 데이터가 비어있을 경우에만 API 호출
             videos = search_youtube_videos(search_query, st.session_state.youtube_key)
        
        if videos:
            cols = st.columns(3)
            for i, v in enumerate(videos):
                with cols[i]:
                    st.markdown(f"""
                    <div class="glass-card" style="padding: 0; overflow: hidden; margin-bottom:10px;">
                        <img src="{v['thumbnail']}" style="width: 100%; height: 180px; object-fit: cover;">
                        <div style="padding: 15px;">
                            <h4 style="margin: 0 0 10px 0; font-size: 1rem; line-height: 1.4; height: 44px; overflow: hidden;">{v['title'][:50]}...</h4>
                            <p style="color: #666; font-size: 0.8rem;">📺 {v['channel']}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.link_button("▶️ 시청하기", v['url'])
        else:
            st.warning(f"'{search_query}' 관련 추천 영상을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.")
        
        st.markdown("---")
        
        # 개선 가이드 출력
        st.markdown("### 💡 개선 가이드")
        for rec in res.get('recommendations', []):
            st.info(f"• {rec}")
            
        st.markdown("---")
        
        c1, c2 = st.columns([1, 1])
        
        # 리포트 저장 기능
        with c1:
            report_text = f"""[YouTube Diet 진단 리포트]
날짜: {time.strftime('%Y-%m-%d')}
진단명: {res['diagnosis_name']}
다양성 점수: {res['diversity_score']}점

[영양소 점수]
- 탄수화물(재미): {res['scores'].get('Carbs', 0)}%
- 단백질(지식): {res['scores'].get('Protein', 0)}%
- 지방(휴식): {res['scores'].get('Fats', 0)}%
- 비타민(다양성): {res['scores'].get('Vitamins', 0)}%

[진단 소견]
{res['summary_text']}

[처방 키워드]
{res['prescription_keyword']}
(실제 검색 키워드: {search_query})

[추천 영상]
"""
            if videos:
                for v in videos:
                    report_text += f"- {v['title']} ({v['url']})\n"
            else:
                report_text += "(추천 영상 없음)\n"
            
            report_text += "\n[개선 가이드]\n"
            for rec in res.get('recommendations', []):
                report_text += f"- {rec}\n"

            st.download_button(
                label="📄 진단 결과 리포트 저장하기",
                data=report_text,
                file_name="youtube_diet_report.txt",
                mime="text/plain"
            )
            
        # 처음으로 돌아가기
        with c2:
            if st.button("🔄 새로운 분석 시작"):
                # 세션 초기화 (모든 데이터 삭제)
                keys_to_clear = ['step', 'result', 'user_context', 'user_input_data', 'raw_text_for_vector']
                for key in keys_to_clear:
                    if key in st.session_state: del st.session_state[key]
                st.session_state.step = 1
                scroll_to_top()
                st.rerun()
    
    # 전체 컨테이너 닫기

    st.markdown('</div>', unsafe_allow_html=True)
