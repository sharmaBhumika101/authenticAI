// AuthenticAI Custom Icon Set — Geometric, Outline, Glowing
interface IconProps {
  size?: number;
  className?: string;
  glow?: "cyan" | "green" | "amber" | "red" | "none";
}
const glowMap = {
  cyan: "hsl(186 100% 50%)",
  green: "hsl(145 100% 50%)",
  amber: "hsl(45 100% 55%)",
  red: "hsl(355 100% 55%)",
  none: "transparent",
};
// Cryptographic Shield Icon
export const ShieldIcon = ({ size = 24, className = "", glow = "cyan" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <path
      d="M12 2L4 5.5V11.5C4 16 7.5 20 12 22C16.5 20 20 16 20 11.5V5.5L12 2Z"
      stroke={glowMap[glow]}
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      style={{ filter: `drop-shadow(0 0 4px ${glowMap[glow]})` }}
    />
    {/* Inner lattice */}
    <path
      d="M12 6L8 8V11.5C8 14 9.8 16.2 12 17.2C14.2 16.2 16 14 16 11.5V8L12 6Z"
      stroke={glowMap[glow]}
      strokeWidth="0.75"
      strokeOpacity="0.4"
    />
    {/* Circuit nodes */}
    <circle cx="12" cy="2" r="1" fill={glowMap[glow]} />
    <circle cx="4" cy="5.5" r="0.75" fill={glowMap[glow]} fillOpacity="0.6" />
    <circle cx="20" cy="5.5" r="0.75" fill={glowMap[glow]} fillOpacity="0.6" />
    {/* Hash lines */}
    <line x1="9" y1="11" x2="15" y2="11" stroke={glowMap[glow]} strokeWidth="0.75" strokeOpacity="0.5" />
    <line x1="9" y1="13" x2="15" y2="13" stroke={glowMap[glow]} strokeWidth="0.75" strokeOpacity="0.3" />
  </svg>
);
// Neural Node / AI Icon
export const NeuralIcon = ({ size = 24, className = "", glow = "cyan" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* Central hub */}
    <circle cx="12" cy="12" r="2.5" stroke={glowMap[glow]} strokeWidth="1.5"
      style={{ filter: `drop-shadow(0 0 4px ${glowMap[glow]})` }} />
    {/* Node connections */}
    <circle cx="4" cy="8" r="1.5" stroke={glowMap[glow]} strokeWidth="1" strokeOpacity="0.7" />
    <circle cx="20" cy="8" r="1.5" stroke={glowMap[glow]} strokeWidth="1" strokeOpacity="0.7" />
    <circle cx="4" cy="16" r="1.5" stroke={glowMap[glow]} strokeWidth="1" strokeOpacity="0.7" />
    <circle cx="20" cy="16" r="1.5" stroke={glowMap[glow]} strokeWidth="1" strokeOpacity="0.7" />
    <circle cx="12" cy="4" r="1.5" stroke={glowMap[glow]} strokeWidth="1" strokeOpacity="0.7" />
    <circle cx="12" cy="20" r="1.5" stroke={glowMap[glow]} strokeWidth="1" strokeOpacity="0.7" />
    {/* Connection lines */}
    <line x1="5.2" y1="8.8" x2="10.3" y2="10.9" stroke={glowMap[glow]} strokeWidth="0.75" strokeOpacity="0.4" />
    <line x1="18.8" y1="8.8" x2="13.7" y2="10.9" stroke={glowMap[glow]} strokeWidth="0.75" strokeOpacity="0.4" />
    <line x1="5.2" y1="15.2" x2="10.3" y2="13.1" stroke={glowMap[glow]} strokeWidth="0.75" strokeOpacity="0.4" />
    <line x1="18.8" y1="15.2" x2="13.7" y2="13.1" stroke={glowMap[glow]} strokeWidth="0.75" strokeOpacity="0.4" />
    <line x1="12" y1="5.5" x2="12" y2="9.5" stroke={glowMap[glow]} strokeWidth="0.75" strokeOpacity="0.4" />
    <line x1="12" y1="14.5" x2="12" y2="18.5" stroke={glowMap[glow]} strokeWidth="0.75" strokeOpacity="0.4" />
  </svg>
);
// Verification Tick Seal
export const VerifyIcon = ({ size = 24, className = "", glow = "green" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* Outer ring segments */}
    <circle cx="12" cy="12" r="10" stroke={glowMap[glow]} strokeWidth="1"
      strokeOpacity="0.3" strokeDasharray="4 2" />
    {/* Badge shape */}
    <path
      d="M12 3L14 5H17L18 8L21 9L19 12L21 15L18 16L17 19H14L12 21L10 19H7L6 16L3 15L5 12L3 9L6 8L7 5H10L12 3Z"
      stroke={glowMap[glow]}
      strokeWidth="1.2"
      style={{ filter: `drop-shadow(0 0 4px ${glowMap[glow]})` }}
    />
    {/* Checkmark */}
    <polyline
      points="8.5,12 11,14.5 15.5,9.5"
      stroke={glowMap[glow]}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      style={{ filter: `drop-shadow(0 0 6px ${glowMap[glow]})` }}
    />
  </svg>
);
// Hash / Fingerprint Icon
export const HashIcon = ({ size = 24, className = "", glow = "cyan" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* Horizontal lines */}
    <line x1="3" y1="9" x2="21" y2="9" stroke={glowMap[glow]} strokeWidth="1.5" strokeLinecap="round"
      style={{ filter: `drop-shadow(0 0 3px ${glowMap[glow]})` }} />
    <line x1="3" y1="15" x2="21" y2="15" stroke={glowMap[glow]} strokeWidth="1.5" strokeLinecap="round"
      strokeOpacity="0.7" />
    {/* Vertical lines */}
    <line x1="9" y1="3" x2="9" y2="21" stroke={glowMap[glow]} strokeWidth="1.5" strokeLinecap="round"
      strokeOpacity="0.7" />
    <line x1="15" y1="3" x2="15" y2="21" stroke={glowMap[glow]} strokeWidth="1.5" strokeLinecap="round"
      style={{ filter: `drop-shadow(0 0 3px ${glowMap[glow]})` }} />
    {/* Corner markers */}
    <rect x="3" y="3" width="3" height="3" stroke={glowMap[glow]} strokeWidth="1" fill="none" strokeOpacity="0.4" />
    <rect x="18" y="18" width="3" height="3" stroke={glowMap[glow]} strokeWidth="1" fill="none" strokeOpacity="0.4" />
  </svg>
);
// Authenticity Badge Icon
export const BadgeIcon = ({ size = 24, className = "", glow = "cyan" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    {/* Outer frame */}
    <rect x="3" y="3" width="18" height="18" rx="2" stroke={glowMap[glow]} strokeWidth="1.5"
      style={{ filter: `drop-shadow(0 0 4px ${glowMap[glow]})` }} />
    {/* Inner circuit cross */}
    <line x1="12" y1="3" x2="12" y2="21" stroke={glowMap[glow]} strokeWidth="0.5" strokeOpacity="0.2" />
    <line x1="3" y1="12" x2="21" y2="12" stroke={glowMap[glow]} strokeWidth="0.5" strokeOpacity="0.2" />
    {/* Center emblem */}
    <circle cx="12" cy="12" r="4" stroke={glowMap[glow]} strokeWidth="1.2" strokeOpacity="0.8" />
    <circle cx="12" cy="12" r="1.5" fill={glowMap[glow]}
      style={{ filter: `drop-shadow(0 0 4px ${glowMap[glow]})` }} />
    {/* Corner dots */}
    <circle cx="5" cy="5" r="1" fill={glowMap[glow]} fillOpacity="0.5" />
    <circle cx="19" cy="5" r="1" fill={glowMap[glow]} fillOpacity="0.5" />
    <circle cx="5" cy="19" r="1" fill={glowMap[glow]} fillOpacity="0.5" />
    <circle cx="19" cy="19" r="1" fill={glowMap[glow]} fillOpacity="0.5" />
  </svg>
);
// Scan / Radar Icon
export const ScanIcon = ({ size = 24, className = "", glow = "cyan" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <circle cx="12" cy="12" r="10" stroke={glowMap[glow]} strokeWidth="1"
      strokeOpacity="0.3" />
    <circle cx="12" cy="12" r="6" stroke={glowMap[glow]} strokeWidth="1"
      strokeOpacity="0.5" />
    <circle cx="12" cy="12" r="2" fill={glowMap[glow]}
      style={{ filter: `drop-shadow(0 0 6px ${glowMap[glow]})` }} />
    <line x1="12" y1="2" x2="12" y2="6" stroke={glowMap[glow]} strokeWidth="1.5"
      style={{ filter: `drop-shadow(0 0 3px ${glowMap[glow]})` }} />
    <line x1="12" y1="18" x2="12" y2="22" stroke={glowMap[glow]} strokeWidth="1.5" strokeOpacity="0.6" />
    <line x1="2" y1="12" x2="6" y2="12" stroke={glowMap[glow]} strokeWidth="1.5" strokeOpacity="0.6" />
    <line x1="18" y1="12" x2="22" y2="12" stroke={glowMap[glow]} strokeWidth="1.5" strokeOpacity="0.6" />
  </svg>
);
// Signal / Broadcast Icon
export const SignalIcon = ({ size = 24, className = "", glow = "amber" }: IconProps) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" className={className}>
    <circle cx="12" cy="12" r="2" fill={glowMap[glow]}
      style={{ filter: `drop-shadow(0 0 6px ${glowMap[glow]})` }} />
    <path d="M8.5 8.5C9.5 7.5 10.7 7 12 7C13.3 7 14.5 7.5 15.5 8.5" stroke={glowMap[glow]}
      strokeWidth="1.5" strokeLinecap="round" strokeOpacity="0.8" />
    <path d="M5 5C7.1 2.9 9.9 2 12 2C14.1 2 16.9 2.9 19 5" stroke={glowMap[glow]}
      strokeWidth="1.5" strokeLinecap="round" strokeOpacity="0.5" />
    <path d="M8.5 15.5C9.5 16.5 10.7 17 12 17C13.3 17 14.5 16.5 15.5 15.5" stroke={glowMap[glow]}
      strokeWidth="1.5" strokeLinecap="round" strokeOpacity="0.8" />
    <path d="M5 19C7.1 21.1 9.9 22 12 22C14.1 22 16.9 21.1 19 19" stroke={glowMap[glow]}
      strokeWidth="1.5" strokeLinecap="round" strokeOpacity="0.5" />
  </svg>
);
