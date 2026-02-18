import { MeshBackground } from "@/components/MeshBackground";
import { VerificationConsole } from "@/components/VerificationConsole";
const Index = () => {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="text-center">
        <h1 className="mb-4 text-4xl font-bold">Welcome to Your Blank App</h1>
        <p className="text-xl text-muted-foreground">Start building your amazing project here!</p>
      </div>
    <div className="relative min-h-screen overflow-x-hidden"
      style={{ background: "hsl(220 40% 3%)" }}>
      {/* Animated matrix + mesh background */}
      <MeshBackground />
      {/* Main content layer */}
      <main className="relative flex flex-col items-center justify-start pt-4 pb-12"
        style={{ zIndex: 10 }}>
        <VerificationConsole />
      </main>
    </div>
  );