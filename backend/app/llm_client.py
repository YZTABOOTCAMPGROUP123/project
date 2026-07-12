"""
llm_client.py — AI Yön Raporu üretici (OpenAI + sağlayıcı-bağımsız + stub fallback).

Sorumluluk: skorlayıcının çıktısını ve ~8-10 alanı bir Türkçe mentor prompt'una
gömüp LLM'den TAM 3 maddelik Waze/GPS tarzı bir navigasyon raporu almak.

Token tasarrufu: prompt'a SADECE alanlar + skor girer; ASLA CSV satırı girmez.
max_tokens düşük tutulur, tıklama başına tek çağrı yapılır.

Dayanıklılık: API anahtarı yoksa VEYA çağrı/parse hatası olursa `_stub_report`
devreye girer — demo asla çökmez, UI birebir aynı görünür (report_source="stub").
"""

from __future__ import annotations

import json
import os

from .scorer import ScoreResult


SYSTEM_PROMPT = (
    "Sen bir girişim mentorusun — öğretmen değil, akıllı bir Waze/GPS "
    "navigasyonu gibisin. Sana verilen girişim verilerine ve bizim modelimizin "
    "ürettiği Olgunluk Skoru ile Risk yüzdesine bakarak, öğretmenlik taslamadan, "
    "girişimcinin önündeki riskleri ve yön önerilerini TAM 3 maddede yaz. "
    "Her madde en fazla 2 cümle olsun ve bir yol/rota metaforu içersin "
    "(örn. 'Önünde görünmez bir duvar var…', 'Bu virajda yavaşla…'). "
    "Genel motivasyon cümlesi KURMA; sadece bu veriye özel, somut, aksiyon "
    "alınabilir uyarılar ver. Yanıtı SADECE şu formatta bir JSON dizisi olarak "
    'döndür: [{"title": "...", "body": "..."}, ...] — tam 3 eleman, başka metin yok.'
)


def generate_report(branch: str, features: dict, result: ScoreResult) -> dict:
    """3 maddelik navigasyon raporu üretir.

    Returns:
        {"items": [{"title","body"} x3], "source": "llm" | "stub"}
    Bu fonksiyon hiçbir zaman exception fırlatmaz; hata durumunda stub'a düşer.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    api_key = (
        os.getenv("OPENAI_API_KEY")
        or os.getenv("ANTHROPIC_API_KEY")
        or os.getenv("GEMINI_API_KEY")
    )

    if not api_key:
        return _stub_report(result)

    try:
        user_prompt = _build_user_prompt(branch, features, result)
        if provider == "openai":
            text = _call_openai(user_prompt)
        elif provider == "anthropic":
            text = _call_anthropic(user_prompt)
        else:
            # Gemini vb. henüz eklenmedi -> güvenli stub
            return _stub_report(result)

        items = _parse_three_items(text)
        return {"items": items, "source": "llm"}
    except Exception:
        # Ağ/parse/kota — ne olursa olsun demo çalışsın.
        return _stub_report(result)


def _build_user_prompt(branch: str, features: dict, result: ScoreResult) -> str:
    """Prompt'a sadece askable alanlar + skor girer (CSV satırı ASLA)."""
    # Dahili yardımcı anahtarları (alt çizgiyle başlayan) prompt'a koyma.
    public = {k: v for k, v in features.items() if not k.startswith("_")}
    return (
        f"Dal: {branch}\n"
        f"Girişim verileri: {json.dumps(public, ensure_ascii=False)}\n"
        f"Olgunluk Skoru: {result.maturity_score}/100\n"
        f"Risk: %{round(result.risk_probability * 100)} ({result.risk_band})\n"
        f"Skorun sürücüleri (aynı gerekçeleri kullan): {result.drivers}\n"
        f"Bu verilere göre tam 3 maddelik navigasyon raporunu üret."
    )


def _call_openai(user_prompt: str) -> str:
    from openai import OpenAI

    client = OpenAI()  # OPENAI_API_KEY env'den okunur
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    resp = client.chat.completions.create(
        model=model,
        max_tokens=400,
        temperature=0.5,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return resp.choices[0].message.content or ""


def _call_anthropic(user_prompt: str) -> str:
    import anthropic

    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY env'den okunur
    model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")
    msg = client.messages.create(
        model=model,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")


def _parse_three_items(text: str) -> list[dict]:
    """LLM çıktısından tam 3 {title, body} maddesi çıkar."""
    # Model bazen ```json ... ``` sarabilir; en dıştaki diziyi yakala.
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("JSON dizisi bulunamadı")
    items = json.loads(text[start : end + 1])
    if not isinstance(items, list) or len(items) < 3:
        raise ValueError("En az 3 madde bekleniyordu")
    cleaned = []
    for it in items[:3]:
        cleaned.append(
            {
                "title": str(it.get("title", "Rota Uyarısı")),
                "body": str(it.get("body", "")).strip(),
            }
        )
    return cleaned


def _stub_report(result: ScoreResult) -> dict:
    """Anahtar/erişim yokken deterministik 3 maddelik rapor (drivers'tan)."""
    titles = ["Nakit Rotası", "Ekip Sağlığı", "Pazar Yönü"]
    drivers = result.drivers or ["Veriler dengeli, rotan şimdilik açık."]

    items: list[dict] = []
    for i in range(3):
        driver = drivers[i] if i < len(drivers) else None
        if driver:
            body = f"Akıllı radar uyarısı : {driver}. Bu sinyali önümüzdeki 2 haftada ele al."
        else:
            body = "Rota temiz görünüyor; bir sonraki 5 müşteri görüşmeni planla."
        items.append({"title": titles[i], "body": body})

    return {"items": items, "source": "stub"}
