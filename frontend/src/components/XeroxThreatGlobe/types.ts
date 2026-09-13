export type ThreatSeverity = "CRITICAL" | "HIGH" | "ELEVATED" | "MEDIUM";

export type ThreatNode = {
  id: string;
  type: string;
  severity: ThreatSeverity;
  region: string;
  signalStrength: string;
  detectionTime: string;
  latitude: number;
  longitude: number;
};

export type ThreatConnection = {
  from: string;
  to: string;
  phase?: number;
  speed?: number;
};

export type XeroxThreatGlobeProps = {
  /** Demo nodes shown on the globe. Coordinates use geographic latitude/longitude degrees. */
  threats?: ThreatNode[];
  /** Optional explicit arc definitions. Defaults to a connected demo network. */
  connections?: ThreatConnection[];
  /** Called when a node is selected. */
  onThreatSelect?: (threat: ThreatNode) => void;
  /** Called when the current selection is cleared. */
  onThreatDeselect?: () => void;
  /** Controlled selected node id. Omit to let the component manage selection internally. */
  selectedThreatId?: string | null;
  /** Whether the compact HUD and node detail panel are rendered by the component. */
  showHud?: boolean;
  /** Whether the globe slowly rotates when the user is idle. */
  autoRotate?: boolean;
  /** Optional class name applied to the component root. */
  className?: string;
  /** Optional accessible label for the canvas stage. */
  ariaLabel?: string;
};
