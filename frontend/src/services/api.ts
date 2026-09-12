import {
  ThreatReport,
  ScanHistoryItem,
  StatsSummary,
} from "@/types";

const API_BASE = import.meta.env.VITE_API_URL || "/api/v1";

export async function checkBackendHealth(): Promise<{
  status: string;
  service: string;
  version: string;
}> {
  const res = await fetch(`${API_BASE}/health`, {
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.statusText}`);
  }
  return res.json();
}

export async function scanUrl(url: string): Promise<ThreatReport> {
  const res = await fetch(`${API_BASE}/analyze/url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ url, deep_scan: true }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Scan failed" }));
    throw new Error(err.detail || "URL scan failed");
  }
  return res.json();
}

export async function scanMessage(
  content: string,
  senderMetadata?: string,
  subject?: string,
  sender?: string
): Promise<ThreatReport> {
  const res = await fetch(`${API_BASE}/analyze/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({
      content,
      sender_metadata: senderMetadata,
      subject,
      sender,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Scan failed" }));
    throw new Error(err.detail || "Message scan failed");
  }
  return res.json();
}

export async function scanScreenshot(file: File): Promise<ThreatReport> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/analyze/screenshot`, {
    method: "POST",
    credentials: "include",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Screenshot scan failed" }));
    throw new Error(err.detail || "Screenshot scan failed");
  }
  return res.json();
}

export async function getHistory(limit: number = 50): Promise<ScanHistoryItem[]> {
  const res = await fetch(`${API_BASE}/analyze/history?limit=${limit}`, {
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to load scan history");
  }
  return res.json();
}

export async function getReport(scanId: string): Promise<ThreatReport> {
  const res = await fetch(`${API_BASE}/analyze/${scanId}`, {
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Report not found");
  }
  return res.json();
}

export async function getStats(): Promise<StatsSummary> {
  const res = await fetch(`${API_BASE}/analyze/stats/summary`, {
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error("Failed to load telemetry stats");
  }
  return res.json();
}
