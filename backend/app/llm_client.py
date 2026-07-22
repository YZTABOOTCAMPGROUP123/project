"""
llm_client.py — AI Yön Raporu üretici (sağlayıcı-bağımsız + stub fallback).

Sorumluluk: skorlayıcının çıktısını ve ~8-10 alanı bir Türkçe mentor prompt'una
gömüp LLM'den TAM 3 maddelik Waze/GPS tarzı bir navigasyon raporu almak.

Sağlayıcı seçimi: LLM_PROVIDER ortam değişkeni ile yapılır
(openai | anthropic | gemini | openrouter). Varsayılan: openai.

Token tasarrufu: prompt'a SADECE alanlar + skor girer; ASLA CSV satırı girmez.
max_tokens düşük tutulur, tıklama başına tek çağrı yapılır.

Dayanıklılık: seçili sağlayıcının API anahtarı yoksa VEYA çağrı/parse hatası
olursa `_stub_report` devreye girer — demo asla çökmez, UI birebir aynı
görünür (report_source="stub").

NOT: google-genai / anthropic / openai gibi sağlayıcı SDK'ları burada
FONKSİYON İÇİNDE import edilir (üst seviyede değil). Bunun nedeni: sadece
kullandığın sağlayıcının paketinin requirements.txt'de olması yeterli olsun;
diğer paketler kurulu olmasa bile modül import edilirken patlamasın.
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
    "alınabilir uyarılar ver. Yanıtın kesinlikle TÜRKÇE olmalıdır. "
    "Yanıtı SADECE şu formatta bir JSON dizisi olarak "
    'döndür: [{"title": "...", "body": "..."}, ...] — tam 3 eleman, başka metin yok.'
)

COMPREHENSIVE_SYSTEM_PROMPT = (
    "Sen StartMetrics platformunun strateji danışmanısın. Bir girişimcinin 4 aşamalık "
    "analiz sürecinden elde edilen verilere bakarak kapsamlı, kişiselleştirilmiş ve "
    "uygulanabilir bir stratejik yol haritası raporu yazacaksın. "
    "Rapor Türkçe olacak. Markdown formatında olacak (## başlıklar, - madde işaretleri). "
    "Şu bölümleri içermelidir: "
    "## 🎯 Genel Değerlendirme (2-3 cümle özet), "
    "## 💡 Kritik Bulgular (en önemli 3-5 tespit), "
    "## 🗺️ 30 Günlük Eylem Planı (somut adımlar), "
    "## 🚀 90 Günlük Büyüme Rotası (stratejik yönelim), "
    "## ⚠️ Öncelikli Riskler ve Çözüm Önerileri. "
    "Genel tavsiyeler değil, VERİLERE ÖZGÜ, uygulanabilir öneriler ver. "
    "Motivasyon konuşması yapma."
)

# Sağlayıcı adı -> o sağlayıcının API anahtarını tuttuğu ortam değişkeni
_PROVIDER_KEY_ENV = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}


def _active_provider_and_key() -> tuple[str, str | None]:
    """LLM_PROVIDER ortam değişkenine göre aktif sağlayıcıyı ve anahtarını döndürür."""
    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
    if provider not in _PROVIDER_KEY_ENV:
        # Bilinmeyen bir değer yazılmışsa openai'ye düş (ama uyar).
        print(f"Bilinmeyen LLM_PROVIDER='{provider}', 'openai' varsayılana dönülüyor.", flush=True)
        provider = "openai"
    api_key = os.getenv(_PROVIDER_KEY_ENV[provider])
    return provider, api_key


def _dispatch_call(
    provider: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
) -> str:
    """Aktif sağlayıcıya göre doğru _call_* fonksiyonunu çağırır."""
    if provider == "openai":
        return _call_openai(system_prompt, user_prompt, max_tokens, temperature)
    if provider == "anthropic":
        return _call_anthropic(system_prompt, user_prompt, max_tokens, temperature)
    if provider == "gemini":
        return _call_gemini(system_prompt, user_prompt, max_tokens, temperature)
    if provider == "openrouter":
        return _call_openrouter(system_prompt, user_prompt, max_tokens, temperature)
    raise ValueError(f"Desteklenmeyen LLM_PROVIDER: {provider}")


def generate_report(branch: str, features: dict, result: ScoreResult) -> dict:
    """3 maddelik navigasyon raporu üretir.

    Returns:
        {"items": [{"title","body"} x3], "source": "llm" | "stub"}
    Bu fonksiyon hiçbir zaman exception fırlatmaz; hata durumunda stub'a düşer.
    """
    provider, api_key = _active_provider_and_key()

    if not api_key:
        print(f"'{provider}' için API anahtarı bulunamadı, stub rapora düşülüyor.", flush=True)
        return _stub_report(result)

    try:
        user_prompt = _build_user_prompt(branch, features, result)
        text = _dispatch_call(provider, SYSTEM_PROMPT, user_prompt, max_tokens=400, temperature=0.5)

        items = _parse_three_items(text)
        return {"items": items, "source": "llm"}

    except Exception as e:
        print(f"generate_report LLM API Hatası ({provider}): {e}", flush=True)
        fallback = _stub_report(result)
        fallback["items"][0]["body"] = f"🔴 API HATASI: {e} | " + fallback["items"][0]["body"]
        return fallback


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


def _call_openai(system_prompt: str, user_prompt: str, max_tokens: int, temperature: float) -> str:
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    resp = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return resp.choices[0].message.content or ""


def _call_anthropic(system_prompt: str, user_prompt: str, max_tokens: int, temperature: float) -> str:
    import anthropic

    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY env'den okunur
    model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")


def _call_gemini(system_prompt: str, user_prompt: str, max_tokens: int, temperature: float) -> str:
    from google import genai
    from google.genai import types

    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    resp = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system_prompt,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return resp.text or ""


def _call_openrouter(system_prompt: str, user_prompt: str, max_tokens: int, temperature: float) -> str:
    from openai import OpenAI

    api_key = os.getenv("OPENROUTER_API_KEY")
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")
    resp = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return resp.choices[0].message.content or ""


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


# ===========================================================================
# Kapsamlı Yol Haritası Raporu (Adım 5) — tüm metodoloji verileri birleşik
# ===========================================================================


def generate_comprehensive_report(
    branch: str,
    step1_answers: dict,
    methodology1_answers: dict,
    methodology2_answers: dict,
    score_result: ScoreResult,
) -> dict:
    """Tüm adımların verisini birleştirerek kapsamlı AI yol haritası üretir.

    Returns:
        {"roadmap": "<markdown metin>", "source": "llm" | "stub"}
    Bu fonksiyon hiçbir zaman exception fırlatmaz; hata durumunda stub'a düşer.
    """
    provider, api_key = _active_provider_and_key()

    if not api_key:
        print(f"'{provider}' için API anahtarı bulunamadı, stub rapora düşülüyor.", flush=True)
        return _stub_comprehensive_report(score_result)

    try:
        user_prompt = _build_comprehensive_prompt(
            branch, step1_answers, methodology1_answers, methodology2_answers, score_result
        )
        text = _dispatch_call(
            provider, COMPREHENSIVE_SYSTEM_PROMPT, user_prompt, max_tokens=1500, temperature=0.6
        )

        return {"roadmap": text.strip(), "source": "llm"}
    except Exception as e:
        print(f"generate_comprehensive_report LLM API Hatası ({provider}): {e}", flush=True)
        fallback = _stub_comprehensive_report(score_result)
        fallback["roadmap"] = (
            f"### 🔴 Sistem Hatası (Lütfen Bunu Okuyun)\n**LLM API şu hatayı verdi:** `{e}`\n\n---\n\n"
            + fallback["roadmap"]
        )
        return fallback


def _build_comprehensive_prompt(
    branch: str,
    step1: dict,
    metho1: dict,
    metho2: dict,
    result: ScoreResult,
) -> str:
    """Tüm adımların verilerini tek bir prompt'ta birleştirir."""
    # Dahili anahtarları filtrele
    public_step1 = {k: v for k, v in step1.items() if not k.startswith("_")}

    branch_labels = {
        "fikrim_var": "Fikrim Var (Pre-Seed)",
        "startup_var": "Startup'ım Var (Seed)",
        "sirketim_var": "Şirketim Var (Bootstrapped)",
    }

    return (
        f"Kategori: {branch_labels.get(branch, branch)}\n\n"
        f"=== ADIM 1: Kullanıcı Profili ===\n{json.dumps(public_step1, ensure_ascii=False, indent=2)}\n\n"
        f"=== ML ANALİZ SONUCU ===\n"
        f"Olgunluk Skoru: {result.maturity_score}/100\n"
        f"Risk: %{round(result.risk_probability * 100)} ({result.risk_band})\n"
        f"Temel Sinyaller: {', '.join(result.drivers)}\n\n"
        f"=== ADIM 3: Metodoloji Formu-1 ===\n{json.dumps(metho1, ensure_ascii=False, indent=2)}\n\n"
        f"=== ADIM 4: Metodoloji Formu-2 ===\n{json.dumps(metho2, ensure_ascii=False, indent=2)}\n\n"
        f"Yukarıdaki tüm verileri analiz ederek kapsamlı stratejik yol haritası raporunu yaz."
    )


