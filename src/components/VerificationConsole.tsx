import { useState, useEffect } from "react";
import { ScanRing } from "./ScanRing";
import { HashStream, TypewriterLog } from "./HashStream";
import { ShieldIcon, NeuralIcon, VerifyIcon, HashIcon, BadgeIcon, ScanIcon } from "./CyberIcons";
import { AuthenticLogo } from "./AuthenticLogo";
type VerificationStatus = "idle" | "scanning" | "verified" | "failed";
interface VerificationResult {
  status: "verified" | "failed";
  score: number;
  hash: string;
  timestamp: string;
  flags: string[];
}
const SCAN_LOGS = [
  "Initializing cryptographic verifier v3.1.4...",
  "Loading ECDSA-SECP256k1 validation module...",
  "Connecting to distributed trust network...",
  "Establishing secure channel...",
  "Parsing content payload...",
  "Computing SHA-256 hash fingerprint...",
  "Cross-referencing signature database...",
  "Running neural authenticity analysis...",
  "Validating temporal consistency...",
  "Aggregating trust signals...",
];
const SAMPLE_CONTENTS = [
  "🛡️ Zero-day vulnerabilities are the ghost passages of software architecture. They exist before anyone knows to look for them. Always audit your dependencies.",
  "AI-powered vishing attacks are cloning voices with 99.7% fidelity. If your CEO is asking for gift cards over the phone — that's not your CEO.",
  "Multi-factor authentication isn't magic. A well-placed reverse proxy can still intercept your session token. MFA buys time, not immunity.",
];
export const VerificationConsole = () => {
  const [inputText, setInputText] = useState("");
  const [status, setStatus] = useState<VerificationStatus>("idle");
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [scanLogs, setScanLogs] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<"verify" | "logs" | "network">("verify");
  const [stats, setStats] = useState({ verified: 2847, flagged: 193, pending: 12 });
  const [hoveredSample, setHoveredSample] = useState<number | null>(null);
  const runScan = async () => {
    if (!inputText.trim()) return;
    setStatus("scanning");
    setResult(null);
    setScanLogs([]);
    for (let i = 0; i < SCAN_LOGS.length; i++) {
      await new Promise((r) => setTimeout(r, 280 + Math.random() * 200));
      setScanLogs((prev) => [...prev, SCAN_LOGS[i]]);
    }
    await new Promise((r) => setTimeout(r, 400));
    const isVerified = Math.random() > 0.35;
    const score = isVerified ? 78 + Math.floor(Math.random() * 22) : 12 + Math.floor(Math.random() * 38);
    const hash = Array.from({ length: 64 }, () => "0123456789abcdef"[Math.floor(Math.random() * 16)]).join("");
    setResult({
      status: isVerified ? "verified" : "failed",
      score,
      hash,
      timestamp: new Date().toISOString(),
      flags: isVerified
        ? ["ECDSA_VALID", "NEURAL_PASS", "TEMPORAL_OK", "SOURCE_TRUSTED"]
        : ["SIGNATURE_MISMATCH", "ORIGIN_UNKNOWN", "ANOMALY_DETECTED"],
    });
    setStatus(isVerified ? "verified" : "failed");
    setStats((s) => ({
      verified: isVerified ? s.verified + 1 : s.verified,
      flagged: !isVerified ? s.flagged + 1 : s.flagged,
      pending: Math.max(0, s.pending - 1),
    }));
  };
  const reset = () => {
    setStatus("idle");
    setResult(null);
    setScanLogs([]);
    setInputText("");
  };
  const tabs = ["verify", "logs", "network"] as const;
  return (
    <div className="relative w-full max-w-6xl mx-auto px-4" style={{ zIndex: 10 }}>
      {/* === HEADER NAV === */}
      <header className="flex items-center justify-between py-6 mb-8">
        <div className="flex items-center gap-3">
          <AuthenticLogo size={40} animated />
          <div>
            <div className="font-display font-bold text-lg tracking-tight gradient-text-cyan">
              AuthenticAI
            </div>
            <div className="font-mono text-[10px] tracking-[0.2em]"
              style={{ color: "hsl(186 100% 50% / 0.5)" }}>
              TRUTH·VERIFICATION·SYSTEM
            </div>
          </div>
        </div>
        {/* System status indicators */}
        <div className="flex items-center gap-4">
          {[
            { label: "NEURAL", active: true },
            { label: "CHAIN", active: true },
            { label: "SYNC", active: status === "scanning" },
          ].map(({ label, active }) => (
            <div key={label} className="flex items-center gap-1.5">
              <div
                className="w-1.5 h-1.5 rounded-full"
                style={{
                  background: active ? "hsl(145 100% 50%)" : "hsl(220 20% 30%)",
                  boxShadow: active ? "0 0 6px hsl(145 100% 50%)" : "none",
                  animation: active && status === "scanning" && label === "SYNC"
                    ? "glowPulse 0.8s ease-in-out infinite" : undefined,
                }}
              />
              <span className="font-mono text-[10px] tracking-widest"
                style={{ color: "hsl(220 20% 40%)" }}>{label}</span>
            </div>
          ))}
        </div>
        {/* Nav links */}
        <nav className="hidden md:flex items-center gap-6">
          {["DOCS", "API", "NODES", "ABOUT"].map((item) => (
            <button
              key={item}
              className="font-mono text-[11px] tracking-[0.2em] transition-all duration-200"
              style={{ color: "hsl(220 20% 40%)" }}
              onMouseEnter={(e) => {
                (e.target as HTMLElement).style.color = "hsl(186 100% 50%)";
                (e.target as HTMLElement).style.textShadow = "0 0 12px hsl(186 100% 50% / 0.6)";
              }}
              onMouseLeave={(e) => {
                (e.target as HTMLElement).style.color = "hsl(220 20% 40%)";
                (e.target as HTMLElement).style.textShadow = "none";
              }}
            >
              {item}
            </button>
          ))}
        </nav>
      </header>
      {/* === STATS ROW === */}
      <div className="grid grid-cols-3 gap-3 mb-8">
        {[
          { label: "VERIFIED", value: stats.verified.toLocaleString(), color: "hsl(145 100% 50%)", icon: <VerifyIcon size={16} glow="green" /> },
          { label: "FLAGGED", value: stats.flagged.toLocaleString(), color: "hsl(355 100% 55%)", icon: <ShieldIcon size={16} glow="red" /> },
          { label: "PENDING", value: stats.pending.toLocaleString(), color: "hsl(45 100% 55%)", icon: <ScanIcon size={16} glow="amber" /> },
        ].map(({ label, value, color, icon }) => (
          <div key={label} className="glass rounded-lg p-4 flex items-center gap-3 animate-float"
            style={{ boxShadow: "0 4px 24px hsl(220 40% 0% / 0.4)" }}>
            <div className="p-2 rounded" style={{ background: `${color.replace(")", " / 0.1)")}` }}>
              {icon}
            </div>
            <div>
              <div className="font-mono text-[10px] tracking-[0.2em]"
                style={{ color: "hsl(220 20% 40%)" }}>{label}</div>
              <div className="font-display font-bold text-xl" style={{ color }}>{value}</div>
            </div>
          </div>
        ))}
      </div>
      {/* === MAIN CONSOLE === */}
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_280px] gap-6">
        {/* LEFT: Verification chamber */}
        <div className="flex flex-col gap-4">
          {/* Console header tabs */}
          <div className="glass rounded-t-xl px-4 pt-3 pb-0 flex items-center gap-0 border-b"
            style={{ borderColor: "hsl(186 100% 50% / 0.08)" }}>
            {tabs.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className="px-4 pb-3 font-mono text-[11px] tracking-[0.15em] uppercase transition-all duration-200 border-b-2"
                style={{
                  borderColor: activeTab === tab ? "hsl(186 100% 50%)" : "transparent",
                  color: activeTab === tab ? "hsl(186 100% 50%)" : "hsl(220 20% 35%)",
                }}
              >
                {tab}
              </button>
            ))}
            <div className="ml-auto flex items-center gap-2 pb-3">
              <div className="w-2 h-2 rounded-full" style={{ background: "hsl(355 100% 55%)", boxShadow: "0 0 4px hsl(355 100% 55%)" }} />
              <div className="w-2 h-2 rounded-full" style={{ background: "hsl(45 100% 55%)", boxShadow: "0 0 4px hsl(45 100% 55%)" }} />
              <div className="w-2 h-2 rounded-full" style={{ background: "hsl(145 100% 50%)", boxShadow: "0 0 4px hsl(145 100% 50%)" }} />
            </div>
          </div>
          {/* Console body */}
          <div className="glass glass-strong rounded-b-xl rounded-t-none p-6 flex flex-col gap-5 min-h-[420px]"
            style={{ boxShadow: "0 8px 40px hsl(220 40% 0% / 0.6)" }}>
            {activeTab === "verify" && (
              <>
                {/* Input zone */}
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <HashIcon size={14} glow="cyan" />
                    <span className="font-mono text-[10px] tracking-[0.2em]"
                      style={{ color: "hsl(186 100% 50% / 0.6)" }}>
                      CONTENT INPUT — VERIFICATION TARGET
                    </span>
                  </div>
                  <div className="relative">
                    <textarea
                      value={inputText}
                      onChange={(e) => setInputText(e.target.value)}
                      placeholder="Paste content to verify authenticity..."
                      disabled={status === "scanning"}
                      rows={5}
                      className="w-full rounded-lg p-4 font-mono text-sm resize-none transition-all duration-200"
                      style={{
                        background: "hsl(220 40% 4%)",
                        border: "1px solid hsl(186 100% 50% / 0.15)",
                        color: "hsl(186 60% 85%)",
                        outline: "none",
                        caretColor: "hsl(186 100% 50%)",
                      }}
                      onFocus={(e) => {
                        e.target.style.borderColor = "hsl(186 100% 50% / 0.4)";
                        e.target.style.boxShadow = "0 0 0 1px hsl(186 100% 50% / 0.2), inset 0 0 20px hsl(186 100% 50% / 0.03)";
                      }}
                      onBlur={(e) => {
                        e.target.style.borderColor = "hsl(186 100% 50% / 0.15)";
                        e.target.style.boxShadow = "none";
                      }}
                    />
                    {status === "scanning" && (
                      <div className="absolute inset-0 rounded-lg pointer-events-none overflow-hidden">
                        <div
                          className="absolute left-0 right-0 h-[2px]"
                          style={{
                            background: "linear-gradient(90deg, transparent, hsl(45 100% 55% / 0.8), transparent)",
                            animation: "scanBeam 2s ease-in-out infinite",
                          }}
                        />
                      </div>
                    )}
                  </div>
                </div>
                {/* Sample presets */}
                <div>
                  <div className="font-mono text-[10px] tracking-[0.2em] mb-2"
                    style={{ color: "hsl(220 20% 30%)" }}>
                    — SAMPLE CONTENT PRESETS —
                  </div>
                  <div className="flex flex-col gap-1.5">
                    {SAMPLE_CONTENTS.map((content, i) => (
                      <button
                        key={i}
                        onClick={() => setInputText(content)}
                        onMouseEnter={() => setHoveredSample(i)}
                        onMouseLeave={() => setHoveredSample(null)}
                        className="text-left px-3 py-2 rounded font-mono text-[11px] transition-all duration-200 truncate"
                        style={{
                          background: hoveredSample === i ? "hsl(186 100% 50% / 0.06)" : "transparent",
                          border: "1px solid",
                          borderColor: hoveredSample === i ? "hsl(186 100% 50% / 0.3)" : "hsl(220 30% 12%)",
                          color: hoveredSample === i ? "hsl(186 80% 75%)" : "hsl(220 20% 35%)",
                        }}
                      >
                        <span style={{ color: "hsl(186 100% 50% / 0.4)" }}>PRESET_{i + 1} › </span>
                        {content.slice(0, 80)}…
                      </button>
                    ))}
                  </div>
                </div>
                {/* Action buttons */}
                <div className="flex gap-3 mt-auto">
                  <button
                    onClick={runScan}
                    disabled={!inputText.trim() || status === "scanning"}
                    className="flex-1 flex items-center justify-center gap-2 py-3 rounded-lg font-mono text-sm tracking-[0.1em] font-semibold transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed"
                    style={{
                      background: status === "scanning"
                        ? "hsl(45 100% 55% / 0.1)"
                        : "linear-gradient(135deg, hsl(186 100% 50% / 0.15), hsl(210 100% 60% / 0.1))",
                      border: "1px solid",
                      borderColor: status === "scanning" ? "hsl(45 100% 55% / 0.5)" : "hsl(186 100% 50% / 0.4)",
                      color: status === "scanning" ? "hsl(45 100% 55%)" : "hsl(186 100% 50%)",
                      boxShadow: status !== "scanning" && inputText ? "0 0 20px hsl(186 100% 50% / 0.15)" : "none",
                    }}
                  >
                    <ScanIcon size={16} glow={status === "scanning" ? "amber" : "cyan"} />
                    {status === "scanning" ? "SCANNING..." : "INITIATE SCAN"}
                  </button>
                  {status !== "idle" && (
                    <button
                      onClick={reset}
                      className="px-4 py-3 rounded-lg font-mono text-sm tracking-widest transition-all duration-200"
                      style={{
                        border: "1px solid hsl(220 30% 18%)",
                        color: "hsl(220 20% 40%)",
                      }}
                      onMouseEnter={(e) => {
                        (e.target as HTMLElement).style.borderColor = "hsl(355 100% 55% / 0.4)";
                        (e.target as HTMLElement).style.color = "hsl(355 100% 55%)";
                      }}
                      onMouseLeave={(e) => {
                        (e.target as HTMLElement).style.borderColor = "hsl(220 30% 18%)";
                        (e.target as HTMLElement).style.color = "hsl(220 20% 40%)";
                      }}
                    >
                      RESET
                    </button>
                  )}
                </div>
              </>
            )}
            {activeTab === "logs" && (
              <div>
                <div className="font-mono text-[10px] tracking-[0.2em] mb-4"
                  style={{ color: "hsl(186 100% 50% / 0.4)" }}>
                  — SYSTEM EVENT LOG —
                </div>
                <div className="space-y-1">
                  {[
                    "2026-02-18T04:23:11Z · VERIFY · Content ID #a7f2b9 — AUTHENTICATED",
                    "2026-02-18T04:18:44Z · ALERT  · Content ID #3c91de — SIGNATURE_MISMATCH",
                    "2026-02-18T04:12:02Z · VERIFY · Content ID #8e4fa1 — AUTHENTICATED",
                    "2026-02-18T04:07:55Z · VERIFY · Content ID #2d7bc3 — AUTHENTICATED",
                    "2026-02-18T03:58:31Z · ALERT  · Content ID #f5a203 — AI_GENERATED_FLAG",
                    "2026-02-18T03:44:17Z · VERIFY · Content ID #91c6e8 — AUTHENTICATED",
                    "2026-02-18T03:31:09Z · WARN   · Content ID #b48da5 — LOW_CONFIDENCE",
                    "2026-02-18T03:22:40Z · VERIFY · Content ID #6f3e91 — AUTHENTICATED",
                  ].map((log, i) => {
                    const isAlert = log.includes("ALERT");
                    const isWarn = log.includes("WARN");
                    return (
                      <div key={i} className="font-mono text-[11px] py-1 px-2 rounded flex gap-3"
                        style={{
                          background: isAlert ? "hsl(355 100% 55% / 0.04)" : isWarn ? "hsl(45 100% 55% / 0.04)" : "transparent",
                          color: isAlert ? "hsl(355 100% 60%)" : isWarn ? "hsl(45 100% 60%)" : "hsl(145 100% 50% / 0.7)",
                        }}>
                        <span style={{ opacity: 0.5 }}>{log.split("·")[0]}</span>
                        <span>{log.split("·").slice(1).join("·")}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
            {activeTab === "network" && (
              <div>
                <div className="font-mono text-[10px] tracking-[0.2em] mb-4"
                  style={{ color: "hsl(186 100% 50% / 0.4)" }}>
                  — TRUST NETWORK NODES —
                </div>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { id: "NODE-A1", ping: "12ms", status: "online" },
                    { id: "NODE-B7", ping: "34ms", status: "online" },
                    { id: "NODE-C4", ping: "8ms", status: "online" },
                    { id: "NODE-D2", ping: "67ms", status: "degraded" },
                    { id: "NODE-E9", ping: "15ms", status: "online" },
                    { id: "NODE-F3", ping: "—", status: "offline" },
                  ].map(({ id, ping, status: nodeStatus }) => (
                    <div key={id} className="glass rounded p-3 text-center"
                      style={{ borderColor: nodeStatus === "online" ? "hsl(145 100% 50% / 0.1)" : nodeStatus === "degraded" ? "hsl(45 100% 55% / 0.1)" : "hsl(355 100% 55% / 0.1)" }}>
                      <div className="font-mono text-[10px] tracking-widest mb-1"
                        style={{ color: "hsl(220 20% 40%)" }}>{id}</div>
                      <div className="text-lg font-display font-bold"
                        style={{ color: nodeStatus === "online" ? "hsl(145 100% 50%)" : nodeStatus === "degraded" ? "hsl(45 100% 55%)" : "hsl(355 100% 55%)" }}>
                        {ping}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
        {/* RIGHT: Scan chamber */}
        <div className="flex flex-col gap-4">
          {/* Scan ring panel */}
          <div className="glass rounded-xl p-6 flex flex-col items-center gap-4"
            style={{ boxShadow: "0 8px 40px hsl(220 40% 0% / 0.6)" }}>
            <ScanRing size={220} status={status}>
              <div className="flex flex-col items-center gap-2">
                {status === "idle" && <NeuralIcon size={32} glow="cyan" />}
                {status === "scanning" && (
                  <div className="font-mono text-[10px] tracking-widest text-center"
                    style={{ color: "hsl(45 100% 55%)" }}>
                    <div style={{ filter: "drop-shadow(0 0 8px hsl(45 100% 55%))" }}>⟳</div>
                  </div>
                )}
                {status === "verified" && <VerifyIcon size={32} glow="green" />}
                {status === "failed" && <ShieldIcon size={32} glow="red" />}
                {result && (
                  <div className="text-center">
                    <div className="font-display text-2xl font-bold"
                      style={{
                        color: result.status === "verified" ? "hsl(145 100% 50%)" : "hsl(355 100% 55%)",
                        filter: `drop-shadow(0 0 10px ${result.status === "verified" ? "hsl(145 100% 50%)" : "hsl(355 100% 55%)"})`,
                      }}>
                      {result.score}%
                    </div>
                    <div className="font-mono text-[9px] tracking-widest"
                      style={{ color: "hsl(220 20% 35%)" }}>
                      TRUST SCORE
                    </div>
                  </div>
                )}
              </div>
            </ScanRing>
            {/* Trust bar */}
            {result && (
              <div className="w-full">
                <div className="flex justify-between font-mono text-[10px] mb-1"
                  style={{ color: "hsl(220 20% 35%)" }}>
                  <span>TRUST INDEX</span>
                  <span style={{ color: result.status === "verified" ? "hsl(145 100% 50%)" : "hsl(355 100% 55%)" }}>
                    {result.score}/100
                  </span>
                </div>
                <div className="h-1 rounded-full overflow-hidden" style={{ background: "hsl(220 30% 10%)" }}>
                  <div
                    className="h-full rounded-full transition-all duration-1000"
                    style={{
                      width: `${result.score}%`,
                      background: result.status === "verified"
                        ? "linear-gradient(90deg, hsl(145 100% 50%), hsl(186 100% 55%))"
                        : "linear-gradient(90deg, hsl(355 100% 55%), hsl(340 100% 50%))",
                      boxShadow: result.status === "verified"
                        ? "0 0 8px hsl(145 100% 50% / 0.6)"
                        : "0 0 8px hsl(355 100% 55% / 0.6)",
                    }}
                  />
                </div>
              </div>
            )}
          </div>
          {/* Scan logs / hash panel */}
          <div className="glass rounded-xl p-4 flex-1"
            style={{ boxShadow: "0 8px 40px hsl(220 40% 0% / 0.6)" }}>
            <div className="font-mono text-[10px] tracking-[0.2em] mb-3 flex items-center gap-2"
              style={{ color: "hsl(186 100% 50% / 0.4)" }}>
              <HashIcon size={12} glow="cyan" />
              {status === "scanning" ? "SCAN LOG" : result ? "HASH DIGEST" : "AWAITING INPUT"}
            </div>
            {scanLogs.length > 0 && status === "scanning" && (
              <TypewriterLog lines={scanLogs} speed={30} />
            )}
            {result && status !== "scanning" && (
              <div className="space-y-3">
                <HashStream hash={result.hash} active={false} />
                <div className="border-t pt-3" style={{ borderColor: "hsl(220 30% 12%)" }}>
                  <div className="space-y-1.5">
                    {result.flags.map((flag) => (
                      <div key={flag} className="flex items-center gap-2">
                        <div
                          className="w-1 h-1 rounded-full"
                          style={{
                            background: result.status === "verified" ? "hsl(145 100% 50%)" : "hsl(355 100% 55%)",
                            boxShadow: `0 0 4px ${result.status === "verified" ? "hsl(145 100% 50%)" : "hsl(355 100% 55%)"}`,
                          }}
                        />
                        <span className="font-mono text-[11px]"
                          style={{ color: result.status === "verified" ? "hsl(145 100% 50% / 0.7)" : "hsl(355 100% 55% / 0.7)" }}>
                          {flag}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="font-mono text-[10px]" style={{ color: "hsl(220 20% 30%)" }}>
                  TS: {result.timestamp}
                </div>
              </div>
            )}
            {status === "idle" && scanLogs.length === 0 && (
              <div className="flex flex-col gap-1.5">
                {["Awaiting content payload...", "Neural networks: online", "Trust chain: synchronized"].map((msg, i) => (
                  <div key={i} className="font-mono text-[11px] flex gap-2"
                    style={{ color: "hsl(220 20% 28%)" }}>
                    <span style={{ color: "hsl(186 100% 50% / 0.2)" }}>›</span>
                    {msg}
                  </div>
                ))}
              </div>
            )}
          </div>
          {/* Icon system showcase */}
          <div className="glass rounded-xl p-4">
            <div className="font-mono text-[10px] tracking-[0.2em] mb-3"
              style={{ color: "hsl(186 100% 50% / 0.3)" }}>
              — VERIFICATION MODULES —
            </div>
            <div className="grid grid-cols-3 gap-2">
              {[
                { icon: <ShieldIcon size={20} glow="cyan" />, label: "CRYPTO" },
                { icon: <NeuralIcon size={20} glow="cyan" />, label: "NEURAL" },
                { icon: <VerifyIcon size={20} glow="green" />, label: "SIGN" },
                { icon: <HashIcon size={20} glow="cyan" />, label: "HASH" },
                { icon: <BadgeIcon size={20} glow="cyan" />, label: "BADGE" },
                { icon: <ScanIcon size={20} glow="amber" />, label: "SCAN" },
              ].map(({ icon, label }) => (
                <div key={label}
                  className="flex flex-col items-center gap-1 p-2 rounded transition-all duration-200 cursor-default"
                  style={{ border: "1px solid hsl(220 30% 12%)" }}
                  onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.borderColor = "hsl(186 100% 50% / 0.2)"; (e.currentTarget as HTMLElement).style.background = "hsl(186 100% 50% / 0.03)"; }}
                  onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.borderColor = "hsl(220 30% 12%)"; (e.currentTarget as HTMLElement).style.background = "transparent"; }}>
                  {icon}
                  <span className="font-mono text-[9px] tracking-widest"
                    style={{ color: "hsl(220 20% 30%)" }}>{label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      {/* === FOOTER === */}
      <footer className="mt-12 pb-8 flex items-center justify-between">
        <div className="font-mono text-[10px] tracking-[0.2em]"
          style={{ color: "hsl(220 20% 20%)" }}>
          AUTHENTICAI · TRUTH VERIFICATION ENGINE · v3.1.4
        </div>
        <div className="flex items-center gap-3">
          {["SECP256K1", "SHA-256", "ECDSA", "AES-256"].map((tag) => (
            <span key={tag}
              className="font-mono text-[9px] tracking-widest px-2 py-0.5 rounded"
              style={{
                border: "1px solid hsl(186 100% 50% / 0.1)",
                color: "hsl(186 100% 50% / 0.3)",
              }}>
              {tag}
            </span>
          ))}
        </div>
      </footer>
    </div>
  );
};