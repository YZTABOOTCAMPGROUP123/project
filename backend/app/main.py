"""
main.py — FastAPI giriş noktası.

Uç noktalar:
    GET  /health         -> sağlık kontrolü
    GET  /config         -> 3 dalın form konfigürasyonu (frontend tek kaynaktan besler)
    POST /analyze        -> skor + risk + 3 maddelik navigasyon raporu
    POST /certificate    -> skor>75 & risk düşükse PDF sertifika (application/pdf)

Mimari: ince bir HTTP katmanı. Tüm iş mantığı orchestrator/scorer/llm_client/pdf
modüllerinde; bu dosya sadece istekleri onlara yönlendirir.
"""

from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()  # .env -> ortam değişkenleri (OPENAI_API_KEY vb.)

from fastapi import APIRouter, FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import Response  # noqa: E402

from . import orchestrator, pdf  # noqa: E402
from .form_config import FORM_CONFIG, get_branch  # noqa: E402
from .schemas import AnalysisResponse, AnalyzeRequest  # noqa: E402


# Sertifikada gösterilecek veriliş tarihi (Sprint 1 sabiti; now() kullanmıyoruz).
ISSUED_DATE = "2026-07-05"

app = FastAPI(title="StartMetrics API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    # Prod'da (Vercel) frontend ve backend aynı domain -> CORS gerekmez ama
    # geliştirmede localhost, sunumda "*" ile serbest bırakıyoruz (PoC).
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tüm uç noktalar /api altında toplanır. Böylece hem lokal (Vite proxy /api'yi
# olduğu gibi iletir) hem Vercel (/api/* -> Python function) aynı yolu kullanır.
api = APIRouter(prefix="/api")


@api.get("/health")
def health():
    return {"ok": True}


@api.get("/config")
def config():
    """Frontend'in dinamik formu çizmesi için dal konfigürasyonu."""
    return {
        branch: {
            "title": cfg["title"],
            "funding_stage": cfg["funding_stage"],
            "fields": cfg["fields"],
        }
        for branch, cfg in FORM_CONFIG.items()
    }


@api.post("/analyze", response_model=AnalysisResponse)
def analyze(req: AnalyzeRequest):
    try:
        return orchestrator.analyze(req.branch, req.answers)
    except ValueError as exc:  # bilinmeyen dal vb.
        raise HTTPException(status_code=400, detail=str(exc))


@api.post("/certificate")
def certificate(req: AnalyzeRequest):
    """Analizi tekrar çalıştırıp uygunsa PDF döndürür (durumsuz)."""
    try:
        result = orchestrator.analyze(req.branch, req.answers)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not result.certificate_available:
        raise HTTPException(
            status_code=403,
            detail="Sertifika için Olgunluk Skoru 75 üstü ve risk düşük olmalı.",
        )

    branch_title = get_branch(req.branch)["title"]
    data = pdf.build_certificate(result, branch_title, ISSUED_DATE)
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=startmetrics_sertifika.pdf"},
    )


app.include_router(api)
