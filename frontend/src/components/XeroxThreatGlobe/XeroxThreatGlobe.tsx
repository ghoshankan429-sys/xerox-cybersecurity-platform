import { useMemo, useRef, useState } from "react";
import { Html, Line, OrbitControls, Stars } from "@react-three/drei";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";
import type { OrbitControls as OrbitControlsImpl } from "three-stdlib";
import type { ThreatConnection, ThreatNode, XeroxThreatGlobeProps } from "./types";
import { DEFAULT_CONNECTIONS, DEFAULT_THREATS, SEVERITY_COLORS, latLonToVector } from "./utils";
import "./XeroxThreatGlobe.css";

function GlobeContours() {
  const contours = useMemo(() => {
    const shapes: Array<Array<[number, number]>> = [
      [[72, -140], [58, -126], [49, -118], [32, -112], [23, -98], [14, -84], [25, -78], [39, -72], [51, -62], [62, -74], [70, -102], [72, -140]],
      [[12, -81], [2, -79], [-12, -70], [-24, -64], [-37, -65], [-53, -70], [-55, -50], [-34, -40], [-14, -48], [1, -60], [12, -81]],
      [[71, -18], [60, -8], [45, 2], [37, 12], [30, 25], [12, 34], [-4, 30], [-21, 17], [-34, 22], [-35, 40], [-17, 51], [6, 46], [27, 50], [45, 36], [59, 26], [71, -18]],
      [[68, 38], [62, 63], [55, 87], [41, 102], [26, 117], [8, 124], [6, 145], [25, 143], [39, 129], [52, 139], [65, 116], [71, 83], [68, 38]],
      [[-11, 112], [-19, 123], [-26, 137], [-36, 145], [-40, 153], [-28, 161], [-16, 153], [-11, 137], [-11, 112]],
    ];
    return shapes.map((shape) => shape.map(([lat, lon]) => latLonToVector(lat, lon, 2.012)));
  }, []);

  return (
    <group>
      {contours.map((points, index) => (
        <Line key={index} points={points} color="#7e8b8f" lineWidth={1.05} transparent opacity={0.42} />
      ))}
      {[20, 42, 64].map((lat) => (
        <Line
          key={`lat-${lat}`}
          points={Array.from({ length: 65 }, (_, index) => latLonToVector(lat, -180 + index * 5, 2.006))}
          color="#8f9a9e"
          lineWidth={0.45}
          transparent
          opacity={0.13}
        />
      ))}
      {[-120, -60, 0, 60, 120].map((lon) => (
        <Line
          key={`lon-${lon}`}
          points={Array.from({ length: 37 }, (_, index) => latLonToVector(-90 + index * 5, lon, 2.006))}
          color="#8f9a9e"
          lineWidth={0.45}
          transparent
          opacity={0.13}
        />
      ))}
    </group>
  );
}

function ThreatNodeMesh({
  threat,
  selected,
  onSelect,
}: {
  threat: ThreatNode;
  selected: boolean;
  onSelect: (threat: ThreatNode) => void;
}) {
  const group = useRef<THREE.Group>(null);
  const halo = useRef<THREE.Mesh>(null);
  const point = useMemo(() => latLonToVector(threat.latitude, threat.longitude), [threat.latitude, threat.longitude]);
  const color = SEVERITY_COLORS[threat.severity];

  useFrame(({ clock }) => {
    const pulse = 1 + Math.sin(clock.elapsedTime * (2.1 + threat.latitude / 90) + threat.longitude) * 0.12;
    if (group.current) group.current.scale.setScalar(selected ? 1.35 : pulse);
    if (halo.current) {
      halo.current.scale.setScalar(1.25 + (Math.sin(clock.elapsedTime * 1.7 + threat.longitude) + 1) * 0.22);
      (halo.current.material as THREE.MeshBasicMaterial).opacity =
        0.08 + (Math.sin(clock.elapsedTime * 1.4 + threat.latitude) + 1) * 0.035;
    }
  });

  return (
    <group ref={group} position={point}>
      {/* Expanded invisible hit target for smooth hover and click interaction */}
      <mesh
        onClick={(event) => {
          event.stopPropagation();
          onSelect(threat);
        }}
        onPointerOver={(event) => {
          event.stopPropagation();
          document.body.style.cursor = "pointer";
        }}
        onPointerOut={() => {
          document.body.style.cursor = "default";
        }}
      >
        <sphereGeometry args={[0.24, 16, 16]} />
        <meshBasicMaterial transparent opacity={0} depthWrite={false} />
      </mesh>
      {/* Visual node geometry */}
      <mesh>
        <sphereGeometry args={[0.055, 16, 16]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={selected ? 3.2 : 1.8}
          roughness={0.3}
          metalness={0.2}
        />
      </mesh>
      <mesh ref={halo} rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.075, 0.088, 24]} />
        <meshBasicMaterial color={color} transparent opacity={0.12} side={THREE.DoubleSide} />
      </mesh>
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[0.095, 0.008, 6, 24]} />
        <meshBasicMaterial color={color} transparent opacity={selected ? 0.9 : 0.45} />
      </mesh>
      {selected && (
        <Html center distanceFactor={7} position={[0.16, 0.12, 0]}>
          <div className="xerox-node-label">
            <span style={{ background: color }} />
            {threat.id}
          </div>
        </Html>
      )}
    </group>
  );
}

