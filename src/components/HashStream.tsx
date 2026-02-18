import { useState, useEffect, useRef } from "react";
interface HashStreamProps {
  hash?: string;
  active?: boolean;
  className?: string;
}
const generateHash = () => {
  const chars = "0123456789abcdef";
  return Array.from({ length: 64 }, () => chars[Math.floor(Math.random() * chars.length)]).join("");
};
export const HashStream = ({ hash, active = false, className = "" }: HashStreamProps) => {
  const [displayHash, setDisplayHash] = useState(hash || generateHash());
  const intervalRef = useRef<ReturnType<typeof setInterval>>(null);
  useEffect(() => {
    if (active) {
      intervalRef.current = setInterval(() => {
        setDisplayHash(generateHash());
      }, 80);
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (hash) setDisplayHash(hash);
    }
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [active, hash]);
  return (
    <div className={`font-mono text-[11px] leading-relaxed break-all select-all ${className}`}
      style={{ color: active ? "hsl(45 100% 55%)" : "hsl(145 100% 50%)" }}>
      <span style={{ 
        filter: active ? "drop-shadow(0 0 4px hsl(45 100% 55%))" : "drop-shadow(0 0 3px hsl(145 100% 50%))",
        opacity: active ? 0.9 : 0.8 
      }}>
        {displayHash.match(/.{1,8}/g)?.map((chunk, i) => (
          <span key={i} className="inline-block">
            {chunk}{i < 7 ? " " : ""}
          </span>
        ))}
      </span>
    </div>
  );
};
interface TypewriterProps {
  lines: string[];
  speed?: number;
  className?: string;
}
export const TypewriterLog = ({ lines, speed = 40, className = "" }: TypewriterProps) => {
  const [displayed, setDisplayed] = useState<string[]>([]);
  const [currentLine, setCurrentLine] = useState(0);
  const [currentChar, setCurrentChar] = useState(0);
  useEffect(() => {
    if (currentLine >= lines.length) return;
    if (currentChar < lines[currentLine].length) {
      const t = setTimeout(() => {
        setDisplayed((prev) => {
          const updated = [...prev];
          if (!updated[currentLine]) updated[currentLine] = "";
          updated[currentLine] = lines[currentLine].slice(0, currentChar + 1);
          return updated;
        });
        setCurrentChar((c) => c + 1);
      }, speed);
      return () => clearTimeout(t);
    } else {
      const t = setTimeout(() => {
        setCurrentLine((l) => l + 1);
        setCurrentChar(0);
      }, speed * 3);
      return () => clearTimeout(t);
    }
  }, [currentLine, currentChar, lines, speed]);
  return (
    <div className={`font-mono text-xs space-y-0.5 ${className}`}>
      {displayed.map((line, i) => (
        <div key={i} className="flex items-start gap-2">
          <span style={{ color: "hsl(186 100% 50% / 0.4)" }}>›</span>
          <span style={{ color: "hsl(145 100% 50% / 0.8)" }}>{line}</span>
          {i === displayed.length - 1 && i === currentLine && (
            <span className="animate-type-cursor" style={{ color: "hsl(186 100% 50%)" }}>█</span>
          )}
        </div>
      ))}
    </div>
  );
};
