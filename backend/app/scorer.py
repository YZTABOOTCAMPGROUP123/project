"""
scorer.py — StartMetrics Hibrit Analitik ve ML Model Motoru (Sprint 1 + Sprint 2).

ARAYÜZ DONDURULMUŞTUR: `score(features) -> ScoreResult`.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
import joblib

# Dal başına olgunluk taban ofseti
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
    drivers: list[str] = field(default_factory=list)  # İnsan-okur gerekçeler


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _num(value, default: float) -> float:
    if value is None or value == "":
        return float(default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


# =================================================================
# ⚙️ MODEL ENTEGRASYON KATMANI (DİNAMİK PATH & DEBUG KATMANI)
# =================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENCODER_PATH = os.path.join(BASE_DIR, "encoders.pkl")

# Vercel'in sys.path dizinine geçerli klasörü açıkça enjekte ediyoruz
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

INIT_ERROR = None
try:
    # Tüm alternatif import kombinasyonlarını deniyoruz
    try:
        import model_logic as ml_logic
    except ImportError:
        try:
            import app.model_logic as ml_logic
        except ImportError:
            import backend.app.model_logic as ml_logic

    label_encoders = joblib.load(ENCODER_PATH)
    
    MODEL_FEATURES = [
        'Founder_Type', 'Economic_Climate', 'Founder_Age', 'Founder_Experience_Years', 
        'Industry', 'Funding_Stage', 'Work_Mode', 'Team_Size', 'Startup_Age_Months', 
        'Weekly_Work_Hours', 'Sleep_Hours', 'Exercise_Days_Per_Week', 'Vacation_Days_Taken', 
        'Investor_Pressure_Score', 'Cofounder_Conflict_Score', 'Stress_Score', 
        'Decision_Fatigue_Score', 'Monthly_Revenue_Growth_Percent', 'Runway_Months_Remaining', 
        'Product_Market_Fit_Score', 'Employee_Turnover_Percent', 'Work_Life_Balance_Score', 
        'Seeks_Mental_Health_Support'
    ]
    USE_ML = True
except Exception as e:
    USE_ML = False
    INIT_ERROR = str(e)


def score(features: dict) -> ScoreResult:
    """Askable feature'lardan Olgunluk Skoru ve Risk olasılığı üretir."""
    
    # -----------------------------------------------------------------
    # [DURUM A] GEÇERLİ BİR ML MODELİ VARSA (Sprint 2 Akışı)
    # -----------------------------------------------------------------
    if USE_ML:
        try:
            input_row = []
            for col in MODEL_FEATURES:
                raw_val = features.get(col, None)
                
                if col in label_encoders:
                    le = label_encoders[col]
                    val_str = str(raw_val) if raw_val is not None else "Seed"
                    if val_str in le.classes_:
                        input_row.append(le.transform([val_str])[0])
                    else:
                        input_row.append(0)
                else:
                    input_row.append(_num(raw_val, 0.0))

            # m2cgen çıktısı lokal testte iki elemanlı liste döndü: [Class_0, Class_1]
            res = ml_logic.score(input_row)
            if isinstance(res, (list, tuple)):
                risk_probability = float(res[1])  # Sınıf 1: Batma Olasılığı
            else:
                risk_probability = float(res)

            risk_probability = round(_clamp(risk_probability, 0.01, 0.99), 2)
            maturity_score = int(_clamp(round((1.0 - risk_probability) * 100), 0, 100))

            if risk_probability < 0.34:
                risk_band = "Düşük"
            elif risk_probability < 0.67:
                risk_band = "Orta"
            else:
                risk_band = "Yüksek"

            return ScoreResult(
                maturity_score=maturity_score,
                risk_probability=risk_probability,
                risk_band=risk_band,
                drivers=[
                    "[ML MODELİ] Tahmin örüntüleri başarıyla işlendi.",
                    "Model Ayırt Ediciliği (ROC-AUC): %93.05 genellenebilirlik odaklı."
                ],
            )
        except Exception as runtime_error:
            # Çalışma anında bir hata olursa bunu yakalayıp aşağıda göstereceğiz
            INIT_ERROR = f"Runtime Hatası: {runtime_error}"

    # -----------------------------------------------------------------
    # [DURUM B] ML MODELİ YOKSA VEYA HATA ALDIYSA (Sprint 1 Fallback Akışı)
    # -----------------------------------------------------------------
    funding_stage = features.get("Funding_Stage", "Seed")
    maturity = 50.0 + BRANCH_OFFSET.get(funding_stage, 0)
    risk = 0.15
    drivers: list[str] = []

    # --- Ürün-Pazar Uyumu (PMF) ---
    pmf = _num(features.get("Product_Market_Fit_Score"), 5)
    maturity += (pmf - 5) * 4
    if pmf < 4:
        risk += 0.20
        drivers.append("PMF düşük — pazar uyumu henüz zayıf")
    elif pmf >= 8:
        risk -= 0.15
        drivers.append(f"PMF {pmf:.0f}/10 güçlü — pazar sinyali sağlam")

    # --- Nakit ömrü (Runway) ---
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

    # --- Ortak çatışması ---
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
    risk_probability = round(_clamp(risk, 0.01, 0.99), 2)

    if risk_probability < 0.34:
        risk_band = "Düşük"
    elif risk_probability < 0.67:
        risk_band = "Orta"
    else:
        risk_band = "Yüksek"

    # Eğer arka planda bir import veya runtime hatası yakaladıysak ekranda göster
    if INIT_ERROR:
        drivers.append(f"🚨 ML Sinyal Hatası: {INIT_ERROR}")
    elif not drivers:
        drivers.append("Girdiler dengeli — belirgin bir kritik sinyal yok")

    return ScoreResult(
        maturity_score=maturity_score,
        risk_probability=risk_probability,
        risk_band=risk_band,
        drivers=drivers,
    )