import { useMemo } from "react";
import Particles, { ParticlesProvider } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import type { Engine, ISourceOptions } from "@tsparticles/engine";

// Koyu/açık hero için "constellation / partikül-ağ" arka planı.
// Referans görseldeki (three.js/unicorn.studio tarzı) bağlantılı nokta ağı.
// tsParticles v4 API: <ParticlesProvider init={...}> sarmalar, içinde <Particles/>.
// Renkler temaya göre CSS değişkenlerinden okunur (açık modda daha koyu bağlantılar).

async function initEngine(engine: Engine) {
  await loadSlim(engine);
}

// Aktif tema için partikül renklerini <html>'nin computed stilinden alır.
function readParticleColors(theme: string) {
  const s = getComputedStyle(document.documentElement);
  const v = (name: string, fallback: string) =>
    s.getPropertyValue(name).trim() || fallback;
  return {
    dots: [
      v("--particle-color-1", "#818cf8"),
      v("--particle-color-2", "#38bdf8"),
      v("--particle-color-3", "#c7d2fe"),
    ],
    link: v("--particle-link", "#4f5b93"),
    // açık modda bağlantılar daha az saydam olmalı ki görünsün
    linkOpacity: theme === "light" ? 0.5 : 0.35,
  };
}

export default function ParticleBackground({ theme }: { theme: string }) {
  const options: ISourceOptions = useMemo(() => {
    const c = readParticleColors(theme);
    return {
      fpsLimit: 60,
      detectRetina: true,
      background: { color: "transparent" },
      particles: {
        number: { value: 70, density: { enable: true } },
        color: { value: c.dots },
        links: {
          enable: true,
          distance: 150,
          color: c.link,
          opacity: c.linkOpacity,
          width: 1,
        },
        move: {
          enable: true,
          speed: 0.7,
          direction: "none",
          outModes: { default: "bounce" },
        },
        opacity: {
          value: { min: 0.3, max: 0.8 },
          animation: { enable: true, speed: 0.6, sync: false },
        },
        size: { value: { min: 1, max: 2.6 } },
      },
      interactivity: {
        events: {
          onHover: { enable: true, mode: "grab" },
        },
        modes: {
          grab: { distance: 160, links: { opacity: 0.6 } },
        },
      },
    };
  }, [theme]);

  return (
    // key ile temaya göre yeniden kur -> yeni renkler uygulansın
    <ParticlesProvider init={initEngine}>
      <Particles
        key={theme}
        id="tsparticles"
        className="hero-particles"
        options={options}
      />
    </ParticlesProvider>
  );
}
