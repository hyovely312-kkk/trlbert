# KoTRL v4.0 GitHub 업데이트 초보자 가이드

## 1. 이번 HTML에서 바뀐 점

이번 파일은 `kotrl_v4_api_ready.html`입니다.

핵심 변경사항은 아래와 같습니다.

1. **HTML은 모델이 아니라 화면/인터페이스로 분리**했습니다.
2. TRL 판정은 우선 `FastAPI` 백엔드 모델 API를 호출합니다.
3. 백엔드 서버가 없거나 꺼져 있으면 HTML 내부의 로컬 `evidence guardrail` 판정으로 fallback합니다.
4. 기술분류는 기존 방향대로 `분류표 기반 로컬 consensus` 방식으로 유지했습니다.
5. 결과 JSON/CSV에 `engine`, `model_version`, `fallback_used`, `api_endpoint`를 넣어 모델 판정인지 로컬 판정인지 구분되게 했습니다.
6. 사람이 검토한 TRL 보정값을 저장하고 CSV로 내려받을 수 있게 했습니다.

---

## 2. GitHub Pages에 올릴 때 가장 쉬운 방법

### Step 1. 파일명 바꾸기

GitHub Pages에서 바로 첫 화면으로 보이게 하려면 파일명을 아래처럼 바꾸세요.

```text
kotrl_v4_api_ready.html → index.html
```

즉, GitHub 저장소에는 최종적으로 `index.html`이라는 파일이 있어야 합니다.

---

### Step 2. GitHub 저장소에 업로드

1. GitHub 접속
2. 본인 저장소 들어가기
3. `Add file` 클릭
4. `Upload files` 클릭
5. `index.html` 파일 드래그해서 올리기
6. 아래 Commit message에 다음처럼 입력

```text
Update KoTRL v4 API-ready HTML
```

7. `Commit changes` 클릭

---

### Step 3. GitHub Pages 설정 확인

1. 저장소 상단 `Settings` 클릭
2. 왼쪽 메뉴에서 `Pages` 클릭
3. `Build and deployment`에서 다음처럼 설정

```text
Source: Deploy from a branch
Branch: main
Folder: /root
```

4. 저장 후 1~3분 기다리기
5. Pages URL 접속

---

## 3. 중요한 제한사항

GitHub Pages는 정적 HTML만 실행합니다.

즉, 아래는 가능합니다.

```text
HTML 화면 표시
입력값 작성
로컬 fallback TRL 판정
로컬 기술분류
JSON/CSV 다운로드
```

하지만 아래는 GitHub Pages만으로는 안 됩니다.

```text
Python FastAPI 서버 실행
학습된 TRL-BERT 모델 직접 로드
joblib / pytorch 모델 추론
```

그래서 GitHub Pages에 올리면 기본적으로 `Local Fallback`으로 작동합니다.

실제 학습모델을 연결하려면 별도 백엔드 서버가 필요합니다.

---

## 4. 로컬에서 FastAPI 백엔드까지 테스트하는 방법

### Step 1. 폴더 만들기

```bash
mkdir kotrl_backend
cd kotrl_backend
```

### Step 2. 필요한 패키지 설치

```bash
pip install fastapi uvicorn pydantic numpy scikit-learn joblib
```

### Step 3. `app.py` 만들기

아래 예시는 실제 학습모델이 없는 상태에서도 API 연결 테스트가 되도록 만든 샘플입니다.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="KoTRL Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TRLRequest(BaseModel):
    tech_name: str = ""
    overview: str = ""
    goal: str = ""
    core_tech: str = ""
    application: str = ""
    validation: str = ""
    business: str = ""
    source: str = ""
    strict_mode: str = "balanced"

