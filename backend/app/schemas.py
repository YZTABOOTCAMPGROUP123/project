"""
schemas.py — Pydantic request/response modelleri.

Edge doğrulaması burada yapılır (rubrikteki "girdi temizleme"nin bir parçası).
AnalysisResponse frontend ile aramızdaki kontrattır.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """Frontend'den gelen analiz isteği."""

    branch: str = Field(..., description="fikrim_var | startup_var | sirketim_var")
    # Serbest sözlük: form_config'e göre değişen alanlar. Orchestrator
    # bunları kanonik veri seti anahtarlarına eşleyip clamp'ler.
    answers: dict = Field(default_factory=dict)


class NavigationItem(BaseModel):
    """3 maddelik navigasyon raporunun tek bir maddesi."""

    title: str
    body: str


class AnalysisResponse(BaseModel):
    """Analiz sonucu — sol panel (skor) + sağ panel (rapor) + sertifika bayrağı."""

    maturity_score: int = Field(..., ge=0, le=100)
    risk_probability: float = Field(..., ge=0.0, le=1.0)
    risk_percent: int = Field(..., ge=0, le=100)
    risk_band: str
    drivers: list[str] = Field(default_factory=list)
    navigation_report: list[NavigationItem]
    certificate_available: bool
    # "llm" | "stub" — dürüstlük bayrağı; UI'da gösterilmez, teşhis içindir.
    report_source: str
