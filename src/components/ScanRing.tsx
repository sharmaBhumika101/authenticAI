interface ScanRingProps {
  size?: number;
  status?: "idle" | "scanning" | "verified" | "failed";
  children?: React.ReactNode;
}
const statusConfig = {
  idle: { color: "hsl(186 100% 50%)", dimColor: "hsl(186 100% 50% / 0.15)", label: "STANDBY" },
  scanning: { color: "hsl(45 100% 55%)", dimColor: "hsl(45 100% 55% / 0.15)", label: "SCANNING" },
  verified: { color: "hsl(145 100% 50%)", dimColor: "hsl(145 100% 50% / 0.15)", label: "VERIFIED" },
  failed: { color: "hsl(355 100% 55%)", dimColor: "hsl(355 100% 55% / 0.15)", label: "FAILED" },
};
export const ScanRing = ({ size = 260, status = "idle", children }: ScanRingProps) => {
  const cfg = statusConfig[status];
  const r1 = size / 2 - 8;
  const r2 = size / 2 - 20;
  const r3 = size / 2 - 36;
  const c = size / 2;
  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      {/* Outer ambient glow */}
      <div
        className="absolute inset-0 rounded-full"
        style={{
          background: `radial-gradient(circle, ${cfg.dimColor} 0%, transparent 70%)`,
          animation: status === "scanning" ? "glowPulse 1.5s ease-in-out infinite" : undefined,
        }}
      />
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        fill="none"
        className="absolute inset-0"
      >
        {/* Outermost dashed ring */}
        <circle
          cx={c}
          cy={c}
          r={r1}
          stroke={cfg.color}
          strokeWidth="1"
          strokeOpacity="0.2"
          strokeDasharray="6 4"
        />
        {/* Main spinning ring */}
        <circle
          cx={c}
          cy={c}
          r={r1}
          stroke={cfg.color}
          strokeWidth="1.5"
          strokeOpacity="0.7"
          strokeDasharray={`${r1 * 0.7} ${r1 * 0.3}`}
          strokeLinecap="round"
          style={{
            transformOrigin: `${c}px ${c}px`,
            animation: "scan-spin 4s linear infinite",
            filter: `drop-shadow(0 0 4px ${cfg.color})`,
          }}
        />
        {/* Reverse spinning mid ring */}
        <circle
          cx={c}
          cy={c}
          r={r2}
          stroke={cfg.color}
          strokeWidth="1"
          strokeOpacity="0.4"
          strokeDasharray={`${r2 * 0.4} ${r2 * 0.6}`}
          strokeLinecap="round"
          style={{
            transformOrigin: `${c}px ${c}px`,
            animation: "scan-spin-reverse 8s linear infinite",
          }}
        />
        {/* Inner ring */}
        <circle
          cx={c}
          cy={c}
          r={r3}
          stroke={cfg.color}
          strokeWidth="0.75"
          strokeOpacity="0.25"
          strokeDasharray="3 6"
          style={{
            transformOrigin: `${c}px ${c}px`,
            animation: "scan-spin 12s linear infinite",
          }}
        />
        {/* Cardinal marks */}
        {[0, 90, 180, 270].map((angle) => {
          const rad = (angle * Math.PI) / 180;
          const x1 = c + (r1 - 4) * Math.cos(rad);
          const y1 = c + (r1 - 4) * Math.sin(rad);
          const x2 = c + (r1 + 4) * Math.cos(rad);
          const y2 = c + (r1 + 4) * Math.sin(rad);
          return (
            <line
              key={angle}
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke={cfg.color}
              strokeWidth="2"
              strokeLinecap="round"
              style={{ filter: `drop-shadow(0 0 4px ${cfg.color})` }}
            />
          );
        })}
        {/* Scan beam (only when scanning) */}
        {status === "scanning" && (
          <line
            x1={c}
            y1={c}
            x2={c + r1}
            y2={c}
            stroke={cfg.color}
            strokeWidth="1.5"
            strokeOpacity="0.6"
            style={{
              transformOrigin: `${c}px ${c}px`,
              animation: "scan-spin 2s linear infinite",
            }}
          />
        )}
        {/* Status dots ring */}
        {[0, 45, 90, 135, 180, 225, 270, 315].map((angle, i) => {
          const rad = (angle * Math.PI) / 180;
          const r = r2 - 6;
          return (
            <circle
              key={i}
              cx={c + r * Math.cos(rad)}
              cy={c + r * Math.sin(rad)}
              r="1.5"
              fill={cfg.color}
              fillOpacity={i % 2 === 0 ? 0.6 : 0.2}
            />
          );
        })}
      </svg>
      {/* Center content */}
      <div className="relative z-10 flex flex-col items-center justify-center"
        style={{ width: r3 * 2 - 12, height: r3 * 2 - 12 }}>
        {children}
      </div>
      {/* Status label */}
      <div
        className="absolute font-mono text-[9px] tracking-[0.25em] font-medium"
        style={{
          bottom: 8,
          color: cfg.color,
          filter: `drop-shadow(0 0 4px ${cfg.color})`,
          letterSpacing: "0.25em",
        }}
      >
        {cfg.label}
      </div>
    </div>
  );
};