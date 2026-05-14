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

    # 샘플 로직입니다. 실제 배포 시 이 부분을 joblib / PyTorch 모델 추론으로 교체하세요.
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
