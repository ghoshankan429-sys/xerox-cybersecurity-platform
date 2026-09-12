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
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.statusText}`);
  }
  return res.json();
}

export async function scanUrl(url: string): Promise<ThreatReport> {
  const res = await fetch(`${API_BASE}/scans/url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
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
  senderMetadata?: string
): Promise<ThreatReport> {
  const res = await fetch(`${API_BASE}/scans/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, sender_metadata: senderMetadata }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Scan failed" }));
    throw new Error(err.detail || "Message scan failed");
  }
  return res.json();
}

export async function getHistory(limit: number = 50): Promise<ScanHistoryItem[]> {
  const res = await fetch(`${API_BASE}/scans/history?limit=${limit}`);
  if (!res.ok) {
    throw new Error("Failed to load scan history");
  }
  return res.json();
}

export async function getReport(scanId: string): Promise<ThreatReport> {
  const res = await fetch(`${API_BASE}/scans/${scanId}`);
  if (!res.ok) {
    throw new Error("Report not found");
  }
  return res.json();
}

export async function getStats(): Promise<StatsSummary> {
  const res = await fetch(`${API_BASE}/scans/summary/stats`);
  if (!res.ok) {
    throw new Error("Failed to load telemetry stats");
  }
  return res.json();
}
