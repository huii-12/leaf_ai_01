import streamlit as st
import pytz
from datetime import datetime
import sqlite3
from db_utils import get_conn, init_all_tables

st.set_page_config(
    page_title="AI 나뭇잎 분류 & 윤리 시뮬레이터",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_all_tables()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'userid' not in st.session_state:
    st.session_state['userid'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None

# Sidebar menu guide
with st.sidebar:
    st.markdown("### 🌱 학습 메뉴 안내")
    if st.session_state['logged_in']:
        st.success(f"접속 계정: **{st.session_state['username']}** (`{st.session_state['userid']}`)")
    else:
        st.info("로그인 후 아래 메뉴를 이용할 수 있습니다.")

if not st.session_state['logged_in']:
    st.title("🌱 AI 나뭇잎 분류 & 윤리 시뮬레이터")
    st.write("학급 실시간 공유 데이터베이스 기반 나뭇잎 분류 및 데이터 윤리 학습 플랫폼입니다. 서비스를 이용하려면 로그인해 주세요.")

    tab1, tab2 = st.tabs(["로그인", "신규등록"])

    with tab1:
        st.subheader("로그인")
        with st.form("login_form"):
            login_id = st.text_input("아이디")
            login_pw = st.text_input("비밀번호", type="password")
            submit_login = st.form_submit_button("로그인", type="primary")

            if submit_login:
                if login_id and login_pw:
                    conn = get_conn()
                    c = conn.cursor()
                    c.execute("SELECT username FROM users WHERE userid=? AND passwd=?", (login_id, login_pw))
                    result = c.fetchone()
                    conn.close()

                    if result:
                        st.session_state['logged_in'] = True
                        st.session_state['userid'] = login_id
                        st.session_state['username'] = result[0]
                        st.success(f"{result[0]}님 환영합니다!")
                        st.rerun()
                    else:
                        st.error("아이디 또는 비밀번호가 일치하지 않습니다.")
                else:
                    st.warning("아이디와 비밀번호를 모두 입력해 주세요.")

    with tab2:
        st.subheader("신규 회원가입")
        with st.form("signup_form"):
            reg_name = st.text_input("이름 (예: 1모둠 홍길동)")
            reg_id = st.text_input("아이디")
            reg_pw = st.text_input("비밀번호", type="password")
            reg_pw2 = st.text_input("비밀번호 확인", type="password")
            submit_signup = st.form_submit_button("가입하기")

            if submit_signup:
                if not reg_name or not reg_id or not reg_pw:
                    st.warning("모든 항목을 입력해 주세요.")
                elif reg_pw != reg_pw2:
                    st.warning("비밀번호가 일치하지 않습니다.")
                else:
                    try:
                        conn = get_conn()
                        c = conn.cursor()
                        kst = pytz.timezone('Asia/Seoul')
                        now = datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')
                        c.execute(
                            "INSERT INTO users (username, userid, passwd, created_at) VALUES (?, ?, ?, ?)",
                            (reg_name, reg_id, reg_pw, now)
                        )
                        conn.commit()
                        conn.close()
                        st.success("회원가입이 완료되었습니다. 로그인 탭에서 로그인해 주세요.")
                    except sqlite3.IntegrityError:
                        st.error("이미 존재하는 아이디입니다.")

else:
    st.title("🌱 AI 나뭇잎 분류 & 윤리 시뮬레이터에 오신 것을 환영합니다!")
    st.write(f"**{st.session_state['username']}**님, 환영합니다! 🎉")
    st.write("이 웹앱은 **학급 실시간 공유 데이터베이스(`myproject.db`)**와 연동되어 있어 모든 학생이 입력·수정한 데이터가 실시간으로 공유됩니다.")

    st.subheader("🧭 학습 단계별 바로가기")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.page_link("pages/1_Data_Input.py", label="1. 공유 DB 데이터 입력", icon="📥", use_container_width=True)
    with c2:
        st.page_link("pages/2_3D_Outlier_Check.py", label="2. 3D 산점도 & 이상치 검증", icon="📐", use_container_width=True)
    with c3:
        st.page_link("pages/3_AI_Classifier.py", label="3. AI 자동 분류 시뮬레이터", icon="🤖", use_container_width=True)
    with c4:
        st.page_link("pages/4_Ethics_Survey.py", label="4. AI 윤리 실태조사", icon="📝", use_container_width=True)

    st.divider()
    if st.button("로그아웃"):
        st.session_state['logged_in'] = False
        st.session_state['userid'] = None
        st.session_state['username'] = None
        st.rerun()
