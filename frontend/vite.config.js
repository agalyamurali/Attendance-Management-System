import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Standard Vite + React config. No extra plugins — the project spec
// explicitly asks us to avoid unnecessary frontend libraries.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
});