@app.post("/api/v1/trl/predict")
def predict(req: TRLRequest):
    text = "\n".join([
        req.tech_name,
        req.overview,
        req.goal,
        req.core_tech,
        req.application,
        req.validation,
        req.business,
    ])

    # 샘플 로직: 실제 배포 시 이 부분을 학습모델 추론으로 교체
    if any(k in text for k in ["현장실증", "운용", "상용화", "납품", "양산"]):
        cls = "High"
        proba = {"Low": 0.05, "Mid": 0.25, "High": 0.70}
    elif any(k in text for k in ["시제품", "검증", "테스트베드", "프로토타입"]):
        cls = "Mid"
        proba = {"Low": 0.15, "Mid": 0.70, "High": 0.15}
    else:
        cls = "Low"
        proba = {"Low": 0.70, "Mid": 0.25, "High": 0.05}

    return {
        "engine": "trlbert_backend_sample",
        "model_name": "sample-api-not-real-trained-model",
        "model_version": "sample-v0",
        "predicted_class": cls,
        "predicted_label": f"{cls} · TRL {'1-3' if cls == 'Low' else '4-6' if cls == 'Mid' else '7-9'}",
        "confidence": proba[cls],
        "class_proba": proba,
        "estimated_trl": 5 if cls == "Mid" else 2 if cls == "Low" else 7,
        "evidence_sentences": ["API 연결 테스트용 샘플 결과입니다."],
        "flags": ["실제 학습모델이 아니라 API 연결 테스트용 샘플입니다."],
    }
```

### Step 4. 서버 실행

```bash
uvicorn app:app --reload --port 8000
```

브라우저에서 아래 주소가 열리면 성공입니다.

```text
http://127.0.0.1:8000/docs
```

---

## 5. HTML에서 API 연결 확인

1. `index.html`을 더블클릭해서 브라우저로 엽니다.
2. 2페이지 TRL 판정 화면으로 이동합니다.
3. API Endpoint가 아래인지 확인합니다.

```text
http://127.0.0.1:8000/api/v1/trl/predict
```

4. `TRL 모델/API 판정 실행` 클릭
5. 결과에 `Backend API`가 뜨면 API 연결 성공입니다.
6. `Local Fallback`이 뜨면 백엔드 연결이 실패한 것입니다.

---

## 6. 실제 학습모델을 붙일 때 교체해야 하는 부분

FastAPI의 `predict()` 함수 안에서 샘플 if문을 제거하고, 아래 구조로 바꾸면 됩니다.

```python
# 예시
X = vectorizer.transform([text])
proba = model.predict_proba(X)[0]
```

또는 BERT 계열이면 아래 구조입니다.

```python
# 예시
inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
outputs = model(**inputs)
proba = torch.softmax(outputs.logits, dim=-1).detach().numpy()[0]
```

중요한 점은 HTML이 받는 JSON 형식을 유지해야 한다는 것입니다.

필수 반환값은 아래입니다.

```json
{
  "predicted_class": "Mid",
  "predicted_label": "Mid · TRL 4-6",
  "confidence": 0.72,
  "class_proba": {
    "Low": 0.12,
    "Mid": 0.72,
    "High": 0.16
  },
  "evidence_sentences": [],
  "flags": []
}
```

---

## 7. 초보자용 최종 체크리스트

- [ ] 파일명을 `index.html`로 바꿨는가?
- [ ] GitHub 저장소 루트 폴더에 올렸는가?
- [ ] GitHub Pages가 `main` branch, `/root`로 설정되어 있는가?
- [ ] 접속 후 화면이 뜨는가?
- [ ] TRL 판정 결과에 `Local Fallback`이 뜨는가? 그러면 GitHub Pages 시연은 정상입니다.
- [ ] 실제 모델 API를 연결하려면 FastAPI 서버를 별도로 실행했는가?
- [ ] API 연결 성공 시 결과에 `Backend API`가 뜨는가?

---

## 8. 논문/특허/보고서에서의 정확한 표현

권장 표현:

```text
본 시스템은 TRL 학습모델 API와 연동 가능한 웹 기반 TRL 예비진단 인터페이스이며, API 미연결 시 rule-based evidence guardrail을 통해 fallback 판정을 제공한다.
```

피해야 할 표현:

```text
이 HTML 자체가 TRL-BERT 모델이다.
```

정확히는 HTML은 화면이고, 모델은 백엔드에서 실행됩니다.
