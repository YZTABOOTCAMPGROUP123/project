import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Backend'e (http://localhost:8000) /api önekiyle proxy.
// NOT: backend route'ları da /api altında (APIRouter prefix). Bu yüzden path'i
// YENİDEN YAZMIYORUZ — lokal ve Vercel aynı /api/* yolunu kullansın diye.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
