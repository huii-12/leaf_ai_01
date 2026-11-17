# 🌱 AI 나뭇잎 분류 & 윤리 시뮬레이터 (Streamlit Cloud 배포용)

## 1. GitHub 업로드 시 주의사항 (사이드바 정상 출력)
- 압축을 푼 뒤 **상위 폴더를 한 번 더 감싸지 말고**, 아래 파일들이 GitHub 저장소의 **최상위(Root)**에 바로 보이도록 업로드하세요.
  - `run.py`
  - `db_utils.py`
  - `myproject.db`
  - `requirements.txt`
  - `.streamlit/config.toml`
  - `data/leaf_data.csv`
  - `pages/1_Data_Input.py`
  - `pages/2_3D_Outlier_Check.py`
  - `pages/3_AI_Classifier.py`
  - `pages/4_Ethics_Survey.py`
- Linux 기반 Streamlit Cloud에서 한글 파일명 인코딩 문제로 사이드바가 누락되지 않도록 `pages/` 내부 파일명을 영문으로 통일하고 `initial_sidebar_state="expanded"`를 적용했습니다.

## 2. 로컬 실행 방법
```bash
pip install -r requirements.txt
streamlit run run.py
```

## 3. 기본 계정 정보
- 아이디: `taehuie` / 비밀번호: `taehui`