function ThreatArc({
  from,
  to,
  phase = 0,
  speed = 0.06,
}: {
  from: ThreatNode;
  to: ThreatNode;
  phase?: number;
  speed?: number;
}) {
  const particle = useRef<THREE.Mesh>(null);
  const start = useMemo(() => latLonToVector(from.latitude, from.longitude, 2.055), [from.latitude, from.longitude]);
  const end = useMemo(() => latLonToVector(to.latitude, to.longitude, 2.055), [to.latitude, to.longitude]);
  const curve = useMemo(() => {
    const mid = start
      .clone()
      .add(end)
      .multiplyScalar(0.5)
      .normalize()
      .multiplyScalar(2.55 + start.distanceTo(end) * 0.18);
    return new THREE.CatmullRomCurve3([start, mid, end]);
  }, [start, end]);
  const points = useMemo(() => curve.getPoints(48), [curve]);

  useFrame(({ clock }) => {
    if (particle.current) {
      particle.current.position.copy(curve.getPointAt((clock.elapsedTime * speed + phase) % 1));
    }
  });

  return (
    <group>
      <Line points={points} color="#e4373f" lineWidth={0.65} transparent opacity={0.28} />
      <mesh ref={particle}>
        <sphereGeometry args={[0.026, 8, 8]} />
        <meshBasicMaterial color="#ff6b70" transparent opacity={0.92} />
      </mesh>
    </group>
  );
}

function HolographicPlatform() {
  const platform = useRef<THREE.Group>(null);
  const inner = useRef<THREE.Group>(null);
  const markers = useMemo(() => Array.from({ length: 24 }, (_, index) => index), []);

  useFrame((_, delta) => {
    if (platform.current) platform.current.rotation.y += delta * 0.045;
    if (inner.current) inner.current.rotation.y -= delta * 0.1;
  });

  return (
    <group position={[0, -2.35, 0]}>
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <cylinderGeometry args={[1.86, 2.02, 0.14, 64]} />
        <meshStandardMaterial color="#171d20" metalness={0.9} roughness={0.27} />
      </mesh>
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.08, 0]}>
        <cylinderGeometry args={[1.2, 1.48, 0.04, 64]} />
        <meshStandardMaterial color="#30393d" metalness={0.85} roughness={0.28} />
      </mesh>
      <group ref={platform}>
        {[1.65, 1.88, 2.08].map((radius, index) => (
          <mesh key={radius} rotation={[-Math.PI / 2, 0, index * 0.45]} position={[0, 0.15 + index * 0.03, 0]}>
            <torusGeometry args={[radius, index === 1 ? 0.018 : 0.009, 8, 80]} />
            <meshBasicMaterial
              color={index === 1 ? "#e4373f" : "#839094"}
              transparent
              opacity={index === 1 ? 0.54 : 0.3}
            />
          </mesh>
        ))}
      </group>
      <group ref={inner} position={[0, 0.18, 0]}>
        {markers.map((index) => {
          const angle = (index / markers.length) * Math.PI * 2;
          const r = 1.83;
          return (
            <mesh
              key={index}
              position={[Math.cos(angle) * r, 0, Math.sin(angle) * r]}
              rotation={[-Math.PI / 2, 0, -angle]}
            >
              <boxGeometry args={[index % 3 === 0 ? 0.11 : 0.045, 0.012, 0.018]} />
              <meshBasicMaterial
                color={index % 3 === 0 ? "#e4373f" : "#7d898d"}
                transparent
                opacity={index % 3 === 0 ? 0.7 : 0.35}
              />
            </mesh>
          );
        })}
      </group>
      <pointLight color="#e4373f" intensity={0.9} distance={4.2} position={[0, 0.1, 0]} />
    </group>
  );
}

