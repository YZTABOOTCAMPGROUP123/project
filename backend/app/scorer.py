"""
scorer.py — BİZİM deterministik analitik modelimiz (Sprint 1).

Bu modül StartMetrics'in "kendi modeli"dir: kural tabanlı, tam deterministik,
saf fonksiyon (I/O yok, ağ yok, LLM yok). Aynı girdi her zaman aynı çıktıyı
verir; "güvenilir/tutarlı Olgunluk Skoru" savunmasının teknik temeli budur.

Ağırlıklar veri setinin ilk 10 satırından ve doğrulanmış korelasyonlardan
türetilmiştir (tam CSV EĞİTİLMEZ). Shutdown_Probability'ye karşı örneklem
korelasyonları:
    Runway_Months_Remaining     r = -0.51
    Cofounder_Conflict_Score    r = +0.52
    Product_Market_Fit_Score    r = -0.50
    Weekly_Work_Hours           r = +0.39

ARAYÜZ DONDURULMUŞTUR: `score(features) -> ScoreResult`.
Sprint 2'de gerçek ML modeli (XGBoost/LightGBM) sadece bu fonksiyonun GÖVDESİNİ
değiştirir; imza, orchestrator, şema ve frontend aynen kalır.
"""

from __future__ import annotations

from dataclasses import dataclass, field


# Dal başına olgunluk taban ofseti: erken aşama girişim gelir yok diye
# haksız cezalandırılmasın (Pre-Seed'den henüz traction beklemiyoruz).
BRANCH_OFFSET = {
    "Pre-Seed": 6,
    "Seed": 2,
    "Bootstrapped": 0,
    "Series A": 0,
}


@dataclass
class ScoreResult:
    """Skorlayıcının çıktısı. UI ve LLM zemini bu nesneyi tüketir."""

    maturity_score: int          # 0-100 Olgunluk/Sağlık Skoru
    risk_probability: float      # 0-1 Kapanma/Batma olasılığı
    risk_band: str               # "Düşük" | "Orta" | "Yüksek"
    drivers: list[str] = field(default_factory=list)  # insan-okur gerekçeler


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def score(features: dict) -> ScoreResult:
    """Askable feature'lardan Olgunluk Skoru ve Risk olasılığı üretir.

    Args:
        features: kanonik veri seti anahtarlarıyla temizlenmiş girdi sözlüğü
            (orchestrator._clean tarafından hazırlanır). Eksik alanlar için
            nötr varsayılanlar kullanılır.

    Returns:
        ScoreResult: maturity_score, risk_probability, risk_band, drivers.
    """
    funding_stage = features.get("Funding_Stage", "Seed")

    maturity = 50.0 + BRANCH_OFFSET.get(funding_stage, 0)
    risk = 0.15
    drivers: list[str] = []

    # --- Ürün-Pazar Uyumu (PMF): en güçlü çift-yönlü sürücü ---
    pmf = _num(features.get("Product_Market_Fit_Score"), 5)
    maturity += (pmf - 5) * 4
    if pmf < 4:
        risk += 0.20
        drivers.append("PMF düşük — pazar uyumu henüz zayıf")
    elif pmf >= 8:
        risk -= 0.15
        drivers.append(f"PMF {pmf:.0f}/10 güçlü — pazar sinyali sağlam")

    # --- Nakit ömrü (Runway): batmanın en net habercisi ---
    runway = _num(features.get("Runway_Months_Remaining"), 12)
    if runway < 3:
        maturity -= 20
        risk += 0.40
        drivers.append(f"Runway {runway:.0f} ay — acil nakit riski")
    elif runway < 6:
        maturity -= 12
        risk += 0.25
        drivers.append(f"Runway {runway:.0f} ay — kritik seviye")
    elif runway > 12:
        maturity += 12
        drivers.append(f"Runway {runway:.0f} ay — güçlü nakit tamponu")
    if runway > 18:
        risk -= 0.10

    # --- Ortak çatışması: yumuşak eşikli ceza ---
    conflict = _num(features.get("Cofounder_Conflict_Score"), 3)
    risk += max(0.0, conflict - 4) * 0.05
    if conflict >= 6:
        drivers.append(f"Ortak çatışması {conflict:.0f}/10 — yüksek gerilim")

    # --- Aşırı çalışma / tükenmişlik proxy'si ---
    work_hours = _num(features.get("Weekly_Work_Hours"), 45)
    if work_hours > 65:
        risk += 0.15
        drivers.append(f"Haftalık {work_hours:.0f} saat — tükenmişlik riski")

    # --- Gelir büyümesi ---
    growth = _num(features.get("Monthly_Revenue_Growth_Percent"), 0)
    maturity += _clamp(growth, -15, 25) * 0.6
    if growth < 0:
        risk += 0.10
        drivers.append(f"Aylık gelir büyümesi %{growth:.0f} — negatif trend")

    # --- Yatırımcı baskısı ---
    pressure = _num(features.get("Investor_Pressure_Score"), 5)
    risk += max(0.0, pressure - 6) * 0.03

    # --- Çalışan devir oranı ---
    turnover = _num(features.get("Employee_Turnover_Percent"), 20)
    maturity -= max(0.0, turnover - 20) * 0.3
    if turnover > 45:
        drivers.append(f"Çalışan devri %{turnover:.0f} — ekip istikrarsız")

    # --- Kurucu tecrübesi ---
    experience = _num(features.get("Founder_Experience_Years"), 0)
    maturity += min(experience, 10) * 1.0

    # --- İş-yaşam dengesi ---
    wlb = _num(features.get("Work_Life_Balance_Score"), 5)
    maturity += (wlb - 5) * 1.5

    # --- Normalize & bandla ---
    maturity_score = int(_clamp(round(maturity), 0, 100))
    # Taban risk %1: hiçbir girişim %0 riskli değildir; ayrıca "%0" ekranda
    # bozuk/güvenilmez görünür. Üst sınır %99, alt sınır %1.
    risk_probability = round(_clamp(risk, 0.01, 0.99), 2)

    if risk_probability < 0.34:
        risk_band = "Düşük"
    elif risk_probability < 0.67:
        risk_band = "Orta"
    else:
        risk_band = "Yüksek"

    if not drivers:
        drivers.append("Girdiler dengeli — belirgin bir kritik sinyal yok")

    return ScoreResult(
        maturity_score=maturity_score,
        risk_probability=risk_probability,
        risk_band=risk_band,
        drivers=drivers,
    )


def _num(value, default: float) -> float:
    """Girdiyi float'a çevir; boş/None/hatalıysa nötr varsayılana düş."""
    if value is None or value == "":
        return float(default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)
