// api.ts — backend ile tipli iletişim katmanı.
// Vite proxy sayesinde "/api/*" -> http://localhost:8000/* yönlendirilir.

const BASE = "/api";

export type FieldKind = "select" | "number" | "scale";

export interface FormField {
  key: string;
  label: string;
  kind: FieldKind;
  options?: string[];
  min?: number;
  max?: number;
}

export interface BranchConfig {
  title: string;
  funding_stage: string;
  fields: FormField[];
}

export type ConfigResponse = Record<string, BranchConfig>;

export interface NavigationItem {
  title: string;
  body: string;
}

export interface AnalysisResponse {
  maturity_score: number;
  risk_probability: number;
  risk_percent: number;
  risk_band: string;
  drivers: string[];
  navigation_report: NavigationItem[];
  certificate_available: boolean;
  report_source: string;
}

export async function fetchConfig(): Promise<ConfigResponse> {
  const res = await fetch(`${BASE}/config`);
  if (!res.ok) throw new Error("Form konfigürasyonu alınamadı");
  return res.json();
}

export async function analyze(
  branch: string,
  answers: Record<string, string | number>
): Promise<AnalysisResponse> {
  const res = await fetch(`${BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ branch, answers }),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || "Analiz başarısız oldu");
  }
  return res.json();
}

// Sertifikayı indirir (PDF blob). certificate_available true iken çağrılır.
export async function downloadCertificate(
  branch: string,
  answers: Record<string, string | number>
): Promise<void> {
  const res = await fetch(`${BASE}/certificate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ branch, answers }),
  });
  if (!res.ok) throw new Error("Sertifika üretilemedi");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "startmetrics_sertifika.pdf";
  a.click();
  URL.revokeObjectURL(url);
}