function GlobeScene({
  threats,
  connections,
  selectedId,
  onSelect,
  autoRotate,
}: {
  threats: ThreatNode[];
  connections: ThreatConnection[];
  selectedId: string | null;
  onSelect: (threat: ThreatNode) => void;
  autoRotate: boolean;
}) {
  const stage = useRef<THREE.Group>(null);
  const controls = useRef<OrbitControlsImpl>(null);

  useFrame(({ pointer }) => {
    if (stage.current) {
      stage.current.rotation.x = THREE.MathUtils.lerp(stage.current.rotation.x, pointer.y * 0.035, 0.04);
      stage.current.rotation.z = THREE.MathUtils.lerp(stage.current.rotation.z, pointer.x * -0.025, 0.04);
    }
  });

  const threatById = useMemo(() => new Map(threats.map((threat) => [threat.id, threat])), [threats]);

  return (
    <>
      <color attach="background" args={["#050607"]} />
      <fog attach="fog" args={["#050607", 7, 14]} />
      <ambientLight intensity={0.48} color="#8b9395" />
      <directionalLight position={[4, 5, 7]} intensity={2.2} color="#e9eff0" />
      <directionalLight position={[-5, 1, -4]} intensity={1.1} color="#a5b0b2" />
      <pointLight position={[0, 1.4, 3.8]} intensity={1.2} color="#d9e2e2" distance={8} />
      <Stars radius={22} depth={18} count={900} factor={1.15} saturation={0} fade speed={0.25} />
      <group ref={stage}>
        <group>
          <mesh>
            <sphereGeometry args={[2, 64, 64]} />
            <meshStandardMaterial color="#252d31" roughness={0.78} metalness={0.66} />
          </mesh>
          <mesh scale={1.035}>
            <sphereGeometry args={[2, 48, 48]} />
            <meshBasicMaterial color="#11171a" wireframe transparent opacity={0.22} />
          </mesh>
          <mesh scale={1.075}>
            <sphereGeometry args={[2, 48, 48]} />
            <meshBasicMaterial color="#9ba9ac" transparent opacity={0.035} side={THREE.BackSide} />
          </mesh>
          <GlobeContours />
          {threats.map((threat) => (
            <ThreatNodeMesh
              key={threat.id}
              threat={threat}
              selected={selectedId === threat.id}
              onSelect={onSelect}
            />
          ))}
          {connections.map((connection) => {
            const from = threatById.get(connection.from);
            const to = threatById.get(connection.to);
            return from && to ? (
              <ThreatArc
                key={`${connection.from}-${connection.to}`}
                from={from}
                to={to}
                phase={connection.phase}
                speed={connection.speed}
              />
            ) : null;
          })}
        </group>
        <HolographicPlatform />
      </group>
      <OrbitControls
        ref={controls}
        makeDefault
        enablePan={false}
        enableDamping
        dampingFactor={0.06}
        autoRotate={autoRotate}
        autoRotateSpeed={0.34}
        minDistance={4.5}
        maxDistance={8}
        minPolarAngle={Math.PI * 0.28}
        maxPolarAngle={Math.PI * 0.73}
      />
    </>
  );
}

