"""
pdf.py — "Girişim Güvenirlik Sertifikası" üretici (fpdf2 + Unicode font).

Türkçe karakter desteği için repoda gömülü DejaVuSans (Unicode TTF) kaydedilir;
böylece ç/ş/ğ/ı/İ/ö/ü gibi karakterler her ortamda doğru basılır (ASCII-fold
yok). Font dosyaları backend/app/fonts/ altında repoya dahildir.

Tetik koşulu orchestrator'da hesaplanır (skor>75 ve risk düşük); burada sadece
PDF baytları üretilir.
"""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

from .schemas import AnalysisResponse


_FONT_DIR = Path(__file__).parent / "fonts"
_FONT_FAMILY = "DejaVu"


def _new_pdf() -> FPDF:
    """Unicode fontları kayıtlı yeni bir FPDF örneği döndürür."""
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_font(_FONT_FAMILY, "", str(_FONT_DIR / "DejaVuSans.ttf"))
    pdf.add_font(_FONT_FAMILY, "B", str(_FONT_DIR / "DejaVuSans-Bold.ttf"))
    pdf.add_font(_FONT_FAMILY, "I", str(_FONT_DIR / "DejaVuSans-Oblique.ttf"))
    return pdf


def build_certificate(result: AnalysisResponse, branch_title: str, issued_date: str) -> bytes:
    """Tek sayfalık sertifika PDF'ini bayt olarak döndürür.

    Args:
        result: analiz sonucu (skor, risk).
        branch_title: "Fikrim Var" gibi okunur dal adı.
        issued_date: "2026-07-05" biçiminde veriliş tarihi (dışarıdan gelir;
            deterministik/test edilebilir olsun diye now() kullanmıyoruz).
    """
    pdf = _new_pdf()
    pdf.add_page()

    # Dış çerçeve (ince, kurumsal)
    pdf.set_draw_color(79, 70, 229)   # indigo (Mercury Trust marka rengi)
    pdf.set_line_width(1.0)
    pdf.rect(10, 10, 190, 277)
    pdf.set_draw_color(203, 213, 225)
    pdf.set_line_width(0.3)
    pdf.rect(13, 13, 184, 271)

    pdf.ln(32)
    pdf.set_font(_FONT_FAMILY, "B", 26)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 18, "Girişim Güvenirlik Sertifikası", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font(_FONT_FAMILY, "", 13)
    pdf.set_text_color(79, 70, 229)
    pdf.cell(0, 10, "StartMetrics — Girişim Sağlık & Risk Navigasyonu", align="C",
             new_x="LMARGIN", new_y="NEXT")

    pdf.ln(16)
    pdf.set_font(_FONT_FAMILY, "", 14)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 10, f"Dal: {branch_title}", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(8)
    pdf.set_font(_FONT_FAMILY, "B", 30)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 16, f"Olgunluk Skoru: {result.maturity_score}/100", align="C",
             new_x="LMARGIN", new_y="NEXT")

    pdf.set_font(_FONT_FAMILY, "", 16)
    pdf.set_text_color(22, 163, 74)   # yeşil: bu belge yalnızca düşük riskte üretilir
    pdf.cell(0, 12, f"Risk: %{result.risk_percent} ({result.risk_band})", align="C",
             new_x="LMARGIN", new_y="NEXT")

    pdf.ln(22)
    pdf.set_font(_FONT_FAMILY, "I", 11)
    pdf.set_text_color(110, 116, 132)
    pdf.multi_cell(
        0, 7,
        "Bu belge StartMetrics analiz motoru tarafından üretilmiştir. "
        "Skor, deterministik bir analitik model tarafından hesaplanmış; "
        "yön raporu bir yapay zekâ mentor katmanı ile oluşturulmuştur.",
        align="C",
    )

    pdf.ln(12)
    pdf.set_font(_FONT_FAMILY, "", 11)
    pdf.set_text_color(71, 85, 105)
    cert_id = _certificate_id(branch_title, result.maturity_score)
    pdf.cell(0, 8, f"Tarih: {issued_date}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Sertifika No: {cert_id}", align="C", new_x="LMARGIN", new_y="NEXT")

    out = pdf.output()
    return bytes(out)


_TR_TRANSLIT = str.maketrans("çÇğĞıİöÖşŞüÜ", "cCgGiIoOsSuU")


def _certificate_id(branch_title: str, maturity: int) -> str:
    """Deterministik, okunur sertifika numarası (now() yok).

    Türkçe harfleri ASCII'ye çevirir (Ş->S, ı->i) ki numara "IRK" gibi
    bozuk değil, "SIR" gibi anlamlı bir önek üretsin.
    """
    ascii_title = branch_title.translate(_TR_TRANSLIT)
    prefix = ascii_title.upper().replace(" ", "")[:3] or "STM"
    return f"SM-{prefix}-{maturity:03d}"
