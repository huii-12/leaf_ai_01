import streamlit as st
import pytz
import pandas as pd
from datetime import datetime
from db_utils import get_conn, init_all_tables

st.set_page_config(
    page_title="4. AI 윤리 실태조사",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_all_tables()

if not st.session_state.get('logged_in', False):
    st.warning("🔒 서비스를 이용하려면 먼저 메인 페이지(run)에서 로그인해 주세요.")
    st.page_link("run.py", label="메인 로그인 페이지로 이동", icon="🏠")
    st.stop()

st.title("📝 4. AI 데이터 윤리 의식 및 디지털 소양 자기점검 (실태조사)")
st.markdown("1~8차시 프로젝트를 통해 체득한 **데이터 무결성, 공정성, 투명성, 책임성**에 대한 나의 윤리 의식을 점검하고 결과를 공유 데이터베이스에 기록합니다.")

questions = [
    "1. (진실성) 실험이나 관찰 데이터를 수집할 때 내 예상과 다르더라도 수치를 임의로 고치지 않고 있는 그대로 기록한다.",
    "2. (무결성) 작은 측정 실수나 누락된 데이터가 전체 AI 분석 결과에 큰 오류를 일으킬 수 있음을 이해한다.",
    "3. (투명성) AI가 내놓은 분류·예측 결과를 무조건 맹신하지 않고 어떤 데이터를 근거로 판단했는지 확인하려 노력한다.",
    "4. (공정성) 특정 종류의 데이터만 지나치게 많이 학습시키면 AI가 편향된 판단을 내릴 수 있음을 설명할 수 있다.",
    "5. (비판적 사고) 3차원 산점도와 같은 시각화 도구를 통해 데이터 속 이상치(가짜 데이터)를 스스로 검증할 수 있다.",
    "6. (책임성) 공유 데이터베이스에 자료를 입력할 때 공동체 전체에 미칠 영향을 생각하며 책임감 있게 행동한다.",
    "7. (사회적 파급력) 조작된 가짜 데이터가 의료·자율주행·환경 등 실생활 AI에 쓰일 경우 심각한 사회적 불평등과 위험을 초래함을 안다.",
    "8. (협력적 소통) 모둠 활동에서 분류 기준을 정할 때 다수결이 아닌 수학적·과학적 근거를 바탕으로 동료와 합의한다.",
    "9. (디지털 소양) 인터넷이나 SNS에서 접하는 AI 생성 정보의 출처와 타당성을 비판적으로 평가하는 태도를 지녔다.",
    "10. (윤리적 실천) 앞으로 AI 기술을 개발하거나 활용할 때 인간의 존엄성과 데이터 윤리 원칙을 최우선으로 지키겠다."
]

with st.form("ethics_survey_form"):
    st.info("각 문항을 읽고 자신의 생각과 가장 가까운 점수를 선택해 주세요. (1점: 전혀 그렇지 않다 ~ 5점: 매우 그렇다)")
    answers = []
    for q in questions:
        val = st.radio(q, [1, 2, 3, 4, 5], index=3, horizontal=True)
        answers.append(val)

    submitted = st.form_submit_button("✅ 윤리 점검 결과 제출 및 저장", type="primary", use_container_width=True)
    if submitted:
        conn = get_conn()
        c = conn.cursor()
        kst = pytz.timezone('Asia/Seoul')
        now = datetime.now(kst).strftime('%Y-%m-%d %H:%M:%S')
        sql = "INSERT INTO inventory (userid, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        c.execute(sql, (st.session_state['userid'], *answers, now))
        conn.commit()
        conn.close()
        st.success("🎉 AI 데이터 윤리 점검 결과가 데이터베이스(myproject.db)에 안전하게 저장되었습니다!")

st.divider()
st.subheader("📊 학급 전체 제출 현황 및 나의 기록")
conn = get_conn()
hist_df = pd.read_sql_query(
    "SELECT id_num AS 번호, userid AS 아이디, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, created_at AS 제출시각 FROM inventory ORDER BY id_num DESC",
    conn
)
conn.close()

if len(hist_df) > 0:
    hist_df['평균 점수'] = hist_df[['q1','q2','q3','q4','q5','q6','q7','q8','q9','q10']].mean(axis=1).round(2)
    st.dataframe(hist_df, use_container_width=True)
else:
    st.caption("아직 제출된 윤리 점검 기록이 없습니다.")
