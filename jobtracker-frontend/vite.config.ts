// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import fs from "fs";
import path from "path";

// Adjust the paths below if your cert/key live elsewhere
const certFile = path.resolve("../", "localhost.pem");
const keyFile = path.resolve("../", "localhost-key.pem");

export default defineConfig({
  plugins: [react()],
  server: {
    https: {
      key: fs.readFileSync(keyFile),
      cert: fs.readFileSync(certFile),
    },
    port: 5173,
    // You may want to define your API proxy here as well so you avoid CORS
    // proxy: {
    //   "/api": {
    //     target: "https://localhost:8000",
    //     changeOrigin: true,
    //     secure: false,  // since we're using a self-signed cert
    //   },
    // },
  },
});