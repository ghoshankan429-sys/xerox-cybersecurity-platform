import * as THREE from "three";
import type { ThreatNode, ThreatSeverity } from "./types";

export const SEVERITY_COLORS: Record<ThreatSeverity, string> = {
  CRITICAL: "#ff5a5f",
  HIGH: "#e4373f",
  ELEVATED: "#be454c",
  MEDIUM: "#8b686c",
};

export function latLonToVector(latitude: number, longitude: number, radius = 2.04) {
  const phi = (90 - latitude) * (Math.PI / 180);
  const theta = (longitude + 180) * (Math.PI / 180);
  return new THREE.Vector3(
    -radius * Math.sin(phi) * Math.cos(theta),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta),
  );
}

export const DEFAULT_THREATS: ThreatNode[] = [
  { id: "TK-091", type: "Credential Harvesting", severity: "CRITICAL", region: "Northern Europe", signalStrength: "98.7%", detectionTime: "04:32:19 UTC", latitude: 56, longitude: 12 },
  { id: "TK-127", type: "Ransomware Beacon", severity: "HIGH", region: "Eastern Seaboard", signalStrength: "91.2%", detectionTime: "04:31:48 UTC", latitude: 38, longitude: -74 },
  { id: "TK-204", type: "Protocol Anomaly", severity: "ELEVATED", region: "Southeast Asia", signalStrength: "78.4%", detectionTime: "04:30:57 UTC", latitude: 8, longitude: 104 },
  { id: "TK-318", type: "Data Exfiltration", severity: "HIGH", region: "West Africa", signalStrength: "86.1%", detectionTime: "04:30:11 UTC", latitude: 9, longitude: -3 },
  { id: "TK-419", type: "Botnet Coordination", severity: "MEDIUM", region: "Southern Brazil", signalStrength: "63.9%", detectionTime: "04:29:44 UTC", latitude: -15, longitude: -48 },
  { id: "TK-531", type: "Lateral Movement", severity: "ELEVATED", region: "Central Asia", signalStrength: "72.6%", detectionTime: "04:28:52 UTC", latitude: 42, longitude: 67 },
  { id: "TK-688", type: "Supply Chain Drift", severity: "HIGH", region: "Eastern Australia", signalStrength: "88.9%", detectionTime: "04:27:23 UTC", latitude: -27, longitude: 146 },
];

export const DEFAULT_CONNECTIONS = [
  { from: "TK-091", to: "TK-127", phase: 0.08 },
  { from: "TK-127", to: "TK-419", phase: 0.34 },
  { from: "TK-204", to: "TK-531", phase: 0.56 },
  { from: "TK-318", to: "TK-091", phase: 0.72 },
  { from: "TK-419", to: "TK-688", phase: 0.18 },
];
