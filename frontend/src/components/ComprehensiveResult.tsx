import { useState, useEffect } from "react";
import { motion, useMotionValue, animate } from "framer-motion";
import type { ComprehensiveReportResponse } from "../api";
import { downloadCertificateFromComprehensive } from "../api";

// Adım 5 — Kapsamlı Sonuç Ekranı: ML Skor + AI Yol Haritası + Sertifika

interface Props {
  result: ComprehensiveReportResponse;
  branch: string;
  step1Answers: Record<string, string | number>;
  methodology1Answers: Record<string, string>;
  methodology2Answers: Record<string, string>;
  onRestart: () => void;
}

const RISK_COLOR: Record<string, string> = {
  Düşük: "var(--risk-low)",
  Orta: "var(--risk-med)",
  Yüksek: "var(--risk-high)",
};
const RISK_SOFT: Record<string, string> = {
  Düşük: "var(--risk-low-soft)",
  Orta: "var(--risk-med-soft)",
  Yüksek: "var(--risk-high-soft)",
};

function scoreColor(score: number): string {
  if (score >= 75) return "var(--risk-low)";
  if (score >= 45) return "var(--brand)";
  return "var(--risk-med)";
}

const R = 78;
const CIRC = 2 * Math.PI * R;

// Basit markdown→HTML dönüştürücü (sadece ## başlık, **bold**, - madde)
function renderMarkdown(text: string): string {
  return text
    .replace(/^## (.+)$/gm, '<h3 class="roadmap-h3">$1</h3>')
    .replace(/^### (.+)$/gm, '<h4 class="roadmap-h4">$1</h4>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/gs, (m) => `<ul class="roadmap-ul">${m}</ul>`)
    .replace(/^---$/gm, '<hr class="roadmap-hr" />')
    .replace(/\n\n/g, '</p><p class="roadmap-p">')
    .replace(/^\*(.+)$/gm, '<em>$1</em>');
}

export default function ComprehensiveResult({
  result,
  branch,
  step1Answers,
  methodology1Answers,
  methodology2Answers,
  onRestart,
}: Props) {
  const { maturity_score, risk_percent, risk_band, drivers, certificate_available, roadmap_report } = result;
  const [display, setDisplay] = useState(0);
  const [downloading, setDownloading] = useState(false);
  const mv = useMotionValue(0);

  useEffect(() => {
    const controls = animate(mv, maturity_score, {
      duration: 1.2,
      ease: "easeOut",
      onUpdate: (v) => setDisplay(Math.round(v)),
    });
    return controls.stop;
  }, [maturity_score, mv]);

  const offset = CIRC - (display / 100) * CIRC;
  const color = scoreColor(maturity_score);

  async function handleDownload() {
    setDownloading(true);
    try {
      await downloadCertificateFromComprehensive(
        branch,
        step1Answers,
        methodology1Answers,
        methodology2Answers
      );
    } finally {
      setDownloading(false);
    }
  }

  return (
    <motion.div
      className="comprehensive-result"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
    >
      {/* === ÜSTBILGI === */}
      <div className="result-header">
        <motion.span
          className="result-badge"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
        >
          ✦ Kapsamlı Analiz Tamamlandı
        </motion.span>
        <motion.h2
          className="result-main-title"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
        >
          Stratejik Yol Haritanız Hazır
        </motion.h2>
        <motion.p
          className="result-main-sub"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          ML modeli ve Yapay Zeka analizinin birleştirildiği kişiselleştirilmiş rapor
        </motion.p>
      </div>

      {/* === ANA GRID: SKOR SOL + SERTIFIKA SAĞ === */}
      <div className="result-top-grid">
        {/* SOL — Olgunluk Skoru */}
        <motion.div
          className="card panel"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.25 }}
        >
          <h3 className="panel-title">Olgunluk Skoru</h3>
          <p className="panel-cap">
            {drivers.some(d => d.includes("[ML MODELİ]"))
              ? "Akıllı Tahmin Motoru • Aktif"
              : "Standart Analiz Motoru • Güvenli Mod"}
          </p>

          <div className="gauge-wrap">
            <div className="gauge">
              <svg width="180" height="180" viewBox="0 0 180 180">
                <circle cx="90" cy="90" r={R} fill="none" stroke="var(--surface-2)" strokeWidth="13" />
                <motion.circle
                  cx="90" cy="90" r={R}
                  fill="none" stroke={color} strokeWidth="13" strokeLinecap="round"
                  strokeDasharray={CIRC}
                  strokeDashoffset={offset}
                  transform="rotate(-90 90 90)"
                />
              </svg>
              <div className="gauge-center">
                <span className="gauge-value">{display}</span>
                <span className="gauge-max">/ 100</span>
              </div>
            </div>
          </div>

          <div
            className="risk-badge"
            style={{ background: RISK_SOFT[risk_band], color: RISK_COLOR[risk_band] }}
          >
            <span className="risk-dot" style={{ background: RISK_COLOR[risk_band] }} />
            Batma Riski: %{risk_percent} ({risk_band})
          </div>

          {drivers.length > 0 && (
            <>
              <p className="drivers-title">Skoru Etkileyen Sinyaller</p>
              <ul className="drivers">
                {drivers.map((d, i) => (
                  <motion.li
                    className="driver"
                    key={i}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + i * 0.08 }}
                  >
                    <span className="tick">▸</span>
                    <span>{d}</span>
                  </motion.li>
                ))}
              </ul>
            </>
          )}
        </motion.div>

        {/* SAĞ — Sertifika Paneli */}
        <motion.div
          className="card panel cert-panel"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <h3 className="panel-title">Güvenirlik Sertifikası</h3>
          {certificate_available ? (
            <>
              <div className="cert-trophy">🏆</div>
              <p className="cert-congrats">
                Tebrikler! Olgunluk skoru <strong>%75 üzeri</strong> ve risk <strong>düşük</strong> seviyede — sertifika hak kazandınız.
              </p>
              <motion.button
                className="cert-btn"
                onClick={handleDownload}
                disabled={downloading}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {downloading ? "Hazırlanıyor…" : "⬇️ Sertifikayı İndir (PDF)"}
              </motion.button>
            </>
          ) : (
            <>
              <div className="cert-lock">🔒</div>
              <p className="cert-hint-main">
                Sertifika için Olgunluk Skoru <strong>75 üzeri</strong> ve risk <strong>düşük</strong> olmalı.
              </p>
              <div className="cert-progress">
                <div className="cert-progress-bar">
                  <div
                    className="cert-progress-fill"
                    style={{ width: `${Math.min(maturity_score, 100)}%` }}
                  />
                </div>
                <span className="cert-progress-label">%{maturity_score} / 75 hedef</span>
              </div>
            </>
          )}

          <div className="cert-divider" />

          <button className="restart-btn" onClick={onRestart}>
            ↺ Yeni Analiz Başlat
          </button>
        </motion.div>
      </div>

      {/* === AI YOL HARİTASI RAPORU === */}
      <motion.div
        className="card roadmap-card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <div className="roadmap-header">
          <h3 className="roadmap-title">
            🗺️ AI Yol Haritası Raporu
          </h3>
          <span className={`roadmap-source ${result.report_source}`}>
            {result.report_source === "llm" ? "✦ Gemini AI" : "⚙ Otomatik"}
          </span>
        </div>
        <div
          className="roadmap-content"
          dangerouslySetInnerHTML={{ __html: renderMarkdown(roadmap_report) }}
        />
      </motion.div>
    </motion.div>
  );
}
