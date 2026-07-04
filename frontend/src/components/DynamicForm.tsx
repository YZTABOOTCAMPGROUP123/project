import { motion } from "framer-motion";
import type { BranchConfig } from "../api";

// Dinamik form: alanları backend /config tanımına göre çizer (staggered giriş).

interface Props {
  config: BranchConfig;
  answers: Record<string, string | number>;
  onChange: (key: string, value: string) => void;
  onSubmit: () => void;
  loading: boolean;
}

export default function DynamicForm({
  config,
  answers,
  onChange,
  onSubmit,
  loading,
}: Props) {
  return (
    <motion.form
      className="card form-card"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
    >
      <div className="fields">
        {config.fields.map((field, i) => (
          <motion.label
            key={field.key}
            className="field"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.04 }}
          >
            <span className="field-label">{field.label}</span>

            {field.kind === "select" ? (
              <select
                value={answers[field.key] ?? ""}
                onChange={(e) => onChange(field.key, e.target.value)}
                required
              >
                <option value="" disabled>
                  Seçiniz…
                </option>
                {field.options?.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="number"
                value={answers[field.key] ?? ""}
                min={field.min}
                max={field.max}
                step={field.kind === "scale" ? 1 : "any"}
                placeholder={
                  field.kind === "scale"
                    ? `${field.min}–${field.max} arası`
                    : "Sayısal değer"
                }
                onChange={(e) => onChange(field.key, e.target.value)}
                required
              />
            )}
          </motion.label>
        ))}
      </div>

      <button type="submit" className="analyze-btn" disabled={loading}>
        {loading ? (
          <>
            <span className="spinner" /> Analiz ediliyor…
          </>
        ) : (
          <>⚡ Analiz Et</>
        )}
      </button>
    </motion.form>
  );
}
