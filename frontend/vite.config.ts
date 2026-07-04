import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Backend'e (http://localhost:8000) /api önekiyle proxy.
// Böylece frontend fetch("/api/analyze") çağırır, CORS derdi minimize olur.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
