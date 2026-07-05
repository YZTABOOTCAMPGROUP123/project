# StartMetrics — Girişim Sağlık & Risk Navigasyonu

> YZTA Bootcamp 2026 · Sprint 1 · Çalışan Konsept Kanıtı (PoC)

Girişimcilerin (**Fikrim Var / Startup'ım Var / Şirketim Var**) sağlık ve batma
riskini, onları 20 sayfalık iş planlarıyla boğmadan tek sayfalık dinamik bir
formla ölçen ve akıllı bir **"Waze / GPS"** gibi yön veren analiz motoru.

**Akış:** Dal seç → ~8-10 kritik soruyu doldur → **Analiz Et** → solda 0-100
**Olgunluk Skoru** + Risk %, sağda **3 maddelik AI Navigasyon Raporu** → skor > 75
ve risk düşükse **PDF Sertifika** indir. Süreç burada biter.

---

## Mimari (Hibrit AI)

```
[Kullanıcı Form Verisi]
          │
          ▼
┌──────────────────────────────┐
│   ORKESTRASYON KATMANI        │  orchestrator.py  (temizler + dağıtır)
└───────────┬──────────────────┘
     ┌──────┴───────┐
     ▼              ▼
┌──────────┐  ┌──────────────┐
│ BİZİM     │  │  HAZIR LLM   │
│ MODELİMİZ │  │  API (OpenAI)│
│ scorer.py │  │ llm_client.py│
│(deterministik)│ (mentor raporu)│
└─────┬────┘  └──────┬───────┘
      └──────┬───────┘
             ▼
 [Olgunluk Skoru + Risk %  +  3 maddelik rapor  +  PDF Sertifika]
```

- **`scorer.py` (bizim modelimiz):** Kural tabanlı, **tam deterministik** skorlayıcı.
  Aynı girdi → aynı skor. "Güvenilir/tutarlı Olgunluk Skoru"nun teknik temeli.
  Ağırlıklar veri setinin ilk 10 satırından ve doğrulanmış korelasyonlardan
  türetildi (tam CSV **eğitilmedi**).
- **`orchestrator.py` (ekstra puan katmanı):** Girdiyi temizler, skorlar, LLM
  prompt'unu kurar, raporu birleştirir.
- **`llm_client.py`:** OpenAI ile 3 maddelik Türkçe mentor raporu. **Anahtar
  yoksa** kural tabanlı stub rapora düşer → demo asla çökmez.

**Hibrit dağılım (hedef vizyon):** ~%60 LLM / %40 kendi modelimiz. Sprint 1'de
raporu LLM üretir; skorlayıcı %100 bizim kodumuzdur. **Sprint 2'de** `scorer.py`
gövdesi gerçek bir ML modeliyle (XGBoost/LightGBM) değişir — arayüz
(`score(features) -> ScoreResult`) sabit kaldığı için orchestrator/şema/frontend
**hiç değişmez.**

---

## Teknoloji Yığını

| Katman | Teknoloji |
|---|---|
| Backend | Python · FastAPI · Pydantic · Uvicorn |
| Skorlayıcı | Saf Python (kural tabanlı, deterministik) |
| LLM | OpenAI (sağlayıcı-bağımsız; `LLM_PROVIDER` ile Anthropic'e de geçer) |
| PDF | fpdf2 + gömülü DejaVuSans (Unicode / tam Türkçe karakter desteği) |
| Frontend | Vite · React · TypeScript |
| UI/Tema | "Mercury Trust" indigo paleti · açık + koyu tema |
| Animasyon | Framer Motion (geçişler, gauge sayaç) · tsParticles (koyu hero partikül-ağı) |

---

## Kurulum & Çalıştırma

### 1) Backend (Terminal 1)

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows PowerShell
pip install -r requirements.txt
copy .env.example .env              # OPENAI_API_KEY doldur (opsiyonel)
uvicorn app.main:app --reload --port 8000
```

> `.env`'de anahtar boşsa uygulama yine çalışır: **stub** rapor devreye girer.

Kontrol: <http://localhost:8000/health> → `{"ok": true}`
API dokümanı (otomatik): <http://localhost:8000/docs>

### 2) Frontend (Terminal 2)

```powershell
cd frontend
npm install
npm run dev                         # http://localhost:5173
```

Tarayıcıda <http://localhost:5173> aç. Frontend `/api/*` isteklerini Vite proxy
ile backend'e (`:8000`) yönlendirir.

---

## API Uç Noktaları

| Metot | Yol | Açıklama |
|---|---|---|
| GET | `/health` | Sağlık kontrolü |
| GET | `/config` | 3 dalın form konfigürasyonu (frontend tek kaynaktan çizer) |
| POST | `/analyze` | Skor + risk + 3 maddelik navigasyon raporu |
| POST | `/certificate` | Skor>75 & risk düşükse PDF sertifika |

**Örnek istek:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"branch":"sirketim_var","answers":{"Product_Market_Fit_Score":9,"Runway_Months_Remaining":22,"Cofounder_Conflict_Score":1}}'
```

---

## Klasör Yapısı

```
StartMetrics/
├─ backend/
│  ├─ app/
│  │  ├─ main.py            # FastAPI: /analyze, /certificate, /config, /health
│  │  ├─ schemas.py         # Pydantic request/response
│  │  ├─ form_config.py     # 3 dal veri-güdümlü soru konfigürasyonu (TEK KAYNAK)
│  │  ├─ orchestrator.py    # temizle → skorla → prompt → LLM → birleştir
│  │  ├─ scorer.py          # BİZİM deterministik modelimiz (dondurulmuş arayüz)
│  │  ├─ llm_client.py      # OpenAI + Türkçe mentor prompt + stub fallback
│  │  └─ pdf.py             # fpdf2 sertifika üretici
│  ├─ requirements.txt
│  └─ .env.example
├─ frontend/                # Vite + React + TS (tek sayfa, iki ekran)
│  └─ src/{App.tsx, api.ts, useTheme.ts, components/*, styles.css}
└─ data/
   └─ startup_founder_burnout_2026.csv   # referans; çalışma anında OKUNMAZ
```

---

## Sprint Sınırları

**Sprint 1 (bu teslim):** 3 dal + dinamik form → deterministik skorlayıcı →
orkestrasyon → LLM raporu (stub fallback'li) → skor/risk UI → PDF sertifika.

**Sprint 2+:** Gerçek ML modeli (XGBoost/LightGBM/BERT) `scorer.py`'ye takılır
(arayüz sabit). **Kapsam dışı (kalıcı):** yatırımcı eşleştirme, login, kalıcılık,
mesajlaşma.