def _stub_comprehensive_report(result: ScoreResult) -> dict:
    """API anahtarı yokken deterministik yol haritası raporu."""
    score = result.maturity_score
    band = result.risk_band
    drivers_text = "\n".join(f"- {d}" for d in result.drivers) if result.drivers else "- Belirgin sinyal yok."

    roadmap = f"""## 🎯 Genel Değerlendirme

Girişiminizin Olgunluk Skoru **{score}/100** olarak hesaplanmıştır. Risk bandı **{band}** seviyesindedir. Bu rapor, girişiminizin mevcut durumunu özetlemekte ve öncelikli aksiyon adımlarını içermektedir.

## 💡 Kritik Bulgular

{drivers_text}

## 🗺️ 30 Günlük Eylem Planı

- **Hafta 1-2:** Temel riskleri önceliklendirin ve hızlı kazanımlar için fırsatları belirleyin.
- **Hafta 3-4:** Müşteri doğrulama süreçlerini güçlendirin ve geri bildirim döngüsü kurun.
- Metodoloji formlarınızda belirttiğiniz varsayımları en az 5 gerçek müşteri görüşmesiyle test edin.

## 🚀 90 Günlük Büyüme Rotası

- **Ay 1:** Ürün-pazar uyumunu doğrulayacak minimum ölçülebilir deney tasarlayın.
- **Ay 2:** İlk 10 sadık kullanıcıyı kazanın ve onların geri bildirimlerini ürüne yansıtın.
- **Ay 3:** Büyüme kanallarınızı test edin ve en düşük maliyetli kanalı ölçeklendirin.

## ⚠️ Öncelikli Riskler ve Çözüm Önerileri

- **Risk:** Pazar doğrulaması henüz tamamlanmamış olabilir. **Çözüm:** Ödeme yapan ilk müşteri veya LOI (İlgi Mektubu) almadan kaynak harcamayı minimumda tutun.
- **Risk:** Ekip kapasitesi sınırlı. **Çözüm:** Kritik olmayan görevleri erteleyerek tek bir önceliğe odaklanın.

---
*Bu rapor otomatik olarak oluşturulmuştur. Kapsamlı AI analizi için geçerli bir API anahtarı yapılandırın.*
"""
    return {"roadmap": roadmap, "source": "stub"}
