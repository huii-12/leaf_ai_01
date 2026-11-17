import streamlit as st
import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from db_utils import get_leaf_df

st.set_page_config(
    page_title="3. AI 자동 분류 시뮬레이터",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

if not st.session_state.get('logged_in', False):
    st.warning("🔒 서비스를 이용하려면 먼저 메인 페이지(run)에서 로그인해 주세요.")
    st.page_link("run.py", label="메인 로그인 페이지로 이동", icon="🏠")
    st.stop()

col_t1, col_t2 = st.columns([4, 1])
with col_t1:
    st.title("🤖 3. 머신러닝 AI 자동 분류 및 데이터 오염 파급력 시뮬레이터")
with col_t2:
    st.write("")
    if st.button("🔄 공유 DB 새로고침", use_container_width=True):
        st.rerun()

st.markdown("현재 **학급 공유 DB**에 저장된 나뭇잎 데이터를 실시간 학습시켜 **새로운 나뭇잎의 종을 자동 예측**하고, **가짜 데이터 오염(Data Poisoning)**의 영향을 검증합니다.")

df = get_leaf_df()
fake_count = int(df['가짜여부'].sum())

if fake_count > 0:
    st.error(f"🚨 주의! 현재 학급 공유 DB에 **조작된 가짜 데이터(이상치) {fake_count}개**가 포함되어 있습니다! AI 모델의 결정 경계면이 왜곡될 수 있습니다.")
else:
    st.success(f"✅ 현재 학급 공유 DB(총 {len(df)}개)에 조작된 데이터가 없습니다. 깨끗한 데이터셋으로 AI 모델을 학습합니다.")

col_model, col_pred = st.columns([1, 1.2], gap="large")

with col_model:
    st.subheader("⚙️ 1단계: AI 분류 알고리즘 선택 및 학습")
    algo_name = st.radio(
        "머신러닝 알고리즘 선택",
        ["KNN (K-최근접 이웃 분류기)", "SVM (서포트 벡터 머신 - 결정 경계면)"],
        help="4차시 수학 시간에 찾은 '가상의 분류 경계면'과 가장 유사한 원리의 모델입니다."
    )

    X = df[['가로', '세로', '잎자루']].values
    y = df['종'].values

    if "KNN" in algo_name:
        k_val = st.slider("이웃 개수 (K)", min_value=1, max_value=9, value=3, step=2)
        model = KNeighborsClassifier(n_neighbors=k_val)
    else:
        c_val = st.slider("규제 강도 (C)", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
        model = SVC(C=c_val, kernel='rbf', probability=True, random_state=42)

    model.fit(X, y)

    clean_df = df[~df['가짜여부']]
    clean_acc = cross_val_score(model, clean_df[['가로', '세로', '잎자루']].values, clean_df['종'].values, cv=5).mean() * 100
    curr_acc = cross_val_score(model, X, y, cv=5).mean() * 100

    m1, m2 = st.columns(2)
    m1.metric("깨끗한 DB 교차검증 정확도", f"{clean_acc:.1f}%")
    delta_val = curr_acc - clean_acc
    m2.metric("현재 공유 DB 모델 정확도", f"{curr_acc:.1f}%", delta=f"{delta_val:.1f}%" if abs(delta_val) > 0.05 else "정상")

with col_pred:
    st.subheader("🌿 2단계: 새로운 나뭇잎 특징량 입력 및 종 예측")
    st.write("새로 채집한 나뭇잎의 가로, 세로, 잎자루 길이를 입력하여 AI의 예측 결과를 확인해 보세요.")

    in_w = st.number_input("가로 길이 (X, cm)", min_value=0.1, max_value=50.0, value=10.4, step=0.1)
    in_l = st.number_input("세로 길이 (Y, cm)", min_value=0.1, max_value=50.0, value=6.0, step=0.1)
    in_p = st.number_input("잎자루 길이 (Z, cm)", min_value=0.0, max_value=50.0, value=5.8, step=0.1)

    if st.button("🚀 AI 식물 종 자동 분류 실행", type="primary", use_container_width=True):
        sample = np.array([[in_w, in_l, in_p]])
        pred_species = model.predict(sample)[0]
        probs = model.predict_proba(sample)[0]
        classes = model.classes_

        prob_df = pd.DataFrame({'식물 종': classes, '예측 확률(%)': (probs * 100).round(1)}).sort_values(by='예측 확률(%)', ascending=False)
        top_conf = prob_df.iloc[0]['예측 확률(%)']

        if fake_count > 0:
            st.warning(f"⚠️ **예측 결과: {pred_species}** (신뢰도: {top_conf}%) — *주의: 공유 DB 내 가짜 데이터({fake_count}개)로 인해 분류 경계가 오염된 상태입니다!*")
        else:
            st.success(f"🎯 **예측 결과: {pred_species}** (신뢰도: {top_conf}%)")

        st.bar_chart(prob_df.set_index('식물 종'))
