import { useEffect, useRef } from "react";
interface Drop {
  x: number;
  y: number;
  speed: number;
  chars: string[];
  opacity: number;
  color: string;
}
export const MeshBackground = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);
    const charSet = "01アイウエオカキ∑∆Ω≈∫◆■▲▼←→↑↓⊕⊗∧∨¬≡≠≤≥";
    const cols = Math.floor(canvas.width / 22);
    const drops: Drop[] = [];
    for (let i = 0; i < cols; i++) {
      drops.push({
        x: i * 22 + 4,
        y: Math.random() * -canvas.height,
        speed: 0.3 + Math.random() * 0.8,
        chars: Array.from({ length: 20 }, () => charSet[Math.floor(Math.random() * charSet.length)]),
        opacity: 0.04 + Math.random() * 0.06,
        color: Math.random() > 0.85 ? "0, 255, 136" : "0, 229, 255",
      });
    }
    let animId: number;
    const draw = () => {
      ctx.fillStyle = "rgba(5, 8, 14, 0.08)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.font = "11px 'JetBrains Mono', monospace";
      drops.forEach((drop) => {
        drop.chars.forEach((char, j) => {
          const alpha = drop.opacity * (1 - j / drop.chars.length);
          ctx.fillStyle = `rgba(${drop.color}, ${alpha})`;
          ctx.fillText(char, drop.x, drop.y + j * 16);
        });
        drop.y += drop.speed;
        if (drop.y > canvas.height + 200) {
          drop.y = -Math.random() * 400;
          drop.chars = Array.from({ length: 20 }, () => charSet[Math.floor(Math.random() * charSet.length)]);
        }
        // Randomly mutate chars
        if (Math.random() < 0.02) {
          const idx = Math.floor(Math.random() * drop.chars.length);
          drop.chars[idx] = charSet[Math.floor(Math.random() * charSet.length)];
        }
      });
      animId = requestAnimationFrame(draw);
    };
    draw();
    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
    };
  }, []);
  return (
    <>
      {/* Matrix canvas */}
      <canvas
        ref={canvasRef}
        className="fixed inset-0 pointer-events-none"
        style={{ opacity: 0.7, zIndex: 0 }}
      />
      {/* Grid overlay */}
      <div
        className="fixed inset-0 pointer-events-none mesh-grid"
        style={{ zIndex: 1, opacity: 0.6 }}
      />
      {/* Radial gradient overlays */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          zIndex: 2,
          background:
            "radial-gradient(ellipse 60% 50% at 50% 50%, transparent 0%, hsl(220 40% 3% / 0.4) 60%, hsl(220 40% 3% / 0.9) 100%)",
        }}
      />
      {/* Ambient glow spots */}
      <div
        className="fixed pointer-events-none"
        style={{
          zIndex: 2,
          top: "10%",
          left: "20%",
          width: 400,
          height: 400,
          borderRadius: "50%",
          background: "radial-gradient(circle, hsl(186 100% 50% / 0.04) 0%, transparent 70%)",
        }}
      />
      <div
        className="fixed pointer-events-none"
        style={{
          zIndex: 2,
          bottom: "10%",
          right: "15%",
          width: 300,
          height: 300,
          borderRadius: "50%",
          background: "radial-gradient(circle, hsl(145 100% 50% / 0.04) 0%, transparent 70%)",
        }}
      />
    </>
  );
};