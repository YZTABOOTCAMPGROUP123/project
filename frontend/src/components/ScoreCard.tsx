import { useEffect, useState } from "react";
import { motion, useMotionValue, animate } from "framer-motion";
import type { AnalysisResponse } from "../api";

// Sol panel: SVG dairesel gösterge (sayaç animasyonlu) + risk rozeti + sürücüler.

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

// Skor rengi: gauge dolgusu markadan, ama düşük skorda uyarı tonuna kayar.
function scoreColor(score: number): string {
  if (score >= 75) return "var(--risk-low)";
  if (score >= 45) return "var(--brand)";
  return "var(--risk-med)";
}

const R = 82;
const CIRC = 2 * Math.PI * R;

export default function ScoreCard({ result }: { result: AnalysisResponse }) {
  const { maturity_score, risk_percent, risk_band, drivers } = result;
  const [display, setDisplay] = useState(0);
  const mv = useMotionValue(0);

  // Sayaç: 0 -> skor, gösterge ile senkron.
  useEffect(() => {
    const controls = animate(mv, maturity_score, {
      duration: 1.1,
      ease: "easeOut",
      onUpdate: (v) => setDisplay(Math.round(v)),
    });
    return controls.stop;
  }, [maturity_score, mv]);

  const offset = CIRC - (display / 100) * CIRC;
  const color = scoreColor(maturity_score);

  return (
    <div className="card panel">
      <h3 className="panel-title">Olgunluk Skoru</h3>
      <p className="panel-cap">Analitik Model · Deterministik</p>

      <div className="gauge-wrap">
        <div className="gauge">
          <svg width="190" height="190" viewBox="0 0 190 190">
            <circle
              cx="95" cy="95" r={R}
              fill="none" stroke="var(--surface-2)" strokeWidth="14"
            />
            <motion.circle
              cx="95" cy="95" r={R}
              fill="none" stroke={color} strokeWidth="14" strokeLinecap="round"
              strokeDasharray={CIRC}
              strokeDashoffset={offset}
              transform="rotate(-90 95 95)"
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
    </div>
  );
}
