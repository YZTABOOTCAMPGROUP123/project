"""
api/index.py — Vercel Python (serverless) giriş noktası.

Vercel bu dosyadaki `app` değişkenini bir ASGI (FastAPI) uygulaması olarak
yükler. Gerçek uygulama backend/app/main.py içindedir; burada sadece onu
import edip Vercel'e sunuyoruz.

Yönlendirme vercel.json'da: /api/* istekleri buraya gelir. FastAPI route'ları
da /api altında (APIRouter prefix) olduğu için yollar birebir eşleşir.
"""

import os
import sys

# backend/ klasörünü modül aramasına ekle ki `app` paketi import edilebilsin.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BACKEND = os.path.join(_ROOT, "backend")
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from app.main import app  # noqa: E402  (Vercel'in yükleyeceği ASGI uygulaması)

__all__ = ["app"]