function ThreatDetail({ threat, onClose }: { threat: ThreatNode; onClose: () => void }) {
  return (
    <aside className="xerox-threat-detail">
      <div className="xerox-detail-kicker">
        <span /> SIMULATED EVENT / {threat.id}
        <button onClick={onClose} aria-label="Close threat details">
          ×
        </button>
      </div>
      <div className="xerox-detail-title-row">
        <h2>{threat.type}</h2>
        <b
          style={{
            color: SEVERITY_COLORS[threat.severity],
            borderColor: `${SEVERITY_COLORS[threat.severity]}66`,
          }}
        >
          {threat.severity}
        </b>
      </div>
      <p>Demo intelligence packet. Not a live attack or production signal.</p>
      <div className="xerox-detail-grid">
        <div>
          <span>REGION</span>
          <strong>{threat.region}</strong>
        </div>
        <div>
          <span>SIGNAL STRENGTH</span>
          <strong>{threat.signalStrength}</strong>
        </div>
        <div>
          <span>DETECTION TIME</span>
          <strong>{threat.detectionTime}</strong>
        </div>
        <div>
          <span>CONTAINMENT</span>
          <strong className="xerox-green">MONITORING</strong>
        </div>
      </div>
      <button className="xerox-trace-button" onClick={onClose}>
        RETURN TO FIELD <span>↗</span>
      </button>
    </aside>
  );
}

export function XeroxThreatGlobe({
  threats = DEFAULT_THREATS,
  connections = DEFAULT_CONNECTIONS,
  onThreatSelect,
  onThreatDeselect,
  selectedThreatId,
  showHud = true,
  autoRotate = true,
  className = "",
  ariaLabel = "Interactive simulated cybersecurity threat globe",
}: XeroxThreatGlobeProps) {
  const [internalSelectedId, setInternalSelectedId] = useState<string | null>(null);
  const activeId = selectedThreatId === undefined ? internalSelectedId : selectedThreatId;
  const selected = threats.find((threat) => threat.id === activeId) ?? null;

  const selectThreat = (threat: ThreatNode) => {
    if (selectedThreatId === undefined) setInternalSelectedId(threat.id);
    onThreatSelect?.(threat);
  };

  const closeThreat = () => {
    if (selectedThreatId === undefined) setInternalSelectedId(null);
    onThreatDeselect?.();
  };

  return (
    <section className={`xerox-threat-globe ${className}`} aria-label={ariaLabel}>
      <div className="xerox-globe-frame">
        <div className="xerox-frame-corner xerox-tl" />
        <div className="xerox-frame-corner xerox-tr" />
        <div className="xerox-frame-corner xerox-bl" />
        <div className="xerox-frame-corner xerox-br" />
        <div className="xerox-globe-status">
          <span /> GLOBE / GLOBAL SIGNAL MAP <b>{String(threats.length).padStart(2, "0")} NODES ONLINE</b>
        </div>
        <Canvas
          dpr={[1, 1.65]}
          camera={{ position: [0, 0.18, 6.65], fov: 38 }}
          gl={{ antialias: true, powerPreference: "high-performance" }}
        >
          <GlobeScene
            threats={threats}
            connections={connections}
            selectedId={activeId}
            onSelect={selectThreat}
            autoRotate={autoRotate}
          />
        </Canvas>
        <div className="xerox-globe-hint">
          ⌁ &nbsp; DRAG TO ROTATE <i>/</i> SCROLL TO ZOOM
        </div>
      </div>
      {showHud && (
        <>
          <div className="xerox-globe-hud">
            <span>REAL-TIME THREAT INTELLIGENCE</span>
            <strong>12,487</strong>
            <small>MONITORED SIGNALS</small>
            <em>THREAT LEVEL: HIGH</em>
          </div>
          <div className="xerox-globe-scan">
            SCAN <i>•</i> ANALYZE <i>•</i> DEFEND
          </div>
        </>
      )}
      {selected && showHud && <ThreatDetail threat={selected} onClose={closeThreat} />}
    </section>
  );
}

export type { ThreatConnection, ThreatNode, ThreatSeverity, XeroxThreatGlobeProps } from "./types";
export { DEFAULT_CONNECTIONS, DEFAULT_THREATS, SEVERITY_COLORS } from "./utils";
export default XeroxThreatGlobe;
