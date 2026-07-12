# StartMetrics — Girişim Sağlık & Risk Navigasyonu


> YZTA Bootcamp 2026 · Sprint 2 · Canlı Yapay Zekâ & Makine Öğrenmesi Entegrasyonu

Girişimcilerin (**Fikrim Var / Startup'ım Var / Şirketim Var**) sağlık ve batma riskini, onları 20 sayfalık iş planlarıyla boğmadan tek sayfalık dinamik bir formla ölçen ve akıllı bir **"Dinamik Yol Haritası / Radar"** gibi yön veren analiz motoru.

**Akış:** Dal seç → ~8-10 kritik soruyu doldur → **Analiz Et** → solda 0-100 **Olgunluk Skoru** + Risk %, sağda **3 maddelik AI Navigasyon Raporu** → skor > 75 ve risk düşükse **PDF Sertifika** indir.

---

## Mimari & Hibrit AI Evrimi (Sprint 2)

Sprint 1'de verilen **"Dondurulmuş Arayüz (Frozen Interface)"** sözü Sprint 2'de başarıyla yerine getirilmiştir. `score(features) -> ScoreResult` fonksiyon imzası, Pydantic şemaları ve frontend katmanı **hiç değiştirilmeden**, deterministik motorun gövdesi gerçek bir Makine Öğrenmesi (ML) modeliyle hibrit hale getirilmiştir.


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
│(hibrit)   │ (mentor raporu)│
└─────┬────┘  └──────┬───────┘
      └──────┬───────┘
             ▼
 [Olgunluk Skoru + Risk %  +  3 maddelik rapor  +  PDF Sertifika]
```
- **`scorer.py` (bizim modelimiz):** Gerçek makine öğrenmesi (ML) modelinin (`train.py` ile eğitilen Random Forest) karar ağacı mantığını `m2cgen` ile **saf Python koduna (`model_logic.py`) transpile ederek** barındıran akıllı motor. Vercel üzerinde 0 MB ek yükle çalışır, `scikit-learn` bağımlılığı olmadan mikro saniyeler seviyesinde dinamik tahmin üretir. Düştüğü acil durumlarda sıfır kesinti (Zero-Downtime) sağlayan kural tabanlı koruma katmanına sahiptir. 3 maddelik nokta atışı bir Türkçe Mentor öneri Raporu.
- **`orchestrator.py` (ekstra puan katmanı):** Girdiyi temizler, skorlar, LLM
  prompt'unu kurar, raporu birleştirir.
- **`llm_client.py`:** OpenAI ile kullanıcının iş modeli raporu. **Anahtar
  yoksa** kural tabanlı stub rapora düşer → demo asla çökmez.

---

## 📊 Veri Bilimi & Jüri Savunma Metrikleri (`train.py`)

Model eğitimi, jüri karşısında teknik ve akademik olarak tam savunulabilir bir zemin oluşturmak adına sıkı doğrulama aşamalarından geçirilmiştir:

*   **Veri Seti:** `startup_founder_burnout_2026.csv` içerisindeki **50.000 satır** verinin tamamı eğitim ve test süreçlerinde kullanılmıştır.
*   **Veri Sızıntısı (Data Leakage) Arındırması:** İlk aşamada ortaya çıkan yanıltıcı %100 başarı oranları analiz edilmiş; hedef değişkenin türevi olan `Shutdown_Probability`, `Shutdown_Risk`, `Burnout_Score`, `Burnout_Level` ve `Founder_Burnout_Flag` sütunları veri bilimsel etikle **eğitimden tamamen çıkarılmıştır.** Modelin sadece kullanıcının formda doldurduğu ham girdilerden öğrenmesi sağlanmıştır.
*   **Overfitting (Ezberleme) Yoktur İspatı:**
    *   *Eğitim (Train) Seti Doğruluğu:* %89.33
    *   *Test Seti Başarısı:* %87.35
    *   Train ve Test doğrulukları arasındaki farkın yalnızca **%1.98** olması, modelin ezberlemediğinin ve yüksek genellenebilirlik kapasitesinin somut ispatıdır.
*   **Kararlılık (5-Fold Cross-Validation):** Veri seti 5 farklı alt kümeye bölünerek çapraz doğrulanmıştır. **CV Accuracy: %87.72** çıkarken, katmanlar arası standart sapma yalnızca **+/- %0.43** olarak ölçülmüştür. Bu durum, modelin veri manipülasyonlarına karşı kararlılığını kanıtlar.
*   **Ayırt Edicilik Gücü (ROC-AUC):** **0.9305** skoru ile modelin başarılı girişimler ile batma riski taşıyan yapıları birbirinden ayırt etme yeteneği mükemmel seviyetedir.
*   **Risk Yakalama (Sınıf 1 - Sınıflandırma Raporu):**
    *   *Precision (%82):* Model bir girişime "Riskli" alarmı veriyorsa %82 ihtimalle haklıdır (False Positive oranı düşüktür).
    *   *Recall (%60):* Gerçekte batacak olan erken aşama girişimlerin %60'ı hiçbir LLM bağımlılığı olmadan ham verilerden yakalanabilmektedir. "Fikrim Var" (Pre-Seed) gibi aşamalarda henüz sorulmayan eksik alanlar ise model mimarisi tarafından çökme yaşanmadan güvenli varsayılan değerlerle tolere edilir.

---

## Teknoloji Yığını

| Katman | Teknoloji |
|---|---|
| Backend | Python · FastAPI · Pydantic · Uvicorn |
| Makine Öğrenmesi | Random Forest Mantığı (Saf Python Matematiksel Matris Dönüşümü - m2cgen) · Joblib (Lokal Eğitim) |
| LLM | OpenAI (sağlayıcı-bağımsız; `LLM_PROVIDER` ile Anthropic'e de geçer) |
| PDF | fpdf2 + gömülü DejaVuSans (Unicode / tam Türkçe karakter desteği) |
| Frontend | Vite · React · TypeScript |
| UI/Tema | "Mercury Trust" indigo paleti · açık + koyu tema |
| Animasyon | Framer Motion · tsParticles |

---

## Kurulum & Çalıştırma

### 1) Modelin Eğitilmesi (Offline)
Canlı ortamda (production) sunucuya ek yük bindirmemek adına model lokalde bir kez eğitilir ve ağırlıklar dondurulur:
```powershell
# Sanal ortam aktifken backend dizininde çalıştırın
python train.py
python app/convert.py
```
Bu komut trained_model.pkl ve encoders.pkl dosyalarını otomatik olarak backend/app/ dizinine üretir.

### 2) Backend (Terminal 1)

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

### 3) Frontend (Terminal 2)

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
│  │  ├─ main.py            # FastAPI uç noktaları (/analyze, /certificate...)
│  │  ├─ schemas.py         # Pydantic veri modelleri
│  │  ├─ form_config.py     # 3 dalın form şeması (Tek Kaynak)
│  │  ├─ orchestrator.py    # Entegrasyon ve LLM rapor birleştirme
│  │  ├─ scorer.py          # HİBRİT MOTOR (Dinamik ML Yükleyici + Fallback)
│  │  ├─ trained_model.pkl  # Dondurulmuş Random Forest Model Ağırlıkları (Yeni)
│  │  ├─ encoders.pkl       # Kategorik Label Encoder nesneleri (Yeni)
│  │  ├─ llm_client.py      # OpenAI + Türkçe mentor prompt altyapısı
│  │  ├─ pdf.py             # fpdf2 sertifika motoru
│  │  ├─ convert.py         # ML modelini saf Python if-else yapılarına çeviren araç (Yeni)
│  │  └─ model_logic.py     # m2cgen tarafından üretilen bağımlılıksız saf ML mantığı (Yeni)
│  ├─ requirements.txt      # Vercel serverless limiti için tamamen hafifletildi (No sklearn/No pandas)
│  └─ train.py              # ML Eğitim, Veri Temizleme ve Doğrulama Betiği (Yeni)
├─ frontend/                # Vite + React + TS UI Katmanı
│  └─ src/{App.tsx, api.ts, useTheme.ts, components/*, styles.css}
└─ data/
   └─ startup_founder_burnout_2026.csv   # 50.000 Satırlık Referans Eğitim Veri Seti

```

---

## Sprint Sınırları

**Sprint 1 (Tamamlandı):** 3 dal + dinamik form → deterministik skorlayıcı →
orkestrasyon → LLM raporu (stub fallback'li) → skor/risk UI → PDF sertifika.

**Sprint 2 (Bu Teslim):** Veri sızıntılarından arındırılmış 50.000 satırlık ML model eğitimi (train.py) → Çapraz doğrulama ve overfitting analizlerinin tamamlanması → m2cgen transpile mimarisiyle Vercel serverless bundle limitinin (500 MB) aşılması → scorer.py gövdesine dondurulmuş arayüz standartlarına sadık kalınarak tamamen Türkçe, hafif ve dinamik akıllı tahmin motoru entegrasyonu → Zero-Downtime Fallback mekanizmasının kurulması.

**Kapsam dışı (kalıcı):** yatırımcı eşleştirme, login, kalıcılık, mesajlaşma.
