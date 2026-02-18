import { useEffect, useState } from "react";
interface AuthenticLogoProps {
  size?: number;
  animated?: boolean;
  className?: string;
}
export const AuthenticLogo = ({ size = 48, animated = true, className = "" }: AuthenticLogoProps) => {
  const [active, setActive] = useState(false);
  useEffect(() => {
    if (animated) {
      const t = setTimeout(() => setActive(true), 300);
      return () => clearTimeout(t);
    }
  }, [animated]);
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Outer hexagon ring */}
      <polygon
        points="50,4 93,27.5 93,72.5 50,96 7,72.5 7,27.5"
        stroke="hsl(186 100% 50% / 0.6)"
        strokeWidth="1.5"
        fill="none"
        style={{
          filter: "drop-shadow(0 0 6px hsl(186 100% 50% / 0.5))",
          strokeDasharray: 280,
          strokeDashoffset: active ? 0 : 280,
          transition: "stroke-dashoffset 1.2s ease-out",
        }}
      />
      {/* Inner hexagon */}
      <polygon
        points="50,18 80,35 80,65 50,82 20,65 20,35"
        stroke="hsl(186 100% 50% / 0.25)"
        strokeWidth="1"
        fill="hsl(220 40% 6% / 0.8)"
      />
      {/* Neural nodes — outer ring */}
      {[0, 60, 120, 180, 240, 300].map((angle, i) => {
        const rad = (angle * Math.PI) / 180;
        const r = 32;
        const cx = 50 + r * Math.cos(rad);
        const cy = 50 + r * Math.sin(rad);
        return (
          <g key={i}>
            <circle
              cx={cx}
              cy={cy}
              r={2.5}
              fill="hsl(186 100% 50%)"
              style={{ filter: "drop-shadow(0 0 4px hsl(186 100% 50%))" }}
            />
            {/* Connection line to center */}
            <line
              x1={cx}
              y1={cy}
              x2={50}
              y2={50}
              stroke="hsl(186 100% 50% / 0.2)"
              strokeWidth="0.75"
            />
          </g>
        );
      })}
      {/* Center verification mark */}
      <circle
        cx={50}
        cy={50}
        r={10}
        fill="hsl(145 100% 50% / 0.15)"
        stroke="hsl(145 100% 50% / 0.7)"
        strokeWidth="1.5"
        style={{ filter: "drop-shadow(0 0 8px hsl(145 100% 50% / 0.5))" }}
      />
      {/* Checkmark */}
      <polyline
        points="44,50 48,55 57,44"
        stroke="hsl(145 100% 50%)"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        style={{
          filter: "drop-shadow(0 0 4px hsl(145 100% 50%))",
          strokeDasharray: 20,
          strokeDashoffset: active ? 0 : 20,
          transition: "stroke-dashoffset 0.6s ease-out 1s",
        }}
      />
      {/* Corner accent marks */}
      <line x1="7" y1="27.5" x2="15" y2="27.5" stroke="hsl(186 100% 50% / 0.8)" strokeWidth="2" strokeLinecap="round" />
      <line x1="7" y1="72.5" x2="15" y2="72.5" stroke="hsl(186 100% 50% / 0.8)" strokeWidth="2" strokeLinecap="round" />
      <line x1="50" y1="4" x2="50" y2="12" stroke="hsl(186 100% 50% / 0.8)" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
};
